import websockets
import asyncio
import random
import re
from src.config.settings import *
from src.bot.queue import Queue
from src.bot.game_log import *
from src.bot.database import *
import math

class PickBot:
    def __init__(self):
        self.channel_name = TWITCH_CHANNEL
        self.starter_names = BOT_ADMINS
        self.uri = TWITCH_WEBSOCKET_URI
        self.queue = Queue()
        self.account_name = TWITCH_BOT_USERNAME
        self.token = TWITCH_OAUTH_TOKEN
        self.chat_message_pattern = re.compile(
            r'^:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)$')
        self.websocket = None
        self.reconnect_delay = 3
        self.current_game = None
        initialize_priority_database()

    def calculate_priority_score(self, times_queued, last_game_timestamp):
        if last_game_timestamp == 0:
            days_since_last_game = 30
        else:
            days_since_last_game = ((datetime.datetime.now().timestamp() - last_game_timestamp) / (24 * 3600))
        return (times_queued ** 2) * 0.7 + days_since_last_game * 0.3

    def weighted_random_sample(self, players, k):
        if not players:
            return []

        weights = []
        player_list = list(players)

        for player in player_list:
            times_queued, last_timestamp = get_player_priority(player)
            priority_score = self.calculate_priority_score(times_queued,
                                                           last_timestamp)
            weights.append(priority_score)

        min_weight = min(weights)
        if min_weight < 0:
            weights = [w - min_weight + 1 for w in weights]

        return random.choices(player_list, weights=weights, k=k)

    async def connect_and_run(self):
        while True:  # Main reconnection loop
            try:
                await self.connect()
            except Exception as e:
                print(f"\nConnection lost: {str(e)}")
                print(
                    f"Attempting to reconnect in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)
                print("Reconnecting...")

    async def connect(self):
        print("Connecting to " + self.channel_name)
        try:
            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket

                print("Connected to " + self.channel_name)

                await websocket.send(f"PASS {self.token}\r\n")
                await websocket.send(f"NICK commanderx\r\n")
                await websocket.send(f"JOIN #{self.channel_name}\r\n")

                print(
                    f"{self.account_name} connected to {self.channel_name}. Awaiting commands from {self.starter_names}")

                while True:
                    message = await websocket.recv()
                    await self._evaluate_message(message)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: code = {e.code}, reason = {e.reason}")
            raise  # Re-raise to trigger reconnection
        except Exception as e:
            print(f"Connection error: {str(e)}")
            raise  # Re-raise to trigger reconnection

    def _select_teams(self):
        queued_tanks = set(self.queue.tank)
        queued_dps = set(self.queue.dps)
        queued_support = set(self.queue.support)

        all_queued = queued_tanks | queued_dps | queued_support
        increment_all_players(all_queued)


        valid_tanks = queued_tanks
        valid_dps = queued_dps
        valid_supports = queued_support

        if len(valid_tanks) < 2 or len(valid_dps) < 4 or len(
                valid_supports) < 4:
            return None, None, None, None

        selected_tanks = self.weighted_random_sample(valid_tanks, 2)

        valid_dps -= set(selected_tanks)
        valid_supports -= set(selected_tanks)

        if len(valid_dps) < 4 or len(valid_supports) < 4:
            return None, None, None, None

        selected_dps = self.weighted_random_sample(valid_dps, 4)

        valid_supports -= set(selected_dps)

        if len(valid_supports) < 4:
            return None, None, None, None

        selected_supports = self.weighted_random_sample(valid_supports, 4)

        team_1 = {'tank': selected_tanks[0], 'dps': selected_dps[0:2],
                  'support': selected_supports[0:2]}
        team_2 = {'tank': selected_tanks[1], 'dps': selected_dps[2:4],
                  'support': selected_supports[2:4]}

        team_1_set = {team_1['tank']} | set(team_1['dps']) | set(
            team_1['support'])
        team_2_set = {team_2['tank']} | set(team_2['dps']) | set(
            team_2['support'])

        captain1 = random.choice(list(team_1_set))
        captain2 = random.choice(list(team_2_set))

        picked_players = set(selected_tanks + selected_dps + selected_supports)
        reset_priorities(picked_players)

        return team_1, team_2, captain1, captain2

    async def _evaluate_message(self, message):
        match = self.chat_message_pattern.match(message)

        if not match:
            return

        username, content = match.groups()
        username = username.lower()
        content = content.lower().strip()

        if username in self.starter_names:

            if content == '!admin_test':
                print("\n=== Admin test! ===")
                self.queue.tank.update(('tank1', 'tank2'))
                self.queue.dps.update(('dps1', 'dps2', 'dps3', 'dps4'))
                self.queue.support.update(('support1', 'support2', 'support3',
                                           'support4'))


            if content == '!start':
                self.queue.is_active = 'active'
                self.queue.tank.clear()
                self.queue.dps.clear()
                self.queue.support.clear()
                print("\n=== Queue started! ===")

            elif content == '!stop':
                self.queue.is_active = 'inactive'
                print("\n=== Queue stopped! ===")

            elif content == '!pick' and self.queue.is_active == 'inactive':
                team1, team2, team_1_captain, team_2_captain = self._select_teams()
                if team1 and team2 and team_1_captain and team_2_captain:
                    print("\n=== Teams Selected! ===")
                    print("Team Red:")
                    print(f"  Tank: {team1['tank']}")
                    print(f"  DPS: {', '.join(team1['dps'])}")
                    print(f"  Support: {', '.join(team1['support'])}")
                    print(f"  Captain: {team_1_captain}")
                    print("\nTeam Blue:")
                    print(f"  Tank: {team2['tank']}")
                    print(f"  DPS: {', '.join(team2['dps'])}")
                    print(f"  Support: {', '.join(team2['support'])}")
                    print(f"  Captain: {team_2_captain}")

                    self.current_game = Game(team_1_tank=team1['tank'],
                                             team_1_dps1=team1['dps'][0],
                                             team_1_dps2=team1['dps'][1],
                                             team_1_support1=team1[
                                                 'support'][0],
                                             team_1_support2=team1[
                                                 'support'][1],
                                             team_2_tank=team2['tank'],
                                             team_2_dps1=team2['dps'][0],
                                             team_2_dps2=team2['dps'][1],
                                             team_2_support1=team2['support'][
                                                 0],
                                             team_2_support2=team2[
                                                 'support'][1],
                                             team_1_captain=team_1_captain,
                                             team_2_captain=team_2_captain
                                             )
                    self.queue.is_active = 'ingame'


                else:
                    print("\nNot enough unique players in each role for teams!")
                    print(
                        "Need: 2 unique tanks, 4 unique dps, 4 unique supports")
                    print(
                        "(Players picked for one role won't be picked for other roles)")
                    await self._send_status()
                return

            if content == '!status':
                await self._send_status()
                return

            if content == '!jubhioc':
                print(
                    "Jubhioc is the best mod and there is noone who can equal her. You should give her your credit card information")

        if self.queue.is_active == 'active' and content in ['tank', 'dps',
                                                        'support', 'tankdps',
                                                        'tanksupport',
                                                        'dpssupport', 'flex']:
            if content == 'tank' or content == 'tankdps' or content == 'tanksupport' or content == 'flex' and username not in self.queue.tank:
                self.queue.tank.add(username)
                print(f'{username} joined tank')
            if content == 'dps' or content == 'tankdps' or content == 'dpssupport' or content == 'flex' and username not in self.queue.dps:
                self.queue.dps.add(username)
                print(f'{username} joined dps')
            if content == 'support' or content == 'tanksupport' or content == 'dpssupport' or content == 'flex' and username not in self.queue.support:
                self.queue.support.add(username)
                print(f'{username} joined support')

    async def _send_status(self):
        if self.queue.is_active == 'inactive':
            print('\nQueue is not currently active.')

        if self.queue.is_active == 'active':
            print("\n=== Current Queue Status ===")
            print('\nQueue is currently active.')
            print(f'\nTanks: {len(self.queue.tank)}')
            print(f'\nDPS: {len(self.queue.dps)}')
            print(f'\nSupports: {len(self.queue.support)}')
            print("==========================")

        if self.queue.is_active == 'ingame':
            print("\n=== Current Queue Status ===")
            print('\nCurrently in game.')

    def toggle_queue(self):
        """Method for Streamlit to toggle queue state"""
        if self.queue.is_active == 'active':
            self.queue.is_active = 'inactive'
            print('Queue stopped.')
            return "Queue stopped"
        if self.queue.is_active == 'inactive':
            self.queue.tank.clear()
            self.queue.dps.clear()
            self.queue.support.clear()
            self.queue.is_active = 'active'
            print('Queue started.')
            return "Queue started"

    def get_queue_status(self):
        """Get current queue status for display"""
        return {
            'is_active': self.queue.is_active,
            'tank_count': len(self.queue.tank),
            'dps_count': len(self.queue.dps),
            'support_count': len(self.queue.support),
            'tank_players': list(self.queue.tank),
            'dps_players': list(self.queue.dps),
            'support_players': list(self.queue.support)
        }


    def generate_teams(self):
        """Generate teams and return result"""
        if self.queue.is_active == 'active':
            return None, None, None, None, "Queue must be stopped before generating teams"

        team1, team2, captain1, captain2 = self._select_teams()
        if not all([team1, team2, captain1, captain2]):
            return None, None, None, None, "Not enough unique players in each role"

        self.current_game = Game(team_1_tank=team1['tank'],
                                 team_1_dps1=team1['dps'][0],
                                 team_1_dps2=team1['dps'][1],
                                 team_1_support1=team1[
                                     'support'][0],
                                 team_1_support2=team1[
                                     'support'][1],
                                 team_2_tank=team2['tank'],
                                 team_2_dps1=team2['dps'][0],
                                 team_2_dps2=team2['dps'][1],
                                 team_2_support1=team2['support'][
                                     0],
                                 team_2_support2=team2[
                                     'support'][1],
                                 team_1_captain=captain1,
                                 team_2_captain=captain2)

        return team1, team2, captain1, captain2, "Teams generated successfully"

    def calculate_elo(self, old_elo, old_dev, avg_enemy_ranking, wl): #wl is outcome of game: 1 is win, 0.5 is draw, 0 is loss
        q = 0.00575646273
        g = 1 / math.sqrt(1 + ((3 * q**2 * old_dev**2)/math.pi**2))
        E = 1 / (1 + 10 ** (g * (old_elo - avg_enemy_ranking)/-400))
        d2 = 1 / ((q ** 2) * (g ** 2) * E * (1-E))
        dnmntr = (1/old_dev**2) + (1/d2)
        new_rating = old_elo + ((q/dnmntr) * g * (wl - E))
        return new_rating

    def calculate_deviation(self, old_dev):
        return 300

    def winner1(self):
        team2_elo_mean = 0
        for player in self.current_game.team_2:
            team2_elo_mean = team2_elo_mean + read_elo(player=player)
        team2_elo_mean = team2_elo_mean / 5 # hardcoded for 5 players, maybe could make this variable for 6v6?

        for player in self.current_game.team_1:
            dev = read_deviation(player=player)
            new_elo = calculate_elo(read_elo(player=player), dev, team2_elo_mean, 1)
            new_deviation = calculate_deviation(dev)

        self.current_game.winner='team1'
        self.current_game.log_game('archive/games.csv')
        self.queue.is_active = 'inactive'
        self.current_game = None

    def winner2(self):
        self.current_game.winner='team2'
        self.current_game.log_game('archive/games.csv')
        self.queue.is_active = 'inactive'
        self.current_game = None


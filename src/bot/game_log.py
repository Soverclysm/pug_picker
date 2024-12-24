import csv
from dataclasses import dataclass
import datetime
import os

@dataclass
class Game:
    team_1_tank: str
    team_2_tank: str
    team_1_dps1: str
    team_1_dps2: str
    team_2_dps1: str
    team_2_dps2: str
    team_1_support1: str
    team_1_support2: str
    team_2_support1: str
    team_2_support2: str
    team_1_captain: str
    team_2_captain: str
    timestamp: str = None
    winner: str = None
    players: tuple[str, ...] = None
    team_1: tuple[str, ...] = None
    team_2: tuple[str, ...] = None
    game_id: str = None


    def __post_init__(self):
        self.team_1 = (self.team_1_tank, self.team_1_dps1, self.team_1_dps2,
                       self.team_1_support1, self.team_1_support2)
        self.team_2 = (self.team_2_tank, self.team_2_dps1, self.team_2_dps2,
                       self.team_2_support1, self.team_2_support2)
        self.players = self.team_1 + self.team_2
        timestamp_temp = datetime.datetime.now()
        self.timestamp = timestamp_temp.strftime("%Y%m%d-%H%M%S")
        self.game_id = timestamp_temp.strftime("%Y%m%d%H%M%S")
    def _return_role(self, player):
        if player in [self.team_1_tank, self.team_2_tank]:
            return 'tank'
        if player in [self.team_1_dps1, self.team_1_dps2, self.team_2_dps1,
                      self.team_2_dps2]:
            return 'dps'
        if player in [self.team_1_support1, self.team_1_support2,
                      self.team_2_support1, self.team_2_support2]:
            return 'support'

    def log_game(self, file):
        game_dic = vars(self)

        for player in game_dic['players']:
            player_team = 'team1' if player in game_dic['team_1'] else 'team2'
            player_captain = (player == game_dic['team_1_captain'] or player ==
                              game_dic['team_2_captain'])
            result = int(player_team == game_dic['winner'])

            player_dic = {
                'game_id' : game_dic['game_id'],
                'nickname' : player,
                'role' : self._return_role(player),
                'timestamp' : game_dic['timestamp'],
                'team' : player_team,
                'captain' : player_captain,
                'result' : result
            }

            file_exists = os.path.exists(file)

            with open(file, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=player_dic.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(player_dic)

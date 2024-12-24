import pandas as pd
import numpy as np
import random
import datetime
import csv
import os

players = ['Vestola', 'Chasetorch', 'Kevster', 'FunnyAstro', 'Hadi', 'Rupal',
           'Vega', 'Seeker', 'tr33', 'Kai', 'Quartz', 'Junbin', 'Hanbin',
           'Bliss', 'Twilight', 'Proper', 'Heesang', 'Proud', 'S1mple']


def team_to_csv(team1, team2):
    team_1_dict = {
        'team_1_tank' : team1[0],
        'team_1_dps1': team1[1],
        'team_1_dps2': team1[2],
        'team_1_support1' : team1[3],
        'team_1_support2' : team1[4],
        'team_1_captain' : random.choice(team1)
    }
    team_2_dict = {
        'team_2_tank' : team2[0],
        'team_2_dps1': team2[1],
        'team_2_dps2': team2[2],
        'team_2_support1' : team2[3],
        'team_2_support2' : team2[4],
        'team_2_captain' : random.choice(team2)
    }

    return team_1_dict, team_2_dict

def log_game(team_1_dict, team_2_dict, team1, team2,players):
    game_dict = team_1_dict | team_2_dict
    timestamp_temp = datetime.datetime.now() + datetime.timedelta(minutes =
                                                             random.randint(
                                                                 -1000, 1000))
    timestamp = timestamp_temp.strftime("%Y%m%d-%H%M%S")
    game_id = timestamp_temp.strftime("%Y%m%d%H%M%S")

    team_1 = '|'.join(team1)
    team_2 = '|'.join(team2)
    players = '|'.join(players)
    winner = random.choice(['team1', 'team2'])
    game_dict.update({'team_1' : team_1, 'team_2' : team_2, 'players' :
        players, 'timestamp' : timestamp, 'game_id' : game_id, 'winner': winner})

    return game_dict

def populate_csv(num_matches, player_list, csv_file):
    for match in range(num_matches):
        players = players = random.sample(player_list, k = 10)
        team1 = players[0:5]
        team2 = players[5:10]

        team_1_dict, team_2_dict = team_to_csv(team1, team2)
        game_dict = log_game(team_1_dict, team_2_dict,team1, team2, players)

        file_exists = os.path.exists(csv_file)

        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=game_dict.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(game_dict)


populate_csv(100, players, '../../archive/test.csv')
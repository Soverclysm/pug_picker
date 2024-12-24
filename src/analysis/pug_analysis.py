import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class PUGAnalysis:

    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)

    def _select_players(self, nicknames):
        nicknames = [nicknames]
        print(nicknames)
        return self.data[self.data['nickname'].isin(nicknames)]

    def create_role_distribution(self, nickname):
        player_data = self._select_players(nickname)
        role_distribution = player_data['role'].value_counts()
        # Create pie plot
        plt.figure(figsize=(8, 8))
        plt.pie(role_distribution.values,
                labels=role_distribution.index,
                autopct='%1.1f%%',
                colors=sns.color_palette('pastel'))
        plt.title('Roles distribution')
        plt.axis('equal')
        plt.show()

    def descriptive_statistics(self, nickname):
        player_data = self._select_players(nickname)
        total_games = len(player_data)
        wins = len(player_data[player_data['result'] == 1])
        winrate = wins / total_games if total_games > 0 else 0

        role_distribution = player_data['role'].value_counts()
        role_winrates = player_data.groupby('role')['result'].mean()

        games_as_captain = len(player_data[player_data['captain'] == True])
        captain_winrate = player_data[player_data['captain'] == True &
                                      player_data['result'] == 1].mean()



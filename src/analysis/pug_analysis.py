import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import figaspect


class PUGAnalysis:

    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)

    def _select_players(self, nicknames):
        nicknames = [nicknames] if isinstance(nicknames, str) else list(nicknames)
        return self.data[self.data['nickname'].isin(nicknames)]

    def create_role_distribution(self, nickname):
        player_data = self._select_players(nickname)
        fig, ax = plt.subplots()
        role_distribution = player_data['role'].value_counts()
        # Create pie plot
        ax.pie(role_distribution.values,
                labels=role_distribution.index,
                autopct='%1.1f%%',
                colors=sns.color_palette('pastel'))
        ax.title('Roles distribution')
        ax.axis('equal')
        return fig

    def descriptive_statistics(self, nickname):
        player_data = self._select_players(nickname)
        total_games = len(player_data)
        wins = len(player_data[player_data['result'] == 1])
        winrate = wins / total_games if total_games > 0 else 0

        role_distribution = player_data['role'].value_counts()
        role_winrates = player_data.groupby('role')['result'].mean()

        captain_games = player_data[player_data['captain'] == True]
        captain_games_amount = len(captain_games)
        captain_winrate = captain_games['result'].mean()

        player_stats = {
            'total_games': total_games,
            'wins': wins,
            'winrate': winrate,
            'role_distribution': role_distribution,
            'captain_games_amount': captain_games_amount,
            'captain_winrate': captain_winrate,
            'role_winrates': role_winrates
        }
        return player_stats


    def plot_winrates(self, nickname):
        player_data = self._select_players(nickname)
        fig, ax = plt.subplots()
        sns.barplot(x='role', y='result', data=player_data, estimator=np.mean, ax=ax)
        plt.xlabel('Role')
        plt.ylabel('Result')
        return fig


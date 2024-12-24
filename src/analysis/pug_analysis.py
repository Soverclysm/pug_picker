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

    def _plot_winrates_overlay(self, player_data):
        fig, ax = plt.subplots()
        sns.barplot(data=player_data, x=' ', y='result', estimator=np.mean,hue='nickname', ax=ax)
        ax.set_xticks([])
        return fig, ax

    def _plot_winrates_separate(self, player_data):
        g = sns.FacetGrid(player_data, col='nickname')
        g.map(sns.barplot, x = ' ', y = 'result', estimator = np.mean)
        for ax in g.axes.flat:
            ax.set_xticks([])
            ax.set_ylabel('Winrate')
        return g.fig

    def plot_winrates(self, players, style = 'separate'):
        if style == 'overlay':
            fig = self._plot_winrates_overlay(players)
        if style == 'separate':
            fig = self._plot_winrates_separate(players)
        return fig




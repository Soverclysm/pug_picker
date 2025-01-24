import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def load_data(file_path='archive/games.csv'):
    """Load and preprocess the game data"""
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'],
                                         format='%Y%m%d-%H%M%S')
        return df
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")


def plot_winrates(data, players):
    """
    Plot winrates vs total games played for selected players.

    Args:
        data (pd.DataFrame): DataFrame containing game data
        players (list): List of player nicknames to include in the plot

    Returns:
        matplotlib.figure.Figure or None: The plot figure, or None if no data available
    """
    player_data = data[data['nickname'].isin(players)].copy()

    if len(player_data) == 0:
        return None

    # Split up the groupby operation
    grouped = player_data.groupby('nickname')
    player_games = grouped.agg({'game_id': 'nunique'})
    player_winrate = grouped.agg({'result': 'mean'})

    # Combine the results
    player_stats = pd.DataFrame()
    player_stats['game_id'] = player_games['game_id']
    player_stats['result'] = player_winrate['result']
    player_stats = player_stats.reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.scatterplot(
        data=player_stats,
        x='game_id',
        y='result',
        ax=ax,
        s=100
    )

    for _, row in player_stats.iterrows():
        ax.annotate(
            row['nickname'],
            (row['game_id'], row['result']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=10,
            alpha=0.8
        )

    ax.set_title('Player Winrate vs Games Played')
    ax.set_xlabel('Total Games Played')
    ax.set_ylabel('Win Rate')

    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    return fig


def calculate_player_stats(data, player):
    """Calculate detailed statistics for a player"""
    player_games = data[data['nickname'] == player]

    total_games = len(player_games)
    wins = len(player_games[player_games['result'] == 1])
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0

    role_stats = player_games['role'].value_counts()
    roles_list = []
    for role, count in role_stats.items():
        roles_list.append(f"{role}: {count}")
    roles = ', '.join(roles_list)

    captain_filter = player_games['captain'] == True
    captain_games = len(player_games[captain_filter])

    return {
        'Player': player,
        'Total Games': total_games,
        'Wins': wins,
        'Win Rate': f"{win_rate:.1f}%",
        'Roles Played': roles,
        'Times as Captain': captain_games
    }


def main():
    st.title("PUG Statistics Analysis")

    if 'data' not in st.session_state:
        try:
            st.session_state.data = load_data()
            st.session_state.all_players = sorted(
                st.session_state.data['nickname'].unique())
        except Exception as e:
            st.error(str(e))
            return

    with st.sidebar:
        st.header("Analysis Controls")

        min_date = st.session_state.data['timestamp'].min()
        max_date = st.session_state.data['timestamp'].max()

        date_range = st.date_input(
            "Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        selected_roles = st.multiselect(
            "Filter by Role",
            options=sorted(st.session_state.data['role'].unique()),
            default=sorted(st.session_state.data['role'].unique())
        )

        date_mask = st.session_state.data['timestamp'].dt.date >= date_range[0]
        date_mask = date_mask & (
                    st.session_state.data['timestamp'].dt.date <= date_range[1])
        role_mask = st.session_state.data['role'].isin(selected_roles)
        filtered_data = st.session_state.data[date_mask & role_mask]

        available_players = sorted(filtered_data['nickname'].unique())

        selected_players = st.multiselect(
            "Select Players to Analyze",
            options=available_players,
            default=available_players[:2] if len(
                available_players) >= 2 else None
        )

    if not selected_players:
        st.warning("Please select at least one player to analyze")
        return

    try:
        st.header("Player Win Rates")
        fig = plot_winrates(filtered_data, selected_players)
        if fig:
            st.pyplot(fig)

        st.header("Player Statistics")
        stats = []
        for player in selected_players:
            stats.append(calculate_player_stats(filtered_data, player))

        if stats:
            st.dataframe(pd.DataFrame(stats))

        st.header("Recent Games")

        player_filter = filtered_data['nickname'].isin(selected_players)
        player_games = filtered_data[player_filter]
        game_ids = player_games['game_id'].unique()
        recent_game_ids = sorted(game_ids, reverse=True)[:10]

        if len(recent_game_ids) > 0:
            recent_games = filtered_data[
                filtered_data['game_id'].isin(recent_game_ids)]

            for game_id in recent_game_ids:
                game_data = recent_games[recent_games['game_id'] == game_id]
                timestamp_str = game_data['timestamp'].iloc[0].strftime(
                    '%Y-%m-%d %H:%M')

                with st.expander(f"Game {game_id} - {timestamp_str}"):
                    cols = st.columns(2)

                    with cols[0]:
                        st.subheader("Team 1")
                        team1_data = game_data[game_data['team'] == 'team1']
                        team1_sorted = team1_data.sort_values('role')

                        for role in ['tank', 'dps', 'support']:
                            role_players = team1_sorted[
                                team1_sorted['role'] == role]
                            for _, player in role_players.iterrows():
                                is_selected = player[
                                                  'nickname'] in selected_players
                                highlighted = "**" if is_selected else ""
                                is_captain = " (Captain)" if player[
                                    'captain'] else ""
                                st.write(
                                    f"{role.upper()}: {highlighted}{player['nickname']}{highlighted}{is_captain}")

                    with cols[1]:
                        st.subheader("Team 2")
                        team2_data = game_data[game_data['team'] == 'team2']
                        team2_sorted = team2_data.sort_values('role')

                        for role in ['tank', 'dps', 'support']:
                            role_players = team2_sorted[
                                team2_sorted['role'] == role]
                            for _, player in role_players.iterrows():
                                is_selected = player[
                                                  'nickname'] in selected_players
                                highlighted = "**" if is_selected else ""
                                is_captain = " (Captain)" if player[
                                    'captain'] else ""
                                st.write(
                                    f"{role.upper()}: {highlighted}{player['nickname']}{highlighted}{is_captain}")

                    team1_result = \
                    game_data[game_data['team'] == 'team1'].iloc[0]['result']
                    winner = "Team 1" if team1_result == 1 else "Team 2"
                    st.write(f"Winner: {winner}")

    except Exception as e:
        st.error(f"Error generating analysis: {str(e)}")


if __name__ == "__main__":
    main()
import sqlite3
import datetime
from src.config import *

def initialize_elo_database(self, file):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_ratings (
        nickname TEXT PRIMARY KEY,
        elo INTEGER DEFAULT 1500,
        peak_elo INTEGER DEFAULT 1500,
        games_played INTEGER DEFAULT 0,
        last_updated INTEGER DEFAULT 0,
        last_deviation REAL DEFAULT 300
    )
    ''')

    conn.commit()
    conn.close()


def read_elo(self, file, player, change):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO player_ratings (nickname) VALUES (?)''',
                   (player,))
    cursor.execute('SELECT elo FROM player_ratings WHERE nickname = ?',
                   (player,))
    elo = cursor.fetchone()[0]

    conn.commit()
    conn.close()
    return elo


def update_elo( file, player, elo, deviation):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    conn.execute('''UPDATE player_ratings SET elo = ?, last_updated = ?, last_deviation = ? 
    WHERE 
    nickname = ?''',
                 (elo, timestamp, deviation, player))

    conn.commit()
    conn.close()

def read_deviation(self, file, player, change):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO player_ratings (nickname) VALUES (?)''',
                   (player,))
    cursor.execute('SELECT last_deviation FROM player_ratings WHERE nickname = ?',
                   (player,))
    elo = cursor.fetchone()[0]

    conn.commit()
    conn.close()
    return elo

def initialize_priority_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS player_priority ("
                   "nickname TEXT PRIMARY KEY,"
                   "times_queued INTEGER DEFAULT 0,"
                   "last_game_time INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

def get_player_priority(name):
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO player_priority (nickname) VALUES (?)",
                       (name,))
        cursor.execute("SELECT times_queued, last_game_time FROM "
                       "player_priority WHERE nickname = ?", (name,))
        result = cursor.fetchone()

        conn.commit()
        return result
    finally:
        conn.close()

def increment_all_players(queued_players):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        for player in queued_players:
            cursor.execute("INSERT OR IGNORE INTO player_priority (nickname) VALUES (?)",
                           (player,))
        cursor.execute('UPDATE player_priority SET times_queued = times_queued + 1 WHERE nickname IN ({})'.format(','.join('?' * len(queued_players))), queued_players)

        conn.commit()
    finally:
        conn.close()

def reset_priorities(picked_players):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        timestamp = int(datetime.datetime.now().timestamp())
        cursor.execute('UPDATE player_priority SET times_queued = 0, last_game_time = ? WHERE nickname IN ({})'.format(','.join('?' * len(picked_players))), [timestamp] + list(picked_players))
        conn.commit()

    finally:
        conn.close()
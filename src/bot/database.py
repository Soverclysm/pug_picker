import sqlite3

def initialize_elo_database(self, file):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_ratings (
        nickname TEXT PRIMARY KEY,
        elo INTEGER DEFAULT 1500,
        peak_elo INTEGER DEFAULT 1500,
        games_played INTEGER DEFAULT 0,
        last_updated INTEGER DEFAULT 0
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


def update_elo(self, file, player, elo):
    conn = sqlite3.connect(file)
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    conn.execute('''UPDATE player_ratings SET elo = ?, last_updated = ? 
    WHERE 
    nickname = ?''',
                 (elo, timestamp, player))

    conn.commit()
    conn.close()

#!/usr/bin/env python3
import sqlite3
import pandas as pd
import os

# Paths relative to project root
top = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(top, "data")
CSV_PATH = os.path.join(DATA_PATH, "players.csv")
DB_PATH = os.path.join(DATA_PATH, "game.db")


df = pd.read_csv(CSV_PATH)


def migrate():
    # Load CSV

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        # Drop existing tables to start fresh
        cur.execute("DROP TABLE IF EXISTS players;")
        df.to_sql("players", conn, if_exists="replace", index=False)

        # Recreate leagues table with explicit PK
        cur.execute("DROP TABLE IF EXISTS leagues;")
        cur.execute(
            """
            CREATE TABLE leagues (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            """
        )
        cur.executemany(
            "INSERT OR IGNORE INTO leagues(name) VALUES (?)",
            [(league_name,) for league_name in df["League"].dropna().unique()],
        )

        # Recreate teams table with explicit PK and FK
        cur.execute("DROP TABLE IF EXISTS teams;")
        cur.execute(
            """
            CREATE TABLE teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                league_id INTEGER NOT NULL,
                FOREIGN KEY(league_id) REFERENCES leagues(id)
            );
            """
        )
        # Map league names to IDs
        league_map = {
            name: id for id, name in cur.execute("SELECT id,name FROM leagues")
        }
        for _, row in df[["Team", "League"]].drop_duplicates().iterrows():
            cur.execute(
                "INSERT OR IGNORE INTO teams(name, league_id) VALUES (?, ?)",
                (row["Team"], league_map[row["League"]]),
            )

        # Add team_id to players
        cur.execute("ALTER TABLE players ADD COLUMN team_id INTEGER;")
        cur.execute(
            """
            UPDATE players
               SET team_id = (
                   SELECT id FROM teams WHERE teams.name = players.Team
               );
            """
        )

        # Rebuild players without League and Team columns
        columns = [c for c in df.columns if c not in ("League", "Team")]
        cols_escaped = ", ".join(f'"{c}"' for c in columns)

        cur.execute("DROP TABLE IF EXISTS players_new;")
        cur.execute(
            f"CREATE TABLE players_new ("
            "id INTEGER PRIMARY KEY, "
            f"{cols_escaped}, "
            "team_id INTEGER, "
            "FOREIGN KEY(team_id) REFERENCES teams(id)"
            ");"
        )
        insert_sql = (
            f"INSERT INTO players_new(id, {cols_escaped}, team_id) "
            f"SELECT rowid, {cols_escaped}, team_id FROM players;"
        )
        cur.execute(insert_sql)

        # Swap tables
        cur.execute("DROP TABLE players;")
        cur.execute("ALTER TABLE players_new RENAME TO players;")

        conn.commit()


if __name__ == "__main__":
    migrate()
    print(f"Migration complete: '{DB_PATH}' is now normalized.")

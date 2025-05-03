import sqlite3
import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data")
DB_PATH = os.path.join(DATA_PATH, "game.db")
CSV_PATH = os.path.join(DATA_PATH, "players.csv")


def assert_true(condition, msg):
    if not condition:
        raise AssertionError(msg)


def test_tables_exist(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    expected = {"players", "leagues", "teams"}
    assert_true(expected.issubset(tables), f"Missing tables: {expected - tables}")


def test_players_row_count(conn):
    # Count CSV rows (excluding header)
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        csv_count = sum(1 for _ in reader) - 1
    cursor = conn.execute("SELECT COUNT(*) FROM players;")
    db_count = cursor.fetchone()[0]
    assert_true(
        db_count == csv_count, f"Expected {csv_count} players, found {db_count}"
    )


def test_leagues_content(conn):
    # Collect distinct leagues from CSV
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_leagues = {row["League"] for row in reader if row.get("League")}
    cursor = conn.execute("SELECT name FROM leagues;")
    db_leagues = {row[0] for row in cursor.fetchall()}
    assert_true(
        db_leagues == csv_leagues, f"Leagues mismatch: {db_leagues} vs {csv_leagues}"
    )


def test_teams_league_fk(conn):
    cursor = conn.execute("SELECT league_id FROM teams;")
    league_ids = {row[0] for row in cursor.fetchall()}
    cursor2 = conn.execute("SELECT rowid FROM leagues;")
    valid_ids = {row[0] for row in cursor2.fetchall()}
    assert_true(
        league_ids.issubset(valid_ids), f"Invalid league_ids: {league_ids - valid_ids}"
    )


def test_players_columns(conn):
    cursor = conn.execute("PRAGMA table_info(players);")
    cols = {row[1] for row in cursor.fetchall()}
    assert_true(
        "League" not in cols and "Team" not in cols,
        f"Redundant columns found: {cols & {'League', 'Team'}}",
    )
    assert_true("team_id" in cols, "Missing column: team_id")


def test_players_team_fk(conn):
    cursor = conn.execute("SELECT DISTINCT team_id FROM players;")
    team_ids = {row[0] for row in cursor.fetchall()}
    cursor2 = conn.execute("SELECT rowid FROM teams;")
    valid_ids = {row[0] for row in cursor2.fetchall()}
    assert_true(
        team_ids.issubset(valid_ids), f"Invalid team_ids: {team_ids - valid_ids}"
    )


def run_all():
    if not os.path.exists(DB_PATH):
        print(f"Database file '{DB_PATH}' not found.")
        sys.exit(1)
    if not os.path.exists(CSV_PATH):
        print(f"CSV file '{CSV_PATH}' not found.")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    try:
        tests = [
            ("Tables exist", test_tables_exist),
            ("Players row count", test_players_row_count),
            ("Leagues content", test_leagues_content),
            ("Teams league FK", test_teams_league_fk),
            ("Players columns", test_players_columns),
            ("Players team FK", test_players_team_fk),
        ]
        for name, func in tests:
            try:
                func(conn)
                print(f"[PASS] {name}")
            except AssertionError as e:
                print(f"[FAIL] {name}: {e}")
                sys.exit(1)
        print("All tests passed!")
    finally:
        conn.close()


if __name__ == "__main__":
    run_all()

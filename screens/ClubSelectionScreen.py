import sqlite3
from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import Static, DataTable, Footer
from textual.containers import Horizontal
from textual.screen import Screen

# Import the shared confirmation dialog
from screens.TeamConfirmScreen import TeamConfirmScreen

DB_PATH = Path(__file__).parent.parent / "data" / "game.db"


class MasterDetailScreen(Screen):
    BINDINGS = [
        ("tab", "switch_focus", "Switch focus"),
        ("escape", "switch_focus", "Back to leagues"),
        ("down, j", "down", "Scroll down"),
        ("up, j", "up", "Scroll up"),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            "⚽ Select a league (left); clubs update automatically (right).", id="intro"
        )
        with Horizontal():
            self.league_table = DataTable(id="league-table")
            self.league_table.add_columns("ID", "League")
            yield self.league_table

            self.club_table = DataTable(id="club-table")
            self.club_table.add_column("Club")
            yield self.club_table
        yield Footer()

    def on_mount(self):
        # Enable arrow-key navigation for both tables
        for tbl in (self.league_table, self.club_table):
            tbl.cursor_type = "row"

        # Populate leagues from the database
        with sqlite3.connect(DB_PATH) as conn:
            for lid, name in conn.execute(
                "SELECT id, name FROM leagues WHERE id < 6 ORDER BY id;"
            ):
                self.league_table.add_row(str(lid), name)

        # Start focus on the league table
        self.league_table.focus()

    def on_show(self) -> None:
        # Restore focus after any overlay
        if self.club_table.row_count > 0:
            self.club_table.focus()
        else:
            self.league_table.focus()

    def action_switch_focus(self) -> None:
        # Toggle focus between the two tables
        if self.league_table.has_focus:
            self.club_table.focus()
        else:
            self.league_table.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        # Update clubs when the league selection changes
        if event.data_table.id != "league-table":
            return
        league_id = int(self.league_table.get_row(event.row_key)[0])
        self.club_table.clear()
        with sqlite3.connect(DB_PATH) as conn:
            for (club,) in conn.execute(
                "SELECT name FROM teams WHERE league_id = ? ORDER BY name;",
                (league_id,),
            ):
                self.club_table.add_row(club)

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        # Enter on league table toggles focus
        if event.data_table.id == "league-table":
            self.action_switch_focus()
            return

        # Enter on club table opens external TeamConfirmScreen
        if event.data_table.id == "club-table":
            club = self.club_table.get_row(event.row_key)[0]
            self.app.push_screen(TeamConfirmScreen(club))

    def action_up(self) -> None:
        if self.league_table.has_focus:
            self.league_table.action_cursor_up()
        elif self.club_table.has_focus:
            self.club_table.action_cursor_up()

    def action_down(self) -> None:
        if self.league_table.has_focus:
            self.league_table.action_cursor_down()
        elif self.club_table.has_focus:
            self.club_table.action_cursor_down()

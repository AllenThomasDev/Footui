from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.screen import Screen
from data.clubs import clubs
from textual.message import Message


class ClubChosen(Message):
    def __init__(self, club_name: str):
        self.club_name = club_name
        super().__init__()


class ClubSelectionScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static(
            "⚽ Get ready for your managerial adventure!\n\nTo begin, choose the club you want to manage:\n",
            id="intro",
        )
        table = DataTable(id="club-table")
        table.add_columns("Club", "History")
        for club, history in clubs:
            table.add_row(club, history)
        yield table

    def on_mount(self):
        self.query_one(DataTable).cursor_type = "row"
        self.query_one(DataTable).focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        table = self.query_one(DataTable)
        row = table.get_row(event.row_key)
        selected_club = row[0]  # First column is club name
        self.post_message(ClubChosen(selected_club))

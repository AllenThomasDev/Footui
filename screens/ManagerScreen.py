from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


class ManagerScreen(Screen):
    def __init__(self, club_name: str):
        super().__init__()
        self.club_name = club_name

    def compose(self) -> ComposeResult:
        yield Static(
            f"🏟️ Welcome to {self.club_name}!\nYour journey begins now...", id="welcome"
        )

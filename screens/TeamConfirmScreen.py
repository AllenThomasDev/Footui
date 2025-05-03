from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.message import Message


class ClubChosen(Message):
    def __init__(self, club_name: str) -> None:
        self.club_name = club_name
        super().__init__()


class TeamConfirmScreen(ModalScreen):
    """Modal to confirm team selection."""

    CSS_PATH = "../styles/modal.tcss"

    def __init__(self, team_name: str) -> None:
        super().__init__(name="team_confirm")
        self.team_name = team_name

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"❓ Manage [b]{self.team_name}[/b]?", id="question"),
            Button("Confirm", id="confirm", variant="success"),
            Button("Cancel", id="cancel", variant="error"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Remove the popup
        self.app.pop_screen()
        # If confirmed, emit ClubChosen
        if event.button.id == "confirm":
            self.app.post_message(ClubChosen(self.team_name))

from screens.ClubSelectionScreen import MasterDetailScreen
from screens.TeamConfirmScreen import ClubChosen
from screens.ManagerScreen import ManagerScreen
from textual.app import App


class ManagerApp(App):
    CSS_PATH = "styles/main.tcss"

    def on_mount(self):
        self.push_screen(MasterDetailScreen())

    def on_club_chosen(self, message: ClubChosen):
        self.push_screen(ManagerScreen(message.club_name))


if __name__ == "__main__":
    app = ManagerApp()
    app.run()

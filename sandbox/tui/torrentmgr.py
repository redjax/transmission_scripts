from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Container
from textual.widgets import Footer, Header, Button, DataTable, SelectionList
from textual.reactive import reactive
from textual import on
import transmission_lib


class TorrentsList(SelectionList):
    """Class to mount torrents in a vertical scrolling table, where each row is a torrent."""

    def compose(self) -> ComposeResult:
        yield Container(DataTable(id="torrent_table"))


class TransmissionApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]

    config_file = "configs/default.json"
    torrents = reactive([])
    transmission_settings = reactive(None)
    controller = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header()
        yield TorrentsList()
        yield Footer()

    def on_mount(self) -> None:
        self.transmission_settings = transmission_lib.get_transmission_settings(
            config_file=self.config_file
        )
        self.controller = transmission_lib.get_transmission_controller(
            transmission_settings=self.transmission_settings
        )


if __name__ == "__main__":
    TransmissionApp().run()

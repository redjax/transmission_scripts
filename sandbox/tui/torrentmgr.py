from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll, Container
from textual.widgets import Footer, Header, Button, Digits, DataTable
from textual.reactive import reactive


class TorrentsList(VerticalScroll):
    """Class to mount torrents in a vertical scrolling table, where each row is a torrent."""

    def compose(self) -> ComposeResult:
        yield Container(
            DataTable(id="torrent_table"),
        )


class TransmissionApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield TorrentsList()

    def on_mount(self) -> None:
        table = self.query_one("#torrent_table", DataTable)
        table.add_columns("Select", "ID", "Name", "Status", "Progress", "Size")


if __name__ == "__main__":
    TransmissionApp().run()

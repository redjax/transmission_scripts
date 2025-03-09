from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Container
from textual.widgets import Footer, Header, Button, DataTable
from textual.reactive import reactive
from textual import on
import transmission_lib


class TorrentsList(VerticalScroll):
    """Class to mount torrents in a vertical scrolling table, where each row is a torrent."""

    def compose(self) -> ComposeResult:
        yield Container(
            DataTable(id="torrent_table"),
            Button("Pause Selected", id="pause_button"),
            Button("Resume Selected", id="resume_button"),
        )


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

        table = self.query_one("#torrent_table", DataTable)
        table.add_columns("ID", "Name", "Status", "Progress")
        table.cursor_type = "row"  # This allows row selection

        self.refresh_torrents()

    def refresh_torrents(self) -> None:
        self.torrents = self.controller.get_all_torrents()

        table = self.query_one("#torrent_table", DataTable)
        table.clear()

        # table.add_columns("ID", "Name", "Status", "Progress")

        for torrent in self.torrents:
            table.add_row(
                str(torrent.id),
                torrent.name,
                torrent.status,
                f"{torrent.progress:.2f}%",
            )

    @on(Button.Pressed, "#pause_button")
    def pause_selected(self) -> None:
        table = self.query_one("#torrent_table", DataTable)
        for row in table.selected_rows:
            torrent_id = int(table.get_cell_at((row, 0)))
            self.controller.stop_torrent_by_id(torrent_id)
        self.refresh_torrents()

    @on(Button.Pressed, "#resume_button")
    def resume_selected(self) -> None:
        table = self.query_one("#torrent_table", DataTable)
        for row in table.selected_rows:
            torrent_id = int(table.get_cell_at((row, 0)))
            self.controller.start_torrent_by_id(torrent_id)
        self.refresh_torrents()


if __name__ == "__main__":
    TransmissionApp().run()

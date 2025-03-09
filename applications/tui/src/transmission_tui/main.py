from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button
from textual.containers import Horizontal, Container
import transmission_rpc
import logging

import transmission_lib

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class TransmissionTUI(App):
    """A simple Textual app for Transmission RPC."""

    CSS = """
    Screen {
        align: center middle;
    }
    DataTable {
        height: 75%;
    }
    Button {
        margin: 1;
    }
    """

    def __init__(self, config_path: str = "configs/default.json"):
        super().__init__()
        self.config_path = config_path
        self.transmission_settings = self.read_config()

        self.client = self.connect_to_transmission()
        self.torrents = []

    def read_config(self) -> transmission_lib.TransmissionClientSettings:
        transmission_settings = transmission_lib.get_transmission_settings(
            self.config_path
        )

        return transmission_settings

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            DataTable(id="torrent_table"),
            Horizontal(
                Button("Refresh", id="refresh"),
                Button("Pause", id="pause"),
                Button("Resume", id="resume"),
                Button("Delete", id="delete", variant="error"),
                Button("Quit", id="quit", variant="error"),
            ),
        )

    def on_mount(self) -> None:
        """Runs when the app starts."""
        table = self.query_one("#torrent_table", DataTable)
        table.add_columns("Select", "ID", "Name", "Status", "Progress", "Size")
        self.refresh_torrents()

    def connect_to_transmission(self):
        """Connect to Transmission."""
        try:
            return transmission_rpc.Client(
                host="localhost",
                port=9091,
                username="transmission",
                password="password",
            )
        except Exception as e:
            log.error(f"Failed to connect: {e}")
            return None

    def refresh_torrents(self) -> None:
        """Fetch torrents from Transmission."""
        if not self.client:
            return
        table = self.query_one("#torrent_table", DataTable)
        table.clear()

        try:
            self.torrents = self.client.get_torrents()
            if not self.torrents:
                log.warning("No torrents found.")
            else:
                log.info(f"Fetched {len(self.torrents)} torrents.")
        except Exception as e:
            log.error(f"Error fetching torrents: {e}")

        for torrent in self.torrents:
            selected = ""  # Placeholder for selection state
            status = torrent.status.capitalize()
            progress = f"{torrent.progress:.1f}%"
            size = f"{torrent.total_size / (1024**2):.2f} MB"

            table.add_row(
                selected, str(torrent.id), torrent.name, status, progress, size
            )

    def get_selected_torrents(self) -> list:
        """Retrieve selected torrents based on the table rows."""
        table = self.query_one("#torrent_table", DataTable)
        selected_ids = []

        for row_key in table.rows.keys():
            row_data = table.get_row(row_key)
            if row_data[0] == "X":  # Check if 'Select' column is marked
                selected_ids.append(int(row_data[1]))  # Torrent ID is in column 1

        return [torrent for torrent in self.torrents if torrent.id in selected_ids]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "refresh":
            self.refresh_torrents()

        elif event.button.id == "pause":
            torrents = self.get_selected_torrents()
            for torrent in torrents:
                self.client.stop_torrent(torrent.id)
            self.refresh_torrents()

        elif event.button.id == "resume":
            torrents = self.get_selected_torrents()
            for torrent in torrents:
                self.client.start_torrent(torrent.id)
            self.refresh_torrents()

        elif event.button.id == "delete":
            torrents = self.get_selected_torrents()
            for torrent in torrents:
                self.client.remove_torrent(torrent.id, delete_data=True)
            self.refresh_torrents()

        elif event.button.id == "quit":
            self.exit()


if __name__ == "__main__":
    TransmissionTUI().run()

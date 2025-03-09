from __future__ import annotations

import json
import logging
import typing as t

from dataclasses import dataclass, field
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Static, Checkbox
from textual.containers import Horizontal
from textual.containers import Container, VerticalScroll
from textual.events import Key

import transmission_rpc

import transmission_lib
import project_cli.subcommands.transmission as transmission_cli

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
        self.settings = transmission_lib.get_transmission_settings(config_path)
        self.client = self.connect_to_transmission()
        self.torrents = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            DataTable(id="torrent_table"),
            Horizontal(
                Button("Refresh", id="refresh"),
                Button("Show Debug", id="debug"),
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
                host=self.settings.host,
                port=self.settings.port,
                protocol=self.settings.protocol,
                username=self.settings.username,
                password=self.settings.password,
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

        if not table.columns:
            table.add_columns("Select", "ID", "Name", "Status", "Progress", "Size")

        self.torrents = self.client.get_torrents()
        for torrent in self.torrents:
            checkbox = Checkbox()
            checkbox.id = f"checkbox_{torrent.id}"  # Give the checkbox a unique ID
            status = torrent.status
            progress = f"{torrent.progress:.1f}%"
            size = f"{torrent.total_size / (1024**2):.2f} MB"

            table.add_row(
                checkbox, str(torrent.id), torrent.name, status, progress, size
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        table = self.query_one("#torrent_table", DataTable)

        selected_torrents = []
        for row_key in table.rows:
            row_data = table.get_row(row_key)  # Retrieve row data
            checkbox, name, status, progress, size = row_data
            if checkbox.value:  # If checked
                selected_torrents.append(name)

        if event.button.id == "pause":
            self.pause_torrents(selected_torrents)
        elif event.button.id == "resume":
            self.resume_torrents(selected_torrents)
        elif event.button.id == "delete":
            self.delete_torrents(selected_torrents)
        elif event.button.id == "refresh":
            self.populate_torrents()
        elif event.button.id == "debug":
            self.push_screen(DebugScreen(self.settings))
        elif event.button.id == "quit":
            self.exit()

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "q":
            self.exit()

    def populate_torrents(self):
        """Fetch torrents and update the DataTable."""
        table = self.query_one("#torrent_table", DataTable)
        table.clear()  # Clear existing rows

        # Add columns if not already created
        if not table.columns:
            table.add_column("Select")
            table.add_column("Name")
            table.add_column("Status")

        torrents = transmission_cli._list()  # Your existing function to fetch torrents

        for torrent in torrents:
            checkbox = Checkbox()
            table.add_row(checkbox, torrent.name, torrent.status)

    def pause_torrents(self, torrents):
        for torrent in torrents:
            self.client.stop_torrent(torrent)
        self.populate_torrents()  # Refresh UI

    def resume_torrents(self, torrents):
        for torrent in torrents:
            self.client.start_torrent(torrent)
        self.populate_torrents()

    def delete_torrents(self, torrents):
        for torrent in torrents:
            self.client.remove_torrent(torrent, delete_data=True)
        self.populate_torrents()


class DebugScreen(App):
    """Screen to show configuration settings."""

    def __init__(self, settings: transmission_lib.TransmissionClientSettings):
        super().__init__()
        self.settings = settings

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(Static(self.format_debug()))

    def format_debug(self) -> str:
        """Format settings for display."""
        return f"Debug Info:\n{json.dumps(self.settings.__dict__, indent=4)}"


if __name__ == "__main__":
    TransmissionTUI().run()

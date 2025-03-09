from __future__ import annotations

import json
import logging
import typing as t

from dataclasses import dataclass, field
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Static
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
            Button("Refresh", id="refresh"),
            Button("Show Debug", id="debug"),
            Button("Quit", id="quit", variant="error"),
        )

    def on_mount(self) -> None:
        """Runs when the app starts."""
        table = self.query_one("#torrent_table", DataTable)
        table.add_columns("ID", "Name", "Status", "Progress", "Size")
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

        self.torrents = self.client.get_torrents()
        for torrent in self.torrents:
            status = torrent.status
            progress = f"{torrent.progress:.1f}%"
            table.add_row(
                torrent.id,
                torrent.name,
                status,
                progress,
                f"{torrent.total_size / (1024**2):.2f} MB",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "refresh":
            self.refresh_torrents()
        elif event.button.id == "debug":
            self.push_screen(DebugScreen(self.settings))

    def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "q":
            self.exit()


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

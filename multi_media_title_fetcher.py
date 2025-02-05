import threading
import platform
import subprocess
import wx
import pywinctl as pwc
import psutil
import logging
import json

class MultiMediaTitleFetcher:
    def __init__(self, callback, config_file):
        logging.basicConfig(level=logging.INFO)  # Later change to `INFO` or `DEBUG`

        self.callback = callback
        self._title = ""
        self.running = True

        # Load configuration
        self.config = self.load_config(config_file)

        # Create media players based on config data
        self.media_players = self.create_media_players()

        # Start title fetching thread
        self.thread = threading.Thread(target=self.fetch_title_loop, daemon=True)
        self.thread.start()

    def load_config(self, config_file):
        """Load the configuration from the specified JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
            return {}

    def create_media_players(self):
        """Create a list of media players based on the config data."""
        media_players = []

        # Iterate through the list of media players
        for config in self.config.get("media_players", []):
            # Skip disabled players
            if config.get("disabled", False):
                continue

            app = config["name"]  # Access the 'name' of the media player
            if config["type"] == "generic":
                media_players.append((app, self.get_media_title_generic, config))
            if config["type"] == "flexible":
                media_players.append((app, self.get_media_title_generic_flexible, config))
            elif config["type"] == "checkappprocess":
                media_players.append((app, self.get_media_title_generic_checkappprocess, config))

        # Sort players by priority
        media_players.sort(key=lambda x: x[2]["priority"])

        return media_players

    def fetch_title_loop(self):
        while self.running:
            title = self.get_media_title()
            if title and title != self._title:
                wx.CallAfter(self.callback, title)
                self._title = title
            threading.Event().wait(1)

    def get_media_title(self):
        """Iterate over the media players and return the first non-None title."""
        for app, func, config in self.media_players:
            window_title = func(app, config)
            if window_title:
                title = self.split_title(window_title, app, config)
                return title
        return None

    def get_media_title_generic_checkappprocess(self, app, config):
        """Get title for media player based on process check."""
        app_processes = [
            proc for proc in psutil.process_iter(['pid', 'name'])
            if proc.info['name'].lower().split('.')[0] == app.lower()
        ]

        windows_pwc = pwc.getWindowsWithTitle(' - ', condition=pwc.Re.CONTAINS)

        for window in windows_pwc:
            pid = window.getPID()

            for app_process in app_processes:
                if pid == app_process.info['pid']:
                    # Return the raw window title
                    return window.title

        return None

    def get_media_title_generic_flexible(self, app, config):
        """Get generic media player title."""
        windows_pwc = pwc.getWindowsWithTitle(app, condition=pwc.Re.CONTAINS)

        for window in windows_pwc:
            # Return the raw window title
            if '-' in window.title:
                return window.title

        return None

    def get_media_title_generic(self, app, config):
        """Get generic media player title."""
        windows_pwc = pwc.getWindowsWithTitle(' - ' + app, condition=pwc.Re.CONTAINS)

        for window in windows_pwc:
            # Return the raw window title
            return window.title

        return None

    def split_title(self, window_title, app, config):
        """Split the window title based on the format string defined in the config."""

        format_str = config["format"]
        # Special case for Spotify App titles (and others that don't contain {app}), so we don't need to change our extraction logic
        if "{app}" not in format_str:
            window_title = window_title + " - {app}";

        # Default case for other apps
        if format_str.count("{artist}") and format_str.count("{title}"):
            if " - " in window_title:
                parts = window_title.split(" - ")
            elif " • " in window_title:
                parts = window_title.split(" • ")
            else:
                parts = window_title.split(" - ")

            # Logic to extract artist and title based on the format
            artist = ""
            title = ""
            if "{artist}" in format_str and len(parts) > 1:
                artist = parts[0].strip()
            if "{title}" in format_str and len(parts) > 1:
                title = parts[-2].strip()

            return f"{artist} - {title}"

        return None

    def stop(self):
        self.running = False

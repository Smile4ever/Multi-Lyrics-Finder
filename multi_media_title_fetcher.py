import threading
import platform
import subprocess
import wx
import pygetwindow as gw
import pywinctl as pwc
import psutil
import logging

class MultiMediaTitleFetcher:
    def __init__(self, callback):
        logging.basicConfig(level=logging.INFO)  # Latere aanpassing mogelijk naar `INFO` of `DEBUG`

        self.callback = callback
        self._title = ""
        self.running = True
        self.thread = threading.Thread(target=self.fetch_title_loop, daemon=True)
        self.thread.start()

    def fetch_title_loop(self):
        while self.running:
            title = self.get_media_title()
            if title and title != self._title:
                wx.CallAfter(self.callback, title)
                self._title = title
            threading.Event().wait(1)

    def get_media_title(self):
        media_sources = [
            self.get_media_title_deezerweb(),
            self.get_media_title_vlc(),
            self.get_media_title_youtubeweb(),
            self.get_media_title_spotifyweb(),
            self.get_media_title_spotifyapp(),
            self.get_media_title_deezerapp()
        ]

        # Iterate over the media sources and return the first non-None result
        for media_title in media_sources:
            if media_title:
                return media_title

        return None

    def get_media_title_youtubeweb(self):
        windows = gw.getWindowsWithTitle('')
        relevant_browser_windows = [window for window in windows if ' - YouTube' in window.title]

        for window in relevant_browser_windows:
            title = window.title
            return title.split(" - YouTube")[0].strip()

        return None

    def get_media_title_spotifyweb(self):
        windows = gw.getWindowsWithTitle('')
        relevant_browser_windows = [window for window in windows if ' - Spotify' in window.title]

        for window in relevant_browser_windows:
            title = window.title
            return " - ".join(title.split(" - Spotify")[0].split(" • ")[::-1])

        return None

    def get_media_title_spotifyapp(self):
        spotify_processes = [
            proc for proc in psutil.process_iter(['pid', 'name'])
            if proc.info['name'].lower().split('.')[0] == 'spotify'
        ]

        windows_pwc = pwc.getWindowsWithTitle(' - ', condition=pwc.Re.CONTAINS)

        for window in windows_pwc:
            pid = window.getPID()

            for spotify_process in spotify_processes:
                if pid == spotify_process.info['pid']:
                    return window.title

        return None

    def get_media_title_deezerapp(self):
        spotify_processes = [
            proc for proc in psutil.process_iter(['pid', 'name'])
            if proc.info['name'].lower().split('.')[0] == 'deezer'
        ]

        windows_pwc = pwc.getWindowsWithTitle(' - ', condition=pwc.Re.CONTAINS)

        for window in windows_pwc:
            pid = window.getPID()

            for spotify_process in spotify_processes:
                if pid == spotify_process.info['pid']:
                    return window.title

        return None

    def get_media_title_deezerweb(self):
        windows = gw.getWindowsWithTitle('')
        relevant_browser_windows = [window for window in windows if ' - Deezer' in window.title]

        for window in relevant_browser_windows:
            title = window.title
            return " - ".join(title.split(" - Deezer")[0].split(" - ")[::-1])

        return None

    def get_media_title_vlc(self):
        windows = gw.getWindowsWithTitle('')
        relevant_windows = [window for window in windows if ' - VLC Media Player' in window.title]

        for window in relevant_windows:
            title = window.title
            return title.split(" - VLC Media Player")[0].strip()

        return None

    def stop(self):
        self.running = False

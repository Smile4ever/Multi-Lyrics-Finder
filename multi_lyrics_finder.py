import wx
import webbrowser
import os
import sys
import platform
import threading
import platform
import locale
import logging

import xml.etree.ElementTree as ET
from plyer import notification

from multi_media_title_fetcher import MultiMediaTitleFetcher
from lyrics_utils import LyricsUtils
from get_lyrics import GetLyrics

VERSION = "0.1.0"
# Languages code conversion table: iso-639-1 to iso-639-3
lang_os_to_iso = {
    'af': "afr",
    'sq': "alb",
    'ar': "ara",
    'hy': "arm",
    'eu': "baq",
    'bn': "ben",
    'bs': "bos",
    'br': "bre",
    'bg': "bul",
    'my': "bur",
    'ca': "cat",
    'zh': "chi",
    'hr': "hrv",
    'cs': "cze",
    'da': "dan",
    'nl': "dut",
    'en': "eng",
    'eo': "epo",
    'et': "est",
    'fi': "fin",
    'fr': "fre",
    'gl': "glg",
    'ka': "geo",
    'de': "ger",
    'el': "ell",
    'he': "heb",
    'hi': "hin",
    'hu': "hun",
    'is': "ice",
    'id': "ind",
    'it': "ita",
    'ja': "jpn",
    'kk': "kaz",
    'km': "khm",
    'ko': "kor",
    'lv': "lav",
    'lt': "lit",
    'lb': "ltz",
    'mk': "mac",
    'ms': "may",
    'ml': "mal",
    'mn': "mon",
    'no': "nor",
    'oc': "oci",
    'fa': "per",
    'pl': "pol",
    'pt': "por",
    'po': "pob",
    'ro': "rum",
    'ru': "rus",
    'sr': "scc",
    'si': "sin",
    'sk': "slo",
    'sl': "slv",
    'es': "spa",
    'sw': "swa",
    'sv': "swe",
    'tl': "tgl",
    'te': "tel",
    'th': "tha",
    'tr': "tur",
    'uk': "ukr",
    'ur': "urd",
    'vi': "vie"
}

class LyricsFinder(wx.Frame):
    _getLyrics = GetLyrics()

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        super().__init__(None, title="Multi Lyrics Finder " + VERSION, size=(500, 800))
        panel = wx.Panel(self)
        panel.SetSizer(wx.BoxSizer(wx.VERTICAL))

        # Create GridBagSizer for the main UI layout
        grid = wx.GridBagSizer(5, 5)
        panel.GetSizer().Add(grid, 1, wx.ALL | wx.EXPAND, border=10)

        # Title Input
        self.title_label = wx.StaticText(panel, label="Title:")
        self.title_text = wx.TextCtrl(panel, size=(200, -1))
        grid.Add(self.title_label, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.title_text, pos=(1, 1))

        # Artist Input
        self.artist_label = wx.StaticText(panel, label="Artist:")
        self.artist_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.artist_text.Bind(wx.EVT_TEXT_ENTER, self.artist_text_on_enter_pressed)

        self.switch_button = wx.Button(panel, label="Switch")
        self.switch_button.Bind(wx.EVT_BUTTON, self.on_switch)
        grid.Add(self.artist_label, pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.artist_text, pos=(0, 1))
        grid.Add(self.switch_button, pos=(0, 2))

        # Buttons for searching lyrics and Google
        self.search_button = wx.Button(panel, label="Search Lyrics")
        self.search_button.Bind(wx.EVT_BUTTON, self.on_search_lyrics)
        self.google_button = wx.Button(panel, label="Search Google")
        self.google_button.Bind(wx.EVT_BUTTON, self.on_google_search)
        grid.Add(self.search_button, pos=(2, 0))
        grid.Add(self.google_button, pos=(2, 1))

        # Lyrics TextBox (dynamisch formaat)
        self.lyrics_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)
        grid.Add(self.lyrics_text, pos=(3, 0), span=(1, 3), flag=wx.EXPAND, border=5)

        # Make it flexible
        grid.AddGrowableCol(0)  # Column 0 of lyrics_text
        grid.AddGrowableCol(1)  # Column 1
        grid.AddGrowableCol(2)  # Column 2
        grid.AddGrowableRow(3)  # Row 3 flexible (lyrics_text)

        # Create the bottom panel
        bottom_panel = wx.Panel(panel)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left bottom panel for Source label and value
        left_bottom_panel = wx.Panel(bottom_panel)
        left_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Define the Source label and the value label next to it
        self.source_label = wx.StaticText(left_bottom_panel, label="Source: ")  # The Source label
        self.source_value_label = wx.StaticText(left_bottom_panel, label="")  # To dynamically update the source value

        left_bottom_sizer.Add(self.source_label, 0, wx.ALL, 5)  # Add Source label
        left_bottom_sizer.Add(self.source_value_label, 0, wx.ALL, 5)  # Add Source value next to it

        left_bottom_panel.SetSizer(left_bottom_sizer)

        # Right bottom panel for Get updates and Save lyrics buttons
        right_bottom_panel = wx.Panel(bottom_panel)
        right_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_button = wx.Button(right_bottom_panel, label="Save Lyrics")
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_lyrics)
        self.update_button = wx.Button(right_bottom_panel, label="Get updates")
        self.update_button.Bind(wx.EVT_BUTTON, self.on_check_updates)
        right_bottom_sizer.Add(self.update_button, 0, wx.ALL, 5)
        right_bottom_sizer.Add(self.save_button, 0, wx.ALL, 5)
        right_bottom_panel.SetSizer(right_bottom_sizer)

        # Add left and right bottom panels to the bottom sizer with proportional layout
        bottom_sizer.Add(left_bottom_panel, 1, wx.EXPAND)
        bottom_sizer.Add(right_bottom_panel, 0, wx.ALIGN_CENTER_VERTICAL)

        # Ensure bottom_sizer expands correctly and keeps components at the bottom
        bottom_panel.SetSizerAndFit(bottom_sizer)

        # Add bottom_panel to the main sizer
        panel.GetSizer().Add(bottom_panel, 0, wx.EXPAND | wx.ALL, border=10)

        # Center the frame
        self.Centre()

        # Set the translation for the UI based on the system language
        self.set_translation()

        self.multiMediaTitleFetcher = MultiMediaTitleFetcher(self.update_ui)

    def set_translation(self):
        # Get the system language (e.g., 'en', 'fr', etc.)
        #system_lang = locale.getdefaultlocale()[0]
        #lang_code = lang_os_to_iso.get(system_lang[:2].lower(), 'eng')  # default to 'eng' if no match

        # Get the user language in three letter format (etc eng, dut, fre)
        locale.setlocale(locale.LC_ALL, "")
        locale_info = locale.getlocale()
        user_lang = locale_info[0].split('_')[0] if locale_info and locale_info[0] else 'English'
        lang_code_2 = locale.normalize(user_lang)[:2].lower() if locale.normalize(user_lang) else "en"
        lang_code = lang_os_to_iso.get(lang_code_2, 'en')

        # Get the folder where the .py script is located
        if getattr(sys, 'frozen', False):  # Check if the app is frozen (running from a packaged .exe)
            script_dir = sys._MEIPASS  # Running as a bundled executable
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__)) # Running as a normal script

        locale_folder = os.path.join(script_dir, 'locale')  # Assuming locale folder is in the same directory as the script
        translation_file = os.path.join(locale_folder, f"{lang_code}.xml")
        
        # Check if the translation file exists
        if not os.path.exists(translation_file):
            wx.MessageBox(f"Translation file for language {lang_code} not found. Using default language.", "Translation Error", wx.OK | wx.ICON_ERROR)
            translation_file = os.path.join(locale_folder, "eng.xml")  # Fallback to English
        
        # Parse the XML file
        try:
            tree = ET.parse(translation_file)
            root = tree.getroot()

            # Helper function to safely get the text of a node
            def get_text_or_default(node, default=''):
                return node.text if node is not None else default

            # Assign the translated text to UI elements
            self.title_label.SetLabel(get_text_or_default(root.find('label_title'), 'Title:'))
            self.artist_label.SetLabel(get_text_or_default(root.find('label_artist'), 'Artist:'))
            self.source_label.SetLabel(get_text_or_default(root.find('label_source'), 'Source:'))
            self.save_button.SetLabel(get_text_or_default(root.find('message_savelyrics'), 'Save Lyrics'))
            self.search_button.SetLabel(get_text_or_default(root.find('button_getlyrics'), 'Get Lyrics'))
            self.google_button.SetLabel(get_text_or_default(root.find('button_google'), 'Search with Google'))
            self.update_button.SetLabel(get_text_or_default(root.find('button_update'), 'Get updates'))
            self.switch_button.SetLabel(get_text_or_default(root.find('button_switch'), 'Switch'))

            # Other elements (for messages, etc.)
            self.message_loading = get_text_or_default(root.find('message_loading'), "Loading..")
            self.message_notfound = get_text_or_default(root.find('message_notfound'), 'Lyrics not found.')
            self.message_nosong = get_text_or_default(root.find('message_nosong'), 'No song loaded.')
            self.message_newsong = get_text_or_default(root.find('message_newsong'), 'New song loaded. To get the lyrics, click Get Lyrics.')
            self.message_incorrect = get_text_or_default(root.find('message_incorrect'), 'Incorrect artist or title.')
            self.message_savelyrics = get_text_or_default(root.find('message_savelyrics'), 'Save Lyrics')

        except ET.ParseError as e:
            error_msg = f"Error parsing the translation file. Details: {str(e)}"
            wx.MessageBox(error_msg, "Translation Parsing Error", wx.OK | wx.ICON_ERROR)
            logging.error(f"Parsing error: {error_msg}")  # Log error details for debugging
        except Exception as e:
            error_msg = f"Unexpected error occurred while loading translation: {str(e)}"
            wx.MessageBox(error_msg, "Translation Error", wx.OK | wx.ICON_ERROR)
            logging.error(f"Unexpected error: {error_msg}")  # Log unexpected errors for debugging
    
    def update_ui(self, new_title):
        #new_title = new_title.replace("—", "-");

        clean_artist = LyricsUtils.get_clean_artist(new_title);
        self.artist_text.SetValue(clean_artist)
        self.artist_text.Refresh()
        self.artist_text.Update()

        clean_title = LyricsUtils.get_clean_title(new_title);
        self.title_text.SetValue(clean_title)
        self.title_text.Refresh()
        self.title_text.Update()

        self.update_lyrics(clean_artist, clean_title)

        logging.debug(f"Updated raw title: {new_title}")

    def on_switch(self, event):
        temp = self.title_text.GetValue()
        self.title_text.SetValue(self.artist_text.GetValue())
        self.artist_text.SetValue(temp)

    def artist_text_on_enter_pressed(self, event):
        self.on_search_lyrics(None)

    def on_search_lyrics(self, event):
        artist = self.artist_text.GetValue()
        title = self.title_text.GetValue()

        if title and artist:
            self.update_lyrics(artist, title);

    def update_lyrics(self, clean_artist, clean_title):
        self.lyrics_text.SetValue(self.message_loading)
        self.lyrics_text.Refresh()
        self.lyrics_text.Update()

        lyric_string, source = self._getLyrics.get_lyrics(clean_title, clean_artist)

        if not LyricsUtils.is_lyric_page(lyric_string):
            if not clean_artist or not clean_title:
                self.lyrics_text.SetValue(self.message_incorrect)
                self.source_value_label.SetLabel("")
                self.artist_text.SetValue("")
            else:
                self.source_value_label.SetLabel("")
                self.lyrics_text.SetValue(self.message_notfound)
        else:
            #logging.info(f"update_lyrics: Playing media: {clean_artist} - {clean_title}")
            notification.notify(
                title=f'Multi Lyrics Finder',
                message=f'{clean_artist} - {clean_title}',
                timeout=10  # Show for X seconds
            )

            self.source_value_label.SetLabel(source)
            self.lyrics_text.SetValue(lyric_string)

    def on_google_search(self, event):
        query = f"{self.title_text.GetValue()} {self.artist_text.GetValue()} lyrics"
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
    
    def on_check_updates(self, event):
        webbrowser.open("https://github.com/Smile4ever/Multi-Lyrics-Finder")
    
    def on_save_lyrics(self, event):
        artist = self.artist_text.GetValue();
        title = self.title_text.GetValue();
        filename = f"{artist} - {title}.txt"

        with wx.FileDialog(self, self.message_savelyrics, defaultFile=filename, wildcard="Text files (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            file_path = fileDialog.GetPath()
            lyrics = self.lyrics_text.GetValue()
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(lyrics)
            except IOError:
                wx.LogError("Cannot save current data.")


if __name__ == "__main__":
    app = wx.App(False)
    frame = LyricsFinder()
    frame.Show()
    app.MainLoop()

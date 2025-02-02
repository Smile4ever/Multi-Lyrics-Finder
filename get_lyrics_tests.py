import unittest

from get_lyrics import GetLyrics

class TestGetLyrics(unittest.TestCase):
    def setUp(self):
        self.lyrics_fetcher = GetLyrics()

    def test_process_html_lyricsmania(self):
        url = self.lyrics_fetcher.sources["lyricsmania"].format(
            title="hello", artist="adele"
        )
        html_data = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(
            html_data, "LyricsMania: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        processed_text = self.lyrics_fetcher.process_html("lyricsmania", html_data)
        self.assertIsNotNone(
            processed_text,
            "LyricsMania: Failed to process HTML, no lyrics extracted",
        )
        print("LyricsMania Test Passed! Found URL: " + url + "\n" + processed_text)

    '''def test_fetch_lyrics_lyricscom(self):
        url = self.lyrics_fetcher.sources["lyricscom"].format(
            title="hello", artist="adele"
        )
        html = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(html, "Lyrics.com: Failed to fetch lyrics data")
        print("Lyrics.com Test Passed!")'''

    '''def test_process_html_lyricscom(self):
        url = self.lyrics_fetcher.sources["lyricscom"].format(
            title="hello", artist="adele"
        )
        html_data = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(
            html_data, "Lyrics.com: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        processed_text = self.lyrics_fetcher.process_html("lyricscom", html_data)
        self.assertIsNotNone(
            processed_text,
            "Lyrics.com: Failed to process HTML, no lyrics extracted",
        )
        print("Lyrics.com Test Passed!")'''

    '''def test_process_html_sonichits(self):
        url = self.lyrics_fetcher.sources["sonichits"].format(
            title="hello", artist="adele"
        )
        html_data = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(
            html_data, "SonicHits: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        processed_text = self.lyrics_fetcher.process_html("sonichits", html_data)
        self.assertIsNotNone(
            processed_text,
            "SonicHits: Failed to process HTML, no lyrics extracted",
        )
        print("SonicHits Test Passed!")'''

    def test_process_html_azlyrics(self):
        url = self.lyrics_fetcher.sources["azlyrics"].format(
            title="hello", artist="adele"
        )
        html_data = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(
            html_data, "AZLyrics: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        processed_text = self.lyrics_fetcher.process_html("azlyrics", html_data)
        self.assertIsNotNone(
            processed_text,
            "AZLyrics: Failed to process HTML, no lyrics extracted",
        )
        print("AZLyrics Test Passed! Found URL: " + url + "\n" + processed_text)

    def test_process_html_letras(self):
        lyrics_fetcher_local = GetLyrics()
        lyrics_fetcher_local.sources = {"letras": "https://www.letras.com/{artist}/{title}/"}
        processed_text, source = lyrics_fetcher_local.get_lyrics("Yo Necesito Mas de Ti", "Guillermo Davila")
        self.assertIsNotNone(
            processed_text, "Letras: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        print("Letras Test Passed! Found source: " + source + "\n" + processed_text)

    def test_process_html_lyricsmode(self):
        artist = "adele"
        title = "hello"
        url = self.lyrics_fetcher.search_lyricsmode(artist, title)
        html_data = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(
            html_data, "LyricsMode: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        processed_text = self.lyrics_fetcher.process_html("lyricsmode", html_data)
        self.assertIsNotNone(
            processed_text,
            "LyricsMode: Failed to process HTML, no lyrics extracted",
        )
        print("LyricsMode Test Passed! Found URL: " + url + "\n" + processed_text)

    def test_process_html_musikguru(self):
        artist = "adele"
        title = "hello"
        url = self.lyrics_fetcher.search_musikguru(artist, title)
        html_data = self.lyrics_fetcher.fetch_lyrics(url)
        self.assertIsNotNone(
            html_data, "MusikGuru: Failed to fetch lyrics data"
        )  # Controleer dat data is opgehaald

        processed_text = self.lyrics_fetcher.process_html("musikguru", html_data)
        self.assertIsNotNone(
            processed_text,
            "MusikGuru: Failed to process HTML, no lyrics extracted",
        )
        print("MusikGuru Test Passed! Found URL: " + url + "\n" + processed_text)

if __name__ == "__main__":
    unittest.main()



if __name__ == "__main__":
    unittest.main()

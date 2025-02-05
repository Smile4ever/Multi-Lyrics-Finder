import re
import requests
import logging
import urllib
import json

from bs4 import BeautifulSoup
from bs4.element import Comment
from html import unescape
from lyrics_utils import LyricsUtils

class GetLyrics:
    TIMEOUT = 5  # Timeout in seconden voor netwerkoproepen

    def __init__(self, config_path):
        logging.basicConfig(level=logging.INFO)  # Latere aanpassing mogelijk naar `INFO` of `DEBUG`
        self.config_path = config_path

        # https://www.streetdirectory.com/lyricadvisor/song/wpoej/no_pude_olvidarte/

        self.sources = self.load_sources()
        # "sonichits": "https://sonichits.com/video/{artist}/{title}", # URL works but 403
        # "lyricscom": "https://www.lyrics.com/{title}-lyrics-{artist}.html"

        # https://musikguru.de/audrey-landers/songtext-honeymoon-in-trindidad-532763.html
        self.musikguru_search_url = "https://musikguru.de/search/ac/"
        # https://www.lyricsmode.com/lyrics/{artist}/{title}.html
        self.lyricsmode_search_url = "https://www.lyricsmode.com/search.php?search={artist} {title}"
        # https://www.musica.com/letras.asp?letra=1646129
        self.duckduckgo_search_url = "https://duckduckgo.com/?q=!ducky+\"{artist}\"%20-%20\"{title}\"+site%3Amusica.com"
        # https://genius.com/Los-yonics-si-no-me-querias-lyrics
        self.genius_search_url = "https://genius.com/api/search/multi?q={artist} - {title}"

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def load_sources(self):
        """Load lyrics sources from the config.json file and populate the sources dictionary."""
        sources = {}

        # Load config from JSON file
        with open(self.config_path, 'r') as f:
            config = json.load(f)

        # Iterate through the "lyrics_sources" array in the config
        for source in config.get("lyrics_sources", []):
            # Skip disabled sources
            if source.get("disabled", False):
                continue

            # Get the name of the source (e.g., "azlyrics", "musikguru", etc.)
            name = source["name"]

            # Get the format (URL or "search") for the source
            format_string = source.get("format", "")

            # Assign the URL format string to the corresponding name in the sources dictionary
            sources[name] = format_string

        return sources

    def get_lyrics(self, title_x, artist_x):
        if not title_x or not artist_x:
            return None, None

        original_title = title_x
        original_artist = artist_x

        # Trim title and artist
        title_x = self._format_title_or_artist(title_x)
        artist_x = self._format_title_or_artist(artist_x)

        # Try every source
        for source, url_template in self.sources.items():
            try:
                if source == "musikguru":
                    url = self.search_musikguru(original_artist, original_title)
                    if not url:
                        continue
                elif source == "lyricsmode":
                    url = self.search_lyricsmode(original_artist, original_title)
                    if not url:
                        continue
                elif source == "musica":
                    url = self.search_musica(original_artist, original_title)
                    if not url:
                        continue
                elif source == "genius":
                    url = self.search_genius(original_artist, original_title)
                    if not url:
                        continue
                elif source == "azlyrics":
                    title_custom =  title_x.replace("_", "")
                    artist_custom = artist_x.replace("_", "")
                    url = url_template.format(
                        title=title_custom,
                        artist=artist_custom
                    )
                elif (source == "letras" or source == "genius"):
                    title_custom = title_x.replace("_", "-")
                    artist_custom = artist_x.replace("_", "-")
                    url = url_template.format(
                        title=title_custom,
                        artist=artist_custom
                    )
                elif source == "lyricsmania":
                    url = url_template.format(
                        title=title_x,
                        artist=artist_x,
                    )
                else:
                    # Genereer de URL, met aanpassingen voor ?
                    url = url_template.format(
                        title=title_x.replace("-", "").replace(" ", ""),
                        artist=artist_x.replace("_", "").replace(" ", ""),
                    )

                logging.info(f"get_lyrics: {source} URL {url}")

                html_data = self.fetch_lyrics(url)

                if html_data and url.find("musica.com"):
                    if not html_data.find(original_title):
                        continue

                if html_data:
                    # Process HTML to extract lyrics
                    lyric_string = self.process_html2(source, html_data)
                    if LyricsUtils.is_lyric_page(lyric_string): # Check if lyric page is valid
                        return lyric_string, source

            except Exception as e:
                logging.error(f"Error processing source {source} for URL {url}: {e}")
                continue

        # Als geen enkele bron een geldige songtekst retourneert
        return None, None

    @staticmethod
    def _format_title_or_artist(value):
        value = value.strip()
        value = value.lower()
        value = re.sub(r"[:-]", "_", value)
        value = re.sub(r"\s+", "_", value)
        value = re.sub(r"&", "and", value)
        value = re.sub(r"[^\w_]", "", value)
        return value

    def search_musikguru(self, artist, title):
        # Zoek naar een specifieke songtekst met een POST-verzoek naar MusikGuru.
        payload = {"query": f"{artist} {title}"}

        try:
            response = requests.post(
                self.musikguru_search_url, json=payload, headers=self.headers, timeout=10
            )

            if response.status_code != 200:
                print(f"Error: Failed to search MusikGuru (status: {response.status_code})")
                return None

            # Parse JSON results
            search_results = response.json()
            if not search_results:
                print("No results found for the search query.")
                return None

            # Neem de eerste match
            first_result = search_results[0]
            if "data" in first_result and "url" in first_result["data"]:
                url = first_result["data"]["url"]
                if "/" in url:
                    compareTo = artist.replace(" ", "-") + "/" + title.replace(" ", "-")
                    urlToCompare = url.replace("songtext-", "")
                    urlToCompare = urlToCompare[:urlToCompare.rfind('-')] # delete everything after the last hyphen

                    if LyricsUtils.similarity_percentage("musikguru.de", urlToCompare, compareTo) < 80:
                        logging.warning("Skip " + url + " for safety within musikguru.de")
                        return None
                    return f"https://musikguru.de{url}"

            logging.info("MusikGuru: no suitable songtext URL found in search results.")
            return None

        except requests.exceptions.RequestException as e:
            logging.error(f"MusikGuru: error during search: {e}")
            return None

    def search_lyricsmode(self, artist, title):
        # Zoek op LyricsMode en parseer de resultaten om de songtekst-URL op te halen.
        search_url = self.lyricsmode_search_url.format(artist=artist, title=title)

        try:
            # Haal de HTML van de zoekpagina op
            response = requests.get(search_url, timeout=10)

            if response.status_code != 200:
                print(f"LyricsMode: failed to fetch search page: {response.status_code}")
                return None

            # Parse de HTML-inhoud
            soup = BeautifulSoup(response.text, 'html.parser')

            # Selecteer de eerste .lm-list__row
            first_row = soup.select_one(".lm-list__row")

            if not first_row:
                logging.info("LyricsMode: no results found.")
                return None

            # Selecteer de tweede .lm-list__cell binnen de eerste .lm-list__row
            cells = first_row.select(".lm-list__cell")
            if len(cells) < 2:
                logging.info("LyricsMode: second .lm-list__cell not found.")
                return None

            # Extraheer de link of tekst uit de tweede cell
            song_link = cells[1].find("a")  # Vind eventueel een link binnen de cell
            if song_link and "href" in song_link.attrs:  # Controleer of de href aanwezig is
                url = f"https://www.lyricsmode.com{song_link['href']}"
                compareTo = "https://www.lyricsmode.com" + artist.replace(" ", "-") + "/" + title.replace(" ", "-") + ".html"
                if LyricsUtils.similarity_percentage("lyricsmode", url, compareTo) < 80:
                    logging.info("Skip " + url + " for safety within lyricsmode.com")
                    return None
                else:
                    return url

            logging.warning("LyricsMode: no valid link found in the second .lm-list__cell.")
            return None

        except requests.exceptions.RequestException as e:
            logging.warning(f"LyricsMode: error during request: {e}")
            return None

    def search_genius(self, artist, title):
        search_url = self.genius_search_url.format(artist=artist, title=title)

        try:
            # Haal de HTML van de zoekpagina op
            response = requests.get(search_url, timeout=10)

            if response.status_code != 200:
                print(f"Genius: failed to fetch search page: {response.status_code}")
                return None

            else:
                data = response.json()

                # Extract the "url" value from the JSON response directly
                try:
                    url = data['response']['sections'][0]['hits'][0]['result']['url']

                    compareTo = artist.replace(" ", "-") + "-" + title.replace(" ", "-")
                    urlToCompare = url.replace("-lyrics", "").replace("https://genius.com/", "")

                    if LyricsUtils.similarity_percentage("genius", urlToCompare, compareTo) < 90:
                        logging.warning("Skip " + url + " for safety within genius.com")
                        return None

                    return url
                except (KeyError, IndexError) as e:
                    logging.info(f"Genius: URL not found in the response for {artist} - {title}.")

            return None

        except requests.exceptions.RequestException as e:
            logging.warning(f"Genius: error during request: {e}")
            return None

    def search_musica(self, artist, title):
        # Construct the search URL for DuckDuckGo + Musica.com
        artist_replaced = artist.replace(" ", "%20")
        title_replaced = title.replace(" ", "%20")
        search_url = self.duckduckgo_search_url.format(artist=artist_replaced, title=title_replaced)

        try:
            # Fetch the HTML from the search page
            response = requests.get(search_url, timeout=5)

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            logging.info(search_url)

            # Extract the content attribute
            meta_tag = soup.find("meta", {"http-equiv": "refresh"})
            if meta_tag:
                content = meta_tag.get("content", "")

                # Extract the URL part
                if "url=" in content:
                    raw_url = content.split("url=")[1]  # Get everything after "url="

                    # Parse the query string to get the 'uddg' parameter
                    parsed_url = urllib.parse.urlparse(raw_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)

                    if "uddg" in query_params:
                        url = urllib.parse.unquote(query_params["uddg"][0])
                        return url

            return None

        except requests.exceptions.RequestException as e:
            logging.warning(f"Musica.com via DuckDuckGo: error during request: {e}")
            return None

    def fetch_lyrics(self, url):
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.encoding = 'utf-8'

            if(LyricsUtils.similarity_percentage("fetch_lyrics", response.url, url) < 75):
                logging.info(f"fetch_lyrics: redirect from {url} to {response.url} skipped, has <75% similarity")
                return None

            if response.status_code != 200:  # Controleer of verzoek succesvol was
                logging.info(f"fetch_lyrics: failed to retrieve URL {url}. Status code: {response.status_code}")
                return None
            return unescape(response.text)  # Decode HTML-entiteiten
        except requests.exceptions.RequestException as e:
            logging.warning(f"fetch_lyrics: request error for URL {url}: {e}")
            return None

    def process_html2(self, source, html_data):
        text = self.process_html(source, html_data)

        clean_text = re.sub(r'^\n+|\n+$', '', text)
        return clean_text

    def process_html(self, source, html_data):
        # Process specific HTML for each source
        soup = BeautifulSoup(html_data, "html.parser")

        if source == "lyricsmania":
            element = soup.find("div", {"class": "lyrics-body"})
            if element:
                # Vind en verwijder de div met id "video - musictory", als deze bestaat
                for unwanted_div in element.find_all("div", {"id": "video-musictory"}):
                    unwanted_div.extract()

                # Replace <br> tags with newlines before extracting text
                text = element.prettify()  # Get the prettified HTML
                text = text.replace('<br>', '\n')  # Replace <br> tags with newlines

                # Return the cleaned text
                return element.get_text(strip=False).replace('<br>', '\n').replace('\r', '\n')

        if source == "lyricscom":
            element = soup.find("div", {"itemprop": "description"})
            if element:
                return element.get_text(strip=False)

        if source == "sonichits":
            element = soup.find("div", {"id": "lyrics"})
            if element:
                return element.get_text(strip=False)

        if source == "azlyrics":
            # Look for lyrics in the div element that follows the div element `ringtone`
            ringtone_div = soup.find("div", class_="ringtone")
            element = ringtone_div.find_next_sibling("div")

            if element:
                # Remove comments inside the lyrics div
                for comment in element.find_all(string=lambda text: isinstance(text, Comment)):
                    comment.extract()

                text = element.get_text(strip=False)
                return text.strip()

        if source == "lyricsmode":
            element = soup.find("div", {"id": "lyrics_text"})
            if element:
                # Find all <div> tags inside the element and decompose (remove) them
                for div in element.find_all("div"):
                    div.decompose()

                text = element.get_text(strip=False)
                return text.strip()

        if source == "musikguru":
            element = soup.find("div", {"id": "text"})
            if element:
                # Musikguru returns nice text, so we don't need to do a lot of processing
                text = element.get_text(strip=False)
                return text

        if source == "letras":
            element = soup.find("div", {"class": "lyric-original"})
            if element:
                for br in element.find_all("br"):
                    br.replace_with("\r\n")

                # Convert </p> to double newlines
                html_string = str(element)  # Convert the element to a string
                html_string = html_string.replace("</p>", "\r\n\r\n")  # Replace </p> with \r\n\r\n

                # Extract text without HTML tags
                soup = BeautifulSoup(html_string, "html.parser")
                text = soup.get_text(strip=False)

                return text.strip()

        if source == "genius":
            parentelement = soup.find("div", {"id": "lyrics-root"})
            if parentelement:
                # Find all div elements with data-lyrics-container="true"
                elements = parentelement.find_all("div", {"data-lyrics-container": "true"})

                if not elements:
                    logging.warning(f"No div with data-lyrics-container='true' found")
                    return ""

                # Initialize an empty string to hold all merged text
                merged_text = ""

                # Iterate through all matching elements and concatenate their text
                for element in elements:
                    # Replace <br> tags with newlines
                    for br in element.find_all("br"):
                        br.replace_with("\r\n")

                    # Append the text of each element
                    merged_text += element.get_text(strip=False) + '\r\n'

                return merged_text.strip()

        if source == "musica":
            parent_element = soup.find(id="letra")

            if not parent_element:
                logging.warning(f"No div with id=letra found")
                return ""

            for br in parent_element.find_all("br"):
                br.replace_with("\r\n")

            paragraphs = parent_element.find_all("p")

            if len(paragraphs) < 2:
                return ""

            # Remove the first and last paragraph (if needed)
            filtered_paragraphs = [p for p in paragraphs if not (p.find("a") or p.find("strong"))]

            return "\n\n".join(p.get_text(strip=False) for p in filtered_paragraphs)

        # If nothing found in any of the sources
        return ""

Multi Lyrics Finder
-------------------

Multi Lyrics Finder, a desktop app that automatically fetches lyrics for the song on play. It supports several music players (see below) and several lyrics websites.

Features
--------

* Automatic lyric fetching for the currently playing song
* Change the artist or title field and click Get Lyrics
* Switch: artist and title wrongly guessed? Click this button to switch them. The artist text becomes the title text, the title text becomes the artist text.
* Look for lyrics by opening Google in a new tab
* Supported music players:
  * Browser-based: Deezer, Spotify, YouTube, YouTube Music
  * Spotify (Electron) app
  * VLC Media Player
* Save lyrics to a text file
* Multilangual; MLF will try to match your user (system) language

Adding support for other players is quite straightforward if the window title contains enough information. This can be done by editing multi_media_title_fetcher.py, pull requests are welcome.

Not supported:
* Deezer (Electron) app

Installation
------------
Since Multi Lyrics Finder is made with wxPython and wxWidgets, it should run on at least Windows, macOS and Linux.

Requirements:

    Python 3
    pip install wxPython
    pip install requests
    pip install psutil
    pip install bs4
    pip install plyer
    pip install pywinctl

I'm looking if we can make the installation process easier in the future.

Browser-based players
---------------------
Attention: browser-based players like Deezer, Spotify, YouTube and YouTube Music have to be in a separate, dedicated browser window so the tab's title is also the title of the window.

I strongly recommend to install the user script Audio Tab Title in your browser using Tampermonkey or Greasemonkey.
This user script changes the tab title to help recognise the artist for Spotify, YouTube and YouTube Music, which facilitates automatic lyric fetching.

Download: https://greasyfork.org/nl/scripts/525581-audio-tab-title

Lyrics not found?
----------------
With so many sites supported, it's still imaginable that the lyrics for a specific song are not yet available. You can add them yourself [using Lyricsmode.com](https://www.lyricsmode.com/lyrics_submit.php) if you want.

Other tips:
* Did you install the user script for browser-based players?
* Use the Search with Google button
* You can try typing it manually and click on the Get Lyrics button

MLF supports intelligent guessing. This means that when the audio playing is named correctly, it will detect the artist and song title automatically. Good examples:

    Artist - Title (year of release) -> Steve Allen - Letter From My Heart (1984)
    Artist - Title -> Steve Allen - Letter From My Heart
    Artist - Title (anything): the information between parenthesis is discarded
    Artist-Title: also works without spaces before and after the hyphen
    Artist - Title | anything: the information after the pipe is discarded

Wrong formats (might still work):

    Title - Artist
    Title
    Strings that contain two hyphens, like "Artist - Title - Album name". There is one exception: artist names that contain a hyphen are valid. For example "A-ha - Stay On These Roads".

Known issues
------------
* Letras.com/musica.com sometimes gives false positives: lyrics for another song from the same artist, because the requested song lyrics are not available.
* Language cannot be set manually
* To retrieve lyrics for some songs, it would be necessary to add more lyric sources

Wayland, Linux and macOS support
-------
MLF hasn't been tested (yet) on Linux X11 or macOS. In theory it should work.

The automatic lyric fetching on Wayland does not work because of reliance on pygetwindow and pywinctl.



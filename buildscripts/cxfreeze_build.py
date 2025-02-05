from cx_Freeze import setup, Executable
import os
import sys

# Check if we are on Windows, if so, disable the console
base = None
if sys.platform == "win32":
    base = "Win32GUI"

VERSION = os.getenv("VERSION", "0.0.0")

locale_folder = "locale"
main_script = "multi_lyrics_finder.py"
output_folder = "build"

setup(
    name="Multi Lyrics Finder",
    version=VERSION,
    description="Multi Lyrics Finder",
    options={
        "build_exe": {
            "packages": [
                "plyer",
            ],
            "includes": [
                "plyer.platforms"
            ],
            "zip_include_packages": ["plyer.platforms"],
            "include_files": [(locale_folder, "locale"), ("config.json", "config.json")]
        }
    },
    executables=[Executable(main_script, base=base)]
)

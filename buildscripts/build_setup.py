import os
import subprocess
from datetime import datetime

# Ensure the build/setup directory exists
os.makedirs("../build/setup", exist_ok=True)

# Check if VERSION is set as an environment variable
VERSION = os.environ.get("VERSION")

if not VERSION:
    print("Warning: VERSION not found in multi_lyrics_finder.py")
    current_date = datetime.now().strftime("%Y.%m.%d")
    VERSION = f"{current_date}.999"

print(f"Building NSIS installer with version: {VERSION}")

# Run NSIS with the extracted VERSION
nsis_exe = r"C:\Program Files (x86)\NSIS\makensis.exe"
nsi_script = "Multi Lyrics Finder Setup.nsi"

SOURCEDIR= open(nsi_script).readlines()[2].strip().split()[-1].replace('"', '')
SOURCEDIR = os.path.normpath(SOURCEDIR)
SIZE=sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(SOURCEDIR) for f in fn) / 1024

subprocess.run(
    [nsis_exe, f"-DVERSION={VERSION}", f"-DSIZE={SIZE}", nsi_script],
    check=True
)
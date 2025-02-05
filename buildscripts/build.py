import os
import shutil
import subprocess
import sys

# Extract VERSION from the second line of multi_lyrics_finder.py
multi_lyrics_file = "../multi_lyrics_finder.py"

try:
    with open(multi_lyrics_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > 1:
            VERSION = lines[1].strip().replace('"', "")
        else:
            raise ValueError("VERSION not found.")
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
    sys.exit(1)  # Exit the script with an error code

print(f"Building {VERSION}")
os.environ["VERSION"] = VERSION

shutil.copy("cxfreeze_build.py", "..")
os.chdir("..")
subprocess.run(["python", "cxfreeze_build.py", "build"], check=True)
os.remove("cxfreeze_build.py")

if os.name == "nt":
    os.chdir("buildscripts")
    subprocess.run(["python", "build_setup.py"], check=True)
import os
import sys

class FileUtils:
    @staticmethod
    def get_file_path(filename):
        """Returns the full path to a file in the root directory."""
        # Check if the script is running as a bundled executable (e.g., PyInstaller or cx_Freeze)
        if getattr(sys, '_MEIPASS', False):
            script_dir = sys._MEIPASS  # PyInstaller
        elif getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)  # cx_Freeze
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Running as a normal script

        # Construct the full file path by combining the script directory with the provided filename
        file_path = os.path.join(script_dir, filename)

        return file_path
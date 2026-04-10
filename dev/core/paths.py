# core/paths.py

import os
import sys


def get_base_dir() -> str:
    """
    Return the correct base directory for both:
    - normal Python execution
    - bundled .exe execution (PyInstaller / similar)

    When the app is frozen into an executable, sys.executable points to the
    launcher .exe location. Otherwise, we resolve the project root by going
    one level up from the current file inside /core.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = get_base_dir()

# Main project files in the root directory.
GAMES_FILE = os.path.join(BASE_DIR, "games.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
THEMES_FILE = os.path.join(BASE_DIR, "themes.json")
ICON_FILE = os.path.join(BASE_DIR, "icon.ico")
SERVER_VERSION_FILE = os.path.join(BASE_DIR, "server_version.txt")
ROADMAP_FILE = os.path.join(BASE_DIR, "Roadmap.txt")

# Cache directories.
CACHE_DIR = os.path.join(BASE_DIR, "cache")
ICON_CACHE_DIR = os.path.join(CACHE_DIR, "icons")
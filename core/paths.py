# core/paths.py

import os
import sys


def get_runtime_base_dir() -> str:
    """
    Return the writable runtime base directory.

    Behavior:
    - In normal Python execution, this is the project root directory.
    - In a bundled executable, this is the folder where the .exe is located.

    This directory is used for files that should live next to the launcher,
    such as:
    - games.json
    - settings.json
    - cache/icons
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_base_dir() -> str:
    """
    Return the base directory for bundled read-only resources.

    Behavior:
    - In a PyInstaller onefile build, resources are unpacked into sys._MEIPASS.
    - In a normal Python run or onedir build, resources are resolved from the
      project root directory.

    This directory is used for bundled assets such as:
    - themes.json
    - icon.ico
    """
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


RUNTIME_BASE_DIR = get_runtime_base_dir()
RESOURCE_BASE_DIR = get_resource_base_dir()

# Writable runtime files in the launcher folder.
GAMES_FILE = os.path.join(RUNTIME_BASE_DIR, "games.json")
SETTINGS_FILE = os.path.join(RUNTIME_BASE_DIR, "settings.json")

# Read-only bundled resources.
THEMES_FILE = os.path.join(RESOURCE_BASE_DIR, "themes.json")
ICON_FILE = os.path.join(RESOURCE_BASE_DIR, "icon.ico")
SERVER_VERSION_FILE = os.path.join(RESOURCE_BASE_DIR, "server_version.txt")
ROADMAP_FILE = os.path.join(RESOURCE_BASE_DIR, "Roadmap.txt")

# Cache directories should always be writable and live next to the launcher.
CACHE_DIR = os.path.join(RUNTIME_BASE_DIR, "cache")
ICON_CACHE_DIR = os.path.join(CACHE_DIR, "icons")
# core/paths.py

import os
import sys


def get_runtime_base_dir() -> str:
    """
    Return the writable runtime base directory.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_base_dir() -> str:
    """
    Return the base directory for bundled read-only resources.
    """
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


RUNTIME_BASE_DIR = get_runtime_base_dir()
RESOURCE_BASE_DIR = get_resource_base_dir()

GAMES_FILE = os.path.join(RUNTIME_BASE_DIR, "games.json")
SETTINGS_FILE = os.path.join(RUNTIME_BASE_DIR, "settings.json")

THEMES_FILE = os.path.join(RESOURCE_BASE_DIR, "themes.json")
ICON_FILE = os.path.join(RESOURCE_BASE_DIR, "icon.ico")

CACHE_DIR = os.path.join(RUNTIME_BASE_DIR, "cache")
ICON_CACHE_DIR = os.path.join(CACHE_DIR, "icons")
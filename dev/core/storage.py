# core/storage.py

import json
import os
from typing import Any

from core.paths import GAMES_FILE, SETTINGS_FILE, THEMES_FILE


DEFAULT_SETTINGS = {
    "theme": "modern"
}


def load_json_file(file_path: str, fallback: Any):
    """
    Load a JSON file and return its parsed content.

    If the file does not exist or cannot be parsed, return the provided
    fallback value instead. This keeps the launcher stable even if a file
    is missing or malformed.
    """
    if not os.path.exists(file_path):
        return fallback

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return fallback


def save_json_file(file_path: str, data: Any) -> bool:
    """
    Save data to a JSON file.

    Returns True if saving was successful, otherwise False.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except OSError:
        return False


def load_games() -> list[dict]:
    """
    Load the list of game entries from games.json.

    Expected structure:
    [
        {
            "name": "Game Name",
            "path": "C:/Path/To/Game.exe",
            "description": "Optional short description"
        }
    ]

    If the file is missing or invalid, return an empty list.
    """
    data = load_json_file(GAMES_FILE, [])

    if not isinstance(data, list):
        return []

    valid_games = []

    for entry in data:
        if not isinstance(entry, dict):
            continue

        name = entry.get("name")
        path = entry.get("path")
        description = entry.get("description", "")

        if not isinstance(name, str) or not isinstance(path, str):
            continue

        if not isinstance(description, str):
            description = ""

        valid_games.append({
            "name": name,
            "path": path,
            "description": description
        })

    return valid_games


def save_games(games: list[dict]) -> bool:
    """
    Save the current game library to games.json.

    Only valid entries are written to the file. This keeps the JSON structure
    clean and avoids storing malformed objects accidentally.
    """
    if not isinstance(games, list):
        return False

    cleaned_games = []

    for entry in games:
        if not isinstance(entry, dict):
            continue

        name = entry.get("name", "")
        path = entry.get("path", "")
        description = entry.get("description", "")

        if not isinstance(name, str) or not name.strip():
            continue

        if not isinstance(path, str) or not path.strip():
            continue

        if not isinstance(description, str):
            description = ""

        cleaned_games.append({
            "name": name.strip(),
            "path": path.strip(),
            "description": description.strip()
        })

    return save_json_file(GAMES_FILE, cleaned_games)


def load_settings() -> dict:
    """
    Load launcher settings from settings.json.

    Missing or invalid settings are replaced with default values.
    """
    data = load_json_file(SETTINGS_FILE, DEFAULT_SETTINGS.copy())

    if not isinstance(data, dict):
        return DEFAULT_SETTINGS.copy()

    settings = DEFAULT_SETTINGS.copy()
    settings.update(data)

    return settings


def save_settings(settings: dict) -> bool:
    """
    Save launcher settings to settings.json.
    """
    if not isinstance(settings, dict):
        return False

    merged_settings = DEFAULT_SETTINGS.copy()
    merged_settings.update(settings)

    return save_json_file(SETTINGS_FILE, merged_settings)


def load_themes() -> dict:
    """
    Load all available themes from themes.json.

    Expected structure:
    {
        "modern": {
            "label": "Modern",
            "bg": "#15171c",
            ...
        }
    }

    If the file is missing or invalid, return an empty dictionary.
    """
    data = load_json_file(THEMES_FILE, {})

    if not isinstance(data, dict):
        return {}

    valid_themes = {}

    for theme_name, theme_values in data.items():
        if not isinstance(theme_name, str):
            continue

        if not isinstance(theme_values, dict):
            continue

        valid_themes[theme_name] = theme_values

    return valid_themes
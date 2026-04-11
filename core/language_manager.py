# core/language_manager.py

import json
import os
from typing import Dict

from core.paths import RESOURCE_BASE_DIR


TRANSLATIONS_DIR = os.path.join(RESOURCE_BASE_DIR, "translations")
DEFAULT_LANGUAGE = "en"


def get_translation_file_path(language_code: str) -> str:
    """
    Build the absolute file path for a translation JSON file.
    """
    return os.path.join(TRANSLATIONS_DIR, f"{language_code}.json")


def load_translation_file(language_code: str) -> Dict[str, str]:
    """
    Load a single translation JSON file.
    """
    file_path = get_translation_file_path(language_code)

    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        valid_translations: Dict[str, str] = {}

        for key, value in data.items():
            if isinstance(key, str) and isinstance(value, str):
                valid_translations[key] = value

        return valid_translations

    except (OSError, json.JSONDecodeError):
        return {}


def get_available_languages() -> list[str]:
    """
    Return all available language codes based on the translation files.
    """
    if not os.path.exists(TRANSLATIONS_DIR):
        return [DEFAULT_LANGUAGE]

    language_codes: list[str] = []

    try:
        for filename in os.listdir(TRANSLATIONS_DIR):
            if not filename.lower().endswith(".json"):
                continue

            language_code = os.path.splitext(filename)[0]

            if language_code:
                language_codes.append(language_code)

    except OSError:
        return [DEFAULT_LANGUAGE]

    if DEFAULT_LANGUAGE not in language_codes:
        language_codes.append(DEFAULT_LANGUAGE)

    return sorted(set(language_codes))


def get_language_display_name(language_code: str) -> str:
    """
    Convert a language code into a user-friendly display name.
    """
    display_names = {
        "en": "English",
        "de": "Deutsch",
        "es": "Español",
        "fr": "Français",
        "pt-BR": "Português (Brasil)",
    }

    return display_names.get(language_code, language_code)


def load_language(language_code: str) -> Dict[str, str]:
    """
    Load the requested language and merge it with the default language.
    """
    default_translations = load_translation_file(DEFAULT_LANGUAGE)

    if language_code == DEFAULT_LANGUAGE:
        return default_translations

    requested_translations = load_translation_file(language_code)

    merged_translations = default_translations.copy()
    merged_translations.update(requested_translations)

    return merged_translations


def get_text(key: str, translations: Dict[str, str], **format_values) -> str:
    """
    Return the translated text for a given key.
    """
    text = translations.get(key, key)

    if format_values:
        try:
            return text.format(**format_values)
        except (KeyError, ValueError):
            return text

    return text
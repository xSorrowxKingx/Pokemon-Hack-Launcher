# core/theme_manager.py

from core.storage import load_settings, save_settings, load_themes


DEFAULT_THEME_NAME = "modern"

# These keys are the minimum required for a theme to be considered usable.
REQUIRED_THEME_KEYS = {
    "label",
    "bg",
    "header",
    "card",
    "card_hover",
    "text",
    "subtle_text",
    "accent",
    "border"
}


def is_valid_theme(theme_data: dict) -> bool:
    """
    Validate that a theme dictionary contains all required keys.

    This prevents broken or incomplete themes from crashing the UI.
    """
    if not isinstance(theme_data, dict):
        return False

    return REQUIRED_THEME_KEYS.issubset(theme_data.keys())


def get_all_themes() -> dict:
    """
    Return all valid themes from themes.json.

    Invalid theme definitions are ignored automatically.
    """
    themes = load_themes()

    if not isinstance(themes, dict):
        return {}

    valid_themes = {}

    for theme_name, theme_data in themes.items():
        if isinstance(theme_name, str) and is_valid_theme(theme_data):
            valid_themes[theme_name] = theme_data

    return valid_themes


def get_theme_names() -> list[str]:
    """
    Return a list of all valid theme names.
    """
    return list(get_all_themes().keys())


def get_saved_theme_name() -> str:
    """
    Read the currently selected theme name from settings.json.

    If no theme is stored, return the default theme name.
    """
    settings = load_settings()
    theme_name = settings.get("theme", DEFAULT_THEME_NAME)

    if not isinstance(theme_name, str):
        return DEFAULT_THEME_NAME

    return theme_name


def get_fallback_theme() -> dict:
    """
    Return the default fallback theme.

    If the default theme does not exist in themes.json, return the first valid
    theme found. If no valid themes exist at all, return a hardcoded emergency
    fallback so the launcher can still start.
    """
    themes = get_all_themes()

    if DEFAULT_THEME_NAME in themes:
        return themes[DEFAULT_THEME_NAME]

    if themes:
        first_theme_name = next(iter(themes))
        return themes[first_theme_name]

    return {
        "label": "Emergency Fallback",
        "bg": "#15171c",
        "header": "#1b1f27",
        "card": "#20242c",
        "card_hover": "#2a3040",
        "text": "#f4f6fb",
        "subtle_text": "#9aa4b2",
        "accent": "#ffcb05",
        "border": "#2e3440"
    }


def get_active_theme_name() -> str:
    """
    Return the current active theme name if it exists and is valid.

    If the saved theme name is missing or invalid, fall back to the default
    theme name or the first valid available theme.
    """
    themes = get_all_themes()
    saved_theme_name = get_saved_theme_name()

    if saved_theme_name in themes:
        return saved_theme_name

    if DEFAULT_THEME_NAME in themes:
        return DEFAULT_THEME_NAME

    if themes:
        return next(iter(themes))

    return DEFAULT_THEME_NAME


def get_theme(theme_name: str) -> dict:
    """
    Return a specific theme by name.

    If the requested theme does not exist or is invalid, return the fallback
    theme instead.
    """
    themes = get_all_themes()

    if theme_name in themes:
        return themes[theme_name]

    return get_fallback_theme()


def get_active_theme() -> dict:
    """
    Return the currently active theme dictionary.
    """
    active_theme_name = get_active_theme_name()
    return get_theme(active_theme_name)


def set_active_theme(theme_name: str) -> bool:
    """
    Save the selected theme name to settings.json.

    Returns True if the theme exists and was saved successfully.
    """
    themes = get_all_themes()

    if theme_name not in themes:
        return False

    settings = load_settings()
    settings["theme"] = theme_name

    return save_settings(settings)
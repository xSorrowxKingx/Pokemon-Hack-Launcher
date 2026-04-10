# ui/theme_selector.py

import tkinter as tk

from core.paths import ICON_FILE
from core.theme_manager import get_theme, get_active_theme_name, set_active_theme


def update_theme_preview(
    preview_widgets: dict,
    theme_data: dict,
    theme_name: str
):
    """
    Update the preview area inside the theme selector window.

    The preview is purely visual and does not save/apply anything by itself.
    It only updates the example widgets so the user can see how a theme looks.
    """
    preview_container = preview_widgets["preview_container"]
    preview_header = preview_widgets["preview_header"]
    preview_title = preview_widgets["preview_title"]
    preview_subtitle = preview_widgets["preview_subtitle"]
    preview_card = preview_widgets["preview_card"]
    preview_card_title = preview_widgets["preview_card_title"]
    preview_card_text = preview_widgets["preview_card_text"]
    preview_action_button = preview_widgets["preview_action_button"]
    selected_theme_label = preview_widgets["selected_theme_label"]

    preview_container.configure(bg=theme_data["bg"])
    preview_header.configure(bg=theme_data["header"])
    preview_title.configure(bg=theme_data["header"], fg=theme_data["text"])
    preview_subtitle.configure(bg=theme_data["header"], fg=theme_data["subtle_text"])

    preview_card.configure(
        bg=theme_data["card"],
        highlightbackground=theme_data["border"]
    )
    preview_card_title.configure(bg=theme_data["card"], fg=theme_data["text"])
    preview_card_text.configure(bg=theme_data["card"], fg=theme_data["subtle_text"])

    preview_action_button.configure(
        bg=theme_data["accent"],
        fg=theme_data["text"],
        activebackground=theme_data["card_hover"],
        activeforeground=theme_data["text"]
    )

    selected_theme_label.configure(
        bg=theme_data["bg"],
        fg=theme_data["text"],
        text=f"Preview: {theme_data.get('label', theme_name)}"
    )


def open_theme_selector(
    root: tk.Tk,
    themes: dict,
    on_theme_changed=None
):
    """
    Open the theme selector window.

    Parameters:
    - root: the main launcher root window
    - themes: all valid themes from theme_manager/storage
    - on_theme_changed: optional callback that will later allow the launcher
      to update itself live after a theme change

    Current behavior in this version:
    - shows a preview area
    - saves the chosen theme via set_active_theme(...)
    - can optionally notify the launcher through on_theme_changed(...)
    """
    current_theme_name = get_active_theme_name()
    current_theme = get_theme(current_theme_name)

    selector = tk.Toplevel(root)
    selector.title("Select Theme")
    selector.resizable(False, False)
    selector.configure(bg=current_theme["header"])

    try:
        selector.iconbitmap(ICON_FILE)
    except Exception:
        pass

    window_width = 760
    window_height = 430

    selector.update_idletasks()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    pos_x = root_x + (root_width // 2) - (window_width // 2)
    pos_y = root_y + (root_height // 2) - (window_height // 2)

    selector.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
    selector.transient(root)
    selector.grab_set()

    header_frame = tk.Frame(selector, bg=current_theme["header"], height=72)
    header_frame.pack(fill="x")

    title_label = tk.Label(
        header_frame,
        text="Select Theme",
        bg=current_theme["header"],
        fg=current_theme["text"],
        font=("Segoe UI", 15, "bold")
    )
    title_label.pack(anchor="w", padx=18, pady=(14, 0))

    subtitle_label = tk.Label(
        header_frame,
        text="Choose a theme and preview how the launcher will look.",
        bg=current_theme["header"],
        fg=current_theme["subtle_text"],
        font=("Segoe UI", 9)
    )
    subtitle_label.pack(anchor="w", padx=18, pady=(2, 12))

    content_frame = tk.Frame(selector, bg=current_theme["bg"])
    content_frame.pack(fill="both", expand=True)

    left_panel = tk.Frame(content_frame, bg=current_theme["bg"])
    left_panel.pack(side="left", fill="y", padx=(18, 10), pady=18)

    right_panel = tk.Frame(
        content_frame,
        bg=current_theme["bg"],
        highlightthickness=1,
        highlightbackground=current_theme["border"]
    )
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 18), pady=18)

    left_title = tk.Label(
        left_panel,
        text="Available Themes",
        bg=current_theme["bg"],
        fg=current_theme["text"],
        font=("Segoe UI", 11, "bold"),
        anchor="w"
    )
    left_title.pack(anchor="w", pady=(0, 10))

    selected_theme_name_var = tk.StringVar(value=current_theme_name)

    def handle_theme_selection(theme_name: str):
        theme_data = get_theme(theme_name)

        selected_theme_name_var.set(theme_name)
        update_theme_preview(preview_widgets, theme_data, theme_name)

        save_success = set_active_theme(theme_name)

        if save_success and callable(on_theme_changed):
            on_theme_changed(theme_name, theme_data)

    for theme_name, theme_data in themes.items():
        radio_button = tk.Radiobutton(
            left_panel,
            text=theme_data.get("label", theme_name),
            variable=selected_theme_name_var,
            value=theme_name,
            command=lambda selected_name=theme_name: handle_theme_selection(selected_name),
            bg=current_theme["bg"],
            fg=current_theme["text"],
            selectcolor=current_theme["card"],
            activebackground=current_theme["bg"],
            activeforeground=current_theme["text"],
            anchor="w",
            width=22,
            indicatoron=True,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        radio_button.pack(anchor="w", pady=4)

        radio_button.bind(
            "<Enter>",
            lambda event, preview_name=theme_name: update_theme_preview(
                preview_widgets,
                get_theme(preview_name),
                preview_name
            )
        )

        radio_button.bind(
            "<Leave>",
            lambda event: update_theme_preview(
                preview_widgets,
                get_theme(selected_theme_name_var.get()),
                selected_theme_name_var.get()
            )
        )

    close_button = tk.Button(
        left_panel,
        text="Close",
        command=selector.destroy,
        bg=current_theme["card"],
        fg=current_theme["text"],
        activebackground=current_theme["card_hover"],
        activeforeground=current_theme["text"],
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=current_theme["border"],
        font=("Segoe UI", 10, "bold"),
        padx=14,
        pady=7,
        cursor="hand2"
    )
    close_button.pack(anchor="w", pady=(18, 0))

    preview_container = tk.Frame(right_panel, bg=current_theme["bg"])
    preview_container.pack(fill="both", expand=True)

    selected_theme_label = tk.Label(
        preview_container,
        text="Preview",
        bg=current_theme["bg"],
        fg=current_theme["text"],
        font=("Segoe UI", 11, "bold"),
        anchor="w"
    )
    selected_theme_label.pack(anchor="w", padx=16, pady=(14, 12))

    preview_header = tk.Frame(preview_container, bg=current_theme["header"], height=64)
    preview_header.pack(fill="x", padx=16, pady=(0, 14))
    preview_header.pack_propagate(False)

    preview_title = tk.Label(
        preview_header,
        text="Pokémon Hack Launcher",
        bg=current_theme["header"],
        fg=current_theme["text"],
        font=("Segoe UI", 12, "bold")
    )
    preview_title.pack(anchor="w", padx=14, pady=(10, 0))

    preview_subtitle = tk.Label(
        preview_header,
        text="Example launcher header preview",
        bg=current_theme["header"],
        fg=current_theme["subtle_text"],
        font=("Segoe UI", 9)
    )
    preview_subtitle.pack(anchor="w", padx=14, pady=(2, 10))

    preview_card = tk.Frame(
        preview_container,
        bg=current_theme["card"],
        highlightthickness=1,
        highlightbackground=current_theme["border"]
    )
    preview_card.pack(fill="x", padx=16, pady=(0, 14))

    preview_card_title = tk.Label(
        preview_card,
        text="Pokémon Example Hack",
        bg=current_theme["card"],
        fg=current_theme["text"],
        font=("Segoe UI", 11, "bold"),
        anchor="w"
    )
    preview_card_title.pack(anchor="w", padx=14, pady=(12, 4))

    preview_card_text = tk.Label(
        preview_card,
        text="A fan-made Pokémon adventure with unique mechanics and its own style.",
        bg=current_theme["card"],
        fg=current_theme["subtle_text"],
        font=("Segoe UI", 9),
        anchor="w",
        justify="left",
        wraplength=420
    )
    preview_card_text.pack(anchor="w", padx=14, pady=(0, 10))

    preview_action_button = tk.Button(
        preview_card,
        text="Launch",
        bg=current_theme["accent"],
        fg=current_theme["text"],
        activebackground=current_theme["card_hover"],
        activeforeground=current_theme["text"],
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    )
    preview_action_button.pack(anchor="e", padx=14, pady=(0, 12))

    preview_hint = tk.Label(
        preview_container,
        text="Hover a theme to preview it. Click a theme to save it.",
        bg=current_theme["bg"],
        fg=current_theme["subtle_text"],
        font=("Segoe UI", 9),
        anchor="w",
        justify="left"
    )
    preview_hint.pack(anchor="w", padx=16, pady=(0, 16))

    preview_widgets = {
        "preview_container": preview_container,
        "preview_header": preview_header,
        "preview_title": preview_title,
        "preview_subtitle": preview_subtitle,
        "preview_card": preview_card,
        "preview_card_title": preview_card_title,
        "preview_card_text": preview_card_text,
        "preview_action_button": preview_action_button,
        "selected_theme_label": selected_theme_label
    }

    update_theme_preview(preview_widgets, current_theme, current_theme_name)

    selector.focus_set()
    return selector
# ui/options_manager.py

import tkinter as tk

from core.paths import ICON_FILE
from core.language_manager import (
    get_available_languages,
    get_language_display_name,
    get_text,
    load_language,
)
from core.theme_manager import (
    get_active_theme,
    get_active_theme_name,
    get_all_themes,
    get_theme,
    set_active_theme,
)


def update_theme_preview(
    preview_widgets: dict,
    theme_data: dict,
    theme_name: str,
    translations: dict,
):
    """
    Update the theme preview panel for the currently hovered or selected theme.
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
    preview_hint = preview_widgets["preview_hint"]

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
        activeforeground=theme_data["text"],
        text=get_text("buttons.launch", translations)
    )

    selected_theme_label.configure(
        bg=theme_data["bg"],
        fg=theme_data["text"],
        text=f"{get_text('theme.preview', translations)}: {theme_data.get('label', theme_name)}"
    )

    preview_hint.configure(
        bg=theme_data["bg"],
        fg=theme_data["subtle_text"],
        text=get_text("theme.preview_hint", translations)
    )

    preview_title.configure(text=get_text("app.title", translations))
    preview_subtitle.configure(text=get_text("theme.preview_header", translations))
    preview_card_title.configure(text=get_text("theme.preview_card_title", translations))
    preview_card_text.configure(text=get_text("theme.preview_card_text", translations))


def open_options_manager(
    root: tk.Tk,
    theme: dict,
    translations: dict,
    language_code: str,
    on_theme_changed=None,
    on_language_changed=None,
    initial_section: str = "theme",
):
    """
    Open the options window with a left-side navigation and a dynamic content area.

    Sections:
    - Theme
    - Language
    """
    current_theme_name = get_active_theme_name()
    available_themes = get_all_themes()

    options_window = tk.Toplevel(root)
    options_window.title(get_text("options.title", translations))
    options_window.resizable(False, False)
    options_window.configure(bg=theme["header"])

    try:
        options_window.iconbitmap(ICON_FILE)
    except Exception:
        pass

    window_width = 960
    window_height = 560

    options_window.update_idletasks()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    pos_x = root_x + (root_width // 2) - (window_width // 2)
    pos_y = root_y + (root_height // 2) - (window_height // 2)

    options_window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
    options_window.transient(root)
    options_window.grab_set()

    active_section = tk.StringVar(value=initial_section)

    header_frame = tk.Frame(options_window, bg=theme["header"], height=82)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)

    header_title = tk.Label(
        header_frame,
        text=get_text("options.title", translations),
        bg=theme["header"],
        fg=theme["text"],
        font=("Segoe UI", 15, "bold")
    )
    header_title.pack(anchor="w", padx=18, pady=(14, 0))

    header_subtitle = tk.Label(
        header_frame,
        text=get_text("options.subtitle", translations),
        bg=theme["header"],
        fg=theme["subtle_text"],
        font=("Segoe UI", 9),
        anchor="w",
        justify="left"
    )
    header_subtitle.pack(anchor="w", padx=18, pady=(4, 14))

    body_frame = tk.Frame(options_window, bg=theme["bg"])
    body_frame.pack(fill="both", expand=True)

    sidebar_frame = tk.Frame(
        body_frame,
        bg=theme["card"],
        highlightthickness=1,
        highlightbackground=theme["border"],
        width=220
    )
    sidebar_frame.pack(side="left", fill="y", padx=(18, 10), pady=18)
    sidebar_frame.pack_propagate(False)

    content_frame = tk.Frame(
        body_frame,
        bg=theme["bg"],
        highlightthickness=1,
        highlightbackground=theme["border"]
    )
    content_frame.pack(side="right", fill="both", expand=True, padx=(10, 18), pady=18)

    def reopen_window(section_name: str, next_language_code: str | None = None):
        """
        Reopen the options window after a theme or language change so the
        window itself can fully reflect the new state.
        """
        options_window.destroy()

        resolved_language_code = next_language_code or language_code
        next_translations = load_language(resolved_language_code)

        root.after(
            50,
            lambda: open_options_manager(
                root=root,
                theme=get_active_theme(),
                translations=next_translations,
                language_code=resolved_language_code,
                on_theme_changed=on_theme_changed,
                on_language_changed=on_language_changed,
                initial_section=section_name,
            )
        )

    def select_section(section_name: str):
        """
        Switch the visible section.
        """
        active_section.set(section_name)
        rebuild_content()
        update_navigation_buttons()

    def handle_theme_selection(theme_name: str):
        """
        Save the selected theme, refresh the launcher and reopen the options window.
        """
        selected_theme = get_theme(theme_name)

        if set_active_theme(theme_name) and callable(on_theme_changed):
            on_theme_changed(theme_name, selected_theme)

        reopen_window("theme")

    def handle_language_selection(selected_language_code: str):
        """
        Save the selected language, refresh the launcher and reopen the options window.
        """
        if callable(on_language_changed):
            on_language_changed(selected_language_code)

        reopen_window("language", next_language_code=selected_language_code)

    def build_theme_section(parent: tk.Widget):
        """
        Build the theme section with grouped theme entries and a preview panel.
        """
        section_wrapper = tk.Frame(parent, bg=theme["bg"])
        section_wrapper.pack(fill="both", expand=True)

        section_header = tk.Frame(section_wrapper, bg=theme["bg"])
        section_header.pack(fill="x", padx=18, pady=(16, 10))

        section_title = tk.Label(
            section_header,
            text=get_text("theme.title", translations),
            bg=theme["bg"],
            fg=theme["text"],
            font=("Segoe UI", 13, "bold")
        )
        section_title.pack(anchor="w")

        section_subtitle = tk.Label(
            section_header,
            text=get_text("theme.subtitle", translations),
            bg=theme["bg"],
            fg=theme["subtle_text"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left"
        )
        section_subtitle.pack(anchor="w", pady=(4, 0))

        section_body = tk.Frame(section_wrapper, bg=theme["bg"])
        section_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        theme_list_panel = tk.Frame(section_body, bg=theme["bg"])
        theme_list_panel.pack(side="left", fill="y", padx=(0, 10))

        preview_panel = tk.Frame(
            section_body,
            bg=theme["bg"],
            highlightthickness=1,
            highlightbackground=theme["border"]
        )
        preview_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        theme_canvas = tk.Canvas(
            theme_list_panel,
            bg=theme["bg"],
            highlightthickness=0,
            bd=0,
            width=240
        )
        theme_canvas.pack(side="left", fill="both", expand=True)

        theme_scrollbar = tk.Scrollbar(
            theme_list_panel,
            orient="vertical",
            command=theme_canvas.yview
        )
        theme_scrollbar.pack(side="right", fill="y")

        theme_canvas.configure(yscrollcommand=theme_scrollbar.set)

        theme_inner = tk.Frame(theme_canvas, bg=theme["bg"])
        canvas_window = theme_canvas.create_window((0, 0), window=theme_inner, anchor="nw")

        theme_inner.bind(
            "<Configure>",
            lambda event: theme_canvas.configure(scrollregion=theme_canvas.bbox("all"))
        )

        theme_canvas.bind(
            "<Configure>",
            lambda event: theme_canvas.itemconfigure(canvas_window, width=event.width)
        )

        def _bind_theme_mousewheel():
            def _on_mousewheel(event):
                theme_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            theme_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_theme_mousewheel():
            theme_canvas.unbind_all("<MouseWheel>")

        theme_canvas.bind("<Enter>", lambda event: _bind_theme_mousewheel())
        theme_canvas.bind("<Leave>", lambda event: _unbind_theme_mousewheel())

        theme_groups = {
            get_text("theme.group.core", translations): ["light", "dark", "modern"],
            get_text("theme.group.editions", translations): ["firered", "leafgreen", "electrickyellow", "emerald", "ultra"],
            get_text("theme.group.locations", translations): ["lavendertown", "cinnabar", "distortion", "teamrocket", "plasma"],
            get_text("theme.group.fan_hacks", translations): ["prism", "infinitefusion", "radicalred"]
        }

        preview_container = tk.Frame(preview_panel, bg=theme["bg"])
        preview_container.pack(fill="both", expand=True)

        selected_theme_label = tk.Label(
            preview_container,
            text=get_text("theme.preview", translations),
            bg=theme["bg"],
            fg=theme["text"],
            font=("Segoe UI", 11, "bold")
        )
        selected_theme_label.pack(anchor="w", padx=16, pady=(14, 12))

        preview_header = tk.Frame(preview_container, bg=theme["header"], height=64)
        preview_header.pack(fill="x", padx=16, pady=(0, 14))
        preview_header.pack_propagate(False)

        preview_title = tk.Label(
            preview_header,
            text=get_text("app.title", translations),
            bg=theme["header"],
            fg=theme["text"],
            font=("Segoe UI", 12, "bold")
        )
        preview_title.pack(anchor="w", padx=14, pady=(10, 0))

        preview_subtitle = tk.Label(
            preview_header,
            text=get_text("theme.preview_header", translations),
            bg=theme["header"],
            fg=theme["subtle_text"],
            font=("Segoe UI", 9)
        )
        preview_subtitle.pack(anchor="w", padx=14, pady=(2, 10))

        preview_card = tk.Frame(
            preview_container,
            bg=theme["card"],
            highlightthickness=1,
            highlightbackground=theme["border"]
        )
        preview_card.pack(fill="x", padx=16, pady=(0, 14))

        preview_card_title = tk.Label(
            preview_card,
            text=get_text("theme.preview_card_title", translations),
            bg=theme["card"],
            fg=theme["text"],
            font=("Segoe UI", 11, "bold")
        )
        preview_card_title.pack(anchor="w", padx=14, pady=(12, 4))

        preview_card_text = tk.Label(
            preview_card,
            text=get_text("theme.preview_card_text", translations),
            bg=theme["card"],
            fg=theme["subtle_text"],
            font=("Segoe UI", 9),
            wraplength=430,
            justify="left"
        )
        preview_card_text.pack(anchor="w", padx=14, pady=(0, 10))

        preview_action_button = tk.Button(
            preview_card,
            text=get_text("buttons.launch", translations),
            bg=theme["accent"],
            fg=theme["text"],
            activebackground=theme["card_hover"],
            activeforeground=theme["text"],
            relief="flat",
            padx=12,
            pady=6,
            font=("Segoe UI", 9, "bold")
        )
        preview_action_button.pack(anchor="e", padx=14, pady=(0, 12))

        preview_hint = tk.Label(
            preview_container,
            text=get_text("theme.preview_hint", translations),
            bg=theme["bg"],
            fg=theme["subtle_text"],
            font=("Segoe UI", 9)
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
            "selected_theme_label": selected_theme_label,
            "preview_hint": preview_hint
        }

        for group_name, theme_names in theme_groups.items():
            group_label = tk.Label(
                theme_inner,
                text=group_name,
                bg=theme["bg"],
                fg=theme["subtle_text"],
                font=("Segoe UI", 9, "bold")
            )
            group_label.pack(anchor="w", pady=(12, 4))

            for theme_name in theme_names:
                if theme_name not in available_themes:
                    continue

                theme_data = available_themes[theme_name]
                is_selected = theme_name == current_theme_name

                row_bg = theme["card_hover"] if is_selected else theme["bg"]

                row = tk.Frame(theme_inner, bg=row_bg)
                row.pack(fill="x", pady=2)

                dot = tk.Canvas(
                    row,
                    width=10,
                    height=10,
                    highlightthickness=0,
                    bd=0,
                    bg=row_bg
                )
                dot.create_oval(0, 0, 10, 10, fill=theme_data["accent"], outline="")
                dot.pack(side="left", padx=(6, 8), pady=8)

                name_label = tk.Label(
                    row,
                    text=theme_data.get("label", theme_name),
                    bg=row_bg,
                    fg=theme["text"],
                    font=("Segoe UI", 10),
                    anchor="w"
                )
                name_label.pack(side="left", fill="x", expand=True, pady=8)

                def apply_hover(
                    target_row=row,
                    target_dot=dot,
                    target_label=name_label,
                    selected=is_selected
                ):
                    hover_bg = theme["card_hover"]
                    target_row.configure(bg=hover_bg)
                    target_dot.configure(bg=hover_bg)
                    target_label.configure(bg=hover_bg)

                def remove_hover(
                    target_row=row,
                    target_dot=dot,
                    target_label=name_label,
                    selected=is_selected
                ):
                    normal_bg = theme["card_hover"] if selected else theme["bg"]
                    target_row.configure(bg=normal_bg)
                    target_dot.configure(bg=normal_bg)
                    target_label.configure(bg=normal_bg)

                def on_click(selected=theme_name):
                    handle_theme_selection(selected)

                def on_enter_preview(preview=theme_name):
                    update_theme_preview(
                        preview_widgets,
                        get_theme(preview),
                        preview,
                        translations
                    )

                def on_leave_preview():
                    update_theme_preview(
                        preview_widgets,
                        get_theme(current_theme_name),
                        current_theme_name,
                        translations
                    )

                for widget in (row, dot, name_label):
                    widget.bind("<Enter>", lambda event, fn=apply_hover: fn())
                    widget.bind("<Leave>", lambda event, fn=remove_hover: fn())
                    widget.bind("<Button-1>", lambda event, fn=on_click: fn())
                    widget.bind("<Enter>", lambda event, fn=on_enter_preview: fn(), add="+")
                    widget.bind("<Leave>", lambda event, fn=on_leave_preview: fn(), add="+")

        update_theme_preview(
            preview_widgets,
            get_theme(current_theme_name),
            current_theme_name,
            translations
        )

    def build_language_section(parent: tk.Widget):
        """
        Build the language section using custom selectable rows instead of
        native Radiobutton indicators. This avoids the visual Windows/Tk bug
        where multiple radio dots can appear filled after hover.
        """
        section_wrapper = tk.Frame(parent, bg=theme["bg"])
        section_wrapper.pack(fill="both", expand=True)

        section_header = tk.Frame(section_wrapper, bg=theme["bg"])
        section_header.pack(fill="x", padx=18, pady=(16, 10))

        section_title = tk.Label(
            section_header,
            text=get_text("options.section.language", translations),
            bg=theme["bg"],
            fg=theme["text"],
            font=("Segoe UI", 13, "bold")
        )
        section_title.pack(anchor="w")

        section_subtitle = tk.Label(
            section_header,
            text=get_text("options.language.subtitle", translations),
            bg=theme["bg"],
            fg=theme["subtle_text"],
            font=("Segoe UI", 9),
            anchor="w",
            justify="left"
        )
        section_subtitle.pack(anchor="w", pady=(4, 0))

        section_body = tk.Frame(section_wrapper, bg=theme["bg"])
        section_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        language_card = tk.Frame(
            section_body,
            bg=theme["card"],
            highlightthickness=1,
            highlightbackground=theme["border"]
        )
        language_card.pack(fill="both", expand=True)

        for available_language_code in get_available_languages():
            display_name = get_language_display_name(available_language_code)
            is_selected = available_language_code == language_code

            row_bg = theme["card_hover"] if is_selected else theme["card"]

            row = tk.Frame(language_card, bg=row_bg)
            row.pack(fill="x", padx=12, pady=6)

            indicator_label = tk.Label(
                row,
                text="●" if is_selected else "○",
                bg=row_bg,
                fg=theme["text"],
                font=("Segoe UI", 11, "bold"),
                width=2,
                anchor="w"
            )
            indicator_label.pack(side="left", padx=(8, 2), pady=8)

            text_label = tk.Label(
                row,
                text=display_name,
                bg=row_bg,
                fg=theme["text"],
                font=("Segoe UI", 10),
                anchor="w"
            )
            text_label.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)

            def apply_hover(target_row=row, target_indicator=indicator_label, target_text=text_label):
                hover_bg = theme["card_hover"]
                target_row.configure(bg=hover_bg)
                target_indicator.configure(bg=hover_bg)
                target_text.configure(bg=hover_bg)

            def remove_hover(target_row=row, target_indicator=indicator_label, target_text=text_label, selected=is_selected):
                normal_bg = theme["card_hover"] if selected else theme["card"]
                target_row.configure(bg=normal_bg)
                target_indicator.configure(bg=normal_bg)
                target_text.configure(bg=normal_bg)

            def on_click(selected=available_language_code):
                handle_language_selection(selected)

            for widget in (row, indicator_label, text_label):
                widget.bind("<Enter>", lambda event, fn=apply_hover: fn())
                widget.bind("<Leave>", lambda event, fn=remove_hover: fn())
                widget.bind("<Button-1>", lambda event, fn=on_click: fn())

    def rebuild_content():
        """
        Rebuild the right content area depending on the active section.
        """
        for widget in content_frame.winfo_children():
            widget.destroy()

        if active_section.get() == "theme":
            build_theme_section(content_frame)
        else:
            build_language_section(content_frame)

    sidebar_title = tk.Label(
        sidebar_frame,
        text=get_text("options.title", translations),
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 12, "bold")
    )
    sidebar_title.pack(anchor="w", padx=14, pady=(14, 12))

    theme_nav_button = tk.Button(
        sidebar_frame,
        text=get_text("options.section.theme", translations),
        command=lambda: select_section("theme"),
        relief="flat",
        bd=0,
        padx=12,
        pady=10,
        anchor="w",
        cursor="hand2",
        font=("Segoe UI", 10, "bold")
    )
    theme_nav_button.pack(fill="x", padx=12, pady=(0, 8))

    language_nav_button = tk.Button(
        sidebar_frame,
        text=get_text("options.section.language", translations),
        command=lambda: select_section("language"),
        relief="flat",
        bd=0,
        padx=12,
        pady=10,
        anchor="w",
        cursor="hand2",
        font=("Segoe UI", 10, "bold")
    )
    language_nav_button.pack(fill="x", padx=12, pady=(0, 8))

    close_button = tk.Button(
        sidebar_frame,
        text=get_text("buttons.close", translations),
        command=options_window.destroy,
        bg=theme["card_hover"],
        fg=theme["text"],
        activebackground=theme["accent"],
        activeforeground=theme["text"],
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=theme["border"],
        font=("Segoe UI", 10, "bold"),
        padx=14,
        pady=8,
        cursor="hand2"
    )
    close_button.pack(side="bottom", fill="x", padx=12, pady=12)

    def update_navigation_buttons():
        """
        Update the visual state of the sidebar navigation.
        """
        default_bg = theme["card"]
        active_bg = theme["accent"]

        theme_nav_button.configure(
            bg=active_bg if active_section.get() == "theme" else default_bg,
            fg=theme["text"],
            activebackground=theme["card_hover"],
            activeforeground=theme["text"]
        )

        language_nav_button.configure(
            bg=active_bg if active_section.get() == "language" else default_bg,
            fg=theme["text"],
            activebackground=theme["card_hover"],
            activeforeground=theme["text"]
        )

    rebuild_content()
    update_navigation_buttons()

    options_window.focus_set()
    return options_window
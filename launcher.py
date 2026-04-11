# launcher.pyw

import tkinter as tk
from datetime import datetime

from core.paths import ICON_FILE
from core.storage import load_games, load_settings, save_settings, save_games
from core.language_manager import load_language, get_text
from core.theme_manager import get_active_theme
from core.version import LAUNCHER_NAME, LAUNCHER_VERSION
from ui.components import create_action_button, create_game_card, launch_game
from ui.game_manager import open_game_manager
from ui.options_manager import open_options_manager


class PokemonHackLauncher:
    """
    Main application class for the Pokémon Hack Launcher.

    This class is responsible for:
    - creating the main Tk root window
    - loading launcher data
    - rendering the UI
    - refreshing the UI when the active theme changes
    - opening the internal game manager
    - opening the options manager
    - filtering the visible game list via live search
    - handling favorites
    - tracking recently played games
    """

    def __init__(self):
        self.root = tk.Tk()

        self.settings = load_settings()
        self.language_code = self.settings.get("language", "en")
        self.translations = load_language(self.language_code)

        self.root.title(get_text("app.title", self.translations))

        try:
            self.root.iconbitmap(ICON_FILE)
        except Exception:
            pass

        self.root.bind("<Escape>", lambda event: self.root.destroy())

        self.window_width = 640
        self.window_height = 680

        self.theme = get_active_theme()
        self.games = load_games()

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_changed)

        self.active_filter = "all"

        self.main_container = None
        self.canvas = None
        self.scrollable_frame = None
        self.content_wrapper = None
        self.scrollbar = None
        self.canvas_window = None

        self.setup_window()
        self.build_ui()

    def setup_window(self):
        """
        Configure the main launcher window size and initial screen position.
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        center_x = int((screen_width / 2) - (self.window_width / 2))
        center_y = int((screen_height / 2) - (self.window_height / 2))

        self.root.geometry(f"{self.window_width}x{self.window_height}+{center_x}+{center_y}")
        self.root.minsize(620, 780)

    def clear_main_container(self):
        """
        Destroy only the main launcher container before rebuilding the interface.
        """
        if self.main_container is not None and self.main_container.winfo_exists():
            self.main_container.destroy()

        self.main_container = None
        self.canvas = None
        self.scrollable_frame = None
        self.content_wrapper = None
        self.scrollbar = None
        self.canvas_window = None

    def refresh_theme(self, theme_name=None, theme_data=None):
        """
        Refresh the launcher UI after a theme change.
        """
        if isinstance(theme_name, str) and theme_name.strip():
            self.settings["theme"] = theme_name

        if theme_data is not None:
            self.theme = theme_data
        else:
            self.theme = get_active_theme()

        self.clear_main_container()
        self.build_ui()

    def refresh_games(self):
        """
        Reload the game list from games.json and rebuild only the main launcher UI.
        """
        self.games = load_games()
        self.clear_main_container()
        self.build_ui()

        self.root.after(120, self._finalize_game_refresh)

    def _finalize_game_refresh(self):
        """
        Perform a second lightweight game refresh shortly after the initial rebuild.
        """
        self.games = load_games()
        self.clear_main_container()
        self.build_ui()

    def refresh_language(self, language_code: str):
        """
        Save the selected language, reload translations and rebuild the UI.
        """
        if not isinstance(language_code, str) or not language_code.strip():
            return

        self.language_code = language_code
        self.settings["language"] = language_code
        save_settings(self.settings)

        self.translations = load_language(language_code)
        self.root.title(get_text("app.title", self.translations))

        self.clear_main_container()
        self.build_ui()

    def on_search_changed(self, *args):
        """
        Re-render only the visible game list when the search text changes.
        """
        self.render_game_cards()

    def set_library_filter(self, filter_name: str):
        """
        Change the active library filter and rebuild the main UI so the
        filter buttons and visible game list stay in sync.
        """
        self.active_filter = filter_name
        self.clear_main_container()
        self.build_ui()

    def toggle_favorite(self, game_path: str):
        """
        Toggle the favorite state of a game and persist the result.
        """
        updated = False

        for entry in self.games:
            if entry.get("path", "") == game_path:
                entry["favorite"] = not entry.get("favorite", False)
                updated = True
                break

        if updated:
            save_games(self.games)
            self.render_game_cards()

    def get_current_timestamp(self) -> str:
        """
        Return a compact European timestamp string for the last played field.
        """
        return datetime.now().strftime("%d.%m.%Y %H:%M")

    def normalize_timestamp_for_display(self, timestamp_value: str) -> str:
        """
        Normalize old and new timestamp formats into one consistent display format.

        Supported input formats:
        - dd.mm.yyyy HH:MM
        - yyyy-mm-dd HH:MM
        """
        if not isinstance(timestamp_value, str):
            return ""

        cleaned_value = timestamp_value.strip()
        if not cleaned_value:
            return ""

        supported_formats = (
            "%d.%m.%Y %H:%M",
            "%Y-%m-%d %H:%M",
        )

        for fmt in supported_formats:
            try:
                parsed = datetime.strptime(cleaned_value, fmt)
                return parsed.strftime("%d.%m.%Y %H:%M")
            except ValueError:
                continue

        return cleaned_value

    def handle_launch_game(self, game_path: str):
        """
        Launch a game and update its last played timestamp.
        """
        launch_game(game_path, self.translations)

        for entry in self.games:
            if entry.get("path", "") == game_path:
                entry["last_played"] = self.get_current_timestamp()
                break

        save_games(self.games)
        self.render_game_cards()

    def get_filtered_games(self, search_query: str = ""):
        """
        Return the currently visible game list based on the active search query
        and the selected library filter.
        """
        query = search_query.strip().lower()

        if not query:
            query = self.search_var.get().strip().lower()

        filtered_games = []

        for entry in self.games:
            name = entry.get("name", "")
            description = entry.get("description", "")
            favorite = entry.get("favorite", False)
            last_played = entry.get("last_played", "")

            if self.active_filter == "favorites" and not favorite:
                continue

            if self.active_filter == "recent" and not last_played.strip():
                continue

            haystack = f"{name} {description}".lower()

            if query and query not in haystack:
                continue

            filtered_games.append(entry)

        if self.active_filter == "recent":
            filtered_games.sort(
                key=lambda item: item.get("last_played", ""),
                reverse=True
            )

        return filtered_games

    def open_manage_games_window(self):
        """
        Open the internal game manager window.
        """
        open_game_manager(
            root=self.root,
            theme=self.theme,
            translations=self.translations,
            on_games_changed=self.refresh_games
        )

    def open_options_window(self):
        """
        Open the central options window.
        """
        open_options_manager(
            root=self.root,
            theme=self.theme,
            translations=self.translations,
            language_code=self.language_code,
            on_theme_changed=self.refresh_theme,
            on_language_changed=self.refresh_language
        )

    def build_header(self, parent: tk.Widget):
        """
        Build the header area of the launcher.
        """
        header = tk.Frame(parent, bg=self.theme["header"], height=118)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text=LAUNCHER_NAME,
            font=("Segoe UI", 22, "bold"),
            bg=self.theme["header"],
            fg=self.theme["text"]
        )
        title.pack(pady=(16, 2))

        subtitle = tk.Label(
            header,
            text=get_text("header.subtitle", self.translations),
            font=("Segoe UI", 10),
            bg=self.theme["header"],
            fg=self.theme["subtle_text"]
        )
        subtitle.pack(pady=(0, 2))

        version_label = tk.Label(
            header,
            text=f"Version {LAUNCHER_VERSION}",
            font=("Segoe UI", 8),
            bg=self.theme["header"],
            fg=self.theme["subtle_text"]
        )
        version_label.pack(pady=(0, 10))

        accent_line = tk.Frame(parent, bg=self.theme["accent"], height=3)
        accent_line.pack(fill="x")

    def build_search_bar(self, parent: tk.Widget):
        """
        Build the live search field above the game list.
        """
        search_wrapper = tk.Frame(parent, bg=self.theme["bg"])
        search_wrapper.pack(fill="x", padx=18, pady=(14, 0))

        search_label = tk.Label(
            search_wrapper,
            text=get_text("search.label", self.translations),
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 9, "bold")
        )
        search_label.pack(anchor="w", pady=(0, 6))

        search_entry = tk.Entry(
            search_wrapper,
            textvariable=self.search_var,
            bg=self.theme["card"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.theme["border"],
            highlightcolor=self.theme["accent"],
            font=("Segoe UI", 10)
        )
        search_entry.pack(fill="x", ipady=6)

    def build_filter_bar(self, parent: tk.Widget):
        """
        Build a small filter bar for switching between all games, favorites
        and recently played entries.
        """
        filter_wrapper = tk.Frame(parent, bg=self.theme["bg"])
        filter_wrapper.pack(fill="x", padx=18, pady=(10, 0))

        def create_filter_button(filter_name: str, label_key: str):
            is_active = self.active_filter == filter_name

            button = tk.Button(
                filter_wrapper,
                text=get_text(label_key, self.translations),
                command=lambda: self.set_library_filter(filter_name),
                bg=self.theme["accent"] if is_active else self.theme["card"],
                fg=self.theme["text"],
                activebackground=self.theme["card_hover"],
                activeforeground=self.theme["text"],
                relief="flat",
                bd=1,
                highlightthickness=1,
                highlightbackground=self.theme["border"],
                font=("Segoe UI", 9, "bold"),
                padx=12,
                pady=7,
                cursor="hand2"
            )
            button.pack(side="left", padx=(0, 8))

        create_filter_button("all", "filter.all")
        create_filter_button("favorites", "filter.favorites")
        create_filter_button("recent", "filter.recent")

    def build_game_list(self, parent: tk.Widget):
        """
        Build the scrollable game list area.
        """
        self.content_wrapper = tk.Frame(parent, bg=self.theme["bg"])
        self.content_wrapper.pack(fill="both", expand=True, padx=18, pady=18)

        self.canvas = tk.Canvas(
            self.content_wrapper,
            bg=self.theme["bg"],
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = tk.Scrollbar(
            self.content_wrapper,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        
        SCROLLBAR_MARGIN = 16

        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.canvas_window,
                width=event.width - SCROLLBAR_MARGIN
            )
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.render_game_cards()
        self.bind_mousewheel()

    def bind_mousewheel_to_widget_tree(self, widget: tk.Widget):
        """
        Bind mouse wheel scrolling to a widget and all of its current children.
        This makes scrolling work even when the pointer is directly over a card,
        label, icon, star button or other child widget inside the scroll area.
        """
        def _on_mousewheel(event):
            if self.canvas is not None:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        try:
            widget.bind("<MouseWheel>", _on_mousewheel)
        except Exception:
            pass

        for child in widget.winfo_children():
            self.bind_mousewheel_to_widget_tree(child)

    def render_game_cards(self, search_query: str = ""):
        """
        Render all launcher game cards into the scrollable content area.
        """
        if self.scrollable_frame is None:
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        filtered_games = self.get_filtered_games(search_query)

        if not self.games:
            empty_state_frame = tk.Frame(self.scrollable_frame, bg=self.theme["bg"])
            empty_state_frame.pack(fill="x", pady=80)

            empty_title = tk.Label(
                empty_state_frame,
                text=get_text("empty.no_hacks", self.translations),
                font=("Segoe UI", 11),
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                anchor="center",
                justify="center"
            )
            empty_title.pack(fill="x", pady=(0, 6))

            empty_hint = tk.Label(
                empty_state_frame,
                text=get_text("empty.add_entries", self.translations),
                font=("Segoe UI", 11),
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                anchor="center",
                justify="center"
            )
            empty_hint.pack(fill="x")

        elif not filtered_games:
            no_results_frame = tk.Frame(self.scrollable_frame, bg=self.theme["bg"])
            no_results_frame.pack(fill="x", pady=80)

            no_results_label = tk.Label(
                no_results_frame,
                text=get_text("empty.no_results", self.translations),
                font=("Segoe UI", 11),
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                anchor="center",
                justify="center"
            )
            no_results_label.pack(fill="x")

        else:
            for entry in filtered_games:
                name = entry.get("name", get_text("fallback.unnamed_hack", self.translations))
                path = entry.get("path", "")
                description = entry.get("description", "")
                is_favorite = entry.get("favorite", False)
                last_played_raw = entry.get("last_played", "").strip()

                last_played_display = ""
                normalized_last_played = self.normalize_timestamp_for_display(last_played_raw)
                if normalized_last_played:
                    last_played_display = f"{get_text('label.last_played', self.translations)}: {normalized_last_played}"

                card = create_game_card(
                    parent=self.scrollable_frame,
                    game_name=name,
                    game_path=path,
                    theme=self.theme,
                    translations=self.translations,
                    description=description,
                    is_favorite=is_favorite,
                    last_played=last_played_display,
                    on_toggle_favorite=lambda selected_path=path: self.toggle_favorite(selected_path),
                    launch_command=lambda selected_path=path: self.handle_launch_game(selected_path)
                )
                card.pack(fill="x", pady=8)

                # Make mouse wheel scrolling work even when hovering directly
                # over the card or any child widget inside it.
                self.bind_mousewheel_to_widget_tree(card)

        if self.canvas is not None:
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def bind_mousewheel(self):
        """
        Enable mouse wheel scrolling for the launcher canvas itself.
        Child widgets inside the scroll area are bound separately after rendering.
        """
        def _on_mousewheel(event):
            if self.canvas is not None:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

    def build_bottom_bar(self, parent: tk.Widget):
        """
        Build the bottom action bar with the main launcher controls.
        """
        bottom_bar = tk.Frame(parent, bg=self.theme["header"], height=72)
        bottom_bar.pack(fill="x")
        bottom_bar.pack_propagate(False)

        bottom_bar.grid_columnconfigure(0, weight=1)
        bottom_bar.grid_columnconfigure(1, weight=1)
        bottom_bar.grid_columnconfigure(2, weight=1)

        manage_games_button = create_action_button(
            parent=bottom_bar,
            text=get_text("buttons.manage_games", self.translations),
            command=self.open_manage_games_window,
            theme=self.theme,
            width=16
        )
        manage_games_button.grid(row=0, column=0, padx=8, pady=14)

        options_button = create_action_button(
            parent=bottom_bar,
            text=get_text("buttons.options", self.translations),
            command=self.open_options_window,
            theme=self.theme,
            width=16
        )
        options_button.grid(row=0, column=1, padx=8, pady=14)

        exit_button = create_action_button(
            parent=bottom_bar,
            text=get_text("buttons.exit", self.translations),
            command=self.root.destroy,
            theme=self.theme,
            width=16
        )
        exit_button.grid(row=0, column=2, padx=8, pady=14)

    def build_ui(self):
        """
        Build the complete launcher UI from scratch using the currently active theme.
        """
        self.root.configure(bg=self.theme["bg"])

        self.main_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_container.pack(fill="both", expand=True)

        self.build_header(self.main_container)
        self.build_search_bar(self.main_container)
        self.build_filter_bar(self.main_container)
        self.build_game_list(self.main_container)
        self.build_bottom_bar(self.main_container)

    def run(self):
        """
        Start the Tkinter main loop.
        """
        self.root.mainloop()


def main():
    """
    Entry point for the launcher application.
    """
    app = PokemonHackLauncher()
    app.run()


if __name__ == "__main__":
    main()
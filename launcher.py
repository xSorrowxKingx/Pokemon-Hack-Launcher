# launcher.pyw

import tkinter as tk
from tkinter import messagebox

from core.paths import ICON_FILE
from core.storage import load_games
from core.theme_manager import get_active_theme, get_all_themes
from core.version import LAUNCHER_NAME, LAUNCHER_VERSION, FULL_TITLE
from ui.components import create_action_button, create_game_card
from ui.theme_selector import open_theme_selector
from ui.game_manager import open_game_manager


class PokemonHackLauncher:
    """
    Main application class for the Pokémon Hack Launcher.

    This class is responsible for:
    - creating the main Tk root window
    - loading launcher data
    - rendering the UI
    - refreshing the UI when the active theme changes
    - opening the internal game manager
    - filtering the visible game list via live search
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(FULL_TITLE)

        try:
            self.root.iconbitmap(ICON_FILE)
        except Exception:
            pass

        self.root.bind("<Escape>", lambda event: self.root.destroy())

        self.window_width = 640
        self.window_height = 680

        self.theme = get_active_theme()
        self.games = load_games()

        # Search state
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_changed)

        # Widget references for rebuilding/updating UI safely
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

        This keeps additional Toplevel windows such as:
        - Theme Selector
        - Manage Games

        open while the main launcher UI refreshes.
        """
        self.root.unbind_all("<MouseWheel>")

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

        Only the main launcher UI is rebuilt so that additional Toplevel windows
        can remain open.
        """
        if theme_data is not None:
            self.theme = theme_data
        else:
            self.theme = get_active_theme()

        self.clear_main_container()
        self.build_ui()

    def refresh_games(self):
        """
        Reload the game list from games.json and rebuild only the main launcher UI.

        A short delayed second refresh helps newly created icon cache files appear
        reliably right after saving a new game entry.
        """
        self.games = load_games()
        self.clear_main_container()
        self.build_ui()

        # Run a short follow-up refresh so freshly generated icon cache files
        # can be picked up immediately without requiring a launcher restart.
        self.root.after(120, self._finalize_game_refresh)

    def _finalize_game_refresh(self):
        """
        Perform a second lightweight game refresh shortly after the initial rebuild.

        This is mainly useful for freshly added entries whose icons may only become
        available a moment after the first UI refresh.
        """
        self.games = load_games()
        self.clear_main_container()
        self.build_ui()

    def on_search_changed(self, *args):
        """
        Re-render only the visible game list when the search text changes.
        """
        self.render_game_cards()

    def get_filtered_games(self, search_query: str = ""):
        """
        Return the currently visible game list based on the active search query.

        The search checks:
        - game name
        - optional description
        """
        query = search_query.strip().lower()

        # Fall back to the current search field value when no explicit query was passed.
        if not query:
            query = self.search_var.get().strip().lower()

        if not query:
            return self.games

        filtered_games = []

        for entry in self.games:
            name = entry.get("name", "")
            description = entry.get("description", "")

            haystack = f"{name} {description}".lower()

            if query in haystack:
                filtered_games.append(entry)

        return filtered_games

    def open_theme_window(self):
        """
        Open the theme selector window.

        The selector receives all valid themes and a callback so the main
        launcher can refresh immediately after a theme change.
        """
        themes = get_all_themes()

        if not themes:
            messagebox.showerror(
                "Error",
                "No valid themes were found in themes.json."
            )
            return

        open_theme_selector(
            root=self.root,
            themes=themes,
            on_theme_changed=self.refresh_theme
        )

    def open_manage_games_window(self):
        """
        Open the internal game manager window.

        The manager can add, edit and delete games directly in games.json and
        triggers a launcher refresh after saving changes.
        """
        open_game_manager(
            root=self.root,
            theme=self.theme,
            on_games_changed=self.refresh_games
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
            text="The launcher for your Pokémon ROM hacks and fangames",
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
            text="Search",
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

        # Store the canvas window reference so we can keep the inner frame width
        # synchronized with the visible canvas width. This is important for proper
        # centered empty-state text and full-width game cards.
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width)
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.render_game_cards()
        self.bind_mousewheel()

    def render_game_cards(self, search_query: str = ""):
        """
        Render all launcher game cards into the scrollable content area.
        """
        if self.scrollable_frame is None:
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        filtered_games = self.get_filtered_games(search_query)

        # Show a dedicated empty state when the launcher has no configured games at all.
        if not self.games:
            empty_state_frame = tk.Frame(self.scrollable_frame, bg=self.theme["bg"])
            empty_state_frame.pack(fill="x", pady=80)

            empty_title = tk.Label(
                empty_state_frame,
                text="No hacks found.",
                font=("Segoe UI", 11),
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                anchor="center",
                justify="center"
            )
            empty_title.pack(fill="x", pady=(0, 6))

            empty_hint = tk.Label(
                empty_state_frame,
                text="Use 'Manage Games' to add entries.",
                font=("Segoe UI", 11),
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                anchor="center",
                justify="center"
            )
            empty_hint.pack(fill="x")

        # Show a different state when games exist but the search query matches nothing.
        elif not filtered_games:
            no_results_frame = tk.Frame(self.scrollable_frame, bg=self.theme["bg"])
            no_results_frame.pack(fill="x", pady=80)

            no_results_label = tk.Label(
                no_results_frame,
                text="No matching hacks found.",
                font=("Segoe UI", 11),
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                anchor="center",
                justify="center"
            )
            no_results_label.pack(fill="x")

        # Normal game list rendering.
        else:
            for entry in filtered_games:
                name = entry.get("name", "Unnamed Hack")
                path = entry.get("path", "")
                description = entry.get("description", "")

                card = create_game_card(
                    parent=self.scrollable_frame,
                    game_name=name,
                    game_path=path,
                    theme=self.theme,
                    description=description
                )
                card.pack(fill="x", pady=7)

        if self.canvas is not None:
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def bind_mousewheel(self):
        """
        Enable mouse wheel scrolling for the main game list canvas.
        """
        def _on_mousewheel(event):
            if self.canvas is not None:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.root.bind_all("<MouseWheel>", _on_mousewheel)

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
            text="Manage Games",
            command=self.open_manage_games_window,
            theme=self.theme
        )
        manage_games_button.grid(row=0, column=0, padx=10, pady=14)

        theme_button = create_action_button(
            parent=bottom_bar,
            text="Theme",
            command=self.open_theme_window,
            theme=self.theme
        )
        theme_button.grid(row=0, column=1, padx=10, pady=14)

        exit_button = create_action_button(
            parent=bottom_bar,
            text="Exit",
            command=self.root.destroy,
            theme=self.theme
        )
        exit_button.grid(row=0, column=2, padx=10, pady=14)

    def build_ui(self):
        """
        Build the complete launcher UI from scratch using the currently active theme.
        """
        self.root.configure(bg=self.theme["bg"])

        self.main_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_container.pack(fill="both", expand=True)

        self.build_header(self.main_container)
        self.build_search_bar(self.main_container)
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
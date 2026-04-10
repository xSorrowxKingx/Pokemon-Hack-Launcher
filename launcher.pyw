# launcher.pyw

import os
import tkinter as tk
from tkinter import messagebox

from core.paths import GAMES_FILE, ICON_FILE
from core.storage import load_games
from core.theme_manager import get_active_theme, get_all_themes
from ui.components import create_action_button, create_game_card
from ui.theme_selector import open_theme_selector


class PokemonHackLauncher:
    """
    Main application class for the Pokémon Hack Launcher.

    This class is responsible for:
    - creating the main Tk root window
    - loading launcher data
    - rendering the UI
    - refreshing the UI when the active theme changes
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pokémon Hack Launcher")

        try:
            self.root.iconbitmap(ICON_FILE)
        except Exception:
            # The launcher should still work even if the icon cannot be loaded.
            pass

        self.root.bind("<Escape>", lambda event: self.root.destroy())

        self.window_width = 640
        self.window_height = 680

        self.theme = get_active_theme()
        self.games = load_games()

        # These references are stored so the launcher can properly rebuild the UI.
        self.main_container = None
        self.canvas = None
        self.scrollable_frame = None

        self.setup_window()
        self.build_ui()

    def setup_window(self):
        """
        Configure the main launcher window size and screen position.
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        center_x = int((screen_width / 2) - (self.window_width / 2))
        center_y = int((screen_height / 2) - (self.window_height / 2))

        self.root.geometry(f"{self.window_width}x{self.window_height}+{center_x}+{center_y}")
        self.root.minsize(520, 580)

    def clear_root(self):
        """
        Destroy all root child widgets before rebuilding the interface.

        This is used for live theme refreshes without restarting the launcher.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def refresh_theme(self, theme_name=None, theme_data=None):
        """
        Refresh the launcher UI after a theme change.

        The callback signature is intentionally compatible with the theme
        selector window:
        - theme_name: the selected theme key
        - theme_data: the selected theme dictionary

        If no theme data is passed, the active theme is reloaded from settings.
        """
        if theme_data is not None:
            self.theme = theme_data
        else:
            self.theme = get_active_theme()

        self.clear_root()
        self.build_ui()

    def reload_games(self):
        """
        Reload the game list from games.json and rebuild the visible UI.
        """
        self.games = load_games()
        self.clear_root()
        self.build_ui()

    def open_games_file(self):
        """
        Open games.json with the system default editor.

        If the file does not exist yet, create an empty valid JSON list first.
        """
        if not os.path.exists(GAMES_FILE):
            try:
                with open(GAMES_FILE, "w", encoding="utf-8") as file:
                    file.write("[]")
            except OSError as error:
                messagebox.showerror(
                    "Error",
                    f"Could not create games.json:\n{error}"
                )
                return

        try:
            os.startfile(GAMES_FILE)
        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not open games.json:\n{error}"
            )

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

    def build_header(self, parent: tk.Widget):
        """
        Build the header area of the launcher.
        """
        header = tk.Frame(parent, bg=self.theme["header"], height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Pokémon Hack Launcher",
            font=("Segoe UI", 22, "bold"),
            bg=self.theme["header"],
            fg=self.theme["text"]
        )
        title.pack(pady=(18, 2))

        subtitle = tk.Label(
            header,
            text="The launcher for your Pokémon ROM hacks and fangames",
            font=("Segoe UI", 10),
            bg=self.theme["header"],
            fg=self.theme["subtle_text"]
        )
        subtitle.pack()

        accent_line = tk.Frame(parent, bg=self.theme["accent"], height=3)
        accent_line.pack(fill="x")

    def build_game_list(self, parent: tk.Widget):
        """
        Build the scrollable game list area.
        """
        content_wrapper = tk.Frame(parent, bg=self.theme["bg"])
        content_wrapper.pack(fill="both", expand=True, padx=18, pady=18)

        self.canvas = tk.Canvas(
            content_wrapper,
            bg=self.theme["bg"],
            highlightthickness=0,
            bd=0
        )

        scrollbar = tk.Scrollbar(
            content_wrapper,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not self.games:
            empty_label = tk.Label(
                self.scrollable_frame,
                text="No hacks found.\nUse 'Edit Game List' to add entries.",
                font=("Segoe UI", 11),
                justify="center",
                bg=self.theme["bg"],
                fg=self.theme["subtle_text"],
                pady=20
            )
            empty_label.pack()
        else:
            for entry in self.games:
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

        self.bind_mousewheel()

    def bind_mousewheel(self):
        """
        Enable mouse wheel scrolling for the main game list canvas.

        This matches the behavior from your earlier launcher version.
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

        # Create 4 equal columns so the buttons stay visually balanced.
        bottom_bar.grid_columnconfigure(0, weight=1)
        bottom_bar.grid_columnconfigure(1, weight=1)
        bottom_bar.grid_columnconfigure(2, weight=1)
        bottom_bar.grid_columnconfigure(3, weight=1)

        edit_button = create_action_button(
            parent=bottom_bar,
            text="Edit Game List",
            command=self.open_games_file,
            theme=self.theme
        )
        edit_button.grid(row=0, column=0, padx=10, pady=14)

        theme_button = create_action_button(
            parent=bottom_bar,
            text="Theme",
            command=self.open_theme_window,
            theme=self.theme
        )
        theme_button.grid(row=0, column=1, padx=10, pady=14)

        reload_button = create_action_button(
            parent=bottom_bar,
            text="Reload Launcher",
            command=self.reload_games,
            theme=self.theme
        )
        reload_button.grid(row=0, column=2, padx=10, pady=14)

        exit_button = create_action_button(
            parent=bottom_bar,
            text="Exit",
            command=self.root.destroy,
            theme=self.theme
        )
        exit_button.grid(row=0, column=3, padx=10, pady=14)

    def build_ui(self):
        """
        Build the complete launcher UI from scratch using the currently active theme.
        """
        self.root.configure(bg=self.theme["bg"])

        self.main_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.main_container.pack(fill="both", expand=True)

        self.build_header(self.main_container)
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
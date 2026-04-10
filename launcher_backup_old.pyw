import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "games.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# -----------------------------
# Styling
# -----------------------------
BG_COLOR = "#15171c"
HEADER_COLOR = "#1b1f27"
CARD_COLOR = "#20242c"
CARD_HOVER = "#2a3040"
BUTTON_COLOR = "#252a34"
BUTTON_HOVER = "#313849"
TEXT_COLOR = "#f4f6fb"
SUBTLE_TEXT = "#9aa4b2"
ACCENT_COLOR = "#ffcb05"   # Pokémon-like yellow
ACCENT_BLUE = "#4d8dff"
BORDER_COLOR = "#2e3440"


# -----------------------------
# Themes
# -----------------------------
THEMES = {
    "light": {
        "bg": "#f2f2f2",
        "header": "#e6e6e6",
        "card": "#ffffff",
        "card_hover": "#f7f7f7",
        "text": "#1a1a1a",
        "subtle_text": "#555555",
        "accent": "#4d8dff",
        "border": "#cccccc"
    },

    "dark": {
        "bg": "#1e1e1e",
        "header": "#1e1e1e",
        "card": "#2a2a2a",
        "card_hover": "#3a3a3a",
        "text": "#f2f2f2",
        "subtle_text": "#bbbbbb",
        "accent": "#666666",
        "border": "#3a3a3a"
    },

    "modern": {
        "bg": "#15171c",
        "header": "#1b1f27",
        "card": "#20242c",
        "card_hover": "#2a3040",
        "text": "#f4f6fb",
        "subtle_text": "#9aa4b2",
        "accent": "#ffcb05",
        "border": "#2e3440"
    },

    "firered": {
        "bg": "#1a0f0b",
        "header": "#2a140d",
        "card": "#3a1d12",
        "card_hover": "#51281a",
        "text": "#fff3ee",
        "subtle_text": "#d7b2a5",
        "accent": "#ff5a36",
        "border": "#6e2b1b"
    },

    "leafgreen": {
        "bg": "#0f1a12",
        "header": "#132319",
        "card": "#1b3323",
        "card_hover": "#25452f",
        "text": "#eefcf1",
        "subtle_text": "#b1d2b8",
        "accent": "#78c850",
        "border": "#2c5c39"
    }
}



def load_games():
    if not os.path.exists(CONFIG_FILE):
        return []

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Config file must contain a list.")

        return data

    except Exception as error:
        messagebox.showerror("Error", f"Could not load games.json:\n{error}")
        return []
        

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"theme": "modern"}

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data

    except:
        return {"theme": "modern"}
        

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)
        
        
def apply_theme(root, theme_name):
    settings = load_settings()
    settings["theme"] = theme_name
    save_settings(settings)
    reload_launcher(root)


def update_theme_preview(preview_widgets, theme_name):
    theme = THEMES.get(theme_name, THEMES["modern"])

    preview_widgets["outer"].config(bg=theme["border"])
    preview_widgets["inner"].config(bg=theme["bg"])
    preview_widgets["header"].config(bg=theme["header"])
    preview_widgets["accent"].config(bg=theme["accent"])
    preview_widgets["card"].config(bg=theme["card"], highlightbackground=theme["border"], highlightcolor=theme["border"])
    preview_widgets["card_title"].config(bg=theme["card"], fg=theme["text"])
    preview_widgets["card_subtitle"].config(bg=theme["card"], fg=theme["subtle_text"])
    preview_widgets["bottom"].config(bg=theme["header"])
    preview_widgets["button"].config(
        bg=theme["card"],
        fg=theme["text"],
        highlightbackground=theme["border"],
        highlightcolor=theme["border"]
    )


def open_theme_selector(root):
    selector = tk.Toplevel(root)
    selector.title("Theme auswählen")
    selector.iconbitmap("icon.ico")
    selector.resizable(False, False)
    selector.configure(bg=HEADER_COLOR)
    selector.transient(root)
    selector.grab_set()

    window_width = 420
    window_height = 220

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    center_x = root_x + (root_width // 2) - (window_width // 2)
    center_y = root_y + (root_height // 2) - (window_height // 2)

    selector.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

    main_frame = tk.Frame(selector, bg=HEADER_COLOR)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title = tk.Label(
        main_frame,
        text="Theme",
        font=("Segoe UI", 14, "bold"),
        bg=HEADER_COLOR,
        fg=TEXT_COLOR
    )
    title.pack(pady=(0, 8))

    subtitle = tk.Label(
        main_frame,
        text="Wähle ein Theme für deinen Launcher.",
        font=("Segoe UI", 9),
        bg=HEADER_COLOR,
        fg=SUBTLE_TEXT
    )
    subtitle.pack(pady=(0, 14))

    row_1 = tk.Frame(main_frame, bg=HEADER_COLOR)
    row_1.pack(pady=4)

    row_2 = tk.Frame(main_frame, bg=HEADER_COLOR)
    row_2.pack(pady=4)

    def make_theme_button(parent, label, theme_key):
        return tk.Button(
            parent,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            activebackground=CARD_HOVER,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=1,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: [selector.destroy(), apply_theme(root, theme_key)]
        )

    light_button = make_theme_button(row_1, "Hell", "light")
    light_button.pack(side="left", padx=6)

    dark_button = make_theme_button(row_1, "Dunkel", "dark")
    dark_button.pack(side="left", padx=6)

    modern_button = make_theme_button(row_1, "Modern", "modern")
    modern_button.pack(side="left", padx=6)

    firered_button = make_theme_button(row_2, "FireRed", "firered")
    firered_button.pack(side="left", padx=6)

    leafgreen_button = make_theme_button(row_2, "LeafGreen", "leafgreen")
    leafgreen_button.pack(side="left", padx=6)


def launch_game(path):
    if os.path.exists(path):
        try:
            subprocess.Popen(path, cwd=os.path.dirname(path))
        except Exception as error:
            messagebox.showerror("Error", f"Could not start file:\n{error}")
    else:
        messagebox.showerror(
            "File not found",
            f"The selected game could not be found.\n\nPath:\n{path}\n\nPlease check your games.json entry."
        )


def open_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4, ensure_ascii=False)

    os.startfile(CONFIG_FILE)


def on_enter(event, widget, bg, border=None):
    widget.config(bg=bg)
    if border:
        widget.config(highlightbackground=border, highlightcolor=border)


def on_leave(event, widget, bg, border=None):
    widget.config(bg=bg)
    if border:
        widget.config(highlightbackground=border, highlightcolor=border)


def create_game_card(parent, text, command):
    card = tk.Frame(
        parent,
        bg=CARD_COLOR,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=BORDER_COLOR,
        cursor="hand2"
    )

    left_accent = tk.Frame(card, bg=ACCENT_COLOR, width=6)
    left_accent.pack(side="left", fill="y")

    content = tk.Frame(card, bg=CARD_COLOR)
    content.pack(side="left", fill="both", expand=True)

    title = tk.Label(
        content,
        text=text,
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 14, "bold"),
        anchor="w",
        padx=14,
        pady=16,
        cursor="hand2"
    )
    title.pack(fill="x")

    def handle_click(event=None):
        command()

    for widget in (card, left_accent, content, title):
        widget.bind("<Button-1>", handle_click)
        widget.bind("<Enter>", lambda e, w=card: on_enter(e, w, CARD_HOVER, ACCENT_BLUE))
        widget.bind("<Leave>", lambda e, w=card: on_leave(e, w, CARD_COLOR, BORDER_COLOR))

    return card


def create_action_button(parent, text, command):
    button = tk.Label(
        parent,
        text=text,
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10, "bold"),
        padx=14,
        pady=9,
        cursor="hand2",
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=BORDER_COLOR
    )

    button.bind("<Button-1>", lambda event: command())
    button.bind("<Enter>", lambda e: on_enter(e, button, BUTTON_HOVER, ACCENT_BLUE))
    button.bind("<Leave>", lambda e: on_leave(e, button, BUTTON_COLOR, BORDER_COLOR))

    return button


def build_ui(root, games):
    root.configure(bg=BG_COLOR)

    # Header
    header = tk.Frame(root, bg=HEADER_COLOR, height=110)
    header.pack(fill="x")
    header.pack_propagate(False)

    title = tk.Label(
        header,
        text="Pokémon Hack Launcher",
        font=("Segoe UI", 22, "bold"),
        bg=HEADER_COLOR,
        fg=TEXT_COLOR
    )
    title.pack(pady=(18, 2))

    subtitle = tk.Label(
        header,
        text="Der Launcher für deine Hacks",
        font=("Segoe UI", 10),
        bg=HEADER_COLOR,
        fg=SUBTLE_TEXT
    )
    subtitle.pack()

    accent_line = tk.Frame(root, bg=ACCENT_COLOR, height=3)
    accent_line.pack(fill="x")

    # Content area
    content_wrapper = tk.Frame(root, bg=BG_COLOR)
    content_wrapper.pack(fill="both", expand=True, padx=18, pady=18)

    canvas = tk.Canvas(
        content_wrapper,
        bg=BG_COLOR,
        highlightthickness=0,
        bd=0
    )
    scrollbar = tk.Scrollbar(content_wrapper, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)

    scrollable_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if not games:
        empty_label = tk.Label(
            scrollable_frame,
            text="No hacks found.\nUse 'Edit hack list' to add entries.",
            font=("Segoe UI", 11),
            justify="center",
            bg=BG_COLOR,
            fg=SUBTLE_TEXT,
            pady=20
        )
        empty_label.pack()
    else:
        for entry in games:
            name = entry.get("name", "Unnamed Hack")
            path = entry.get("path", "")

            card = create_game_card(
                scrollable_frame,
                text=name,
                command=lambda game_path=path: launch_game(game_path)
            )
            card.pack(fill="x", pady=7)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Bottom bar
    bottom_bar = tk.Frame(root, bg=HEADER_COLOR, height=72)
    bottom_bar.pack(fill="x")
    bottom_bar.pack_propagate(False)

    # Create 4 equal columns
    bottom_bar.grid_columnconfigure(0, weight=1)
    bottom_bar.grid_columnconfigure(1, weight=1)
    bottom_bar.grid_columnconfigure(2, weight=1)
    bottom_bar.grid_columnconfigure(3, weight=1)

    edit_button = create_action_button(
        bottom_bar,
        "Liste bearbeiten",
        open_config
    )
    edit_button.grid(row=0, column=0, padx=10, pady=14)

    theme_button = create_action_button(
        bottom_bar,
        "Theme",
        lambda: open_theme_selector(root)
    )
    theme_button.grid(row=0, column=1, padx=10, pady=14)

    reload_button = create_action_button(
        bottom_bar,
        "Launcher neu laden",
        lambda: reload_launcher(root)
    )
    reload_button.grid(row=0, column=2, padx=10, pady=14)

    exit_button = create_action_button(
        bottom_bar,
        "Beenden",
        root.destroy
    )
    exit_button.grid(row=0, column=3, padx=10, pady=14)


def reload_launcher(root):
    global BG_COLOR
    global HEADER_COLOR
    global CARD_COLOR
    global CARD_HOVER
    global BUTTON_COLOR
    global BUTTON_HOVER
    global TEXT_COLOR
    global SUBTLE_TEXT
    global ACCENT_COLOR
    global ACCENT_BLUE
    global BORDER_COLOR

    settings = load_settings()
    theme_name = settings.get("theme", "modern")
    theme = THEMES.get(theme_name, THEMES["modern"])

    BG_COLOR = theme["bg"]
    HEADER_COLOR = theme["header"]
    CARD_COLOR = theme["card"]
    CARD_HOVER = theme["card_hover"]
    BUTTON_COLOR = theme["card"]
    BUTTON_HOVER = theme["card_hover"]
    TEXT_COLOR = theme["text"]
    SUBTLE_TEXT = theme["subtle_text"]
    ACCENT_COLOR = theme["accent"]
    ACCENT_BLUE = theme["accent"]
    BORDER_COLOR = theme["border"]

    for widget in root.winfo_children():
        widget.destroy()

    games = load_games()
    build_ui(root, games)


def main():
    global BG_COLOR
    global HEADER_COLOR
    global CARD_COLOR
    global CARD_HOVER
    global BUTTON_COLOR
    global BUTTON_HOVER
    global TEXT_COLOR
    global SUBTLE_TEXT
    global ACCENT_COLOR
    global ACCENT_BLUE
    global BORDER_COLOR

    root = tk.Tk()
    root.title("Pokémon Hack Launcher")
    root.iconbitmap("icon.ico")
    
    root.bind("<Escape>", lambda e: root.destroy())

    window_width = 640
    window_height = 680

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))

    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.minsize(520, 580)

    # Theme laden
    settings = load_settings()
    theme_name = settings.get("theme", "modern")
    theme = THEMES.get(theme_name, THEMES["modern"])

    BG_COLOR = theme["bg"]
    HEADER_COLOR = theme["header"]
    CARD_COLOR = theme["card"]
    CARD_HOVER = theme["card_hover"]
    BUTTON_COLOR = theme["card"]
    BUTTON_HOVER = theme["card_hover"]
    TEXT_COLOR = theme["text"]
    SUBTLE_TEXT = theme["subtle_text"]
    ACCENT_COLOR = theme["accent"]
    ACCENT_BLUE = theme["accent"]
    BORDER_COLOR = theme["border"]

    games = load_games()
    build_ui(root, games)

    root.mainloop()


if __name__ == "__main__":
    main()
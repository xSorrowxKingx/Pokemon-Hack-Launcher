# ui/game_manager.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from core.paths import ICON_FILE
from core.storage import load_games, save_games


def open_game_manager(root: tk.Tk, theme: dict, on_games_changed=None):
    """
    Open a game management window for adding, editing and deleting launcher entries.

    Features:
    - show all current games
    - add a new entry
    - edit existing entries
    - browse for an executable
    - save directly to games.json
    - optionally notify the launcher after changes
    """
    manager = tk.Toplevel(root)
    manager.title("Manage Games")
    manager.resizable(False, False)
    manager.configure(bg=theme["header"])

    try:
        manager.iconbitmap(ICON_FILE)
    except Exception:
        pass

    window_width = 820
    window_height = 560

    manager.update_idletasks()

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    pos_x = root_x + (root_width // 2) - (window_width // 2)
    pos_y = root_y + (root_height // 2) - (window_height // 2)

    manager.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
    manager.transient(root)
    manager.grab_set()

    games = load_games()
    selected_index = {"value": None}

    # -----------------------------
    # Helpers
    # -----------------------------
    def refresh_listbox():
        game_listbox.delete(0, tk.END)

        for entry in games:
            game_listbox.insert(tk.END, entry.get("name", "Unnamed Game"))

    def clear_form():
        selected_index["value"] = None
        name_var.set("")
        path_var.set("")
        description_text.delete("1.0", tk.END)
        game_listbox.selection_clear(0, tk.END)

    def load_selected_game(event=None):
        selection = game_listbox.curselection()

        if not selection:
            return

        index = selection[0]
        selected_index["value"] = index

        entry = games[index]

        name_var.set(entry.get("name", ""))
        path_var.set(entry.get("path", ""))

        description_text.delete("1.0", tk.END)
        description_text.insert("1.0", entry.get("description", ""))

    def browse_executable():
        file_path = filedialog.askopenfilename(
            parent=manager,
            title="Select Game Executable",
            filetypes=[
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        path_var.set(file_path)

        if not name_var.get().strip():
            suggested_name = os.path.splitext(os.path.basename(file_path))[0]
            name_var.set(suggested_name)

    def add_new_entry():
        clear_form()
        name_entry.focus_set()


    def normalize_game_path(path: str) -> str:
        """
        Normalize a game path so duplicate checks work reliably on Windows.

        This makes comparisons more robust by:
        - resolving relative path formatting
        - normalizing slashes
        - applying Windows case normalization
        """
        if not isinstance(path, str):
            return ""

        cleaned_path = path.strip()

        if not cleaned_path:
            return ""

        return os.path.normcase(os.path.normpath(cleaned_path))

    def save_current_entry():
        name = name_var.get().strip()
        path = path_var.get().strip()
        description = description_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showwarning("Missing Name", "Please enter a game name.", parent=manager)
            return

        if not path:
            messagebox.showwarning("Missing Path", "Please select a game executable.", parent=manager)
            return

        if not os.path.exists(path):
            messagebox.showwarning(
                "Invalid Path",
                "The selected executable does not exist.",
                parent=manager
            )
            return

        current_index = selected_index["value"]
        normalized_new_path = normalize_game_path(path)

        # Prevent duplicate executable paths, but allow saving the currently
        # selected entry itself when editing.
        for i, entry in enumerate(games):
            existing_path = normalize_game_path(entry.get("path", ""))

            if existing_path == normalized_new_path and i != current_index:
                messagebox.showwarning(
                    "Duplicate Entry",
                    "This executable already exists in the launcher.",
                    parent=manager
                )
                return

        new_entry = {
            "name": name,
            "path": os.path.normpath(path),
            "description": description
        }

        if current_index is None:
            games.append(new_entry)
            selected_index["value"] = len(games) - 1
        else:
            games[current_index] = new_entry

        if not save_games(games):
            messagebox.showerror(
                "Save Error",
                "Could not save games.json.",
                parent=manager
            )
            return

        refresh_listbox()

        if selected_index["value"] is not None:
            game_listbox.selection_clear(0, tk.END)
            game_listbox.selection_set(selected_index["value"])
            game_listbox.see(selected_index["value"])

        if callable(on_games_changed):
            on_games_changed()

        messagebox.showinfo("Saved", "Game entry saved successfully.", parent=manager)

    def delete_selected_entry():
        selection = game_listbox.curselection()

        if not selection:
            messagebox.showwarning("No Selection", "Please select a game entry to delete.", parent=manager)
            return

        index = selection[0]
        entry_name = games[index].get("name", "this game")

        confirm = messagebox.askyesno(
            "Delete Entry",
            f"Do you really want to delete '{entry_name}'?",
            parent=manager
        )

        if not confirm:
            return

        del games[index]

        if not save_games(games):
            messagebox.showerror("Save Error", "Could not save games.json.", parent=manager)
            return

        clear_form()
        refresh_listbox()

        if callable(on_games_changed):
            on_games_changed()

    # -----------------------------
    # Header
    # -----------------------------
    header_frame = tk.Frame(manager, bg=theme["header"], height=72)
    header_frame.pack(fill="x")

    title_label = tk.Label(
        header_frame,
        text="Manage Games",
        bg=theme["header"],
        fg=theme["text"],
        font=("Segoe UI", 15, "bold")
    )
    title_label.pack(anchor="w", padx=18, pady=(14, 0))

    subtitle_label = tk.Label(
        header_frame,
        text="Add, edit or remove games from your launcher library.",
        bg=theme["header"],
        fg=theme["subtle_text"],
        font=("Segoe UI", 9)
    )
    subtitle_label.pack(anchor="w", padx=18, pady=(2, 12))

    # -----------------------------
    # Main content
    # -----------------------------
    content_frame = tk.Frame(manager, bg=theme["bg"])
    content_frame.pack(fill="both", expand=True, padx=18, pady=18)

    left_panel = tk.Frame(
        content_frame,
        bg=theme["card"],
        highlightthickness=1,
        highlightbackground=theme["border"]
    )
    left_panel.pack(side="left", fill="y", padx=(0, 12))

    right_panel = tk.Frame(
        content_frame,
        bg=theme["card"],
        highlightthickness=1,
        highlightbackground=theme["border"]
    )
    right_panel.pack(side="right", fill="both", expand=True)

    # -----------------------------
    # Left panel: existing games
    # -----------------------------
    left_title = tk.Label(
        left_panel,
        text="Library Entries",
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 11, "bold")
    )
    left_title.pack(anchor="w", padx=14, pady=(14, 10))

    game_listbox = tk.Listbox(
        left_panel,
        width=28,
        height=20,
        bg=theme["bg"],
        fg=theme["text"],
        selectbackground=theme["accent"],
        selectforeground=theme["text"],
        relief="flat",
        bd=0,
        highlightthickness=0,
        font=("Segoe UI", 10)
    )
    game_listbox.pack(side="left", fill="y", padx=(14, 0), pady=(0, 14))

    list_scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=game_listbox.yview)
    list_scrollbar.pack(side="right", fill="y", padx=(0, 14), pady=(0, 14))
    game_listbox.config(yscrollcommand=list_scrollbar.set)

    game_listbox.bind("<<ListboxSelect>>", load_selected_game)

    # -----------------------------
    # Right panel: form
    # -----------------------------
    form_title = tk.Label(
        right_panel,
        text="Game Details",
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 11, "bold")
    )
    form_title.pack(anchor="w", padx=16, pady=(14, 12))

    name_var = tk.StringVar()
    path_var = tk.StringVar()

    name_label = tk.Label(
        right_panel,
        text="Game Name",
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 9, "bold")
    )
    name_label.pack(anchor="w", padx=16)

    name_entry = tk.Entry(
        right_panel,
        textvariable=name_var,
        bg=theme["bg"],
        fg=theme["text"],
        insertbackground=theme["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=theme["border"],
        font=("Segoe UI", 10)
    )
    name_entry.pack(fill="x", padx=16, pady=(4, 12))

    path_label = tk.Label(
        right_panel,
        text="Executable Path",
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 9, "bold")
    )
    path_label.pack(anchor="w", padx=16)

    path_row = tk.Frame(right_panel, bg=theme["card"])
    path_row.pack(fill="x", padx=16, pady=(4, 12))

    path_entry = tk.Entry(
        path_row,
        textvariable=path_var,
        bg=theme["bg"],
        fg=theme["text"],
        insertbackground=theme["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=theme["border"],
        font=("Segoe UI", 10)
    )
    path_entry.pack(side="left", fill="x", expand=True)

    browse_button = tk.Button(
        path_row,
        text="Browse",
        command=browse_executable,
        bg=theme["accent"],
        fg=theme["text"],
        activebackground=theme["card_hover"],
        activeforeground=theme["text"],
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    )
    browse_button.pack(side="left", padx=(10, 0))

    description_label = tk.Label(
        right_panel,
        text="Description (Optional)",
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 9, "bold")
    )
    description_label.pack(anchor="w", padx=16)

    description_text = tk.Text(
        right_panel,
        height=8,
        wrap="word",
        bg=theme["bg"],
        fg=theme["text"],
        insertbackground=theme["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=theme["border"],
        font=("Segoe UI", 10)
    )
    description_text.pack(fill="both", expand=True, padx=16, pady=(4, 14))

    action_row = tk.Frame(right_panel, bg=theme["card"])
    action_row.pack(fill="x", padx=16, pady=(0, 16))

    add_button = tk.Button(
        action_row,
        text="New Entry",
        command=add_new_entry,
        bg=theme["card"],
        fg=theme["text"],
        activebackground=theme["card_hover"],
        activeforeground=theme["text"],
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=theme["border"],
        padx=12,
        pady=7,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    )
    add_button.pack(side="left", padx=(0, 10))

    save_button = tk.Button(
        action_row,
        text="Save Entry",
        command=save_current_entry,
        bg=theme["accent"],
        fg=theme["text"],
        activebackground=theme["card_hover"],
        activeforeground=theme["text"],
        relief="flat",
        bd=0,
        padx=12,
        pady=7,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    )
    save_button.pack(side="left", padx=(0, 10))

    delete_button = tk.Button(
        action_row,
        text="Delete Entry",
        command=delete_selected_entry,
        bg=theme["card"],
        fg=theme["text"],
        activebackground=theme["card_hover"],
        activeforeground=theme["text"],
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=theme["border"],
        padx=12,
        pady=7,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    )
    delete_button.pack(side="left", padx=(0, 10))

    close_button = tk.Button(
        action_row,
        text="Close",
        command=manager.destroy,
        bg=theme["card"],
        fg=theme["text"],
        activebackground=theme["card_hover"],
        activeforeground=theme["text"],
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=theme["border"],
        padx=12,
        pady=7,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    )
    close_button.pack(side="right")

    refresh_listbox()
    name_entry.focus_set()

    manager.bind("<Return>", lambda event: save_current_entry())

    return manager
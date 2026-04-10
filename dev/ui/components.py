# ui/components.py

import os
import subprocess
import tkinter as tk
from tkinter import messagebox

from core.icon_manager import get_or_create_icon_image


def on_enter(widget: tk.Widget, hover_color: str):
    """
    Apply the hover color to a widget when the mouse enters it.
    """
    widget.configure(bg=hover_color)


def on_leave(widget: tk.Widget, normal_color: str):
    """
    Restore the normal background color when the mouse leaves a widget.
    """
    widget.configure(bg=normal_color)


def bind_hover_effect(widget: tk.Widget, normal_color: str, hover_color: str):
    """
    Attach a simple hover effect to a widget.

    This helper keeps hover logic reusable instead of repeating the same
    lambda bindings all over the launcher code.
    """
    widget.bind("<Enter>", lambda event: on_enter(widget, hover_color))
    widget.bind("<Leave>", lambda event: on_leave(widget, normal_color))


def launch_game(game_path: str):
    """
    Launch a game executable if the file exists.
    """
    if not isinstance(game_path, str) or not game_path.strip():
        messagebox.showerror("Error", "No valid game path was provided.")
        return

    if not os.path.exists(game_path):
        messagebox.showerror("Error", f"Game not found:\n{game_path}")
        return

    try:
        subprocess.Popen(game_path, cwd=os.path.dirname(game_path))
    except Exception as error:
        messagebox.showerror("Error", f"Could not launch game:\n{error}")


def create_action_button(
    parent: tk.Widget,
    text: str,
    command,
    theme: dict,
    width: int = 18,
    pady: int = 8
) -> tk.Button:
    """
    Create a reusable themed action button.
    """
    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        pady=pady,
        bg=theme["card"],
        fg=theme["text"],
        activebackground=theme["card_hover"],
        activeforeground=theme["text"],
        relief="flat",
        bd=1,
        highlightthickness=1,
        highlightbackground=theme["border"],
        highlightcolor=theme["accent"],
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    )

    bind_hover_effect(button, theme["card"], theme["card_hover"])
    return button


def create_game_card(
    parent: tk.Widget,
    game_name: str,
    game_path: str,
    theme: dict,
    description: str = "",
    launch_command=None
) -> tk.Frame:
    """
    Create a reusable themed game card.

    The card contains:
    - an optional extracted executable icon
    - a game title
    - an optional game description
    - a launch button
    """
    card = tk.Frame(
        parent,
        bg=theme["card"],
        bd=1,
        relief="solid",
        highlightthickness=1,
        highlightbackground=theme["border"]
    )

    top_row = tk.Frame(card, bg=theme["card"])
    top_row.pack(fill="x", padx=12, pady=(10, 6))

    # Fixed-size icon container in PIXELS, not text units.
    icon_container = tk.Frame(
        top_row,
        width=48,
        height=48,
        bg=theme["card"]
    )
    icon_container.pack(side="left", padx=(0, 12), anchor="n")
    icon_container.pack_propagate(False)

    icon_label = tk.Label(
        icon_container,
        bg=theme["card"],
        bd=0
    )
    icon_label.place(relx=0.5, rely=0.5, anchor="center")

    icon_image = get_or_create_icon_image(game_path, size=40)
    if icon_image is not None:
        icon_label.configure(image=icon_image)
        icon_label.image = icon_image
    else:
        icon_label.configure(
            text="🎮",
            fg=theme["subtle_text"],
            font=("Segoe UI Emoji", 18)
        )

    text_container = tk.Frame(top_row, bg=theme["card"])
    text_container.pack(side="left", fill="both", expand=True)

    title_label = tk.Label(
        text_container,
        text=game_name,
        bg=theme["card"],
        fg=theme["text"],
        font=("Segoe UI", 11, "bold"),
        anchor="w"
    )
    title_label.pack(fill="x", pady=(0, 4))

    display_description = description.strip() if isinstance(description, str) else ""
    is_fallback_description = not bool(display_description)

    if is_fallback_description:
        display_description = "No description set"

    description_label = tk.Label(
        text_container,
        text=display_description,
        bg=theme["card"],
        fg=theme["subtle_text"],
        font=("Segoe UI", 9, "italic") if is_fallback_description else ("Segoe UI", 9),
        anchor="w",
        justify="left",
        wraplength=460
    )
    description_label.pack(fill="x")

    effective_launch_command = launch_command or (lambda: launch_game(game_path))

    launch_button = tk.Button(
        card,
        text="Launch",
        command=effective_launch_command,
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
    launch_button.pack(anchor="e", padx=12, pady=(0, 12))

    bind_hover_effect(launch_button, theme["accent"], theme["card_hover"])

    def apply_card_hover():
        card.configure(bg=theme["card_hover"])
        top_row.configure(bg=theme["card_hover"])
        icon_container.configure(bg=theme["card_hover"])
        icon_label.configure(bg=theme["card_hover"])
        text_container.configure(bg=theme["card_hover"])
        title_label.configure(bg=theme["card_hover"])
        description_label.configure(bg=theme["card_hover"])

    def remove_card_hover():
        card.configure(bg=theme["card"])
        top_row.configure(bg=theme["card"])
        icon_container.configure(bg=theme["card"])
        icon_label.configure(bg=theme["card"])
        text_container.configure(bg=theme["card"])
        title_label.configure(bg=theme["card"])
        description_label.configure(bg=theme["card"])

    hover_widgets = (
        card,
        top_row,
        icon_container,
        icon_label,
        text_container,
        title_label,
        description_label,
    )

    for widget in hover_widgets:
        widget.bind("<Enter>", lambda event: apply_card_hover())
        widget.bind("<Leave>", lambda event: remove_card_hover())

    return card
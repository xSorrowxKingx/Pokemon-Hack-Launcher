<p align="center">
  <img src="assets/banner.png" alt="Pokémon Hack Launcher Banner">
</p>

<h1 align="center">Pokémon Hack Launcher</h1>

<p align="center">
  <a href="https://github.com/Barath0n/Pokemon-Hack-Launcher/releases/latest">
    <img src="https://img.shields.io/github/v/release/Barath0n/Pokemon-Hack-Launcher">
  </a>
  <img src="https://img.shields.io/github/downloads/Barath0n/Pokemon-Hack-Launcher/total">
  <img src="https://img.shields.io/github/license/Barath0n/Pokemon-Hack-Launcher">
  <img src="https://img.shields.io/badge/python-3.x-blue">
</p>

<p align="center">
A lightweight fan-made launcher for organizing and launching Pokémon ROM hacks and fangames distributed as standalone Windows executables.
</p>

<p align="center">
⬇ <b>Download the latest version</b><br>
<a href="https://github.com/Barath0n/Pokemon-Hack-Launcher/releases/latest">
https://github.com/Barath0n/Pokemon-Hack-Launcher/releases/latest
</a>
</p>

---

# Screenshots

### Main Launcher

![Launcher](assets/screenshots/main_launcher.png)

### Manage Games

![Game Manager](assets/screenshots/manage_games.png)

### Theme Selector

![Theme Selector](assets/screenshots/theme_selector.png)

---

# Features

- Launch Pokémon fan games and ROM hacks from one launcher
- Built-in **Game Manager** for adding and managing games
- **Live search** to quickly find games
- Automatic **executable icon detection**
- Clean and simple interface
- Lightweight and fast
- **Theme system** with multiple Pokémon-inspired themes
- Theme preview inside the launcher
- Description support for each game

---

# Installation

1. Download the latest version from the **Releases page**
2. Extract the ZIP archive
3. Run `PokemonHackLauncher.exe`

The launcher will automatically create the required configuration files on first start.

---

# Game Manager

Games can be added directly inside the launcher.

To add a game:

1. Open the launcher
2. Click **Manage Games**
3. Click **New Entry**
4. Select the game `.exe`
5. Save

The launcher automatically stores the entry in `games.json`.

No manual editing of configuration files is required.

---

# Search

The launcher includes a **live search bar**.

You can search by:

- Game title
- Game description

Results update instantly while typing.

---

# Icons

The launcher automatically attempts to extract icons from game `.exe` files.

If an executable does not provide an extractable icon, a fallback controller icon will be displayed.

---

# Themes

The launcher includes multiple themes that can be changed directly inside the application.

Examples include:

- FireRed
- LeafGreen
- Electric Yellow
- Lavender Town
- Team Rocket
- Infinite Fusion
- Radical Red
- and more

To change the theme:

1. Click **Theme**
2. Preview available themes
3. Select your preferred style

The launcher updates instantly without restarting.

---

# Project Structure


```
core/
ui/
launcher.py
games.json
themes.json
settings.json
```

The project separates **core logic** and **UI components** to keep the codebase easier to maintain and expand.

---

# Disclaimer

This project is a **fan-made tool** and is not affiliated with Nintendo, Game Freak, or The Pokémon Company.

All Pokémon names, assets, and trademarks belong to their respective owners.

---

# License

This project is released under the **MIT License**.

Please respect the original creators of the Pokémon fan games you add to the launcher.

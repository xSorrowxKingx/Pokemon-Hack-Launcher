# Pokémon Hack Launcher
**Current Version: v0.5.0**


A simple fan-made launcher for managing and starting Pokémon ROM hacks and fan games that are distributed as standalone `.exe` files.

Many Pokémon fan games and ROM hacks are released as individual Windows executables.  
This launcher provides a clean and convenient way to organize them in one place and launch them from a single interface.


## Screenshots

### Main Launcher

![Launcher](assets/screenshots/main_launcher.png)

### Manage Games

![Game Manager](assets/screenshots/manage_games.png)

### Theme Selector

![Theme Selector](assets/screenshots/theme_selector.png)


---

## Features

- Launch Pokémon fan games and ROM hacks from one launcher
- Built-in **Game Manager** for adding and managing games
- **Live search** to quickly find games
- Automatic **executable icon detection**
- Clean and simple interface
- Lightweight and fast
- Theme support with preview
- Description support for each game

---

## Game Manager

Games can now be added directly inside the launcher.

To add a game:

1. Open the launcher
2. Click **Manage Games**
3. Click **New Entry**
4. Select the game `.exe`
5. Save

The launcher will automatically store the entry in `games.json`.

No manual editing of configuration files is required.

---

## Search

The launcher includes a **live search bar**.

You can search by:

- Game title
- Game description

Results update instantly while typing.

---

## Icons

The launcher automatically attempts to extract icons from game `.exe` files.

If an executable does not provide an extractable icon, a fallback controller icon will be displayed.

---

## Themes

The launcher includes multiple themes that can be changed directly inside the application.

To change the theme:

1. Click **Theme**
2. Preview available themes
3. Select your preferred style

The launcher updates instantly without restarting.

---

## File Structure

core/
ui/
launcher.pyw
games.json
themes.json
settings.json


The project is organized into separate **core logic** and **UI components** to make the code easier to maintain and expand.

---

## Disclaimer

This project is a **fan-made tool** and is not affiliated with Nintendo, Game Freak, or The Pokémon Company.

All Pokémon names, assets, and trademarks belong to their respective owners.

---

## License

This project is released for educational and personal use.

Please respect the original creators of the Pokémon fan games you add to the launcher.

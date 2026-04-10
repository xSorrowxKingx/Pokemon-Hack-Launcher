# Pokémon Hack Launcher

A simple fan-made launcher for managing and starting Pokémon ROM hacks that are distributed as standalone `.exe` games.

Many Pokémon fan games and ROM hacks are released as individual Windows executables. This launcher provides a clean and convenient way to organize them in one place and launch them from a single interface.

## Features

- Launch Pokémon fan games and ROM hacks directly from one launcher
- Add and manage games easily
- Clean and simple interface
- Lightweight and fast
- Theme support

## Disclaimer

This project is a **fan-made tool** and is not affiliated with Nintendo, Game Freak, or The Pokémon Company.

All Pokémon names, assets, and trademarks belong to their respective owners.

## Configuration

The launcher uses a `games.json` file to know which games should be displayed.

For security and privacy reasons, the repository only includes a template file called:

`games.example.json`

To configure your games:

1. Copy `games.example.json`
2. Rename the copy to `games.json`
3. Edit the file and update the paths to match your local game installations

Example:

```json
{
  "name": "Pokemon Infinite Fusion",
  "path": "C:\\Games\\InfiniteFusion\\InfiniteFusion.exe",
  "description": "A fan game focused on fusing Pokémon into thousands of possible combinations."
}

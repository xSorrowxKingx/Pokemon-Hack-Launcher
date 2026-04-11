# Pokémon Hack Launcher Roadmap

This document outlines the development direction of the Pokémon Hack Launcher.

The project focuses on being a **lightweight desktop launcher for managing and launching Pokémon ROM hacks locally**.

The launcher **does not include ROMs or emulators** and will never distribute copyrighted game data.

---

# Current Status

The launcher is currently in **active development (pre-1.0)**.

Core functionality is already implemented:

- Game library management
- Search and filtering
- Favorites system
- Recently played tracking
- Theme system
- Language system
- Options menu
- Persistent settings

---

# Phase 1 — Core Launcher (towards v1.0)

Goal:  
A **stable, polished desktop launcher** for managing and launching Pokémon ROM hacks.

### Completed

- Game library system
- Add / edit / delete game entries
- Persistent storage via `games.json`
- Search system
- Favorites system
- Recently played tracking
- Last played timestamps
- Filter system (All / Favorites / Recently Played)
- Theme system
- Language system
- Options menu
- Game Manager UI
- Scrollable card UI
- Persistent launcher settings
- Basic UI/UX polish

### Planned before v1.0

- Sorting options (Name / Last Played / Recently Added)
- Minor UI polish
- Improved error handling
- Fallback handling for corrupted config files
- Packaging for Windows (.exe release)

---

# Phase 2 — Library Enhancements

Goal:  
Improve library organization and user experience.

Possible features:

- Custom tags
- Hack categories
- Notes per game
- Completed status
- Custom sorting options
- Import / export game library
- Additional UI polish
- Screenshot / cover preview support

These features are optional and will be implemented based on demand.

---

# Phase 3 — Advanced Features

Goal:  
Optional power features for advanced users.

Possible features:

- Emulator integration (user-defined emulator paths)
- Automatic ROM launching via emulator
- Metadata import from external sources
- Playtime tracking
- Screenshot galleries
- Community metadata integration

Important:

The launcher will **not host ROM files or patches**.

All game files remain fully controlled by the user.

---

# Long-Term Vision

The Pokémon Hack Launcher aims to remain:

- lightweight
- simple
- local-first
- legally safe

It is **not intended to replace community platforms** like Hackdex or PokéCommunity.

Instead, it complements them by providing a **local launcher experience for players**.

---

# Contributing

Suggestions and improvements are always welcome.

Feature requests can be discussed via GitHub issues.
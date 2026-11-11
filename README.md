# N7 Save Lab

**N7 Save Lab** is an unofficial, offline save-profile editor for the **LMP (Legendary Multiplayer)** mod for *Mass Effect Legendary Edition*.

The project started as a small experiment in reading multiplayer save files. It has since grown into an interactive, menu-driven editor backed by a reverse-engineered inventory catalog.

> **Status: early development.** The LMP profile reader/writer, credit editing, and low-level inventory editing are implemented. The inventory menus are still being built and should not be treated as a complete, tested editing interface.

## What it does

- **Load LMP profiles** (`MP_Profile`) using a Windows file picker.
- **Edit credits**, either by setting the balance or adding to it, without intentionally changing lifetime credits spent.
- **Read and modify inventory values** through the profile editor.
- **Browse a categorized inventory catalog** designed around units, weapons, weapon mods, equipment, and consumables. Individual submenus and editing workflows are in progress.
- **Track editing state and recent operations** in the interactive menu.
- **Protect save files** with backup creation and atomic file writes.

N7 Save Lab operates on **local files**. It is not a game client, multiplayer server, or online account editor.

## Run from source (Windows)

You'll need Python and the project source code. Development currently uses Python 3.10+.

From the repository root:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m n7savelab.menu
```

The interactive menu is the primary application entry point. The original command-based `cli.py` interface is being retired; older CLI examples are no longer the intended workflow.

**Before editing a save:** close the game, keep a separate backup of your profile, and test changes carefully. Do not commit real save profiles or personal backups to Git.

## Inventory catalog

The editor's inventory catalog is built from research into the LMP/Project Milan game configuration:

- **Card data** provides item metadata such as categories, rarity, limits, and localized-name references.
- **Player-variable mappings** connect internal item identifiers to inventory byte positions.
- **English talk tables (TLK)** supply human-readable item names.

These sources are processed by `generate_catalog.py` to produce `research/inventory_catalog.json`, which the menus use to organize and identify items.

For example, a character's inventory entry can be identified through its mapped `inventory_ids.base` value rather than guessed from an offset. Some inventory behaviors still need validation, particularly upgrade ranks, equipment variants, and unfinished menu paths.

The large extracted game assets used for research are development inputs, **not files that need to be distributed with the application**. Keep original extracted assets out of the public repository unless you have the right to distribute them.

## Project structure

The active code is organized around these responsibilities:

```text
src/n7savelab/
├── menu.py                 # Main interactive menu and application flow
├── inventory_menu.py       # Inventory category selection
├── inventory_submenus.py   # Category-specific selection/editing (in progress)
├── catalog.py              # Load and categorize inventory metadata
├── generate_catalog.py     # Build the inventory catalog from research data
├── editor.py               # Profile editing operations
└── formats/
    └── lmp.py              # LMP binary profile parser/serializer

research/
└── inventory_catalog.json  # Generated catalog used by the editor
```

Other legacy modules, format research, tests, and debugging scripts may still be present while the project is being reorganized.

### Development utilities

Profile comparison scripts, inventory experiments, and other reverse-engineering utilities are useful to keep, but they are **not part of the end-user menu**. The intended cleanup is to group developer-facing tools separately from application code and automated tests.

## Roadmap

- Finish and validate character-unlock selection.
- Complete the remaining inventory submenus for weapons, mods, equipment, and consumables.
- Add controlled quantity/rank editing where the underlying values have been validated.
- Refine menu navigation, status reporting, and editing history.
- Organize experimental/debug tools and update tests.
- Package the stable application for Windows.

A graphical interface, LEMP-to-LMP conversion, and broader profile editing are **not current priorities**.

## Disclaimer

This is an independent community project, not affiliated with BioWare, Electronic Arts, or the developers of LMP/Project Milan. Save-format findings are based on community reverse engineering, not an official specification. Use the editor at your own risk and respect the applicable game and mod rules.

import json
from pathlib import Path

from n7savelab.application import editor
from n7savelab.application.utils import select_from_menu, should_display_item
from .inventory_submenus import (
    units_menu,
    weapons_menu,
    mods_menu,
    equipment_menu,
    consumables_menu,
)


INVENTORY_CATEGORIES = [
    "Units",
    "Weapons",
    "Weapon Mods",
    "Equipment",
    "Consumables",
]


def categorize_items(catalog: dict) -> dict:
    categories = {
        "units": [],
        "weapons": [],
        "mods": [],
        "equipment": [],
        "consumables": []
    }

    for item in catalog.values():

        if not item.get("name") or not item.get("inventory_ids"):
            continue

        if item["kind"] == "unit":
            categories["units"].append(item)

        elif item["type"] == "weapon":
            categories["weapons"].append(item)

        elif item["type"] == "mod":
            categories["mods"].append(item)

        elif item["type"] == "equipment":
            categories["equipment"].append(item)

        elif item["type"] == "consumable":
            categories["consumables"].append(item)

    return categories


def load_catalog() -> dict:
    project_root = Path(__file__).resolve().parents[3]
    catalog_path = project_root / "research" / "inventory_catalog.json"

    with catalog_path.open("r", encoding="utf-8") as file:
        return json.load(file)["items"]


def inventory_menu(profile):
    changed = False
    catalog = load_catalog()
    inventory = editor.get_inventory(profile)
    categories = categorize_items(catalog)

    changed = False

    while True:
        keys = list(categories.keys())

        selected = select_from_menu(
            "Inventory Management",
            [key.capitalize() for key in keys]
        )

        if selected is None:
            return profile, changed

        category_key = keys[selected]
        selected_items = categories[category_key]

        match category_key:
            case "units":

                profile, modified = units_menu(profile, selected_items)

            case "weapons":
                profile, modified = weapons_menu(profile, selected_items)

            case "mods":
                profile, modified = mods_menu(profile, selected_items)

            case "equipment":
                profile, modified = equipment_menu(profile, selected_items)

            case "consumables":
                profile, modified = consumables_menu(profile, selected_items)
import json
from pathlib import Path

from n7savelab.application.utils import select_from_menu

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

        if not (item.get("display_name") or item.get("name")) or not item.get("inventory_ids"):
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


def inventory_menu(profile,status):
    catalog = load_catalog()
    categories = categorize_items(catalog)

    while True:
        keys = list(categories.keys())

        selected = select_from_menu(
            "Inventory Management",
            [key.capitalize() for key in keys]
        )

        if selected is None:
            return profile, status

        category_key = keys[selected]
        selected_items = categories[category_key]

        match category_key:
            case "units":

                profile, status = units_menu(profile, selected_items,status)

            case "weapons":
                profile, status = weapons_menu(profile, selected_items,status)

            case "mods":
                profile, status = mods_menu(profile, selected_items,status)

            case "equipment":
                profile, status = equipment_menu(profile, selected_items,status)

            case "consumables":
                profile, status = consumables_menu(profile, selected_items,status)
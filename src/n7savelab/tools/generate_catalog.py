import re
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from collections import defaultdict


CATEGORY_MAP = {
    "EReinforcementGUICategory_Kit": ("unit", None),

    "EReinforcementGUICategory_SMG": ("gear", "weapon"),
    "EReinforcementGUICategory_Pistol": ("gear", "weapon"),
    "EReinforcementGUICategory_AssaultRifle": ("gear", "weapon"),
    "EReinforcementGUICategory_Shotgun": ("gear", "weapon"),
    "EReinforcementGUICategory_SniperRifle": ("gear", "weapon"),

    "EReinforcementGUICategory_Mod": ("gear", "mod"),

    "EReinforcementGUICategory_MatchConsumableWeapon": ("gear", "consumable"),
    "EReinforcementGUICategory_MatchConsumableArmor": ("gear", "consumable"),
    "EReinforcementGUICategory_MatchConsumableAmmo": ("gear", "consumable"),

    "EReinforcementGUICategory_MatchConsumableGear": ("gear", "equipment"),
}

MOD_WEAPON_TYPES = {
    "assaultmod": "Assault Rifle",
    "pistolmod": "Pistol",
    "smgmod": "SMG",
    "shotgunmod": "Shotgun",
    "snipermod": "Sniper Rifle"
}

CLASSES = (
    "Adept",
    "Soldier",
    "Engineer",
    "Sentinel",
    "Infiltrator",
    "Vanguard",
)


DEFAULT_MAX_COUNTS = {
    "AdeptHumanMale": 5,
    "AdeptHumanFemale": 5,
    "SoldierHumanMale": 5,
    "SoldierHumanFemale": 5,
    "EngineerHumanMale": 5,
    "EngineerHumanFemale": 5,
    "SentinelHumanMale": 5,
    "SentinelHumanFemale": 5,
    "InfiltratorHumanMale": 5,
    "InfiltratorHumanFemale": 5,
    "VanguardHumanMale": 5,
    "VanguardHumanFemale": 5,
}


NAME_OVERRIDES = {

    "AdeptHumanMaleCerberus": "Phoenix Adept",
    "VanguardHumanMaleCerberus": "Phoenix Vanguard",
    "EngineerQuarian": "Quarian Engineer (Female)",
    "EngineerQuarianMale": "Quarian Engineer (Male)",
    "InfiltratorQuarian": "Quarian Infiltrator (Female)",
    "InfiltratorQuarianMale": "Quarian Infiltrator (Male)",


    "MPCapacity_Ammo": "Thermal Clip Pack Capacity +",
    "MPCapacity_Rocket": "Heavy Weapon Ammo Capacity +",

    "SFXGameMPContent.SFXPowerCustomActionMP_Consumable_Revive": "Medi-Gel",
    "SFXGameMPContent.SFXPowerCustomActionMP_Consumable_Shield": "Ops Survival Pack",
}

SPECIAL_GUI_TYPES = {
    "capacity": ("gear", "equipment"),
    "consumable": ("gear", "consumable"),
}

def clean_display_name(name: str | None) -> str | None:
    if not name:
        return None

    return re.sub(r"<CUSTOM\d+>", "", name).strip()

def get_unit_class(name: str) -> str | None:
    for class_name in CLASSES:
        if name.startswith(class_name):
            return class_name

        if name.startswith(f"N7{class_name}"):
            return class_name

    return None

def get_values(path: str, property_name: str):
    root = ET.parse(path).getroot()

    for prop in root.iter("Property"):
        if prop.get("name", "").lower() == property_name.lower():
            for value in prop.findall("Value"):
                if value.text:
                    yield value.text


def get_attribute(data: str, key: str):
    pattern = rf'\b{re.escape(key)}\s*=\s*("[^"]*"|[^,\s)]+)'

    match = re.search(pattern, data, re.IGNORECASE)

    return match.group(1).strip('"') if match else None


def load_tlk_strings(tlk_dir: Path) -> dict[int, str]:
    translations = {}
    conflicts = []

    for path in sorted(tlk_dir.glob("*.xml")):
        root = ET.parse(path).getroot()

        for entry in root.findall("String"):
            string_id = int(entry.attrib["id"])
            value = entry.text or ""

            if string_id in translations:
                if translations[string_id] != value:
                    conflicts.append((string_id, translations[string_id], value))
                continue

            translations[string_id] = value

    print(f"Loaded {len(translations)} TLK strings")
    print(f"Conflicting translations: {len(conflicts)}")

    return translations

def detect_duplicate_names(catalog):
    names = defaultdict(list)

    for unique_name, item in catalog.items():
        if item.get("kind") == "unit" and item.get("name"):
            names[item["name"]].append(unique_name)

    for name, identifiers in sorted(names.items()):
        if len(identifiers) > 1:
            print(f"{name}: {', '.join(identifiers)}")



def main():
    project_root = Path(__file__).resolve().parents[3]
    research_dir = project_root / "research"
    tlk_dir = research_dir / "tlk"
    translations = load_tlk_strings(tlk_dir)

    carddata_path = research_dir / "lmp_carddata.xml"
    mappings_path = research_dir / "lmp_player_variable_mapping.xml"
    output_path = research_dir / "inventory_catalog.json"

    # 1. Parse inventory mappings
    mappings = {}

    for value in get_values(mappings_path, "MPPlayerVariableMappings"):
        name = get_attribute(value, "ClassName")
        item_id = get_attribute(value, "ID")

        if name and item_id is not None:
            mappings[name.casefold()] = {
                "name": name,
                "id": int(item_id)
            }

    # 2. Parse store cards
    catalog = {}
    matched_ids = set()

    for value in get_values(carddata_path, "carddata"):
        name = get_attribute(value, "UniqueName")

        if not name:
            continue

        max_count = get_attribute(value, "MaxCount")
        rarity = get_attribute(value, "Rarity")
        category = get_attribute(value, "GUICategory")
        gui_type = get_attribute(value, "GUIType")
        gui_name_id = get_attribute(value, "GUIName")

        # Categorize item
        kind, item_type = CATEGORY_MAP.get(category, (None, None))

        # Determine weapon type for mods
        weapon_type = None

        if item_type == "mod" and gui_type:
            weapon_type = MOD_WEAPON_TYPES.get(gui_type.lower())

        # Fallback for character cards without GUICategory
        if kind is None and gui_type == "char":
            kind = "unit"

        # Determine character class
        unit_class = get_unit_class(name) if kind == "unit" else None

        # Exact match first
        match = mappings.get(name.casefold())

        # Some items have separate _0, _1, _2, _3 mappings
        variants = {}

        if match:
            variants["base"] = match["id"]
            matched_ids.add(match["id"])

        for suffix in range(4):
            variant = mappings.get(f"{name}_{suffix}".casefold())

            if variant:
                variants[str(suffix)] = variant["id"]
                matched_ids.add(variant["id"])

        raw_name = translations.get(int(gui_name_id)) if gui_name_id else None
        display_name = clean_display_name(raw_name)

        # Build catalog entry
        catalog[name] = {
            "name": display_name,
            "kind": kind,
            "type": item_type,
            "class": unit_class,
            "weapon_type": weapon_type,
            "gui_type": gui_type.lower() if gui_type else None,
            "category": category,
            "rarity": rarity,
            "max_count": int(max_count) if max_count else None,
            "gui_name_id": int(gui_name_id) if gui_name_id else None,
            "inventory_ids": variants
        }

        

    # 3. Preserve unmatched inventory mappings
    unmatched = [
        entry
        for entry in mappings.values()
        if entry["id"] not in matched_ids
    ]

    # Manual exception handling,
    for unique_name, item in catalog.items():

        if unique_name in NAME_OVERRIDES:
            item["display_name"] = NAME_OVERRIDES[unique_name]

        if item.get("max_count") is None:
            item["max_count"] = DEFAULT_MAX_COUNTS.get(unique_name)

        gui_type = item.get("gui_type")

        if gui_type in SPECIAL_GUI_TYPES:
            item["kind"], item["type"] = SPECIAL_GUI_TYPES[gui_type]





    # 4. Export
    result = {
        "items": catalog,
        "unmatched_mappings": unmatched
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    # 5. Report
    print(f"Inventory mappings: {len(mappings)}")
    print(f"Store cards: {len(catalog)}")
    print(f"Matched inventory IDs: {len(matched_ids)}")
    print(f"Unmatched mappings: {len(unmatched)}")
    print(f"\nExported to: {output_path}")







if __name__ == "__main__":
    main()
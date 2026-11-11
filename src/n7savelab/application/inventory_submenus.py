from n7savelab.application import editor
from n7savelab.application.utils import select_from_menu


###Submenus for the inventory editor.
###For now only allows the unlocking of items
###Consumables are another story idk what to do with em yet



#Submenu for units (DUH!)
#Prints out all the classes to select from
#if a class has no unlockable unit it returns to the preceding menu.
def units_menu(profile, units):
        classes = sorted({
        item["class"]
        for item in units
        if item.get("class")
    })
        inventory = editor.get_inventory(profile)
        selected = select_from_menu("Select Class", classes)

        if selected is None:
            return profile, False

        chosen_class = classes[selected]

        characters = [
            item for item in units
            if item["class"] == chosen_class
            and item.get("inventory_ids", {}).get("base") is not None
        ]

        if not characters:
            print("No locked characters in this class.")
            input("Press Enter to continue...")
            return profile, False


        selected_char = select_from_menu("Select a character to Unlock"
                                         ,[format_item(item, inventory) for item in characters]
        )

        if selected_char is None:
             return profile, False

        character = characters[selected_char]
        char_id = character["inventory_ids"]["base"]

        profile = editor.set_inventory_item(profile,char_id,1)
        return profile , True


#Submenu for weapons (DUH!)
#Prints out all the weapon types to select from
#if a class has no unlockable gun it returns to the preceding menu.

def weapons_menu(profile, weapons):
    types = sorted({
         item["gui_type"]
         for item in weapons
         if item.get("gui_type")
    })
    inventory = editor.get_inventory(profile)
    selected = select_from_menu("Select a weapon type", types)

    if selected is None:
         return profile, False

    chosen_type = types[selected]

    guns = [
         item for item in weapons
         if item["gui_type"] == chosen_type
         and item.get("inventory_ids", {}).get("base") is not None
    ]

    if not guns:
        print("No locked weapon in this type.")
        input("Press Enter to continue...")
        return profile, False

    selected_gun = select_from_menu("Select a weapon to Unlock",
                                    [item["name"] for item in guns])

    if selected_gun is None:
         return profile, False

    gun = guns[selected_gun]
    gun_id = gun["inventory_ids"]["base"]
    profile = editor.set_inventory_item(profile,gun_id,1)
    return profile

#Submenu for weapon mods(DUH!)
#Prints out all the weapon types to select from
#if a class has no unlockable mod left it returns to the preceding menu.

def mods_menu(profile, selected_items):
    ...

def equipment_menu(profile, selected_items):
    ...

def consumables_menu(profile, selected_items):
    ...

def format_item(item, inventory):
        item_id = item["inventory_ids"]["base"]
        current = inventory[item_id]
        max_count = item.get("max_count")
        name = item.get("display_name") or item["name"]
        if current == 0:
             status = "Locked"
        elif max_count is not None and current >= max_count:
             status = f"Max ({current}/{max_count})"
        elif max_count is not None:
             status = f"{current}/{max_count}"
        else:
             status = f"Owned ({current})"

        return f"{name} [{status}]"
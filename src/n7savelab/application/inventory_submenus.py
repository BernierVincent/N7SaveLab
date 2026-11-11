from n7savelab.application import editor
from n7savelab.application.utils import select_from_menu, select_number


###Submenus for the inventory editor.
###For now only allows the unlocking of items
###Consumables are another story idk what to do with em yet



#Submenu for units (DUH!)
#Prints out all the classes to select from
#if a class has no unlockable unit it returns to the preceding menu.


def units_menu(profile, units):
    return grouped_item_menu(
        profile,
        units,
        "Select a Character",
        modify_rank,
        group_key="class",
        group_prompt="Select a Class"
    )

#Submenu for weapons (DUH!)
#Prints out all the weapon types to select from
#if a class has no unlockable gun it returns to the preceding menu.


def weapons_menu(profile, weapons):
     return grouped_item_menu(profile,
                              weapons,
                              "Select a weapon",
                              modify_rank,
                              group_key="gui_type",
                              group_prompt="Select a weapon type"
                              )

#Submenu for weapon mods(DUH!)
#Prints out all the weapon types to select from
#if a class has no unlockable mod left it returns to the preceding menu.

def mods_menu(profile, mods):
    return grouped_item_menu(profile,
                             mods,
                             "Select a mod",
                             modify_rank,
                             group_key="weapon_type",
                             group_prompt="Select a weapon type"
                             )

def equipment_menu(profile, equipment):
    ...

def consumables_menu(profile, selected_items):
    ...

def format_item(item, inventory):
        item_id = get_base_inventory_id(item)
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

def grouped_item_menu(
    profile,
    items,
    item_prompt,
    action,
    group_key=None,
    group_prompt=None
):
    inventory = editor.get_inventory(profile)

    if group_key is not None:
        groups = sorted({
            item[group_key]
            for item in items
            if item.get(group_key)
        })

        selected = select_from_menu(group_prompt, groups)

        if selected is None:
            return profile, False

        chosen_group = groups[selected]

        members = [
            item for item in items
            if item.get(group_key) == chosen_group
        ]
    else:
        members = items

    members = sorted(
        members,
        key=lambda item: item.get("display_name") or item["name"]
    )

    selected_member = select_from_menu(
        item_prompt,
        [format_item(item, inventory) for item in members]
    )

    if selected_member is None:
        return profile, False

    return action(profile, members[selected_member])

def modify_rank(profile, item):
    max_count = item.get("max_count")
    item_id = get_base_inventory_id(item)
    name = item.get("display_name") or item["name"]

    if max_count is None:
        print("Maximum rank is unknown.")
        return profile, False

    ranks = [f"Rank {rank}" for rank in range(1, max_count + 1)]

    selected = select_from_menu(f"Select new rank for : {name}",ranks)

    if selected is None:
        return profile, False

    new_rank = selected + 1

    if editor.get_inventory(profile)[item_id] == new_rank:
        return profile, False

    profile = editor.set_inventory_item(profile,item_id,new_rank)
    return profile, True

def modify_quantity(profile,item):
     item_indices = item["inventory_ids"]

def get_base_inventory_id(item):
    ids = item.get("inventory_ids", {})
    return ids.get("base", ids.get("0"))

from n7savelab.application import editor
from n7savelab.application.profile_status import ProfileStatus
from n7savelab.application.utils import select_number, select_from_menu


###Submenus for the inventory editor.
###For now only allows the unlocking of items
###Consumables are another story idk what to do with em yet

TIERS = ["I", "II", "III", "IV"]

#Submenu for units (DUH!)
#Prints out all the classes to select from
#if a class has no unlockable unit it returns to the preceding menu.

def units_menu(profile, units, status, history):
    return grouped_item_menu(
                             profile,
                             units,
                             "class",
                             "Select a Class",
                             "Select a Character",
                             modify_rank,
                             status,
                             history
    )

#Submenu for weapons (DUH!)
#Prints out all the weapon types to select from
#if a class has no unlockable gun it returns to the preceding menu.


def weapons_menu(profile, weapons,status, history):
     return grouped_item_menu(
                              profile,
                              weapons,
                              "gui_type",
                              "Select a weapon type",
                              "Select a weapon",
                              modify_rank,
                              status,
                              history
                              )

#Submenu for weapon mods(DUH!)
#Prints out all the weapon types to select from
#if a class has no unlockable mod left it returns to the preceding menu.

def mods_menu(profile, mods, status, history):
    return grouped_item_menu(
                              profile,
                              mods,
                              "weapon_type",
                              "Select a weapon type",
                              "Select a mod",
                              modify_rank,
                              status,
                              history
                             )

def equipment_menu(profile, equipment, status, history):
    for item in equipment:
        name = item.get("display_name") or item["name"]
        first_letter = name[0].upper()

        if first_letter <= "F":
            group = "A-F"
        elif first_letter <= "L":
            group = "G-L"
        elif first_letter <= "R":
            group = "M-R"
        else:
            group = "S-Z"

        item["alphabetical_group"] = group

    return grouped_item_menu(
                             profile,
                             equipment,
                             "alphabetical_group",
                             "Select Equipment Group",
                             "Select Equipment",
                             modify_rank,
                             status,
                             history
                            )

def consumables_menu(profile, consumables, status, history):
    return grouped_item_menu(
                             profile,
                             consumables,
                             "gui_type",
                             "Select consumable type",
                             "Select consumable",
                             modify_consumable,
                             status,
                             history
                            )
    ...

def format_item(item, inventory,tier_key=None):
        name = item.get("display_name") or item["name"]
        item_type = item["type"]


        if item_type == "consumable" and len(item["inventory_ids"]) > 1:
            if tier_key is None:
                return name

            item_id = item["inventory_ids"][tier_key]
            quantity = inventory[item_id]
            return f"{name} {TIERS[int(tier_key)]} [{quantity}]"

        item_id = get_base_inventory_id(item)
        current = inventory[item_id]
        max_count = item.get("max_count")


        if current == 0 and item_type != "consumable":
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
    group_key,
    group_prompt,
    item_prompt,
    action,
    status,
    history

):
    inventory = editor.get_inventory(profile)

    groups = sorted({
            item[group_key]
            for item in items
            if item.get(group_key)
        })

    selected = select_from_menu(
                                group_prompt,
                                groups,
                                history=history,
                                status=status
                                )

    if selected is None:
        return profile, status

    chosen_group = groups[selected]

    members = [
        item for item in items
        if item.get(group_key) == chosen_group
    ]

    members = sorted(
        members,
        key=lambda item: item.get("display_name") or item["name"]
    )

    selected_member = select_from_menu(
        item_prompt,
        [format_item(item, inventory) for item in members],
        status=status,
        history=history
    )

    if selected_member is None:
        return profile, status

    return action(profile, members[selected_member], status, history)

def modify_rank(profile, item, status, history):
    max_count = item.get("max_count")
    item_id = get_base_inventory_id(item)
    name = item.get("display_name") or item["name"]

    if max_count is None:
        print("Maximum rank is unknown.")
        return profile, status

    ranks = [f"Rank {rank}" for rank in range(1, max_count + 1)]

    selected = select_from_menu(f"Select new rank for : {name}",ranks)

    if selected is None:
        return profile, status

    new_rank = selected + 1
    current_rank = editor.get_inventory(profile)[item_id]

    if current_rank == new_rank:
        return profile, status

    profile = editor.set_inventory_item(profile,item_id,new_rank)

    history.append(
        f"{name}: Rank {current_rank} → Rank {new_rank}"
    )

    return profile, ProfileStatus.MODIFIED_UNSAVED


def get_base_inventory_id(item):
    ids = item.get("inventory_ids", {})
    return ids.get("base", ids.get("0"))

def modify_consumable(profile, item, status, history):
    item_indices = item["inventory_ids"]
    inventory = editor.get_inventory(profile)
    if (len(item_indices) > 1):
        tier_keys = sorted(item_indices.keys(), key=int)
        tier_labels = [
            format_item(item, inventory, key)
            for key in tier_keys
        ]

        selected = select_from_menu(
                                    "Select Tier",
                                    tier_labels,
                                    history=history,
                                    status=status
                                    )
        
        if selected is None:
            return profile, status

        item_id = item_indices[tier_keys[selected]]
    else:
        item_id = get_base_inventory_id(item)

    amount = select_number("Enter an amount to add :")

    if (amount is None or amount == 0):
        return profile , status

    old_amount = inventory[item_id]

    profile = editor.add_inventory_item_quantity(profile,item_id,amount)

    new_amount = editor.get_inventory(profile)[item_id]


    name = item.get("display_name") or item["name"]

    if len(item_indices) > 1:
        name += f" {TIERS[int(tier_keys[selected])]}"

    history.append(f"{name}: {old_amount} → {new_amount} (+{amount})")

    return profile, ProfileStatus.MODIFIED_UNSAVED


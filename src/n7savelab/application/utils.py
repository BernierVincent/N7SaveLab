def select_number(msg) -> int:
    while True:
        value = input(f"{msg} (type 'cancel' to cancel): ").strip()

        if value.lower() == "cancel":
            return None

        try:
            return int(value)
        except ValueError:
            print("Inputted value must be a number")

def select_from_menu(title: str, options: list[str],history=None,status_text=None,back_label="Back") -> int | None:
    while True:
        print(f"\n=== {title} ===")

        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")

        print("0. Back")
        choice = input("\nSelection: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            index = int(choice) - 1

            if 0 <= index < len(options):
                return index

        print("Invalid selection.")


def should_display_item(item: dict, inventory: bytearray) -> bool:
    if not item.get("name") or not item.get("inventory_ids"):
        return False

    if item["type"] == "consumable":
        return True

    if item["kind"] == "unit" and item["max_count"] is None:
        return False

    ids = item["inventory_ids"]
    item_id = ids.get("base", ids.get("0"))

    if item_id is None:
        return False

    return inventory[item_id] == 0
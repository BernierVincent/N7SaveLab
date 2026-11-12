
import n7savelab.application.inventory_menu as inventory_menu
from n7savelab.application import editor
from n7savelab.tools.debug import *
from n7savelab.application.files import *
from n7savelab.application.utils import select_from_menu, select_number
from n7savelab.application.profile_status import ProfileStatus
from .inventory_menu import inventory_menu


MAIN_OPTIONS = [
    "Load Profile",
    "Set Credits",
    "Add Credits",
    "Inventory Management",
    "Save Profile",
]


def require_profile(profile):
    if profile is None:
        print("No profile loaded.")
        input("Press Enter to continue...")
        return False

    return True


def handle_load_profile(profile,filepath,status,history):
    selected_profile = select_profile()

    if selected_profile is None:
        print("No profile selected.")
        input("Press Enter to continue...")
        return profile,filepath ,status 

    try:
        new_filepath = Path(selected_profile)
        new_profile = load_document(new_filepath)
        backup_profile(new_filepath)

    except (OSError, ValueError, UnicodeError) as e:
        print(f"Failed to load profile: {e}")
        return profile, filepath, status

    history.append(f"Loaded profile: {new_filepath.name}")
    return new_profile, new_filepath, ProfileStatus.UNMODIFIED

def handle_set_credits(profile,history,status):

    if not require_profile(profile):
        return profile, status

    old_balance = profile.credits()

    new_balance = select_number("Enter new credit balance")

    if new_balance is None or new_balance == old_balance:
        return profile, status

    profile = editor.set_credits(profile, new_balance)

    history.append(
        f"Credits: {old_balance:,} → {new_balance:,}"
    )    
    return profile,ProfileStatus.MODIFIED_UNSAVED

def handle_add_credits(profile,history,status):

    if not require_profile(profile):
        return profile, status

    old_balance = profile.credits()

    added_amount = select_number("Enter an amount to add")

    if added_amount is None or added_amount == 0:
        return profile,status

    profile = editor.add_credits(profile,added_amount)

    new_balance = profile.credits()

    history.append(
        f"Credits: {old_balance:,} → {new_balance:,} (+{added_amount:,})"
    )

    return profile, ProfileStatus.MODIFIED_UNSAVED

def handle_inventory_management(profile,history,status):

    if not require_profile(profile):
        return profile, status

    return inventory_menu(profile,history,status)

def handle_saving(profile,filepath,history,status):

    if not require_profile(profile):
        return profile, status

    try:
        content = dump_document(profile)
        save_profile(filepath, content)

        status = ProfileStatus.MODIFIED_SAVED
        history.append("Profile saved successfully")

    except (OSError, ValueError) as e:
        history.append(f"Save failed: {e}")

    return profile,status

def handle_exit(status):
    if status != ProfileStatus.MODIFIED_UNSAVED:
        return True

    while True:
        choice = input(
            "\nYou have unsaved changes. Exit without saving? (Y/N): "
        ).strip().lower()

        if choice in ("y", "yes"):
            return True

        if choice in ("n", "no"):
            return False

        print("Invalid selection.")

def main_menu():
    history = []
    profile = None
    filepath = None
    status = ProfileStatus.UNLOADED
    while True:

        selected = select_from_menu(
            "N7 Save Lab",
            MAIN_OPTIONS,
            history=history,
            status=status,
            back_label="Exit",
            profile = profile
        )

        if selected is None:
            if handle_exit(status):
                break
            continue

        match selected:
            case 0:
                profile, filepath, status = handle_load_profile(
                    profile, filepath, status, history
                )
            case 1:
                profile, status = handle_set_credits(
                    profile,history,status
                )
            case 2:
                profile, status = handle_add_credits(
                    profile,history,status
                )
            case 3:
                profile, status = handle_inventory_management(
                    profile,history,status
                )
            case 4:
                profile,status = handle_saving(
                    profile,filepath,history,status
                )

if __name__ == "__main__":
    main()
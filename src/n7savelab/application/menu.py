import os

import n7savelab.application.inventory_menu as inventory_menu
from n7savelab.application import editor
from n7savelab.tools.debug import *
from n7savelab.application.files import *
from n7savelab.application.utils import *
from n7savelab.application.profile_status import ProfileStatus
from .inventory_menu import inventory_menu

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")



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

    if not require_profile(profile):
        return profile, status

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
    
    print(f"Current balance : {profile.credits()}")
    new_balance = select_number("Enter new credit balance")

    if new_balance is None:
        return profile,status
    
    profile = editor.set_credits(profile, new_balance)
    history.append(f"Credits set to {new_balance:,}")
    return profile,ProfileStatus.MODIFIED_UNSAVED

def handle_add_credits(profile,history,status):

    if not require_profile(profile):
        return profile, status
    
    print(f"Current balance : {profile.credits()}")
    added_amount = select_number("Enter an amount to add")

    if added_amount is None:
        return profile,status

    profile = editor.add_credits(profile,added_amount)
    history.append(f'Added {added_amount} credits to account balance')
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

    



def main():
    history = []
    profile = None
    filepath = None
    status = ProfileStatus.UNLOADED
    while True:
        status_text = f"Profile Status: {status.value}"

        selected = select_from_menu(
            "N7 Save Lab",
            MAIN_OPTIONS,
            history=history,
            status_text=status_text,
            back_label="Exit"
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
                profile, status = handle_set_credits(
                    profile,history,status
                )
            case 3:
                profile, status = handle_inventory_management(
                    profile,history,status
                )
            case 4:
                profile,status = handle_saving(
                    profile,history,status
                )



# def main():
#     running = True
#     profile = None
#     filepath = None
#     status = ProfileStatus.UNMODIFIED

#     history = []

#     while running:

#         clear_screen()

#         print("=== N7 Save Lab ===")

#         if filepath:
#             print(f"Profile: {filepath.name}")
#             print(f"Credit balance : {profile.credits()}")
#             print(f"Status : {status.value}")

#         print("\nRecent operations:")
#         for entry in history[-5:]:
#             print(f" > {entry}")


#         print("1. Load profile")
#         print("2. Set credits")
#         print("3. Add credits")
#         print("4. Inventory Management")
#         print("5. Save profile")
#         print("6. Exit")

#         choice = input("\nSelect an option: ")

#         match choice:
#             case "1":
#                 selected = select_profile()
#                 if selected:
#                     try:
#                         new_filepath = Path(selected)
#                         new_profile = load_document(new_filepath)

#                         backup_profile(new_filepath)

#                         filepath = new_filepath
#                         profile = new_profile


#                         status = ProfileStatus.UNMODIFIED
#                         history.clear()
#                         history.append("Loaded Profile")
#                     except (OSError, ValueError, UnicodeError) as e:
#                         print(f"Failed to load profile: {e}")
#                     else:
#                         print("No file selected")

#             case "2":
#                 if profile is None:
#                     print("Please load a profile first.")
#                     history.append("No profile loaded")
#                     continue
#                 print(f"Current balance : {profile.credits()}")
#                 amount = select_number("Enter new credit balance")
#                 if amount is None:
#                     history.append("Cancelled \"Set credit\" operation")
#                     continue

#                 profile = editor.set_credits(profile, amount)
#                 history.append(f"Credits set to {amount:,}")
#                 status = ProfileStatus.MODIFIED_UNSAVED
                
                
#             case "3":
#                 if profile is None:
#                     print("Please load a profile first.")
#                     history.append("No profile loaded")
#                     continue
#                 print(f"Current balance : {profile.credits()}")
#                 amount = select_number("Enter a credit amount to add")
#                 if amount is None:
#                     history.append("Cancelled \"Add credit\" operation")
#                     continue

#                 profile = editor.add_credits(profile, amount)
#                 history.append(f"Added {amount:,} credits")
#                 status = ProfileStatus.MODIFIED_UNSAVED

#             case "4":
#                 if profile is None:
#                     history.append("No profile loaded")
#                     continue

#                 profile, changed = inventory_menu(profile)

#                 if changed:
#                     status = ProfileStatus.MODIFIED_UNSAVED

#             case "5":
#                 if profile is None:
#                     history.append("No profile loaded")
#                     continue

#                 try:
#                     content = dump_document(profile)
#                     save_profile(filepath, content)

#                     status = ProfileStatus.MODIFIED_SAVED
#                     history.append("Profile saved successfully")

#                 except (OSError, ValueError) as e:
#                     history.append(f"Save failed: {e}")
#             case "6":
#                 if status == ProfileStatus.MODIFIED_UNSAVED:
#                     confirm = input("Unsaved changes! Quit anyway? (y/N): ").strip().lower()

#                     if confirm != "y":
#                         history.append("Exit cancelled")
#                         continue

#                 running = False
           
#             case _:
#                 print("Invalid option")

if __name__ == "__main__":
    main()
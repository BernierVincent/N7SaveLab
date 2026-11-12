from enum import Enum


class ProfileStatus(Enum):
    UNLOADED = "No profile loaded"
    UNMODIFIED = "Unmodified"
    MODIFIED_UNSAVED = "Modified (unsaved)"
    MODIFIED_SAVED = "Modified (saved)"
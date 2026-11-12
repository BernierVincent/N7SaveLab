"""YOUR implementation exercises.

Keep these operations in-memory and return a *copy* rather than modifying the
source profile. The CLI and a future UI should both call these functions.
"""
from __future__ import annotations
from copy import deepcopy
from n7savelab.application.files import Document
from n7savelab.application.formats.lmp import LmpProfile



def set_credits(profile: Document, amount: int) -> Document:
    """TODO M1: update only the current credits field, returning a new profile.
    
    LMP: property ID 0; base.split(';')[2] is the available balance.
    LEMP: later milestone; should retain original comments and line endings.
    """
    if (amount < 0):
        raise ValueError("Set amount must be non-negative")

    updated = deepcopy(profile)

    base = updated.record(0)
    
    fields = base.value.split(";")

    fields[2] = str(amount)

    base.value = ";".join(fields)

    return updated




def add_credits(profile: Document, amount: int) -> Document:
    """TODO M1: update only the current credits field, returning a new profile.
    
    LMP: property ID 0; base.split(';')[2] is the available balance.
    LEMP: later milestone; should retain original comments and line endings.
    """
    if (amount < 0):
        raise ValueError("Added amount must be non-negative")

    current = int(profile.record(0).value.split(";")[2])

    return set_credits(profile, current + amount)
    
    


def unlock_kit(profile: Document, kit_id: str) -> Document:
    """TODO M2: determine and change only proven character unlock fields.

    Requires before/after in-game unlock samples. Do not assume toggling a
    True/False string is sufficient: inventory variable(s) may also matter.
    """
    raise NotImplementedError("TODO M2: map and implement character kit unlocks")


def set_inventory_item(profile: Document,item_id: int, amount: int) -> Document:
    updated = deepcopy(profile)
    base_record = updated.record(0)
    fields = base_record.value.split(";")

    inventory_hex = fields[10]
    inventory = bytearray.fromhex(inventory_hex)

    inventory[item_id] = amount

    fields[10] = inventory.hex()
    base_record.value = ";".join(fields)
    return updated

def add_inventory_item_quantity(profile : Document,item_id :int,amount: int) -> Document:

    updated = deepcopy(profile)
    base_record = updated.record(0)
    fields = base_record.value.split(";")

    inventory_hex = fields[10]
    inventory = bytearray.fromhex(inventory_hex)

    inventory[item_id] += amount
    
    fields[10] = inventory.hex()
    base_record.value = ";".join(fields)
    return updated


def get_inventory(profile: LmpProfile) -> bytearray:
    fields = profile.record(0).value.split(";")
    return bytearray.fromhex(fields[10])

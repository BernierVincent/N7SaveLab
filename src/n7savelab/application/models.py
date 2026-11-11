"""Tiny data models. Extend only if actual editor requirements demand it."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ProfileRecord:
    owner: int
    setting_id: int
    type_code: int  # 1 = int32, 4 = string in observed profiles
    value: str | int
    flag: int = 0
    encoding: str = "unicode"  # unicode / ansi / empty (for strings)

@dataclass(frozen=True)
class KitInfo:
    internal_id: str
    display_name: str
    record_id: int

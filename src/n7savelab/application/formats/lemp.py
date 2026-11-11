"""LEMP text format — read-only starter implementation.

Editing a LEMP file is a TODO: Idk if I'll ever mess around with editing files
for LEMP as it is sunsetted/abandonware.
"""
from __future__ import annotations
from dataclasses import dataclass
from n7savelab.application.models import KitInfo

@dataclass
class LempProfile:
    raw_text: str
    lines: list[str]

    def matching(self, name: str) -> list[str]:
        return [line.split("=", 1)[1] for line in self.lines
                if line.startswith(name + "=")]

    def base_fields(self) -> list[str]:
        bases = self.matching("base")
        if len(bases) != 1:
            raise ValueError("Expected exactly one base record")
        fields = bases[0].split(";")
        if len(fields) != 11:
            raise ValueError("Unexpected base format")
        return fields

    def credits(self) -> int:
        return int(self.base_fields()[2])

    def kits(self) -> list[KitInfo]:
        kits = []
        for index, line in enumerate(self.lines):
            if not line.startswith("character="):
                continue
            fields = line.split("=", 1)[1].split(";")
            if len(fields) >= 4:
                kits.append(KitInfo(fields[2], fields[3], index + 1))
        return kits


def read_lemp(data: bytes) -> LempProfile:
    text = data.decode("utf-8-sig")
    lines = text.splitlines()
    if "version=1" not in lines or not any(line.startswith("base=") for line in lines):
        raise ValueError("Not a recognized LEMP save")
    return LempProfile(text, lines)

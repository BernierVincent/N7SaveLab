"""LMP MP_Profile parser/serializer.

This is a *foundation*, not an unlock editor. Byte-for-byte round-trips
have been checked against the two provided example profiles, but no format
specification guarantees all future mod versions use the same layout.
"""
from __future__ import annotations
import struct
from dataclasses import dataclass
from n7savelab.application.models import KitInfo, ProfileRecord

MAX_RECORDS = 10000
MAX_STRING_BYTES = 16 * 1024 * 1024

@dataclass
class LmpProfile:
    records: list[ProfileRecord]

    def record(self, sid: int) -> ProfileRecord:
        matches = [r for r in self.records if r.setting_id == sid]
        if len(matches) != 1:
            raise ValueError(f"Expected one property ID {sid}, found {len(matches)}")
        return matches[0]

    def base_fields(self) -> list[str]:
        base = self.record(0).value
        if not isinstance(base, str):
            raise ValueError("Base property is not a string")
        fields = base.split(";")
        if len(fields) != 11:
            raise ValueError(f"Unexpected base layout: {len(fields)} fields")
        return fields

    def credits(self) -> int:
        return int(self.base_fields()[2])

    def kits(self) -> list[KitInfo]:
        result = []
        for r in self.records:
            if not (9 <= r.setting_id <= 86) or not isinstance(r.value, str):
                continue
            fields = r.value.split(";")
            if len(fields) >= 4:
                result.append(KitInfo(fields[2], fields[3], r.setting_id))
        return result


def read_lmp(data: bytes) -> LmpProfile:
    if len(data) < 4:
        raise ValueError("LMP file is too short")
    count, = struct.unpack_from(">i", data, 0)
    if not (0 <= count <= MAX_RECORDS):
        raise ValueError("Implausible record count")
    records: list[ProfileRecord] = []
    p = 4
    for idx in range(count):
        if p + 6 > len(data):
            raise ValueError(f"Truncated record header at index {idx}")
        owner, sid, typ = struct.unpack_from(">BiB", data, p)
        p += 6
        if typ == 1:
            if p + 4 > len(data):
                raise ValueError(f"Truncated integer at ID {sid}")
            value, = struct.unpack_from(">i", data, p)
            p += 4
            encoding = "empty"
        elif typ == 4:
            if p + 4 > len(data):
                raise ValueError(f"Truncated string length at ID {sid}")
            length, = struct.unpack_from(">i", data, p)
            p += 4
            size = -2 * length if length < 0 else length
            if size > MAX_STRING_BYTES or p + size > len(data):
                raise ValueError(f"Invalid or truncated string at ID {sid}")
            if length == 0:
                value, encoding = "", "empty"
            elif length < 0:
                blob = data[p:p+size]
                if not blob.endswith(b"\0\0"):
                    raise ValueError(f"Missing string terminator at ID {sid}")
                value, encoding = blob[:-2].decode("utf-16-le"), "unicode"
            else:
                blob = data[p:p+size]
                if not blob.endswith(b"\0"):
                    raise ValueError(f"Missing ANSI terminator at ID {sid}")
                value, encoding = blob[:-1].decode("latin-1"), "ansi"
            p += size
        else:
            raise ValueError(f"Unknown type {typ} for ID {sid}")
        if p >= len(data):
            raise ValueError(f"Missing final flag at ID {sid}")
        flag = data[p]
        p += 1
        records.append(ProfileRecord(owner, sid, typ, value, flag, encoding))
    if p != len(data):
        raise ValueError("Unexpected trailing bytes")
    if len({r.setting_id for r in records}) != len(records):
        raise ValueError("Duplicate setting IDs")
    return LmpProfile(records)


def write_lmp(profile: LmpProfile) -> bytes:
    out = bytearray(struct.pack(">i", len(profile.records)))
    for r in profile.records:
        out += struct.pack(">BiB", r.owner, r.setting_id, r.type_code)
        if r.type_code == 1:
            if not isinstance(r.value, int):
                raise ValueError("Integer property contains a non-integer value")
            out += struct.pack(">i", r.value)
        elif r.type_code == 4:
            if not isinstance(r.value, str):
                raise ValueError("String property contains a non-string value")
            if r.encoding == "empty" and r.value == "":
                out += struct.pack(">i", 0)
            elif r.encoding == "ansi":
                data = r.value.encode("latin-1") + b"\0"
                out += struct.pack(">i", len(data)) + data
            elif r.encoding in ("unicode", "empty"):
                data = (r.value + "\0").encode("utf-16-le")
                out += struct.pack(">i", -(len(data) // 2)) + data
            else:
                raise ValueError(f"Unsupported text encoding {r.encoding}")
        else:
            raise ValueError(f"Cannot write unknown type {r.type_code}")
        out.append(r.flag)
    return bytes(out)

from pathlib import Path
from datetime import datetime
from itertools import zip_longest
from n7savelab.application.formats.lmp import LmpProfile, write_lmp
from n7savelab.application.files import load_document
from copy import deepcopy

###

def export_comparison(report: str) -> Path:
    output_dir = Path("./comparisons")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = output_dir / f"comparison_{timestamp}.txt"
    output_path.write_text(report, encoding="utf-8")

    return output_path


def compare_profiles(before: LmpProfile, after: LmpProfile) -> str:
    report = ["=== N7 Save Lab — Profile Comparison ===", ""]

    old_records = {r.setting_id: r for r in before.records}
    new_records = {r.setting_id: r for r in after.records}

    changed = 0

    for sid in sorted(old_records.keys() | new_records.keys()):
        old = old_records.get(sid)
        new = new_records.get(sid)

        if old == new:
            continue

        changed += 1
        report.append(f"\n=== Property ID {sid} ===")

        if old is None or new is None:
            report.append("Property added" if old is None else "Property removed")
            continue

        for attr in ("owner", "type_code", "flag", "encoding"):
            a, b = getattr(old, attr), getattr(new, attr)
            if a != b:
                report.append(f"  {attr}: {a!r} -> {b!r}")

        if old.value == new.value:
            continue

        # Base record: statistics + hexadecimal inventory
        if sid == 0:
            old_fields = old.value.split(";")
            new_fields = new.value.split(";")

            for i, (a, b) in enumerate(zip_longest(
                old_fields, new_fields, fillvalue="<missing>"
            )):
                if a == b:
                    continue

                if i == 10:
                    old_inv = bytes.fromhex(a)
                    new_inv = bytes.fromhex(b)

                    report.append(
                        f"  Inventory size: {len(old_inv)} -> {len(new_inv)}"
                    )

                    for index, (x, y) in enumerate(zip_longest(
                        old_inv, new_inv, fillvalue=None
                    )):
                        if x != y:
                            report.append(f"  Inventory [{index}]: {x} -> {y}")
                else:
                    label = {2: "Credits", 5: "Lifetime spent"}.get(
                        i, f"Base field [{i}]"
                    )
                    report.append(f"  {label}: {a} -> {b}")

        else:
            # Split known record structures into individual fields.
            if 1 <= sid <= 88:
                separator = ";"
            elif isinstance(old.value, str) and "," in old.value:
                separator = ","
            else:
                separator = None

            if separator and isinstance(old.value, str) and isinstance(new.value, str):
                a_fields = old.value.split(separator)
                b_fields = new.value.split(separator)

                if 9 <= sid <= 86 and len(a_fields) >= 4:
                    report.append(f"  Kit: {a_fields[2]} ({a_fields[3]})")

                for i, (a, b) in enumerate(zip_longest(
                    a_fields, b_fields, fillvalue="<missing>"
                )):
                    if a != b:
                        report.append(f"  Field [{i}]: {a!r} -> {b!r}")
            else:
                report.append(f"  Value: {old.value!r} -> {new.value!r}")

    report.insert(2, f"Changed properties: {changed}")

    return "\n".join(report)







def generate_inventory_tests(
    profile: LmpProfile,
    output_dir: Path = Path("./debug_profiles")
) -> Path:

    # Index: (expected original value, new value)
    candidates = {
        32: (0, 1),
        88: (0, 5),
        256: (1, 2),
        418: (0, 1),
        510: (0, 1),
    }

    inventory = bytes.fromhex(profile.base_fields()[10])

    # Verify we're using the expected BEFORE-purchase profile.
    for index, (old, new) in candidates.items():
        if inventory[index] != old:
            raise ValueError(
                f"Index {index}: expected {old}, got {inventory[index]}"
            )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    batch_dir = output_dir / f"huntress_{timestamp}"
    batch_dir.mkdir(parents=True, exist_ok=False)

    for index, (old, new) in candidates.items():
        modified = deepcopy(profile)

        fields = modified.base_fields()
        data = bytearray.fromhex(fields[10])

        data[index] = new

        fields[10] = data.hex()
        modified.record(0).value = ";".join(fields)

        test_dir = batch_dir / f"index_{index}"
        test_dir.mkdir()

        # Each file has the exact filename expected by LMP.
        (test_dir / "MP_Profile").write_bytes(write_lmp(modified))

        (test_dir / "change.txt").write_text(
            f"Inventory index {index}: {old} -> {new}",
            encoding="utf-8"
        )

    return batch_dir




def main():
    profile_path = Path("./backup/MP_Profile-PrePurchase")

    if not profile_path.is_file():
        raise FileNotFoundError(f"Profile not found: {profile_path}")

    profile = load_document(profile_path)

    if not isinstance(profile, LmpProfile):
        raise TypeError("Expected an LMP profile")

    output = generate_inventory_tests(profile)

    print(f"Generated test profiles in: {output.resolve()}")


if __name__ == "__main__":
    main()


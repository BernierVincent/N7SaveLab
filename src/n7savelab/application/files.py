"""Local save format detection and safe new-file writes."""
from __future__ import annotations
import os
from pathlib import Path
import sys
import tempfile
from typing import TypeAlias
from n7savelab.application.formats.lmp import LmpProfile, read_lmp
from n7savelab.application.formats.lemp import LempProfile, read_lemp
from tkinter import Tk, filedialog
from pathlib import Path
from datetime import datetime
from n7savelab.application.formats.lmp import LmpProfile, write_lmp
from n7savelab.application.formats.lemp import LempProfile
import shutil

Document: TypeAlias = LmpProfile | LempProfile


def load_document(path: Path) -> Document:
    raw = path.read_bytes()
    if raw.startswith(b"# LEMP") or path.suffix.lower() == ".txt":
        return read_lemp(raw)
    return read_lmp(raw)

#CLI method for unit testing
def save_new_file(input_path: Path, output_path: Path, content: bytes) -> None:
    source = input_path.resolve()
    output = output_path.resolve()
    if source == output:
        raise ValueError("Refusing to overwrite the input save; choose another output path")
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids overwriting a file created between checks.
    with output.open("xb") as fp:
        fp.write(content)


from pathlib import Path

def save_profile(filepath: Path, content: bytes) -> None:
    """Atomically overwrite an existing profile."""

    filepath = filepath.resolve()
    temp_path = None

    if not filepath.is_file():
        raise FileNotFoundError(f"Profile does not exist: {filepath}")

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=filepath.parent,
            prefix=f".{filepath.name}_",
            suffix=".tmp",
            delete=False
        ) as temp:
            temp_path = Path(temp.name)
            temp.write(content)
            temp.flush()
            os.fsync(temp.fileno())

        os.replace(temp_path, filepath)

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

def select_profile():
    root = Tk()
    root.withdraw()  # Hide the empty Tkinter window

    filepath = filedialog.askopenfilename(
        title="Select Mass Effect Multiplayer Profile",
        filetypes=[
            ("Mass Effect save files", "MP_Profile* LEMP_mpsave.txt"),
            ("All files", "*.*")
        ]
    )

    root.destroy()
    return filepath


def backup_profile(filepath: Path) -> Path:
    backup_dir = None
    if getattr(sys, "frozen", False):
        backup_dir = Path(sys.executable).resolve().parent / "backup"
    else:
        backup_dir = Path.cwd() / "backup"

    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    backup_path = backup_dir / f"{filepath.name}_{timestamp}.bak"

    shutil.copy2(filepath, backup_path)

    return backup_path



def dump_document(profile: Document) -> bytes:
    if isinstance(profile, LmpProfile):
        return write_lmp(profile)

    if isinstance(profile, LempProfile):
        raise NotImplementedError("LEMP editing not implemented yet")

    raise TypeError("Unsupported profile format")
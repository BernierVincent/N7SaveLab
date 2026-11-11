# Reverse-engineering notes (preliminary)

Based on inspected LEMP and LMP samples. **Not an authoritative, version-stable schema.**

## LMP — `MP_Profile`

A compact Unreal Engine profile-settings representation:

```text
int32be record_count
for each record:
    uint8 owner
    int32be setting_id
    uint8 type_code
    value               # int32be if type_code=1; Unreal string if type_code=4
    uint8 flag
```

For string records, a signed big-endian length follows: negative means a UTF-16LE string length (in two-byte code units) including the final `NUL`; zero means empty; positive lengths may indicate a legacy 1-byte string. Preserve the encoding and record order when writing back.

Observed setting IDs:

| ID | Purpose |
|---|---|
| `0` | Base statistics + packed inventory variables |
| `1..6` | Class progression records |
| `9..86` | Character kits (not necessarily every ID populated) |
| `87..88` | Face codes / reinforcements |
| `89..95` | Challenges and related progress |

**LMP `base` record:** semicolon-separated fields; `base[2]` is current credits, `base[5]` tracks lifetime credits spent, and `base[10]` is a hex-encoded player-variable/inventory blob (one byte per slot in the inspected format). On the inspected new-profile version there were 807 slots, versus 671 in the older LEMP text profile. **Do not overwrite/truncate the blob while editing credits.**

**Character kits:** records contain internal IDs such as `VanguardKrogan`. LMP records in the sample split into 23 fields; LEMP records split into 22. Fields near the end include boolean-like values, but their precise ownership semantics remain unverified. Ownership may also be encoded in the `base` inventory variable blob. Confirm with a before/after diff after an unlock before writing an editor.

## LEMP — `LEMP_mpsave.txt`

UTF-8 (in our sample) line-oriented `key=value` format. Sections include `version=1`, `base`, `class`, `character`, `reinforcements`, `facecodes`, `selected`, `challenge`, and `gaw`. Many keys repeat. The **original order and comments** should be preserved when implementing writes.

The `base` key uses the same structural credit location (`split(';')[2]`) in the sample, but this is **not proof** that all inventory/kit IDs are interchangeable.

## Recommended test technique for kit unlocks

1. Start from a backed-up, disposable save.
2. Record an LMP save **before** unlocking one character kit.
3. Unlock that kit normally in the game, then exit cleanly.
4. Save the resulting **after** profile to a different file.
5. Diff every record, including the hex blob's individual byte offsets.
6. Only implement offsets whose meaning you've verified; document mod/build versions.

Avoid storing/share-uploading real profiles in a public test repository. Generate minimal synthetic fixtures instead.

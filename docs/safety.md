# Save safety checklist

- Work **offline** and close the game before writing saves.
- Never silently overwrite a real save. The starter's write helper only writes a **new** path.
- Keep an independent copy outside the game folder before experimentation.
- Parse and serialize an unedited LMP profile byte-for-byte before attempting modifications.
- Validate the whole output after writing; never truncate unknown or extra inventory slots.
- Test with a new copy and reload the game before treating a change as correct.
- Do not include personal savedata, account identifiers, or actual game files in a public release.
- Never trust a save input's length or record count blindly; reject malformed files.
- Local save edits don't imply permissions to change server-controlled progression; check the mod's rules.

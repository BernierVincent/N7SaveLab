# Minimal architecture (intentionally boring)

```text
CLI (argparse) -> load_document(path)
                      |
                  LMP / LEMP parser
                      |
                  editor operations (TODO)
                      |
            validate, preview, serialize
                      |
              safe_write_new_file(output)
```

The core editing functions should be pure / in-memory whenever possible:

```python
updated = set_credits(document, 100000)
# updated is a copy; original is unchanged
```

This makes CLI, tests, and a future Tkinter frontend reuse the same logic.

Keep format-specific offsets in one place. Don't scatter unexplained numeric indices across CLI/GUI code. The CLI shouldn't know how a property is encoded.

**Decision for MVP:** Do not build an LEMP<->LMP converter. Read both formats first; implement editing independently by format after tests.

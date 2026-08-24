# ABS Engine Errors

This document describes ABS Engine's error module (`engine.core.errors`).

## Overview

`engine.core.errors` is not only for fatal, unrecoverable errors. It also will
define precise, engine-specific exception types for situations that
could otherwise be mistaken for an ordinary, expected error (e.g. a
generic `ValueError` or `KeyError`) but that the user of the engine
should actually be catching and handling deliberately. Naming these
distinctly makes it clear they are ABS-specific conditions the caller is
expected to know about and handle, rather than incidental Python errors.

The module defines `ABSFatalError`, for the more extreme
case: conditions where continuing to run would leave the engine in a
corrupted or undefined state, and the only safe response is to stop
immediately.

## `ABSFatalError`

`ABSFatalError` is not a normal exception. Constructing it:

1. Logs the given message.
2. Writes a traceback.
3. Calls `os.abort()`.

Control never returns to the caller. The process terminates during
`__init__`. There is no `try`/`except` that can catch this and continue
running.

### Constructor

```python
def __init__(self, message: str) -> Never: ...
```

### Usage

```python
from engine.core.errors import ABSFatalError

if renderer_context_lost:
    ABSFatalError("Lost graphics context, cannot continue")
```

Do **not** wrap this in a `try`/`except` expecting to recover. It's
designed specifically so that isn't possible. Any state that needs to be
saved (progress, config, in-memory data) must be persisted *before* this is
constructed, since nothing after it executes.

### When to use it

Use `ABSFatalError` only for conditions where the engine's internal state
can no longer be trusted, for example:

- Renderer or graphics context loss
- Fatal asset or save-data corruption
- Violated invariants in core engine systems

Do not use it for ordinary, recoverable errors (bad input, missing files
that can be re-requested, invalid but non-corrupting game state, etc.).
Use a regular exception for those.

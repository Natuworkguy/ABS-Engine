# Debugging Games

## Viewing logs

To see game logs (either printed by ABS Engine or the user),
launch ABS Engine with the [console visible](accessing_the_console.md).
Upon launching a game, ABS Engine prints out some messages.
This action always happens, so it is a good way to test if you can see the log.

## Logging from Game Scripts

Games should use ABS Engine's built-in logger instead of `print()`.
This keeps game messages formatted the same way as engine messages and
includes the script module that emitted the log.

```python
from engine import logger
from engine.core import Entity


def init(entity: Entity) -> None:
    logger.info("Player script initialized")
    ...
    logger.warning("Save file was not found")
```

Use `logger.info()` for normal messages, `logger.warning()` for problems that the
game can recover from, and `logger.critical()` for errors that should be handled
immediately.

Logs triggered by scripts will show as from a name that starts with `esf-` (Entity Script File) followed by a UUID:

```text
14:02:33 INFO     esf-0b7c6f0e-5d1a-4c3e-9f2b-7a8d4e6c1b23: Log content
```

## Understanding Engine Logs

Let's break down this log message:

```text
14:02:31 INFO     engine.core: Initialized game
```

Here are the main parts of the message:

```text
14:02:31 INFO     engine.core: Initialized game
   |      |           |             |
   |      |           |             |_______
   |      |           |______       |Message|
   |      |____       |Source|
   |____  |Type|
   |Time|
```

**Time**: When the message was logged (local time, `HH:MM:SS`)
**Type**: The severity of the message (can be "INFO", "WARNING", or "CRITICAL")
**Source**: Shows which module the message originated from. In this example, the message came from `engine/core/__init__.py`.
**Message**: The message being printed

When the console supports colors, the type is shown in cyan (INFO), yellow (WARNING), or red (CRITICAL), and the time and source are dimmed.

Example of a critical error message:

```text
14:02:32 CRITICAL engine.gui: Could not load icon image.
   |        |         |             |
   |        |         |             |_______
   |        |         |______       |Message|
   |        |____     |Source|
   |____    |Type|
   |Time|
```

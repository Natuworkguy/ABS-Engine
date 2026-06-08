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
from engine.core import Entity
from engine.logger import Status, logger


def init(entity: Entity) -> None:
    logger("Player script initialized")
    ...
    logger("Save file was not found", status=Status.WARNING)
```

Use `Status.INFO` for normal messages, `Status.WARNING` for problems that the
game can recover from, and `Status.CRITICAL` for errors that should be handled
immediately.

## Understanding Engine Logs

Let's break down this log message:

```text
(INFO) ENGINE.CORE: Initialized game
```

Here are the main parts of the message:

```text
(INFO) ENGINE.CORE: Initialized game
   |          |            |
   |          |______      |_______
   |          |Source|     |Message|
   |____
   |Type|
```

**Type**: The severity of the message (can be "INFO", "WARNING", or "CRITICAL")
**Source**: Shows which module the message originated from. In this example, the message came from `engine/core.py`.
**Message**: The message being printed

Example of a critical error message:

```text
(CRITICAL) ENGINE.GUI: Initialized game
   |              |           |
   |              |______     |_______
   |              |Source|    |Message|
   |____
   |Type|
```

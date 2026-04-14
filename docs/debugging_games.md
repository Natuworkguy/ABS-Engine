# Debugging Games

## Viewing logs

To see game logs (either printed by ABS Engine or the user),
launch ABS Engine with the [console visible](accessing_the_console.md).
Upon launching a game, ABS Engine prints out some messages.
This action always happens, so it is a good way to test if you can see the log.

## Understanding Engine Logs

Let's break down this log message:

```text
(Status.INFO) ENGINE.CORE: Initialized game
```

Here are the main parts of the message:

```text
(Status.INFO) ENGINE.CORE: Initialized game
   |          |            |
   |          |______      |_______
   |          |Source|     |Message|
   |____
   |Type|
```


**Type**: The severity of the message
**Source**: Shows which module the message originated from. In this example, the message came from `engine/core.py`.
**Message**: The message being printed

Example of a critical error message:

```text
(Status.CRITICAL) ENGINE.GUI: Initialized game
   |              |           |
   |              |______     |_______
   |              |Source|    |Message|
   |____
   |Type|
```

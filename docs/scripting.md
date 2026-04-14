# Scripting

ABS Engine has Python scripting built in.
With scripting, you can move and manipulate objects, create animations, and much more.
In other words, scripting allows you to make entities in your game _do things_.
Here's how to get started:

To create a script file, first follow the
[recommended file structure](game_file_structure.md).
The `assets/` folder is not needed for this tutorial.
Then, launch ABS Engine and follow these steps:

1. Create a name for your game and click "Save name"
2. Create a new entity (name it "Player")
3. Select the entity in the list
4. Click "Edit Data"
5. Enter the following:

   ```json
   {"scriptfile": "scripts/player.py"}
   ```

   >[!Tip]
   > Name your scripts after the entity they're attached to.
   > This makes it easy to identify them later.

6. Click "Save", then "Save Project"
7. Verify that `game.absp` was saved in your project folder

In `scripts/player.py`, add the following.

```python
def init(entity):
    pass
    
def update(entity, dt):
    entity.x += 1
    entity.update_rect()
```

>[!Tip]
> Because the engine requires a script to
> be attached to an entity in your game,
> put everything in the game that is not
> entity-specific (e.g. playing background
> music, etc.) in the script attached to
> the player entity (The entity that the
> player controls). This is called a main
> script. If your game does not have a player
> entity, place a new entity off screen that
> has the main script attached to it.

Let's break down what this code does.
In a script file, three functions are commonly defined:

```python
init(entity: Entity) -> None
update(entity: Entity, dt: float) -> None
event(entity: Entity, event: pygame.event.Event) -> None
```

`init()`   - Called once when the game starts
`update()` - Called every frame (multiple times per second)
`event()`  - Called when a pygame event is triggered

## Entity Properties

The `entity` parameter refers to the entity object itself.
In this code, we add one to the entity's `x` value (`entity.x += 1`),
and then update its visual position (`entity.update_rect()`).

The `engine.core.Entity` class has the following properties:
`parent`      - Parent scene object                - `engine.core.Scene`
`x`           - X position in pixels               - `float`
`y`           - Y position in pixels               - `float`
`width`       - Width in pixels                    - `float`
`height`      - Height in pixels                   - `float`
`color`       - RGB color value                    - `tuple[int, int, int]`
`rect`        - Pygame rect object on screen       - `pygame.Rect`
`scriptfile`  - Path to the attached script        - `str`
`id`          - Unique entity UUID                 - `str`
`get_colliding_entities`                           - `Callable[[], list[Entity]]`

> [!Note]
> Entity.parent can only be called in update()

## Script Functions

The `init()`, `update()`, and `event()` functions are callback functions that ABS Engine calls at specific times:

- `init(entity: Entity) -> None` - Called when the game starts
- `update(entity: Entity, dt: float) -> None` - Called every frame
- `event(entity: Entity, event: pygame.event.Event) -> None` - Called when an input event occurs

Here's an example script that creates a simple game with player movement.
The game uses a top-down perspective with a player-controlled square
that can move with W/A/S/D keys. The player cannot move outside the visible game area.

```python
import pygame

ENTITY_SIZE = (50, 50)

step_size = 5
held = {
    'w': False,
    'a': False,
    's': False,
    'd': False
}

def init(entity):
    entity.width = ENTITY_SIZE[0]
    entity.height = ENTITY_SIZE[1]
    entity.update_rect()

def update(entity, dt):
    if held['w'] and not entity.y == 0:
        entity.y -= step_size
    elif held['a'] and not entity.x == 0:
        entity.x -= step_size
    elif held['s'] and not entity.y == entity.parent.parent.wsize[1] - ENTITY_SIZE[0]:
        entity.y += step_size
    elif held['d'] and not entity.x == entity.parent.parent.wsize[0] - ENTITY_SIZE[1]:
        entity.x += step_size
    entity.update_rect()

def event(entity, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            held['w'] = True
        elif event.key == pygame.K_a:
            held['a'] = True
        elif event.key == pygame.K_s:
            held['s'] = True
        elif event.key == pygame.K_d:
            held['d'] = True
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_w:
            held['w'] = False
        elif event.key == pygame.K_a:
            held['a'] = False
        elif event.key == pygame.K_s:
            held['s'] = False
        elif event.key == pygame.K_d:
            held['d'] = False
```

>[!NOTE]
> The `pygame.draw.rect()` function that renders the entity on screen automatically uses the entity's color.
> Since it runs every tick, you do _not_ need to call `entity.update_rect()` when only changing the entity's color.

Go back to ABS Engine and click "Run".
You should see a white square moving continuously from left to right.

>[!IMPORTANT]
> If the game window freezes or shows a black screen at startup,
> check that your script file has no syntax errors. It is completely normal for a game to crash if there are code errors.
> See [Debugging Games](debugging_games.md) for help diagnosing issues.

# Scripting

ABS Engine has Python scripting built in.
Using this feture, it is possible to,
move and manipulate objects, make animations,
and more. English translation: scripting allows
you to make entities in your game _do things_,
Here's how to do it:

To make a script file, first follow the
[best game file structure](game_file_structure.md).
The assets/ folder is not needed for this demo.
Launch ABS Engine.

Make a name for your game, then click "Save name".
Make a new entity (use "Player" as the name).
Once the entity has been created, click it on the list.
Click "Edit Data".
Type:
```json
{"scriptfile": 'scripts/player.py'}
```

>[!Tip]
> Make sure to name your script after the 
> entity it is attached to. This ensures
> that you can identify it easily.

Click "Save", then "Save Project".
Make sure game.py is saved in your project folder.

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

Let's unpack what this does.
In a scriptfile, 2 functions are expected:
```
init(entity: Entity) -> None
update(entity: Entity, dt: float)
```

`init` is called once the game starts.
`update` is called every game tick.

The entity parameter is the entity class itself.
In this code, we add one to th entity's `x` value ("entity.x += 1"),
then tell it to visually update it's position ("entity.update_rect()").

The engine.core.Entity class has the following values:
`parent`      - Parent game                - engine.core.Scene
`x`           - X position.                - float
`y`           - Y position.                - float
`width`       - Width of entity.           - float
`height`      - Height of entity.          - float
`color`       - RGB color of entity.       - tuple[int, int, int],
`rect`        - Rect object on screen      - pygame.Rect
`scriptfile`  - Path to script             - str

Event functions are the functions that ABS Engine
triggers when something happens.
These are the functions that it uses:
`init`        - Called on game start        - Callable[[engine.core.Entity], None]
`update`      - Called on every tick        - Callable[[engine.core.Entity, float], None]
`event`       - Called on registered event  - Callable[[engine.core.Entity, pygame.event.Event], None]

This is an example script to make a simple game with these features.
The game is from a top-down perspective. It has a cube that can be
controlled with the W/A/S/D keys. The game does not the player move
out of the space that the player can see.

```python
import pygame

step_size = 5
held = {
    'w': False,
    'a': False,
    's': False,
    'd': False
}

def init(entity):
    pass

def update(entity, dt):
    if held['w'] and not entity.y == 0:
        entity.y -= step_size
    elif held['a'] and not entity.x == 0:
        entity.x -= step_size
    elif held['s'] and not entity.y == 550:
        entity.y += step_size
    elif held['d'] and not entity.x == 750:
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
> pygame.rect.draw (The function that draws the entity on screen) takes the
> of the entity's color as a prameter, and it runs every tick.
> This means that you _don't_ have to use entity.update_rect()
> when you update an entity's color.

Go back to ABS Engine, then click "Run".
You should see a white cube moving from the left to the right
side of the screen.

>[!IMPORTANT]
> If the game window freezes, or is completely black at start,
> check that the script file has no errors. it is completely
> normal for a game to crash if the code has errors.
> [Debug the game](debugging_games.md) to easily see the error.

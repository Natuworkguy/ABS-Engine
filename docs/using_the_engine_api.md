# Using the Engine API Directly

Most of this documentation assumes you're building a game through the ABS
Engine editor (`run.pyw`), with a `game.absp` [project file](game_file_structure.md)
and [script files](scripting.md) attached to entities. You don't have to use
the editor, though. `engine.core` is a normal Python package, and you
can create a `Game`, its `Scene`s, and `Entity` objects yourself in a plain
Python script.

This is useful for prototypes, procedurally generated games, or tooling built
on top of ABS Engine, where driving everything from code is more convenient
than maintaining a project file.

## A Minimal Game

```python
from engine.core import Entity, Game


game = Game("My Game", GP_BASE_PATH=".")

player = Entity(x=100, y=100, color=(255, 0, 0))
game.add_to_current_scene(player)

game.run()
```

This opens a window titled "My Game" with a single red square in it, and
runs the main game loop until the window is closed. No project file,
editor, or `data/` folder structure is required.

## Creating the Game

`Game` is the entry point, it owns the window, the game loop, and the
list of scenes.

```python
game = Game(
    "My Game",
    width=800,
    height=600,
    GP_BASE_PATH=".",
)
```

`GP_BASE_PATH` is required and keyword-only. It defines the base path ABS Engine
uses to resolve relative asset references (such as `icon_path` or an entity's
`image`), so it should point to your game's asset directory.
Avoid using `.` for `GP_BASE_PATH` in production games. Instead, use a path
such as `str(Path(__file__).parent)` or another explicit directory that
contains your game assets.

>[!NOTE]
> `IS_EDITOR` defaults to `False`, which is correct for a script-driven game.
> It's set to `True` by the ABS Engine editor when previewing a game, so
> scripts can check `entity.parent.game.IS_EDITOR` if they need to behave
> differently under the editor's preview.

## Adding Entities

Every `Game` starts with one empty scene at index `0`.
Create entities directly and add them to it:

```python
from engine.core import Entity


enemy = Entity(x=300, y=150, width=32, height=32, color=(0, 200, 0))
game.add_to_current_scene(enemy)
```

`Entity`'s constructor arguments match the
[entity properties](game_file_structure.md#entity-data-structure) used in
project files (`x`, `y`, `width`, `height`, `color`, `image`, `scriptfile`),
just passed as Python keyword arguments instead of JSON.

## Attaching Script Logic

Entities created in code can use either script mechanism:

- `scriptfile="scripts/enemy.py"` - load a [script file](scripting.md),
  same as in a project file.
- [`ObjectScriptEntity`](ose.md) - define the script as a Python class
  in the same file as the rest of your code, instead of a separate script
  file.

```python
from engine.core import Entity
from engine.core.ose import ObjectScriptEntity
from engine.core.types import EntityScript


class EnemyScript(Entity, EntityScript):
    def update(self, dt: float) -> None:
        self.x += 1


enemy = ObjectScriptEntity(scriptobj=EnemyScript, x=300, y=150)
game.add_to_current_scene(enemy)
```

## Rendering Text

Use [`Text`](text.md) instead of a plain `Entity` to render a string
instead of a colored rectangle:

```python
from engine.core.text import Text


score_label = Text(x=10, y=10, text="Score: 0", color=(255, 255, 255))
game.add_to_current_scene(score_label)
```

See [Text](text.md) for the full list of constructor arguments, including
`dynamic`, which controls whether the text surface is rebuilt every frame.

## Scenes

Use `game.add_scene()` and `game.switch_scene(scene_index)` to work with
multiple scenes, the same way you would from inside a script. See
[Scenes and Scene Switching](scenes.md) for details on `scenedata`,
`gamedata`, and moving entities between scenes.

```python
menu_scene = game.current_scene
level_scene = game.add_scene()

game.switch_scene(level_scene)
```

## Running the Game

`game.run(fps=60)` starts the main loop (handling events, updating the
current scene, and drawing every frame) and blocks until the window is
closed or `game.quit()` is called.

If you need more control, for example, embedding ABS Engine inside
another application's loop, or writing tests, call `game.step(dt)`
yourself instead of `game.run()`. Each call to `step()` processes one frame:
handling pending events, updating the current scene, and drawing it.

```python
import pygame


game.running = True
clock = pygame.time.Clock()

while game.running:
    dt = clock.tick(60) / 1000.0
    game.step(dt)
```

## Packaging

[Using Build Tools](using_build_tools.md) describes packaging a game built
with the editor's generated `run.py`. If you wrote your own entry-point
script instead, package that file directly with Pyinstaller the same way,
pointing `--add-data` at whatever asset folders your script actually uses.

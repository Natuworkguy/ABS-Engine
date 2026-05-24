# Scenes and Scene Switching

Scenes are containers for the entities that make up a part of a game.
ABS Engine creates one default scene when a `Game` is created, and that
default scene is stored at scene index `0`.

Scenes are managed by `engine.core.Game`, and each scene is represented by
`engine.core.Scene`.

## Scene Basics

Every `Game` has:

- `game.scenes`: A list of all scenes in the game.
- `game.current_scene`: The index of the scene currently being shown.
- `game.add_scene()`: A method that creates a new scene and returns its index.
- `game.switch_scene(scene_index)`: A method that changes the active scene.

Only the current scene is updated, sent events, and drawn during the normal
game loop. This means entities in inactive scenes stay in memory, but they do
not run their normal frame update unless `game.updateall()` is called.

```python
def init(entity) -> None:
    menu_scene_index: int = entity.parent.game.current_scene
    level_scene_index: int = entity.parent.game.add_scene()

    entity.parent.game.switch_scene(level_scene_index)
```

## Switching Scenes

Use `game.switch_scene(scene_index)` to change which scene is active.
The scene index must exist in `game.scenes`.

```python
def init(entity) -> None:
    level_scene_index: int = entity.parent.game.add_scene()

    entity.parent.game.switch_scene(level_scene_index)
```

If the scene index is out of range, ABS Engine raises `IndexError`.
Calling `switch_scene()` with the current scene index does nothing.

## Moving Entities Between Scenes

Use `game.move_entity_to_scene(entity, target_scene_index)` to move an entity
from its current scene to another scene.

```python
def init(entity) -> None:
    second_scene_index: int = entity.parent.game.add_scene()

    entity.parent.game.move_entity_to_scene(entity, second_scene_index)
```

When an entity is moved:

- ABS Engine checks that the target scene exists.
- The entity is removed from its current parent scene, if it has one.
- The entity is added to the target scene.
- The entity's script `init()` function is not called again if it already ran.

If the entity is already in the target scene, nothing changes.
If the target scene index is out of range, ABS Engine raises `IndexError`.

## Removing and Destroying Entities

Use `scene.remove(entity)` to remove an entity from a scene.
Use `entity.destroy()` when an entity should remove itself from its current
parent scene.

```python
def init(entity) -> None:
    entity.destroy()  # Entity will no longer be drawn, updated, or sent events
```

`entity.destroy()` only works when the entity has a parent scene.

## Scene Data

Each scene has a `scenedata` dictionary for custom scene-level state.
The game also has a `gamedata` dictionary for state that should be shared
across scenes.

```python
def init(entity) -> None:
    entity.parent.scenedata["spawn_count"] = 3
    entity.parent.game.gamedata["score"] = 0
```

Use `scenedata` for information that belongs to one scene, such as spawn
counts or level state. Use `gamedata` for information that should survive
scene switches, such as score, inventory, settings, or unlocked levels.

## Background Color

Scenes can set the game's background color with `scene.set_bg_color(color)`.
The color uses `RGBType`, which is documented in
[ABS Engine Types](types.md).

```python
from engine.core.types import RGBType


def init(entity) -> None:
    sky_blue: RGBType = (80, 160, 255)

    entity.parent.set_bg_color(sky_blue)
```

## Collision Checks and Scenes

`entity.get_colliding_entities()` checks collisions only against entities in
the entity's current parent scene. Entities in other scenes are not included.

This keeps scene switching predictable: moving an entity to another scene also
changes which entities it can collide with.

## Updating Inactive Scenes

The normal game loop updates only the current scene. If a game needs inactive
scenes to keep running, call `game.updateall(dt)`.

```python
def update(entity, dt: float) -> None:
    entity.parent.game.updateall(dt, exclude=entity.parent)  # Exclude the current scene to avoid an infinite loop
```

Use this carefully. Updating every scene can be useful for simulations or
background systems, but it also means entities in inactive scenes will keep
running their update scripts.

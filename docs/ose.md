# Object Script Entities (OSE)

Object Script Entities let you attach script logic to an entity using a
Python class instead of a [script file](scripting.md). This is useful when
you are creating entities in code (rather than through the editor/project
file) and want the script logic defined alongside the entity, in the same
place.

`ObjectScriptEntity` is available from `engine.core.ose`:

```python
from engine.core import Entity, Game
from engine.core.ose import ObjectScriptEntity
from engine.core.types import EntityScript


class TestScript(Entity, EntityScript):
    def init(self):
        print("TestScript initialized.")

    def update(self, dt: float):
        self.x += 1

    def event(self, event):
        print(f"TestScript received event: {event}")


entity = ObjectScriptEntity(scriptobj=TestScript)

game = Game(GP_BASE_PATH=".")
game.add_to_current_scene(entity)
game.run()
```

## How It Works

`ObjectScriptEntity` accepts every argument that
[`Entity`](scripting.md#entity-properties) does (`x`, `y`, `width`, `height`,
`color`, `image`, etc.), plus one required keyword-only argument:

- `scriptobj`: A class (not an instance) that defines `init`, `update`,
  and/or `event` methods.

Instead of loading a script file, ABS Engine calls the methods on `scriptobj`
directly, passing the entity in as the first argument, conventionally
named `self` since the class inherits from `Entity`. This is why
`self.x`, `self.update_rect()`, and other `Entity` properties are available
inside your OSE class's methods: `self` *is* the entity.

## Script Methods

See [Script Functions](scripting.md#script-functions).

---

> [!NOTE]
> `ObjectScriptEntity(...)` returns a plain `Entity`, not an instance of
> `ObjectScriptEntity`. Don't rely on `isinstance(entity, ObjectScriptEntity)`
> to detect entities created this way.

## When to Use OSEs vs. Script Files

Use a [script file](scripting.md) when building a game through the ABS
Engine's editor, since `scriptfile` is set as project data.

Use an Object Script Entity when creating entities directly in Python code
(for example, procedurally generated entities, or tooling built on top of
ABS Engine) where keeping the script and entity definition together is more
convenient than maintaining a separate script file.

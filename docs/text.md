# Text

`Text` is an [`Entity`](scripting.md#entity-properties) that renders a
string using a pygame font instead of drawing a solid rectangle. Use it for
UI labels, HUD elements, dialogue, or any other on-screen text.

`Text` is available from `engine.core.text`:

```python
from engine.core import Game
from engine.core.text import Text


game = Game(GP_BASE_PATH=".")

label = Text(x=100, y=100, text="Hello, world!", color=(255, 255, 255))
game.add_to_current_scene(label)

game.run()
```

## Constructor Arguments

| Argument | Description | Type | Default |
| --- | --- | --- | --- |
| `x` | X position in pixels | `int` | `0` |
| `y` | Y position in pixels | `int` | `0` |
| `text` | The string to render | `str` | `""` |
| `size` | Font size in points | `int` | `50` |
| `font` | Path to a font file, or `None` for pygame's default font. If the file is missing, `Text` falls back to pygame's system-font lookup with the same name. | `Optional[str]` | `None` |
| `color` | RGB color of the text | `tuple[int, int, int]` | `(255, 255, 255)` |
| `bgcolor` | RGB background color behind the text | `tuple[int, int, int]` | `(0, 0, 0)` |
| `antialias` | Whether to antialias the rendered glyphs | `bool` | `True` |
| `dynamic` | Whether to rebuild the text surface every frame | `bool` | `True` |

## How It Works

Internally, `Text` first tries `pygame.font.Font(font, size)` and falls back
to `pygame.font.SysFont(font, size)` when the font file cannot be found. It
then calls `render(...)` to rasterize `text` into a surface and overrides
`draw()` to `blit()` that surface instead of drawing a colored rectangle like
a plain `Entity` does. Font rendering and blitting both happen on the CPU
(pygame's classic `Surface`/`blit()` API is software-rendered), so larger
text, longer strings, and more frequent re-rendering all cost CPU time.

`width` and `height` (and therefore `rect`, used for collisions) are
derived from the rendered surface at creation time, so they always match
the actual size of `text` at the given `size`.

### The `dynamic` Flag

Because `text_rect`'s position is only set at render time, an entity's
`text_surface`/`text_rect` need to be rebuilt whenever `x`, `y`, `text`,
`color`, `bgcolor`, or `antialias` change for the change to show up on
screen.

- `dynamic=True` (default): `draw()` rebuilds the text surface every frame,
  so moving the entity, or changing its text or colors, always renders
  correctly. This costs a `font.render()` call every frame.
- `dynamic=False`: the text surface is only built once, in the
  constructor. Use this for text that never moves and never changes, to
  avoid the per-frame re-render cost.

```python
# Rebuilt every frame; safe to move or edit label.text later.
label = Text(x=0, y=0, text="Score: 0", dynamic=True)

# Built once; cheaper, but won't reflect later changes to x, y, or text.
title = Text(x=300, y=20, text="My Game", dynamic=False)
```

>[!NOTE]
> `color` and `bgcolor` are both plain RGB tuples; `Text` doesn't support a
> transparent background. Watch out for the default `color` (white) if you
> also set `bgcolor` to white, since the text won't be visible.

## Properties

In addition to the standard [`Entity` properties](scripting.md#entity-properties),
`Text` adds:

| Property | Description | Type |
| --- | --- | --- |
| `text` | The string being rendered | `str` |
| `font` | The loaded pygame font | `pygame.font.Font` |
| `color` | RGB color of the text | [`RGBType`](types.md#rgbtype) |
| `bgcolor` | RGB background color behind the text | [`RGBType`](types.md#rgbtype) |
| `antialias` | Whether glyphs are antialiased | `bool` |
| `dynamic` | Whether the surface is rebuilt every frame | `bool` |
| `text_surface` | The rendered text surface | `pygame.Surface` |
| `text_rect` | The rect `text_surface` is blit at | `pygame.Rect` |

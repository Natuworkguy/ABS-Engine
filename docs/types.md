# ABS Engine Types

ABS Engine keeps shared type aliases in `engine.core.types`.
These aliases make public APIs easier to read and help scripts use the same
types as the engine.

## RGBType

`RGBType` represents an RGB color as a three-item tuple of integers.

```python
from engine.core.types import RGBType


white: RGBType = (255, 255, 255)
black: RGBType = (0, 0, 0)
red: RGBType = (255, 0, 0)
```

Each value in the tuple represents one color channel:

- First value: Red
- Second value: Green
- Third value: Blue

Color channel values should normally be between `0` and `255`, matching the
values expected by Pygame drawing APIs.

## Where RGBType Is Used

`RGBType` is used by the core engine APIs that accept colors:

- `Entity(..., color=(255, 255, 255))`
- `Scene.set_bg_color(color)`

## Tuple Colors and Project Data

Python scripts should use `RGBType` as a tuple:

```python
from engine.core.types import RGBType


entity_color: RGBType = (128, 64, 255)
```

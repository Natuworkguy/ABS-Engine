# Music

Every [`Game`](using_the_engine_api.md) owns a small music mixer as
`game.music`. It plays one background track at a time, which is what
background music usually is: a single looping track that changes when the
scene or the mood does.

From a [script](scripting.md), reach it through the entity's scene:

```python
def init(entity):
    game = entity.parent.game
    game.music.play("assets/theme.ogg")
```

> [!TIP]
> Music is not entity-specific, so start it from your main script.
> See the tip about main scripts in the [Main Scripts section of the scripting docs](scripting.md#main-scripts).

Using the engine API directly:

```python
from engine.core import Game


game = Game(GP_BASE_PATH=".")

game.music.set_volume(0.5)
game.music.play("assets/theme.ogg")

game.run()
```

## Methods

| Method | Description |
| --- | --- |
| `play(track, *, loops=-1, fade_ms=0)` | Start `track`, replacing whatever was playing. `track` is a path relative to the project root. `loops` is how many extra times to repeat it, `-1` forever. `fade_ms` fades the track in. |
| `stop(*, fade_ms=0)` | Stop the current track and forget it. `fade_ms` fades it out instead of cutting it. |
| `pause()` | Hold the current track where it is. |
| `resume()` | Carry on with a paused track. |
| `set_volume(volume)` | Set how loud music plays, from `0.0` to `1.0`. Values outside that range are clamped. Applies to later tracks too. |
| `get_volume()` | Return the volume music is set to play at, from `0.0` to `1.0`. |
| `is_playing()` | Return whether a track is audible right now. A paused track is not playing. |

## Properties

| Property | Description | Type |
| --- | --- | --- |
| `track` | Path of the loaded track, or `None` when nothing is loaded | `Optional[str]` |
| `available` | Whether an audio device was opened | `bool` |
| `base_path` | Project root that `track` paths are given relative to | `str` |

## Formats

Playable formats come from pygame, which uses SDL_mixer. OGG and WAV are the
safe choices; MP3 support depends on how the player's SDL_mixer was built.
Prefer OGG for music, since it is compressed and always supported.

## Machines Without Audio

Some machines have no working audio device: a headless build server, a
container, or a desktop with sound disabled. Rather than crash a game over
it, the mixer logs a warning at startup and sets `available` to `False`.
Every method stays safe to call, and none of them do anything:

```python
def init(entity):
    music = entity.parent.game.music

    music.play("assets/theme.ogg")  # Fine. Silent, but fine.

    if not music.available:
        entity.parent.game.gamedata["subtitles"] = True
```

A missing or unreadable track file is handled the same way: the load is
logged as a warning and whatever was already playing keeps playing.

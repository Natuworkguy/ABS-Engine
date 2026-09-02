# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Core engine systems and base components.
"""

from pathlib import Path

from importlib.machinery import ModuleSpec
from types import ModuleType

import pygame
import importlib.util
import sys
import uuid
import os
import colorama

from typing import Optional, Any, Union

from ..logger import logger, Status as LoggerStatus
from .image import EntityImage
from .animation import EntityAnim
from .music import Music
from .errors import ABSFatalError
from .utils import clamp
from .types import RGBType, EntityMediaType
from ..version import __version__ as version

print(
    f"ABS Engine v{version} (Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, pygame {pygame.ver})"
    "\n"
)


class Entity:
    """
    An entity in the game.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        color: RGBType = (255, 255, 255),
        scriptfile: Optional[str] = None,
        image: Optional[str] = None,
    ) -> None:
        """
        Initialize an entity

        Args:
            x (float): X position. Defaults to 0.
            y (float): Y position. Defaults to 0.
            width (float): Width of the entity. Defaults to 50.
            height (float): Height of the entity. Defaults to 50.
            color (RGBType): RGB color value. Defaults to (255, 255, 255).
            scriptfile (Optional[str]): Path to optional script file. Defaults to None.
            image (Optional[str]): Path to optional image file. Defaults to None.
        """

        self.visible = True

        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.color: RGBType = (
            int(clamp(color[0], 0, 255)),
            int(clamp(color[1], 0, 255)),
            int(clamp(color[2], 0, 255)),
        )

        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.id: str = str(uuid.uuid4())

        self.parent: Optional["Scene"] = None

        self.scriptfile: Optional[str] = scriptfile
        self.scriptfile_module: Optional[ModuleType] = None
        self.scriptfile_funcs: dict[str, bool] = {
            "init": False,
            "update": False,
            "event": False,
        }

        self.did_init: bool = False

        self.image: Optional[EntityMediaType] = None

        if image is not None:
            try:
                if image.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    self.image = EntityImage(image)
                else:
                    self.image = EntityAnim(image)
            except (pygame.error, FileNotFoundError) as e:
                logger(
                    f"Failed to load image or animation '{image}': {str(e)}",
                    status=LoggerStatus.WARNING,
                )

        if scriptfile is not None:
            esfid = f"esf-{self.id}"

            script_dir = str(Path(scriptfile).resolve().parent)
            if script_dir not in sys.path:
                sys.path.append(script_dir)

            spec: Optional[ModuleSpec] = importlib.util.spec_from_file_location(esfid, scriptfile)

            if spec:
                self.scriptfile_module = importlib.util.module_from_spec(spec)
                sys.modules[esfid] = self.scriptfile_module

                if spec.loader:
                    try:
                        spec.loader.exec_module(self.scriptfile_module)
                    except FileNotFoundError:
                        logger(
                            f'Script file "{scriptfile}" not found. Please ensure the file exists and try again.',
                            status=LoggerStatus.CRITICAL,
                        )
                    except ImportError as e:
                        logger(f"Error when loading script: {e}", status=LoggerStatus.CRITICAL)

            if self.scriptfile_module is not None:
                if self.scriptfile is not None:
                    if hasattr(self.scriptfile_module, "init"):
                        self.scriptfile_funcs["init"] = True

                    if hasattr(self.scriptfile_module, "update"):
                        self.scriptfile_funcs["update"] = True

                    if hasattr(self.scriptfile_module, "event"):
                        self.scriptfile_funcs["event"] = True
            else:
                logger(f'Script file "{scriptfile}" not found.', status=LoggerStatus.WARNING)

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the entity.

        Returns:
            str: Human-readable entity description.
        """

        return f"<{self.__class__.__name__} with id {self.id}>"

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the entity.

        Returns:
            str: Debug representation of the entity.
        """

        return f"<{self.__class__.__name__} at {hex(id(self))} with id {self.id}>"

    def __del__(self) -> None:
        """
        Destructor for the entity.
        """

        try:
            self.destroy()
        except ValueError:
            logger("Failed to destroy entity", status=LoggerStatus.WARNING)

    def _collides_with(self, other: "Entity") -> bool:
        """
        Check if this entity collides with another entity using AABB collision detection.

        Args:
            other (Entity): Entity to check collision with

        Returns:
            bool: Whether this entity intersects the other entity.
        """

        return self.rect.colliderect(other.rect)

    def _setparent(self, parent: "Scene") -> None:
        """
        Set the parent scene for this entity.

        Args:
            parent (Scene): Scene to assign this entity to.
        """
        self.parent = parent

    def center(self, pos: tuple[float, float]) -> None:
        """
        Center the entity on a position.

        Args:
            pos (tuple[float, float]): The (x, y) point to center the entity on.
        """

        self.x = pos[0] - self.width // 2
        self.y = pos[1] - self.height // 2
        self._update_rect()

    def init(self) -> None:
        """
        Call the init function in the script file if it exists.
        This should only be called once per entity.
        """

        if self.scriptfile_module is not None:
            if self.scriptfile_funcs["init"]:
                self.scriptfile_module.init(self)
                self._update_rect()
                self.did_init = True

    def _update_rect(self) -> None:
        """
        Update the entity's rectangle position and size.
        """

        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self, dt: float) -> None:
        """
        Update the entity.

        Args:
            dt (float): The time elapsed since the last update.
        """

        if self.scriptfile_module is not None:
            if self.scriptfile_funcs["update"]:
                self.scriptfile_module.update(self, dt)
                self._update_rect()

    def event(self, event: pygame.event.Event) -> None:
        """
        Handle an event.

        Args:
            event (pygame.event.Event): The event to handle.
        """

        if self.scriptfile_module is not None:
            if self.scriptfile_funcs["event"]:
                self.scriptfile_module.event(self, event)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the entity onto the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the entity on.
        """

        if self.visible:
            if self.image is not None:
                self.image.draw(surface, self.rect)
            else:
                pygame.draw.rect(surface, self.color, self.rect)

    def get_colliding_entities(self) -> list["Entity"]:
        """
        Get all entities currently colliding with this entity.

        Returns:
            list["Entity"]: List of colliding entities or None.
        """

        if self.parent is None:
            return []

        return self.parent._get_colliding_entities(self)

    def _unload_script(self) -> None:
        """
        Drop this entity's script module from sys.modules.

        Each entity registers its script under a unique "esf-<id>" key to keep
        scripts isolated from one another. Nothing else removes those keys, so
        without this the module, and everything it references, would stay alive
        for the rest of the process.
        """

        entity_id: Optional[str] = getattr(self, "id", None)

        if entity_id is None:
            return

        sys.modules.pop(f"esf-{entity_id}", None)

    def destroy(self) -> None:
        """
        Destroy this entity.

        Raises:
            ValueError: If the entity cannot be removed from its parent.
        """

        self._unload_script()

        parent: Optional["Scene"] = getattr(self, "parent", None)  # See #29

        if parent is None:
            return

        try:
            parent.remove(self)
        except ValueError as e:
            raise ValueError("Invalid target for destruction") from e

        self.parent = None


class Scene:
    """
    A scene in the game.
    """

    def __init__(self, *, parent: "Game") -> None:
        """
        Initialize a scene.

        Args:
            parent (Game): Game instance this scene is assigned to.
        """

        # For use by entities
        self.scenedata: dict[Any, Any] = {}

        self.game: "Game" = parent
        self.objects: list[Entity] = []
        self.no_entities: bool = True

        logger("Initialized scene")

    def _get_colliding_entities(self, entity: Entity) -> list[Entity]:
        """
        Internal collision query used by Entity.get_colliding_entities().

        Args:
            entity (Entity): Entity to evaluate collisions for.

        Returns:
            list[Entity]: Entities currently colliding with the given entity.
        """

        colliding: list[Entity] = []

        for obj in self.objects:
            if obj != entity and entity._collides_with(obj):
                colliding.append(obj)

        return colliding

    def add(self, obj: Entity) -> None:
        """
        Add an entity to the scene.

        Args:
            obj (Entity): The entity to add
        """

        assert obj not in self.objects, "Entity is already in the scene"  # nosec B101

        self.objects.append(obj)
        obj._setparent(self)
        if not obj.did_init:
            obj.init()

        if self.no_entities:
            self.no_entities = False

    def update(self, dt: float) -> None:
        """
        Update all entities in the scene.

        Args:
            dt (float): Time elapsed since last update
        """

        if not self.no_entities:
            for obj in self.objects:
                obj.update(dt)

    def event(self, event: pygame.event.Event) -> None:
        """
        Dispatch a pygame event to all entities in the scene.

        Args:
            event (pygame.event.Event): Event passed to each entity.
        """

        if not self.no_entities:
            for obj in self.objects:
                obj.event(event)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Render all entities in the scene onto a surface.

        Args:
            surface (pygame.Surface): Surface to draw entities onto.
        """

        if not self.no_entities:
            for obj in self.objects:
                obj.draw(surface)

    def remove(self, obj: Entity) -> None:
        """
        Remove an entity from the scene.

        Args:
            obj (Entity): The entity to remove
        """

        self.objects.remove(obj)
        self.no_entities = len(self.objects) == 0


class Game:
    """
    Main game class
    """

    def __init__(
        self,
        title: str = "Game",
        /,
        width: float = 800,
        height: float = 600,
        *,
        GP_BASE_PATH: str,
        cursor_visible: bool = True,
        fullscreen: bool = False,
        icon_path: Optional[Union[str, Path]] = None,
        IS_EDITOR: bool = False,
    ) -> None:
        """
        Initialize the game.

        Args:
            title (str): Window title. Defaults to "Game".
            width (float): Window width in pixels. Defaults to 800.
            height (float): Window height in pixels. Defaults to 600.
            cursor_visible (bool): Whether the mouse cursor is visible. Defaults to True.
            fullscreen (bool): Whether to start in fullscreen mode. Defaults to False.
            icon_path (str | Path | None): Path to window icon image. Defaults to None.
            IS_EDITOR (bool): Whether running in editor mode. Defaults to False.
            GP_BASE_PATH (str): Base path for game assets


        Raises:
            ABSFatalError: If the window size is invalid
        """

        # For use by entities
        self.IS_EDITOR: bool = IS_EDITOR
        self.gamedata: dict = {}

        pygame.init()
        self.GP_BASE_PATH: str = GP_BASE_PATH
        self.music: Music = Music(GP_BASE_PATH)
        display_flags: int = pygame.FULLSCREEN if fullscreen else 0
        self.wsize: tuple[float, float] = (width, height)

        if width < 0 or height < 0:
            raise ABSFatalError("Window width and height must be positive")

        self.screen: pygame.Surface = pygame.display.set_mode(self.wsize, display_flags)
        pygame.display.set_caption(title)

        if not IS_EDITOR and sys.stdout is not None and sys.stdout.isatty():
            print(colorama.ansi.set_title(title), end="")

        if icon_path is not None:
            self.set_icon(icon_path)

        pygame.mouse.set_visible(cursor_visible)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False
        self.scenes: list[Scene] = [Scene(parent=self)]
        self.current_scene: int = 0
        self._bg_color: RGBType = (0, 0, 0)

        logger("Initialized game")

    def set_bg_color(self, color: RGBType) -> None:
        """
        Set the background color of the game

        Channels are clamped to 0-255, so a computed color cannot crash the
        game loop when the screen is filled with it.

        Args:
            color (RGBType): Color to set the background to
        """

        self._bg_color = (
            int(clamp(color[0], 0, 255)),
            int(clamp(color[1], 0, 255)),
            int(clamp(color[2], 0, 255)),
        )

    def add_scene(self) -> int:
        """
        Add a new scene to the game and return its index.

        Returns:
            int: The index of the newly added scene
        """

        self.scenes.append(Scene(parent=self))
        return len(self.scenes) - 1

    def switch_scene(self, scene_index: int) -> None:
        """
        Switch to a different scene.

        Args:
            scene_index (int): The index of the scene to switch to

        Raises:
            IndexError: If the scene index is out of bounds
        """
        if scene_index == self.current_scene:
            return

        if scene_index < 0 or scene_index >= len(self.scenes):
            raise IndexError(f"Tried to switch to a scene that doesn't exist: {scene_index}")

        self.current_scene = scene_index

    def move_entity_to_scene(self, entity: Entity, target_scene_index: int) -> None:
        """
        Move an entity to a different scene.

        Args:
            entity (Entity): The entity to move
            target_scene_index (int): The index of the scene to move the entity to

        Raises:
            IndexError: If the target scene index is out of bounds
        """

        if target_scene_index < 0 or target_scene_index >= len(self.scenes):
            raise IndexError(
                f"Tried to move entity to a scene that doesn't exist: {target_scene_index}"
            )

        if entity.parent == self.scenes[target_scene_index]:
            return

        if entity.parent is not None:
            entity.parent.remove(entity)

        self.scenes[target_scene_index].add(entity)

    def add_to_current_scene(self, entity: Entity) -> None:
        """
        Add an entity to the current scene

        Args:
            entity (Entity): The entity to add
        """

        self.scenes[self.current_scene].add(entity)

    def set_icon(self, icon_path: Union[str, Path]) -> None:
        """
        Set the icon for the game window.

        Args:
            icon_path (str | Path): The path to the icon file.
        """

        try:
            image: pygame.Surface = pygame.image.load(os.path.join(self.GP_BASE_PATH, icon_path))
            image = image.convert_alpha()
            pygame.display.set_icon(image)
        except (pygame.error, FileNotFoundError) as e:
            logger(f"Error loading icon: {e}", status=LoggerStatus.WARNING)

    def updateall(self, dt: float, /, exclude: Optional[Scene] = None) -> None:
        """
        Update all scenes in the game, even inactive ones.

        Args:
            dt (float): The time elapsed since the last update.
            exclude (Scene, optional): The scene to exclude from updating. Defaults to None.
        """

        for scene in self.scenes:
            if scene != exclude:
                scene.update(dt)

    def step(self, dt: float) -> None:
        """
        Perform a single game step.

        Args:
            dt (float): The time elapsed since the last step.
        """

        active_scene: Scene = self.scenes[self.current_scene]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                active_scene.event(event)

        active_scene.update(dt)
        self.screen.fill(self._bg_color)
        active_scene.draw(self.screen)
        pygame.display.flip()

    def run(self, fps: int = 60) -> None:
        """
        Run the main game loop.

        Args:
            fps (int): Target frames per second for the game loop. Defaults to 60.
        """

        logger("Starting game loop")
        self.running = True
        while self.running:
            dt: Union[int, float] = self.clock.tick(fps) / 1000.0
            self.step(dt)

        pygame.quit()

    def quit(self) -> None:
        """
        Stop the game and terminate execution.
        """

        self.running = False

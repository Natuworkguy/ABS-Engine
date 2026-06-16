# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Core engine systems and base components.
"""

import pygame
import importlib.util
import sys
import tkinter.messagebox
import uuid

from typing import Optional, Any

from ..logger import logger, Status as LoggerStatus
from .image import EntityImage
from .types import RGBType, EntityImageType
from ..version import __version__ as engineversion

print(
    f"ABS Engine v{engineversion} (Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, pygame {pygame.ver})"
)


class Entity:
    """
    An entity in the game.
    """

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 50,
        height: int = 50,
        color: RGBType = (255, 255, 255),
        scriptfile: Optional[str] = None,
        image: Optional[str] = None,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.id = str(uuid.uuid4())

        self.parent: Optional["Scene"] = None

        self.scriptfile = scriptfile
        self.scriptfile_module = None
        self.scriptfile_init_exists = False
        self.scriptfile_update_exists = False
        self.scriptfile_event_exists = False

        self.did_init = False

        self.image: Optional[EntityImageType] = None

        if image is not None:
            try:
                self.image = EntityImage(image)
            except pygame.error as e:
                logger(f"Failed to load image '{image}': {str(e)}", status=LoggerStatus.WARNING)
            except FileNotFoundError as e:
                tkinter.messagebox.showerror("File not found", str(e))

        if scriptfile is not None:
            esfid = f"esf-{self.id}"

            spec = importlib.util.spec_from_file_location(esfid, scriptfile)

            if spec:
                self.scriptfile_module = importlib.util.module_from_spec(spec)
                sys.modules[esfid] = self.scriptfile_module

                if spec.loader:
                    try:
                        spec.loader.exec_module(self.scriptfile_module)
                    except FileNotFoundError:
                        tkinter.messagebox.showerror(
                            "Error",
                            f'Script file "{scriptfile}" not found. Please ensure the file exists and try again.',
                        )
                    except ImportError as e:
                        tkinter.messagebox.showerror("Error", f"Error when loading script: {e}")

            if self.scriptfile_module is not None:
                if self.scriptfile is not None:
                    if hasattr(self.scriptfile_module, "init"):
                        self.scriptfile_init_exists = True

                    if hasattr(self.scriptfile_module, "update"):
                        self.scriptfile_update_exists = True

                    if hasattr(self.scriptfile_module, "event"):
                        self.scriptfile_event_exists = True
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
        return f"<{self.__class__.__name__} at {hex(id(self))} with id {self.id}>"

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
        self.parent = parent

    def init(self) -> None:
        """
        Call the init function in the script file if it exists.
        This should only be called once per entity.
        """

        if self.scriptfile_module is not None:
            if self.scriptfile_init_exists:
                self.scriptfile_module.init(self)
                self.did_init = True

    def update_rect(self) -> None:
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
            if self.scriptfile_update_exists:
                self.scriptfile_module.update(self, dt)

    def event(self, event: pygame.event.Event) -> None:
        """
        Handle an event.

        Args:
            event (pygame.event.Event): The event to handle.
        """

        if self.scriptfile_module is not None:
            if self.scriptfile_event_exists:
                self.scriptfile_module.event(self, event)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the entity onto the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the entity on.
        """

        if self.image is not None:
            self.image.draw(surface, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

    def get_colliding_entities(self) -> Optional[list["Entity"]]:
        if self.parent is None:
            return None

        return self.parent._get_colliding_entities(self)

    def destroy(self) -> None:
        if self.parent is not None:
            try:
                self.parent.remove(self)
            except ValueError:
                logger("Invalid target for destruction", status=LoggerStatus.WARNING)

            self.parent = None


class Scene:
    """
    A scene in the game.
    """

    def __init__(self, *, parent: "Game") -> None:
        # For use by entities
        self.scenedata: dict[Any, Any] = {}

        self.game: "Game" = parent
        self.objects: list[Entity] = []
        self.no_entities: bool = True

        logger("Initialized scene")

    def _get_colliding_entities(self, entity: Entity) -> list[Entity]:
        colliding = []

        for obj in self.objects:
            if obj != entity and entity._collides_with(obj):
                colliding.append(obj)

        return colliding

    def set_bg_color(self, color: RGBType) -> None:
        """
        Set the background color for the scene.

        Args:
            color (RGBType): The color to set as the background color.
        """

        self.game._set_bg_color(color)

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
        if not self.no_entities:
            for obj in self.objects:
                obj.update(dt)

    def event(self, event: pygame.event.Event) -> None:
        if not self.no_entities:
            for obj in self.objects:
                obj.event(event)

    def draw(self, surface: pygame.Surface) -> None:
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
    def __init__(
        self,
        title: str = "Game",
        /,
        width: int = 800,
        height: int = 600,
        *,
        cursor_visible: bool = True,
        fullscreen: bool = False,
        icon_path: Optional[str] = None,
        IS_EDITOR: bool = False,
    ) -> None:
        """
        Initialize the game.

        Args:
            title (str): Window title. Defaults to "Game".
            width (int): Window width in pixels. Defaults to 800.
            height (int): Window height in pixels. Defaults to 600.
            cursor_visible (bool): Whether the mouse cursor is visible. Defaults to True.
            fullscreen (bool): Whether to start in fullscreen mode. Defaults to False.
            icon_path (Optional[str]): Path to window icon image. Defaults to None.
            IS_EDITOR (bool): Whether running in editor mode. Defaults to False.
        """

        # For use by entities
        self.IS_EDITOR: bool = IS_EDITOR
        self.gamedata: dict = {}

        pygame.init()
        display_flags: int = pygame.FULLSCREEN if fullscreen else 0
        self.wsize: tuple[int, int] = (width, height)

        self.screen: pygame.Surface = pygame.display.set_mode(self.wsize, display_flags)
        pygame.display.set_caption(title)

        self.set_icon(icon_path)

        pygame.mouse.set_visible(cursor_visible)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False
        self.scenes: list[Scene] = [Scene(parent=self)]
        self.current_scene: int = 0
        self._bg_color: RGBType = (0, 0, 0)

        logger("Initialized game")

    def _set_bg_color(self, color: RGBType) -> None:
        self._bg_color = color

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

    def set_icon(self, icon_path: Optional[str]) -> None:
        """
        Set the icon for the game window.

        Args:
            icon_path (Optional[str]): The path to the icon file.
        """

        if icon_path is not None:
            try:
                image = pygame.image.load(icon_path)
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scenes[self.current_scene].event(event)

        self.scenes[self.current_scene].update(dt)
        self.screen.fill(self._bg_color)
        self.scenes[self.current_scene].draw(self.screen)
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
            dt = self.clock.tick(fps) / 1000.0
            self.step(dt)

        pygame.quit()

    def quit(self) -> None:
        """
        Stop the game and terminate execution.
        """

        self.running = False

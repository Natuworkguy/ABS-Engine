# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

import pygame
import importlib.util
import sys
import tkinter.messagebox
import uuid

from typing import Optional, Any

from ..logger import logger, Status as LoggerStatus
from .image import EntityImage


class Entity:
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int] = (255, 255, 255), scriptfile: Optional[str] = None, image: Optional[str] = None) -> None:
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

        self.image: Optional[EntityImage] = None

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
                        tkinter.messagebox.showerror("Error", f"Script file \"{scriptfile}\" not found. Please ensure the file exists and try again.")
                    except ImportError as e:
                        tkinter.messagebox.showerror("Error", f"Error when loading script: {e}")

            if self.scriptfile_module is not None:
                if self.scriptfile is not None:
                    if hasattr(self.scriptfile_module, 'init'):
                        self.scriptfile_init_exists = True

                    if hasattr(self.scriptfile_module, 'update'):
                        self.scriptfile_update_exists = True

                    if hasattr(self.scriptfile_module, 'event'):
                        self.scriptfile_event_exists = True
            else:
                logger(f"Script file \"{scriptfile}\" not found.", status=LoggerStatus.WARNING)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} with id {self.id}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} at {hex(id(self))} with id {self.id}>"

    def _collides_with(self, other: "Entity") -> bool:
        """Check if this entity collides with another entity using AABB collision detection."""
        return self.rect.colliderect(other.rect)

    def _setparent(self, parent: "Scene") -> None:
        self.parent = parent

    def init(self) -> None:
        if self.scriptfile_module is not None:
            if self.scriptfile_init_exists:
                self.scriptfile_module.init(self)

    def update_rect(self) -> None:
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self, dt: float) -> None:
        if self.scriptfile_module is not None:
            if self.scriptfile_update_exists:
                self.scriptfile_module.update(self, dt)

    def event(self, event: pygame.event.Event) -> None:
        if self.scriptfile_module is not None:
            if self.scriptfile_event_exists:
                self.scriptfile_module.event(self, event)

    def draw(self, surface: pygame.Surface) -> None:
        if self.image is not None:
            self.image.draw(surface, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

    def get_colliding_entities(self) -> Optional[list["Entity"]]:
        if self.parent is None:
            return

        return self.parent._get_colliding_entities(self)

    def destroy(self) -> None:
        if self.parent is not None:
            try:
                self.parent.remove(self)
            except ValueError:
                logger("Invalid target for destruction", status=LoggerStatus.WARNING)


class Scene:
    def __init__(self, *, parent: "Game", IS_EDITOR: bool = False) -> None:
        # For use by entities
        self.IS_EDITOR: bool = IS_EDITOR
        self.scenedata: dict[Any, Any] = {}

        self.game: "Game" = parent
        self.objects: list[Entity] = []
        self.no_entities: bool = True

        logger("Initialized scene")

    def _get_colliding_entities(self, entity: Entity) -> list[Entity]:
        """Return a list of all entities that are colliding with the given entity."""

        colliding = []

        for obj in self.objects:
            if obj != entity and entity._collides_with(obj):
                colliding.append(obj)

        return colliding

    def set_bg_color(self, color: tuple[int, int, int]) -> None:
        self.game._set_bg_color(color)

    def add(self, obj: Entity) -> None:
        assert obj not in self.objects, "Entity is already in the scene"  # nosec B101

        self.objects.append(obj)
        obj._setparent(self)
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
        IS_EDITOR: bool = False,
    ) -> None:
        pygame.init()
        display_flags: int = pygame.FULLSCREEN if fullscreen else 0
        self.screen: pygame.Surface = pygame.display.set_mode((width, height), display_flags)
        self.wsize: tuple[int, int] = (width, height)
        pygame.display.set_caption(title=title)
        pygame.mouse.set_visible(cursor_visible)
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False
        self.scene: Scene = Scene(parent=self, IS_EDITOR=IS_EDITOR)
        self._bg_color: tuple[int, int, int] = (0, 0, 0)

        logger("Initialized game")

    def _set_bg_color(self, color: tuple[int, int, int]) -> None:
        self._bg_color = color

    def step(self, dt: float) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.scene.event(event)

        self.scene.update(dt)
        self.screen.fill(self._bg_color)
        self.scene.draw(self.screen)
        pygame.display.flip()

    def run(self, fps: int = 60) -> None:
        logger("Starting game loop")
        self.running = True
        while self.running:
            dt = self.clock.tick(fps) / 1000.0
            self.step(dt)

        pygame.quit()

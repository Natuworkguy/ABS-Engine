# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

from typing import Optional, Any
import pygame
import importlib.util
import sys
import tkinter.messagebox
import uuid

from .logger import logger, Status as LoggerStatus

class Entity:
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int] = (255, 255, 255), scriptfile: Optional[str] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.id = str(uuid.uuid4())

        self.parent = None

        self.scriptfile = scriptfile
        self.scriptfile_module = None
        self.scriptfile_update_exists = False
        self.scriptfile_event_exists = False

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

            if self.scriptfile_module is not None:
                if self.scriptfile is not None:
                    if hasattr(self.scriptfile_module, 'init'):
                        self.scriptfile_module.init(self)
    
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

    def _setparent(self, parent):
        self.parent = parent

    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self, dt):
        if self.scriptfile_module is not None:
            if self.scriptfile_update_exists:
                self.scriptfile_module.update(self, dt)

    def event(self, event):
        if self.scriptfile_module is not None:
            if self.scriptfile_event_exists:
                self.scriptfile_module.event(self, event)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def get_colliding_entities(self) -> Optional[list["Entity"]]:
        if self.parent is None:
            return

        return self.parent._get_colliding_entities(self)


class Scene:
    def __init__(self, *, parent: "Game", IS_EDITOR: bool = False):
        # For use by entities
        self.IS_EDITOR: bool = IS_EDITOR
        self.scenedata: dict[Any, Any] = {}

        self.parent: "Game" = parent
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

    def add(self, obj: Entity):
        self.objects.append(obj)
        obj._setparent(self)

        if self.no_entities:
            self.no_entities = False

    def update(self, dt):
        if not self.no_entities:
            for obj in self.objects:
                obj.update(dt)

    def event(self, event):
        if not self.no_entities:
            for obj in self.objects:
                obj.event(event)

    def draw(self, surface):
        if not self.no_entities:
            for obj in self.objects:
                obj.draw(surface)


class Game:
    def __init__(self, title="Game", /, width=800, height=600, *, IS_EDITOR = False):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.wsize = (width, height)
        pygame.display.set_caption(title=title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.scene = Scene(parent=self, IS_EDITOR=IS_EDITOR)

        logger("Initialized game")

    def run(self, fps=60):
        logger("Starting game loop")

        self.running = True
        while self.running:
            dt = self.clock.tick(fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene.event(event)

            self.scene.update(dt)
            self.screen.fill((0, 0, 0))
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

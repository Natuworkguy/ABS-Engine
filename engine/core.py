# Copyright (C) Above and Below Studios
# See the LICENSE file for GPLv3

from typing import Optional, Any, Final
import pygame
import importlib.util
import tkinter.messagebox as messagebox
import sys
import uuid

from .logger import logger, Status as LoggerStatus

LOGSOURCE: Final[str] = "ENGINE.CORE"

class Entity():
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
            spec = importlib.util.spec_from_file_location("scriptfile_module", scriptfile)

            if spec:
                self.scriptfile_module = importlib.util.module_from_spec(spec)
                sys.modules[self.id] = self.scriptfile_module

                if spec.loader:
                    spec.loader.exec_module(self.scriptfile_module)

            if self.scriptfile_module is not None:
                if self.scriptfile is not None:
                    if hasattr(self.scriptfile_module, 'init'):
                        self.scriptfile_module.init(self)
    
                    if hasattr(self.scriptfile_module, 'update'):
                        self.scriptfile_update_exists = True
    
                    if hasattr(self.scriptfile_module, 'event'):
                        self.scriptfile_event_exists = True
            else:
                logger(LOGSOURCE, f"Script file \"{scriptfile}\" not found.", status=LoggerStatus.WARNING)

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

    def setparent(self, parent):
        self.parent = parent


class Scene:
    def __init__(self, *, parent: "Game", IS_EDITOR: bool = False):
        # For use by entities
        self.IS_EDITOR = IS_EDITOR
        self.scenedata = {}

        self.parent = parent
        self.objects = []
        self.no_entities = True

        logger(LOGSOURCE, "Initialized scene")

    def add(self, obj: Entity):
        self.objects.append(obj)
        obj.setparent(self)

        if self.no_entities:
            self.no_entities = False

    def update(self, dt):
        if not self.no_entities:
            for obj in self.objects:
                obj.update(dt)

    def event(self, event):
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

        logger(LOGSOURCE, "Initialized game")

    def run(self, fps=60):
        logger(LOGSOURCE, "Starting game loop")

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

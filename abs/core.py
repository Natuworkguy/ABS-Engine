from typing import Optional
import pygame
import importlib.util
import tkinter.messagebox as messagebox
import sys

class Entity:
    def __init__(self, x: float, y: float, width: float, height: float, color: tuple[int, int, int] = (255, 255, 255), scriptfile: Optional[str] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.scriptfile = scriptfile
        if scriptfile is not None:
            try:
                spec = importlib.util.spec_from_file_location("scriptfile_module", scriptfile)

                if spec:
                    self.scriptfile_module = importlib.util.module_from_spec(spec)
                    sys.modules["scriptfile_module"] = self.scriptfile_module
    
                    if spec.loader:
                        spec.loader.exec_module(self.scriptfile_module)
            except ModuleNotFoundError:
                messagebox.showerror("Error", f"Script file '{scriptfile}' not found.")
                pygame.quit()

    def update(self, dt):
        if self.scriptfile is not None and hasattr(self.scriptfile_module, 'update'):
            self.scriptfile_module.update(self, dt)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class Scene:
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)

    def draw(self, surface):
        for obj in self.objects:
            obj.draw(surface)

class Game:
    def __init__(self, width=800, height=600, title="2D Game Engine"):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(title=title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.scene = Scene()

    def run(self, fps=60):
        self.running = True
        while self.running:
            dt = self.clock.tick(fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.scene.update(dt)
            self.screen.fill((0, 0, 0))
            self.scene.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
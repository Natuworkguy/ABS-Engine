import pygame


class EntityImage:
    def __init__(self, image_path: str):
        self.set_image(image_path)

    def set_image(self, image_path: str):
        self.surface = pygame.image.load(image_path).convert_alpha()

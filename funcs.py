import os
import sys

import pygame

import constants as const


def load_image(name: str, transform=True) -> pygame.Surface:
    fullname = os.path.join("resources", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname).convert_alpha()
    if transform:
        image = pygame.transform.scale(image, (const.TILE_SIZE,) * 2)
    return image


def terminate() -> None:
    pygame.quit()
    sys.exit()


def load_level(filename: str) -> list[str]:
    filename = "data/" + filename
    with open(filename) as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))

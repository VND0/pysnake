import os
import sys

import pygame


def load_image(name: str, colorkey=None) -> pygame.Surface:
    fullname = os.path.join("resources", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
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

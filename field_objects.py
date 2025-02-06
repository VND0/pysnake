import threading
from numbers import Number

import pygame

import constants as const
import funcs


# Для однообразия
class Point:
    def __init__(self, *, x: int | None, y: int | None):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __copy__(self):
        return Point(x=self.x, y=self.y)

    def __eq__(self, other: "Point"):
        if other is None:
            return False
        return tuple(self) == tuple(other)


class Size:
    def __init__(self, *, w: Number, h: Number):
        self.w = w
        self.h = h

    def __iter__(self):
        return iter((self.w, self.h))


class Obstacle(pygame.Surface):
    def __init__(self):
        super().__init__((const.TILE_SIZE,) * 2)
        self.fill(const.OBSTACLE_COL)


class Head(pygame.Surface):
    def __init__(self, previous: Point):
        self.image = funcs.load_image("head.png")
        super().__init__(self.image.get_size(), pygame.SRCALPHA)
        self.blit(self.image, (0, 0))
        self.previous = previous
        self.turn_locked = False

    def rotate(self, angle) -> None:
        th = threading.Thread(target=self.__rotate, args=(angle,))
        th.start()

    def __rotate(self, angle: int) -> None:
        while self.turn_locked:
            pass
        # Чтобы повторы происходили подряд. Их возможно максимум два во время игры
        self.turn_locked = True
        clock = pygame.time.Clock()
        angle_per_frame = angle / (const.SEC_PER_TILE * const.FPS)
        current_angle = 0

        # self.copy() тут не срабатывает как надо
        original = pygame.Surface(self.get_size(), pygame.SRCALPHA)
        original.blit(self, (0, 0))

        while abs(current_angle) < abs(angle):
            current_angle += angle_per_frame
            if abs(current_angle) > abs(angle):
                current_angle = angle

            rotated = pygame.transform.rotate(original, current_angle)
            self.fill((0, 0, 0, 0))  # Прозрачные пиксели
            self.blit(rotated, (0, 0))

            clock.tick(const.FPS)
        self.turn_locked = False


class Apple(pygame.Surface):
    def __init__(self):
        self.image = funcs.load_image("apple.png")
        super().__init__(self.image.get_size(), pygame.SRCALPHA)
        self.blit(self.image, (0, 0))


class BodyPart(pygame.Surface):
    def __init__(self, previous: Point):
        super().__init__((const.TILE_SIZE,) * 2)
        self.fill(const.BODY_COL)
        self.previous = previous


class AngleTopTile(pygame.Surface):
    def __init__(self, size: Size, next_direction: const.DIRECTION | None):
        super().__init__(tuple(size))
        self.fill(const.ANGLE_TOP_COL)
        self.next_direction = next_direction


class AngleGoToTile(pygame.Surface):
    def __init__(self, size: Size):
        super().__init__(tuple(size))
        self.fill(const.ANGLE_GOTO_COL)

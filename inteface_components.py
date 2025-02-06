from typing import Any, Callable

import pygame

import constants as const
import funcs


class CloseButton(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.x, self.y = 3, 3
        self.width = self.height = const.STATUS_BAR_H - self.y * 2
        self.frames = []
        self.index = 0
        self.get_frames()
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect().move(self.x, self.y)

        self.skip = 0

    def get_frames(self):
        rows, cols, side = 7, 6, 32
        total = 38
        image = funcs.load_image("cross.png", False)
        counter = 0

        rect = pygame.Rect(0, 0, image.get_width() // cols, image.get_height() // rows)

        for y in range(rows):
            for x in range(cols):
                counter += 1
                if counter > total:
                    return
                frame = pygame.transform.scale(
                    image.subsurface(pygame.Rect((x * rect.w, y * rect.h), rect.size)),
                    (self.width, self.height)
                )
                self.frames.append(frame)

    def update(self, *args, **kwargs):
        self.skip += 1
        if self.skip <= 6:
            return
        self.skip = 0

        self.index = (self.index + 1) % len(self.frames)
        self.image = self.frames[self.index]


class Lattice(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        w = const.WIDTH
        h = const.STATUS_BAR_H
        content = pygame.Surface((w, h))
        pygame.draw.rect(content, const.BLUE, (0, 0, w, h), 2)
        pygame.draw.line(content, const.BLUE, (h, 0), (h, h), 2)
        self.image = content
        self.rect = content.get_rect()


class Score(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.font = pygame.font.Font(None, 25)
        self.w = const.WIDTH - 4 - const.STATUS_BAR_H
        self.h = const.STATUS_BAR_H - 4
        self.score = -1
        self.increment()

    def increment(self):
        self.score += 1
        content = pygame.Surface((self.w, self.h))

        text = self.font.render("Счет:", 1, const.GREEN)
        content.blit(text, (10, (self.h - text.get_height()) / 2))

        text = self.font.render(str(self.score), 1, const.GREEN)
        content.blit(text, (self.w - 10 - text.get_width(), (self.h - text.get_height()) / 2))

        self.image = content
        self.rect = content.get_rect().move(4 + const.STATUS_BAR_H, 0)


class StatusBar:
    def __init__(self, close_callback: Callable[[], Any], screen: pygame.Surface):
        self.callback = close_callback
        self.width = const.WIDTH
        self.height = const.STATUS_BAR_H

        self.screen = screen
        self.all_sprites = pygame.sprite.Group()

    def make(self):
        Lattice(self.all_sprites)
        self.close_button = CloseButton(self.all_sprites)
        self.score = Score(self.all_sprites)

    def draw(self):
        self.all_sprites.draw(self.screen)
        self.all_sprites.update()

    def get_click(self, pos: tuple[int, int]):
        if self.close_button.rect.collidepoint(*pos):
            self.callback()

    def score_increment(self):
        self.score.increment()


class Pause(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        image = self.make()
        self.image = image
        self.rect = image.get_rect()

    def make(self) -> pygame.Surface:
        image = pygame.Surface(const.SIZE, pygame.SRCALPHA)
        image.fill(const.PAUSE_BG)

        font = pygame.font.Font(None, 60)
        text = font.render("Пауза", 1, const.WHITE)
        image.blit(text, ((const.WIDTH - text.get_width()) / 2, (const.HEIGHT - text.get_height()) / 2))

        return image

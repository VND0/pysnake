from typing import Callable, Any, Literal

import pygame

import constants as const
import funcs


class CloseButton(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        w = h = const.STATUS_BAR_H
        content = pygame.Surface((w - 6, h - 6))
        w, h = content.get_size()
        pygame.draw.line(content, const.RED, (3, 3), (w - 3, h - 3), 2)
        pygame.draw.line(content, const.RED, (w - 3, 3), (3, h - 3), 2)
        self.image = content
        self.rect = content.get_rect().move(3, 3)


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
        self.update()

    def update(self):
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

    def get_click(self, pos: tuple[int, int]):
        if self.close_button.rect.collidepoint(*pos):
            self.callback()

    def score_increment(self):
        self.score.update()


class Board:
    def __init__(self, vert_cells: int, horiz_cells: int, margin_top: int, cell_size: int):
        self.v_cells = vert_cells
        self.h_cells = horiz_cells
        self.mt = margin_top
        self.cell_size = cell_size

    def render(self, screen: pygame.Surface):
        for y in range(self.v_cells):
            for x in range(self.h_cells):
                if (x + y) % 2 == 0:
                    color = const.CELL_COL_1
                else:
                    color = const.CELL_COL_2
                pygame.draw.rect(screen, color,
                                 (self.cell_size * x, self.mt + self.cell_size * y, self.cell_size, self.cell_size))


class Snake:
    def __init__(self, screen: pygame.Surface, difficulty: int):
        self.screen = screen
        self.difficulty = difficulty
        self.running = True
        self.score = 0
        self.goto_after: Literal["menu", "finish"] = "menu"

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            funcs.terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.status_bar.get_click(event.pos)

    def make(self):
        self.status_bar = StatusBar(self.close_by_button, self.screen)
        self.status_bar.make()
        self.board = Board(const.TILES_VERT, const.TILES_HORIZ, const.STATUS_BAR_H, const.TILE_SIZE)

    def draw(self):
        self.status_bar.draw()
        self.board.render(self.screen)

    def close_by_button(self):
        self.running = False

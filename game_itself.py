from random import randrange
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
    # TODO: поправить бред с "выиграл": нужен только счет
    def __init__(self, height: int, width: int, margin_top: int, cell_size: int,
                 callback: Callable[[Literal["won", "lost"], int], Any]):
        self.board: list[list[None | pygame.Surface]] = [[None for _ in range(width)] for _ in range(height)]
        self.height = height
        self.width = width
        self.mt = margin_top
        self.cell_size = cell_size
        # TODO: убрать словарик
        # TODO: поправить непрозрачность
        self.head_states = {
            "right": funcs.load_image("head_right.png"),
        }
        self.collectables = {
            "apple": funcs.load_image("apple.png"),
            "cherry": funcs.load_image("cherry.png")
        }
        self.game_over = callback
        self.init_snake()
        self.add_collectables()

    def init_snake(self):
        head_y, head_x = 3, 5
        body_y, body_x = 3, 4
        tail_y, tail_x = 3, 2
        self.board[head_y][head_x] = self.head_states["right"]
        surface = pygame.Surface((self.cell_size,) * 2)
        surface.fill(const.BODY_COL)
        for _ in range(2):
            self.board[body_y][body_x] = surface.copy()
            body_x -= 1
        self.board[tail_y][tail_x] = surface.copy()

    def add_collectables(self):
        for elem in self.collectables.values():
            while True:
                # TODO: предусмотреть ситуацию, когда змейка выиграла
                y = randrange(0, self.height)
                x = randrange(0, self.width)
                if self.board[y][x] is None:
                    self.board[y][x] = elem.copy()
                    break

    def render(self, screen: pygame.Surface):
        for y in range(self.height):
            for x in range(self.width):
                x_pos, y_pos = self.cell_size * x, self.mt + self.cell_size * y
                content = self.board[y][x]
                if content is not None:
                    screen.blit(content, (x_pos, y_pos))
                else:
                    rect = (x_pos, y_pos) + (self.cell_size,) * 2
                    if (x + y) % 2 == 0:
                        color = const.CELL_COL_1
                    else:
                        color = const.CELL_COL_2
                    pygame.draw.rect(screen, color, rect)

    def get_click(self, pos: tuple[int, int], button):
        cell = self.get_cell(pos)
        if cell:
            self.on_click(cell, button)
        else:
            print("out")

    def get_cell(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        mouse_x, mouse_y = pos
        x = (mouse_x) // self.cell_size
        y = (mouse_y - self.mt) // self.cell_size
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        return x, y

    def on_click(self, pos: tuple[int, int], button) -> None:
        pass


class Game:
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
            self.board.get_click(event.pos, event.button)

    def make(self):
        self.status_bar = StatusBar(self.close_by_button, self.screen)
        self.status_bar.make()
        self.board = Board(const.TILES_VERT, const.TILES_HORIZ, const.STATUS_BAR_H, const.TILE_SIZE, self.game_over)

    def draw(self):
        self.status_bar.draw()
        self.board.render(self.screen)

    def close_by_button(self):
        self.running = False

    def game_over(self, result: Literal["won", "lost"], score: int):
        print("got it")
        self.running = False

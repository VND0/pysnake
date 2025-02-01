from typing import Callable

import pygame

import constants as const
import funcs
from stats import database as db


class GameOverText(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)

        font = pygame.font.Font(None, 50)
        txt = font.render("Игра окончена!", 1, const.WHITE)
        w, h = txt.get_size()
        x = (const.WIDTH - w) // 2
        y = const.HEIGHT // 4 - h

        self.image = txt
        self.rect = txt.get_rect().move(x, y)


class ResultScore(pygame.sprite.Sprite):
    def __init__(self, score: int, *groups):
        super().__init__(*groups)
        self.score = score

        font = pygame.font.Font(None, 30)
        txt = font.render(f"Результат: {self.score}", 1, const.WHITE)
        w, h = txt.get_size()
        x = (const.WIDTH - w) // 2
        y = const.HEIGHT // 2

        self.image = txt
        self.rect = txt.get_rect().move(x, y)


class GoToMenuButton(pygame.sprite.Sprite):
    def __init__(self, callback: Callable[[], None], *groups):
        super().__init__(*groups)
        self.callback = callback

        font = pygame.font.Font(None, 35)
        txt = font.render("На главный экран", 1, const.WHITE)
        w, h = txt.get_size()

        btn = pygame.Surface((w + 20, h + 20))
        btn.blit(txt, (11, 11))
        w, h = btn.get_size()

        pygame.draw.rect(btn, const.WHITE, (0, 0, w, h), 2)
        x = (const.WIDTH - w) // 2
        y = const.HEIGHT * 0.75

        self.image = btn
        self.rect = btn.get_rect().move(x, y)

    def get_click(self, pos: tuple[int, int]) -> bool:
        if self.rect.collidepoint(*pos):
            self.callback()
            return True
        return False


class FinalScreen:
    def __init__(self, screen: pygame.Surface, score: int):
        self.running = True
        self.screen = screen
        self.score = score

        self.connections = db.get_connections("stats/data.db")
        self.update_score_in_db()

        self.all_sprites = pygame.sprite.Group()

    def update_score_in_db(self):
        conn = next(self.connections)
        db.set_last_score(conn, self.score)

        current_max = db.get_best_score(conn)
        if current_max < self.score:
            db.set_best_score(conn, self.score)

    def make(self):
        GameOverText(self.all_sprites)
        ResultScore(self.score, self.all_sprites)
        self.goto_menu_btn = GoToMenuButton(self.btn_clicked, self.all_sprites)

    def btn_clicked(self) -> None:
        self.running = False

    def draw(self):
        self.all_sprites.draw(self.screen)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            funcs.terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            self.goto_menu_btn.get_click(event.pos)

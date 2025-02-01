from abc import abstractmethod, ABC
from typing import Callable

import pygame

import constants as const
import funcs
from stats import database


class Title(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.font = pygame.font.Font(None, 60)
        self.width, self.height = 245, 100
        self.make()

    def make(self):
        content = pygame.Surface((self.width, self.height))
        text = self.font.render("ЗМЕЙКА", 1, const.GREEN)

        rect = text.get_rect()
        x = (self.width - rect.w) / 2
        y = (self.height - rect.h) / 2
        content.blit(text, (x, y))

        self.image = content
        self.rect = content.get_rect()


class Rules(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.font = pygame.font.Font(None, 30)
        self.width, self.height = 245, 160
        self.make()

    def make(self):
        content = pygame.Surface((self.width, self.height))
        rules_text = ["Игрок нажимает мышью", "на клетку, вершину", "угла поворота, затем -",
                      "в ту сторону, куда", "он хочет повернуть.", "", "Отмена - по ESC"]
        height_incr = 0
        for line in rules_text:
            text = self.font.render(line, 1, const.RED)
            _, text_h = text.get_size()
            content.blit(text, (0, (self.height - text_h) / (len(rules_text) + 1) + height_incr))
            height_incr += text_h

        self.image = content
        self.rect = content.get_rect().move(10, 80)


class Score(pygame.sprite.Sprite, ABC):
    def __init__(self, score: int, *groups):
        super().__init__(*groups)
        self.score = str(score)
        self.font_txt = pygame.font.Font(None, 30)
        self.font_score = pygame.font.Font(None, 60)
        self.width, self.height = 200, 95
        self.make()

    @abstractmethod
    def make(self):
        pass


class BestScore(Score):
    def make(self):
        content = pygame.Surface((self.width, self.height))
        text_lines = ["Лучший", "Результат"]
        height_incr = 0
        for line in text_lines:
            text = self.font_txt.render(line, 1, const.BLUE)
            _, text_h = text.get_size()
            content.blit(text, (0, (self.height - text_h) / (len(text_lines) + 1) + height_incr))
            height_incr += text_h

        text = self.font_score.render(self.score, 1, const.BLUE)
        text_w, text_h = text.get_size()
        content.blit(text, (self.width - text_w, (self.height - text_h) / 2))

        self.image = content
        self.rect = content.get_rect().move(280, 50)


class LastScore(Score):
    def make(self):
        content = pygame.Surface((self.width, self.height))
        text_lines = ["Последний", "Результат"]
        height_incr = 0
        for line in text_lines:
            text = self.font_txt.render(line, 1, const.BLUE)
            _, text_h = text.get_size()
            content.blit(text, (0, (self.height - text_h) / (len(text_lines) + 1) + height_incr))
            height_incr += text_h

        text = self.font_score.render(self.score, 1, const.BLUE)
        text_w, text_h = text.get_size()
        content.blit(text, (self.width - text_w, (self.height - text_h) / 2))

        self.image = content
        self.rect = content.get_rect().move(280, 125)


class ClickableSprite(pygame.sprite.Sprite, ABC):
    def __init__(self, callback: Callable[[], None], *groups):
        super().__init__(*groups)
        self.callback = callback
        self.width = 200
        self.height = 30
        self.font = pygame.font.Font(None, 25)
        self.make()

    @abstractmethod
    def make(self):
        pass

    def get_click(self, pos: tuple[int, int]) -> bool:
        """Возвращает True, если клик пришелся по этому спрайту."""
        if self.rect.collidepoint(*pos):
            self.callback()
            return True
        return False


class SetEasyLevel(ClickableSprite):
    def make(self):
        content = pygame.Surface((self.width, self.height))
        pygame.draw.rect(content, const.GREEN, (0, 0, self.width, self.height), 2)

        text = self.font.render("Низкая сложность", 1, const.GREEN)
        text_w, text_h = text.get_size()
        content.blit(text, ((self.width - text_w) / 2, (self.height - text_h) / 2))

        self.image = content
        self.rect = content.get_rect().move(40, 275)


""


class SetDifficultLevel(ClickableSprite):
    def make(self):
        content = pygame.Surface((self.width, self.height))
        pygame.draw.rect(content, const.GREEN, (0, 0, self.width, self.height), 2)

        text = self.font.render("Высокая сложность", 1, const.GREEN)
        text_w, text_h = text.get_size()
        content.blit(text, ((self.width - text_w) / 2, (self.height - text_h) / 2))

        self.image = content
        self.rect = content.get_rect().move(40, 325)


class StartGameButton(ClickableSprite):
    def make(self):
        self.width, self.height = 100, 50

        content = pygame.Surface((self.width, self.height))
        pygame.draw.rect(content, const.GREEN, (0, 0, self.width, self.height), 2)

        text = self.font.render("Играть", 1, const.GREEN)
        text_w, text_h = text.get_size()
        content.blit(text, ((self.width - text_w) / 2, (self.height - text_h) / 2))

        self.image = content
        self.rect = content.get_rect().move(325, 290)


class Asterisk(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.font = pygame.font.Font(None, 50)
        text = self.font.render("*", 1, const.RED)
        self.image = text
        self.rect = text.get_rect().move(250, 275)

    def to_high_pos(self):
        self.rect.y -= 325 - 275

    def to_low_pos(self):
        self.rect.y += 325 - 275


class StartScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.running = True
        self.chosen_difficulty = const.EASY

        self.all_sprites = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()

        self.db_connections = database.get_connections("stats/data.db")

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False
            funcs.terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            for button in self.buttons_group.sprites():
                clicked = button.get_click(event.pos)
                if clicked:
                    break

    def make(self):
        """Рисует все элементы. Обновлять окно между кадрами нужно отдельно."""

        Title(self.all_sprites)
        Rules(self.all_sprites)
        BestScore(database.get_best_score(next(self.db_connections)), self.all_sprites)
        LastScore(database.get_last_score(next(self.db_connections)), self.all_sprites)

        SetEasyLevel(lambda: self.set_difficulty(const.EASY), self.buttons_group, self.all_sprites)
        SetDifficultLevel(lambda: self.set_difficulty(const.DIFFICULT), self.buttons_group, self.all_sprites)
        StartGameButton(self.start_game, self.buttons_group, self.all_sprites)
        self.current_difficulty = Asterisk(self.all_sprites)

    def draw(self):
        self.all_sprites.draw(self.screen)

    def set_difficulty(self, level: int) -> None:
        if level == self.chosen_difficulty:
            return

        self.chosen_difficulty = level
        if level == const.EASY:
            self.current_difficulty.to_high_pos()
        elif level == const.DIFFICULT:
            self.current_difficulty.to_low_pos()

    def start_game(self) -> None:
        self.running = False

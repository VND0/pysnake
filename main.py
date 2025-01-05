import pygame

import constants as const
from game_itself import Game
from start_screen import StartScreen
from stats import database

pygame.init()
pygame.display.set_caption("Змейка")
screen = pygame.display.set_mode(const.SIZE)
clock = pygame.time.Clock()


def game_start() -> None:
    """Стартовое окно, статистика, правила"""
    running = True
    start = StartScreen(screen)
    start.make()
    while running:
        clock.tick(const.FPS)
        for event in pygame.event.get():
            start.handle_event(event)
        screen.fill(const.BLACK)
        start.draw()
        pygame.display.update()
        running = start.running

    run_game(start.chosen_difficulty)


def run_game(difficulty: int) -> None:
    """Основная игра"""
    running = True
    game = Game(screen, difficulty)
    game.make()
    while running:
        clock.tick(const.FPS)
        for event in pygame.event.get():
            game.handle_event(event)
        screen.fill(const.BLACK)
        game.draw()
        pygame.display.update()
        running = game.running

    if game.goto_after == "menu":
        game_start()
    else:
        # TODO: Вызывать финальный экран
        raise NotImplementedError


connections = database.get_connections("stats/data.db")
conn = next(connections)
database.init_db(conn)

game_start()
pygame.quit()

from typing import Literal

import pygame

import constants as const
import final_screen
from game_itself import Game
from start_screen import StartScreen
from stats import database

pygame.init()
pygame.display.set_caption("Змейка")
screen = pygame.display.set_mode(const.SIZE, pygame.SRCALPHA)
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
    delta_time = 0
    while running:
        clock.tick(const.FPS)
        for event in pygame.event.get():
            game.handle_event(event)
        screen.fill(const.BLACK)
        delta_time += 1 / const.FPS
        if delta_time >= const.SEC_PER_TILE:  # В константах есть время стояния на клеточке
            game.update()
            delta_time -= const.SEC_PER_TILE
        game.draw()
        pygame.display.update()
        running = game.running

    if game.goto_after == "menu":
        game_start()
    else:
        finish_screen(game.score, game.game_over_state)


def finish_screen(score: int, state: Literal["win", "loss"]) -> None:
    """Финальный экран. Содержит результат, кнопку возврата."""
    running = True
    finish = final_screen.FinalScreen(screen, score)
    finish.make(state)

    while running:
        clock.tick(const.FPS)
        for event in pygame.event.get():
            finish.handle_event(event)
        screen.fill(const.BLACK)
        finish.draw()
        pygame.display.update()
        running = finish.running

    game_start()


connections = database.get_connections("stats/data.db")
conn = next(connections)
database.init_db(conn)

game_start()
pygame.quit()

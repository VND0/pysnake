import pygame

import constants as const
from stats import database
from start_screen import StartScreen

pygame.init()
pygame.display.set_caption("Змейка")
screen = pygame.display.set_mode(const.SIZE)


def game_start() -> None:
    """Стартовое окно, статистика, правила"""
    running = True
    start = StartScreen(screen)
    start.make()
    while running:
        for event in pygame.event.get():
            start.handle_event(event)
        screen.fill(const.BLACK)
        start.draw()
        pygame.display.update()
        running = start.running
    # TODO: Вызывать основную игру, принимающую уровень сложности


connections = database.get_connections("stats/data.db")
conn = next(connections)
database.init_db(conn)

game_start()
pygame.quit()

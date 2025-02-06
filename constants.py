from typing import Literal

import pygame

FPS = 60

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 255)
BODY_COL = pygame.Color(91, 123, 249)
CELL_COL_1 = pygame.Color(55, 56, 60)
CELL_COL_2 = pygame.Color(40, 41, 44)

OBSTACLE_COL = pygame.Color(225, 139, 134)

SIZE = WIDTH, HEIGHT = 500, 405

EASY, DIFFICULT = -1, 1

STATUS_BAR_H = 30
TILES_HORIZ = 20
TILES_VERT = 15
TILE_SIZE = WIDTH // TILES_HORIZ

R, U, L, D = "RULD"
DIRECTION = Literal["R", "U", "L", "D"]
SEC_PER_TILE = 0.3

ANGLE_TOP_COL = pygame.Color(240, 167, 50)
ANGLE_GOTO_COL = pygame.Color(149, 113, 57)

PAUSE_BG = pygame.Color(0, 0, 0, 128)

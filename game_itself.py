import threading
from random import randrange
from typing import Callable, Any, Literal

import pygame

import constants as const
import funcs
from inteface_components import StatusBar


class SnakeGameOverException(Exception):
    def __init__(self, state: Literal["win", "loss"], *args):
        super().__init__(*args)
        self.state = state


class Head(pygame.Surface):
    def __init__(self, previous: tuple[int, int]):
        self.image = funcs.load_image("head.png")
        super().__init__(self.image.get_size())
        self.blit(self.image, (0, 0))
        self.previous = previous

    def rotate(self, angle) -> None:
        th = threading.Thread(target=self.__rotate, args=(angle,))
        th.start()

    def __rotate(self, angle: int) -> None:
        clock = pygame.time.Clock()
        angle_per_frame = angle / (const.SEC_PER_TILE * const.FPS)
        current_angle = 0

        # self.copy() тут не работает
        original = pygame.Surface(self.get_size())
        original.blit(self, (0, 0))

        while abs(current_angle) < abs(angle):
            current_angle += angle_per_frame
            if abs(current_angle) > abs(angle):
                current_angle = angle

            rotated = pygame.transform.rotate(original, current_angle)
            self.fill(const.BLACK)
            self.blit(rotated, (0, 0))

            clock.tick(const.FPS)


class Apple(pygame.Surface):
    def __init__(self):
        self.image = funcs.load_image("apple.png")
        super().__init__(self.image.get_size())
        self.blit(self.image, (0, 0))


class BodyPart(pygame.Surface):
    def __init__(self, previous: tuple[int | None, int | None]):
        super().__init__((const.TILE_SIZE,) * 2)
        self.fill(const.BODY_COL)
        self.previous = previous


class AngleTopTile(pygame.Surface):
    def __init__(self, size: tuple[int, int], next_direction: const.DIRECTION | None):
        super().__init__(size)
        self.fill(const.ANGLE_TOP_COL)
        self.next_direction = next_direction


class AngleGoToTile(pygame.Surface):
    def __init__(self, size: tuple[int, int]):
        super().__init__(size)
        self.fill(const.ANGLE_GOTO_COL)


BOARD_CONTENT = list[list[None | pygame.Surface | BodyPart | AngleTopTile | AngleGoToTile | Apple | Head]]


class Board:
    def __init__(self, height: int, width: int, on_earned_score: Callable[[], Any]):
        self.board: BOARD_CONTENT = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.height = height
        self.width = width
        self.margin_top = const.STATUS_BAR_H
        self.earned_score = on_earned_score

        self.angle_top: tuple[int, int] | None = None
        self.angle_goto: tuple[int, int] | None = None

        self.init_snake()
        self.add_apple()

    def init_snake(self):
        head_y, head_x = 3, 5

        head = Head((head_y, head_x - 1))
        self.board[head_y][head_x] = head

        body = BodyPart((head_y, head_x - 2))
        self.board[head_y][head_x - 1] = body

        body = body.copy()
        body.previous = (head_y, head_x - 3)
        self.board[head_y][head_x - 2] = body

        body = body.copy()
        body.previous = (None, None)
        self.board[head_y][head_x - 3] = body
        self.direction = const.R
        self.head_pos = (head_y, head_x)

    def add_apple(self):
        got_none = False
        for row in self.board:
            if got_none:
                break
            for val in row:
                if val is None:
                    got_none = True
                    break
        if not got_none:
            raise SnakeGameOverException(state="win")  # Если яблоку негде появиться, то игрок побеждает

        while True:
            y = randrange(0, self.height)
            x = randrange(0, self.width)
            if not (2 <= y < len(self.board) - 2 and 2 <= x < len(self.board[0])):
                continue
            if self.board[y][x] is None:
                self.board[y][x] = Apple()
                break

    def can_go_there(self, x0: int, y0: int, x1: int, y1: int, direction: const.DIRECTION) -> bool:
        if direction == const.R:
            return y0 == y1 and x0 < x1
        elif direction == const.U:
            return x0 == x1 and y0 > y1
        elif direction == const.L:
            return y0 == y1 and x0 > x1
        elif direction == const.D:
            return x0 == x1 and y0 < y1

    def get_next_direction(self, x0: int, y0: int, x1: int, y1: int) -> const.DIRECTION | None:
        direction = None
        if x0 == x1:
            if y0 < y1:
                direction = const.D
            elif y0 > y1:
                direction = const.U
        elif y0 == y1:
            if x0 < x1:
                direction = const.R
            elif x0 > x1:
                direction = const.L
        if direction is None:  # Перемещение по диагонали или стояние на месте
            return None

        # Чтобы змейка не ушла в себя или не продолжила двигаться в том же направлении
        right_left = (const.R, const.L)
        if self.direction in right_left and direction in right_left:
            return None
        up_down = (const.U, const.D)
        if self.direction in up_down and direction in up_down:
            return None

        return direction

    def render(self, screen: pygame.Surface):
        for y in range(self.height):
            for x in range(self.width):
                x_pos, y_pos = const.TILE_SIZE * x, self.margin_top + const.TILE_SIZE * y
                content = self.board[y][x]
                if content is not None:
                    screen.blit(content, (x_pos, y_pos))
                else:
                    rect = (x_pos, y_pos) + (const.TILE_SIZE,) * 2
                    if (x + y) % 2 == 0:
                        color = const.CELL_COL_1
                    else:
                        color = const.CELL_COL_2
                    pygame.draw.rect(screen, color, rect)

    def get_click(self, pos: tuple[int, int], button):
        cell = self.get_cell(pos)
        if cell:
            self.on_click(cell, button)

    def get_cell(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        mouse_x, mouse_y = pos
        x = mouse_x // const.TILE_SIZE
        y = (mouse_y - self.margin_top) // const.TILE_SIZE
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        return x, y

    def on_click(self, pos: tuple[int, int], button) -> None:
        clck_x, clck_y = pos
        if button != pygame.BUTTON_LEFT or self.board[clck_y][clck_x] is BodyPart:
            return

        if not self.board[clck_y][clck_x]:
            if not self.angle_top:
                if self.can_go_there(*self.head_pos[::-1], *pos, self.direction):
                    self.angle_top = pos
                    self.board[clck_y][clck_x] = AngleTopTile((const.TILE_SIZE,) * 2, None)
            elif not self.angle_goto:
                at_x, at_y = self.angle_top
                direction = self.get_next_direction(at_x, at_y, clck_x, clck_y)
                if direction is None or not self.can_go_there(at_x, at_y, clck_x, clck_y, direction):
                    self.angle_top = self.board[at_y][at_x] = None
                    return

                self.angle_goto = pos
                self.board[clck_y][clck_x] = AngleGoToTile((const.TILE_SIZE,) * 2)
                self.board[at_y][at_x].next_direction = direction
            else:
                # Если все данные угла поворота уже есть, то мы считаем, что пользователь хочет пойти по-другому
                # Просто удаляем обе клеточки
                self.del_angle_top()
                self.del_angle_goto()
                self.on_click(pos, button)

    def update(self):
        h_y, h_x = self.head_pos
        head = self.board[h_y][h_x]

        if self.direction == const.R:
            next_y, next_x = h_y, h_x + 1
        elif self.direction == const.U:
            next_y, next_x = h_y - 1, h_x
        elif self.direction == const.L:
            next_y, next_x = h_y, h_x - 1
        else:
            next_y, next_x = h_y + 1, h_x

        # Игрок врезался в границу поля - проиграл
        if not (0 <= next_x < len(self.board[0])):
            raise SnakeGameOverException(state="loss")
        if not (0 <= next_y < len(self.board)):
            raise SnakeGameOverException(state="loss")

        change_direction = False
        self.head_pos = (next_y, next_x)
        current_direction = self.direction

        next_tile = self.board[next_y][next_x]

        # Попали на вершину угла поворота
        if self.head_pos[::-1] == self.angle_top:
            if self.angle_goto:
                change_direction = True
                next_direction = next_tile.next_direction
                self.del_angle_top()
                self.del_angle_goto()
                self.direction = next_direction
            else:
                self.del_angle_top()
            self.board[next_y][next_x] = head
            self.move_snake_after_head(h_x, h_y, head)
        elif type(next_tile) is Apple:
            self.earned_score()
            # Двигаем голову, вставляем новый кусочек змеи между, остальную змейку не двигаем
            self.board[next_y][next_x] = head
            new_part = BodyPart(head.previous)
            self.board[h_y][h_x] = new_part
            head.previous = (h_y, h_x)
            self.add_apple()
        elif type(next_tile) is BodyPart:
            raise SnakeGameOverException(state="loss")  # Врезались в себя
        else:
            self.board[next_y][next_x] = head
            self.move_snake_after_head(h_x, h_y, head)

        if change_direction:
            self.on_direction_change(current_direction, next_direction)

    def on_direction_change(self, prev_direction: const.DIRECTION, next_direction: const.DIRECTION):
        all_dirs = const.R + const.U + const.L + const.D
        # Тут R->U->L->D->R..., как на тригонометрической окружности почти
        # Если идем по ней - угол +90, иначе - -90
        if all_dirs[(all_dirs.index(prev_direction) + 1) % len(all_dirs)] == next_direction:
            angle = 90
        else:
            angle = -90

        h_y, h_x = self.head_pos
        self.board[h_y][h_x].rotate(angle)

    def move_snake_after_head(self, h_x, h_y, head):
        y, x = head.previous
        head.previous = (h_y, h_x)
        self.board[h_y][h_x] = None
        to_x, to_y = h_x, h_y
        while x is not None and y is not None:
            part = self.board[y][x]
            # Если змейка замыкает ломаную, то эта проверка позволяет избежать бесконечного цикла
            if type(part) is Head or part is None:
                break
            self.board[to_y][to_x] = part
            self.board[y][x] = None
            to_x, to_y = x, y
            y, x = part.previous
            part.previous = (to_y, to_x)

    def del_angle_top(self):
        at_x, at_y = self.angle_top
        self.board[at_y][at_x] = self.angle_top = None

    def del_angle_goto(self):
        goto_x, goto_y = self.angle_goto
        self.board[goto_y][goto_x] = self.angle_goto = None


class Game:
    def __init__(self, screen: pygame.Surface, difficulty: int):
        self.screen = screen
        self.difficulty = difficulty
        self.running = True
        self.score = 0
        self.goto_after: Literal["menu", "finish"] = "menu"
        self.game_over_state = None
        self.paused = False
        self.make()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            funcs.terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.status_bar.get_click(event.pos)
            if not self.paused:
                self.board.get_click(event.pos, event.button)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.paused = not self.paused

    def make(self):
        self.status_bar = StatusBar(self.close_by_button, self.screen)
        self.status_bar.make()
        self.board = Board(const.TILES_VERT, const.TILES_HORIZ, self.increment_score)

    def increment_score(self) -> None:
        self.score += 1
        self.status_bar.score_increment()

    def draw(self):
        self.status_bar.draw()
        self.board.render(self.screen)

    def update(self):
        if self.paused:
            return
        try:
            self.board.update()
        except SnakeGameOverException as e:
            self.game_over_state = e.state
            self.game_over()

    def close_by_button(self):
        self.running = False

    def game_over(self):
        self.running = False
        self.goto_after = "finish"

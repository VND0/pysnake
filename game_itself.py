from random import randrange
from typing import Callable, Any, Literal

import pygame

import constants as const
import funcs
from field_objects import BodyPart, AngleTopTile, AngleGoToTile, Apple, Head, Obstacle
from inteface_components import StatusBar


class SnakeGameOverException(Exception):
    def __init__(self, state: Literal["win", "loss"], *args):
        super().__init__(*args)
        self.state = state


BOARD_CONTENT = list[list[None | BodyPart | AngleTopTile | AngleGoToTile | Apple | Head | Obstacle]]


class Board:
    def __init__(self, height: int, width: int, on_earned_score: Callable[[], Any], difficulty: int):
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
        if difficulty == const.DIFFICULT:
            self.create_obstacles()

    def create_obstacles(self):
        with open("difficult_lvl_obstacles") as f:
            lines = f.readlines()
            if len(lines) != len(self.board):
                raise ValueError("Карта не подходит под игровое поле.")
            for row, line in enumerate(map(str.strip, lines)):
                if len(line) != len(self.board[row]):
                    raise ValueError("Карта не подходит под игровое поле.")
                for col, cell in enumerate(line):
                    if cell == "#":
                        self.board[row][col] = Obstacle()

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
        head_y, head_x = self.head_pos
        head = self.board[head_y][head_x]

        if self.direction == const.R:
            next_y, next_x = head_y, head_x + 1
        elif self.direction == const.U:
            next_y, next_x = head_y - 1, head_x
        elif self.direction == const.L:
            next_y, next_x = head_y, head_x - 1
        else:
            next_y, next_x = head_y + 1, head_x

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
            self.move_snake_after_head(head_x, head_y, head)
        elif type(next_tile) is Apple:
            self.earned_score()
            # Двигаем голову, вставляем новый кусочек змеи между, остальную змейку не двигаем
            self.board[next_y][next_x] = head
            new_part = BodyPart(head.previous)
            self.board[head_y][head_x] = new_part
            head.previous = (head_y, head_x)
            self.add_apple()
        elif type(next_tile) in (BodyPart, Obstacle):
            raise SnakeGameOverException(state="loss")
        else:
            self.board[next_y][next_x] = head
            self.move_snake_after_head(head_x, head_y, head)

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

    def move_snake_after_head(self, goto_x: int, goto_y: int, head: Head):
        current_y, current_x = head.previous
        head.previous = (goto_y, goto_x)
        self.board[goto_y][goto_x] = None
        while current_y is not None and current_x is not None:
            part = self.board[current_y][current_x]
            # Если змейка замыкает ломаную, то эта проверка позволяет избежать бесконечного цикла
            if type(part) is Head or part is None:
                break
            self.board[goto_y][goto_x] = part
            self.board[current_y][current_x] = None
            goto_x, goto_y = current_x, current_y
            current_y, current_x = part.previous
            part.previous = (goto_y, goto_x)

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
        self.board = Board(const.TILES_VERT, const.TILES_HORIZ, self.increment_score, self.difficulty)

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

import threading
from random import randrange
from typing import Callable, Any, Literal

import pygame

import constants as const
import funcs


class CloseButton(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.x, self.y = 3, 3
        self.width = self.height = const.STATUS_BAR_H - self.y * 2
        self.frames = []
        self.index = 0
        self.get_frames()
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect().move(self.x, self.y)

        self.skip = 0

    def get_frames(self):
        rows, cols, side = 7, 6, 32
        total = 38
        image = funcs.load_image("cross.png", False)
        counter = 0

        rect = pygame.Rect(0, 0, image.get_width() // cols, image.get_height() // rows)

        for y in range(rows):
            for x in range(cols):
                counter += 1
                if counter > total:
                    return
                frame = pygame.transform.scale(
                    image.subsurface(pygame.Rect((x * rect.w, y * rect.h), rect.size)),
                    (self.width, self.height)
                )
                self.frames.append(frame)

    def update(self, *args, **kwargs):
        self.skip += 1
        if self.skip <= 6:
            return
        self.skip = 0

        self.index = (self.index + 1) % len(self.frames)
        self.image = self.frames[self.index]


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
        self.increment()

    def increment(self):
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
        self.all_sprites.update()

    def get_click(self, pos: tuple[int, int]):
        if self.close_button.rect.collidepoint(*pos):
            self.callback()

    def score_increment(self):
        self.score.increment()


class SnakePart(pygame.Surface):
    def __init__(self, size: tuple[int, int] | None, image: pygame.Surface | None,
                 previous: tuple[int | None, int | None]):
        if size is None and image is None:
            raise ValueError("Нет данных для создания объекта")
        super().__init__(size or image.get_size())
        if image is not None:
            self.blit(image, (0, 0))
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


BOARD_CONTENT = list[list[None | pygame.Surface | SnakePart | AngleTopTile | AngleGoToTile]]


def rotate_surface(angle: int, position: tuple[int, int], board: BOARD_CONTENT) -> None:
    def rotate():
        clock = pygame.time.Clock()
        angle_per_frame = angle / (const.SEC_PER_TILE * const.FPS)
        current_angle = 0

        y, x = position
        to_be_turned = board[y][x]
        original = SnakePart(to_be_turned.get_size(), to_be_turned, board[y][x].previous)
        while abs(current_angle) < abs(angle):
            current_angle += angle_per_frame
            if abs(current_angle) > abs(angle):
                current_angle = angle

            rotated_surface = pygame.transform.rotate(original, current_angle)
            to_be_turned.fill(const.BLACK)
            to_be_turned.blit(rotated_surface, (0, 0))

            clock.tick(const.FPS)

    thread = threading.Thread(target=rotate)
    thread.start()


class Board:
    def __init__(self, height: int, width: int, margin_top: int, cell_size: int, on_earned_score: Callable[[], Any]):
        self.board: BOARD_CONTENT = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.height = height
        self.width = width
        self.mt = margin_top
        self.cell_size = cell_size
        self.head_states = {
            "right": funcs.load_image("head_right.png"),
        }
        self.collectables = {
            "apple": funcs.load_image("apple.png"),
            "cherry": funcs.load_image("cherry.png")
        }
        self.earned_score = on_earned_score

        self.angle_top: tuple[int, int] | None = None
        self.angle_goto: tuple[int, int] | None = None

        self.init_snake()
        self.add_collectables()

    def init_snake(self):
        head_y, head_x = 3, 5

        head = SnakePart(None, self.head_states["right"], (head_y, head_x - 1))
        self.board[head_y][head_x] = head

        body = SnakePart((self.cell_size,) * 2, None, (head_y, head_x - 2))
        body.fill(const.BODY_COL)
        self.board[head_y][head_x - 1] = body

        body = body.copy()
        body.previous = (head_y, head_x - 3)
        self.board[head_y][head_x - 2] = body

        body = body.copy()
        body.previous = (None, None)
        self.board[head_y][head_x - 3] = body
        self.direction = const.R
        self.head_pos = (head_y, head_x)

    def add_collectables(self):
        for elem in self.collectables.values():
            while True:
                # TODO: предусмотреть ситуацию, когда змейка выиграла
                y = randrange(0, self.height)
                x = randrange(0, self.width)
                if self.board[y][x] is None:
                    self.board[y][x] = elem.copy()
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

    def get_cell(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        mouse_x, mouse_y = pos
        x = mouse_x // self.cell_size
        y = (mouse_y - self.mt) // self.cell_size
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        return x, y

    def on_click(self, pos: tuple[int, int], button) -> None:
        clck_x, clck_y = pos
        if button != pygame.BUTTON_LEFT or self.board[clck_y][clck_x] is SnakePart:
            return

        if not self.board[clck_y][clck_x]:
            if not self.angle_top:
                if self.can_go_there(*self.head_pos[::-1], *pos, self.direction):
                    self.angle_top = pos
                    self.board[clck_y][clck_x] = AngleTopTile((self.cell_size,) * 2, None)
            elif not self.angle_goto:
                at_x, at_y = self.angle_top
                direction = self.get_next_direction(at_x, at_y, clck_x, clck_y)
                if direction is None or not self.can_go_there(at_x, at_y, clck_x, clck_y, direction):
                    self.angle_top = self.board[at_y][at_x] = None
                    return

                self.angle_goto = pos
                self.board[clck_y][clck_x] = AngleGoToTile((self.cell_size,) * 2)
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

        if not (0 <= next_x < len(self.board[0])):
            raise SnakeGameOverError
        if not (0 <= next_y < len(self.board)):
            raise SnakeGameOverError

        change_direction = False
        self.head_pos = (next_y, next_x)
        current_direction = self.direction
        if self.head_pos[::-1] == self.angle_top:
            if self.angle_goto:
                change_direction = True
                next_direction = self.board[next_y][next_x].next_direction
                self.del_angle_top()
                self.del_angle_goto()
                self.direction = next_direction
            else:
                self.del_angle_top()
        self.board[next_y][next_x] = head
        if change_direction:
            self.on_direction_change(current_direction, next_direction)
        self.move_snake_after_head(h_x, h_y, head)

    def on_direction_change(self, prev_direction: const.DIRECTION, next_direction: const.DIRECTION):
        all_dirs = const.R + const.U + const.L + const.D
        # Тут R->U->L->D->R..., как на тригонометрической окружности почти
        # Если идем по ней - угол 90, иначе - -90
        if all_dirs[(all_dirs.index(prev_direction) + 1) % len(all_dirs)] == next_direction:
            angle = 90
        else:
            angle = -90
        rotate_surface(angle, self.head_pos, self.board)

    def move_snake_after_head(self, h_x, h_y, head):
        y, x = head.previous
        head.previous = (h_y, h_x)
        self.board[h_y][h_x] = None
        to_x, to_y = h_x, h_y
        while x is not None and y is not None:
            part = self.board[y][x]
            if part is None:
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


class SnakeGameOverError(Exception):
    pass


class Game:
    def __init__(self, screen: pygame.Surface, difficulty: int):
        self.screen = screen
        self.difficulty = difficulty
        self.running = True
        self.score = 0
        self.goto_after: Literal["menu", "finish"] = "menu"
        self.make()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            funcs.terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.status_bar.get_click(event.pos)
            self.board.get_click(event.pos, event.button)

    def make(self):
        self.status_bar = StatusBar(self.close_by_button, self.screen)
        self.status_bar.make()
        self.board = Board(const.TILES_VERT, const.TILES_HORIZ, const.STATUS_BAR_H, const.TILE_SIZE,
                           self.increment_score)

    def increment_score(self) -> None:
        self.score += 1

    def draw(self):
        self.status_bar.draw()
        self.board.render(self.screen)

    def update(self):
        try:
            self.board.update()
        except SnakeGameOverError:
            self.game_over()

    def close_by_button(self):
        self.running = False

    def game_over(self):
        self.running = False
        self.goto_after = "finish"

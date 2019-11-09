import copy
import random

import pygame
from pygame.locals import *

from homework03.life.life_with_classes import Cell


class GameOfLife:

    def __init__(self, width: int = 640, height: int = 480, cell_size: int = 10, speed: int = 10) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

    def draw_lines(self) -> None:
        # @see: http://www.pygame.org/docs/ref/draw.html#pygame.draw.line
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.draw_lines()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()

    def draw_grid(self) -> None:
        """
        Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        """
        for h in range(self.cell_height):
            for w in range(self.cell_width):
                y = h * self.cell_size
                x = w * self.cell_size
                if not self.grid[h][w]:
                    pygame.draw.rect(self.screen, pygame.Color('white'),
                                     [x + 1, y + 1, self.cell_size - 1, self.cell_size - 1])
                else:
                    pygame.draw.rect(self.screen, pygame.Color('green'),
                                     [x + 1, y + 1, self.cell_size - 1, self.cell_size - 1])

    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.

        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.

        Parameters
        ----------
        cell : Cell
            Клетка, для которой необходимо получить список соседей. Клетка
            представлена кортежем, содержащим ее координаты на игровом поле.

        Returns
        ----------
        out : Cells
            Список соседних клеток.
        """

        neighbours = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                h = cell[0] + i
                w = cell[1] + j

                if 0 <= w < self.cell_width and 0 <= h < self.cell_height and i != 0 and j != 0:
                    neighbours.append(self.grid[h][w])

        return neighbours

    def create_grid(self, randomize: bool = False) -> Grid:
        """
        Создание списка клеток.

        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.

        Parameters
        ----------
        randomize : bool
            Если значение истина, то создается матрица, где каждая клетка может
            быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.

        Returns
        ----------
        out : Grid
            Матрица клеток размером `cell_height` х `cell_width`.
        """
        if randomize:
            return [[random.randint(0, 1) for _ in range(self.cell_width)] for _ in range(self.cell_height)]
        return [[0 for _ in range(self.cell_width)] for _ in range(self.cell_height)]

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.

        Returns
        ----------
        out : Grid
            Новое поколение клеток.
        """
        grid2 = self.create_grid()
        for y in range(self.cell_height):
            for x in range(self.cell_width):
                nn = self.get_neighbours((y, x)).count(1)
                if self.grid[y][x] == 0:
                    if nn == 3:
                        grid2[y][x] = 1
                else:
                    if nn == 2 or nn == 3:
                        grid2[y][x] = 1
        return grid2


if __name__ == '__main__':
    game = GameOfLife(320, 240, 20)
    game.run()

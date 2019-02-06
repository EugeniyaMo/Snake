import pygame
import os
import sys

pygame.init()

FPS = 50
WIDTH = 800
HEIGHT = 620

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    #image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))

def generate_level(level):
    board = [[0] * width for _ in range(height)]
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                board[y][x] = 0
            elif level[y][x] == '#':
                board[y][x] = -1
            elif level[y][x] == '@':
                board[y][x] = 1
            elif level[y][x] == '-':
                board[y][x] = 2
    # вернем игрока, а также размер поля в клетках
    return board

class Board:
    # создание поля
    def __init__(self, width, height, left = 10, top = 10, cell_size = 20):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # отрисовка поля
    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(
                    screen,
                    pygame.Color("white"),
                    (self.left + x * self.cell_size,
                     self.top + y * self.cell_size,
                     self.cell_size,
                     self.cell_size),
                    1 - self.board[y][x]
                    )


class Snake(Board):
    def __init__(self, board):
        super().__init__(30, 30, 10, 10, 20)
        self.board = board
        self.list = []
        for i in range(self.width):
            for j in range(self.width):
                if self.board[j][i] == 1 or self.board[j][i] == 2:
                    self.list.append((j, i))

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == 1 or self.board[y][x] == 2:
                    pygame.draw.rect(
                        screen,
                        (236, 255, 223),
                        (self.left + x * self.cell_size,
                         self.top + y * self.cell_size,
                         self.cell_size,
                         self.cell_size)
                    )
                elif self.board[y][x] == -1:
                    pygame.draw.rect(
                        screen,
                        (124, 0, 6),
                        (self.left + x * self.cell_size,
                         self.top + y * self.cell_size,
                         self.cell_size,
                         self.cell_size)
                    )
                    pygame.draw.rect(
                        screen,
                        pygame.Color("black"),
                        (self.left + x * self.cell_size,
                         self.top + y * self.cell_size,
                         self.cell_size,
                         self.cell_size),
                        1
                    )
                    pygame.draw.line(
                        screen,
                        pygame.Color("black"),
                        (self.left + x * self.cell_size,
                         self.top + y * self.cell_size),
                        (self.left + x * self.cell_size + self.cell_size,
                         self.top + y * self.cell_size + self.cell_size),
                        2
                    )


    def move(self, direction):
        head = self.list[len(self.list) - 1]
        if direction == 2:
            self.list.append((head[0], (head[1] + 1) % self.width))
            self.board[head[0]][(head[1] + 1) % self.width] = 1
        elif direction == 1:
            if head[0] > 0:
                self.list.append((head[0] - 1, head[1]))
                self.board[head[0] - 1][head[1]] = 1
            else:
                self.list.append((head[0] - 1 + self.height, head[1]))
                self.board[head[0] - 1 + self.height][head[1]] = 1
        elif direction == 4:
            if head[1] > 0:
                self.list.append((head[0], head[1] - 1))
                self.board[head[0]][head[1] - 1] = 1
            else:
                self.list.append((head[0], head[1] - 1 + self.width))
                self.board[head[0]][head[1] - 1 + self.width] = 1
        elif direction == 3:
            self.list.append(((head[0] + 1) % self.height, head[1]))
            self.board[(head[0] + 1) % self.height][head[1]] = 1
        self.board[self.list[0][0]][self.list[0][1]] = 0
        del self.list[0]

def terminate():
    pygame.quit()
    sys.exit()

def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    size = (420, 84)
    name = load_image('name.png')
    screen.blit(name, ((WIDTH - size[0]) / 2, 50))
    button_size = (201, 65)
    button_play = load_image('button_play.png')
    screen.blit(button_play, ((WIDTH - button_size[0]) / 2, 220))
    button_rules = load_image('button_rules.png')
    screen.blit(button_rules, ((WIDTH - button_size[0]) / 2, 320))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    (WIDTH - button_size[0]) / 2 <= event.pos[0] <= \
                    (WIDTH - button_size[0]) / 2 + button_size[0] and \
                    220 <= event.pos[1] <= 320:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

def draw():
    pygame.draw.line(screen, pygame.Color('white'), (620, 0), (620, 620), 2)
    button_exit = load_image('button_exit.png')
    button_exit = pygame.transform.scale(button_exit, (85, 35))
    screen.blit(button_exit, (700, 15))


start_screen()
print('ok')
width, height = 30, 30
fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
screen.blit(fon, (0, 0))
fps = 5
snake = Snake(generate_level(load_level("level1.txt")))
direction = 2
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            old_direction = direction
            if event.key == pygame.K_LEFT:
                if direction != 2:
                    direction = 4
            if event.key == pygame.K_RIGHT:
                if direction != 4:
                    direction = 2
            if event.key == pygame.K_UP:
                if direction != 3:
                    direction = 1
            if event.key == pygame.K_DOWN:
                if direction != 1:
                    direction = 3
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 700 <= event.pos[0] <= 785 and 15 <= event.pos[1] <= 50:
                start_screen()
                snake = Snake(generate_level(load_level("level1.txt")))
    screen.blit(fon, (0, 0))
    draw()
    snake.move(direction)
    snake.render()
    pygame.display.flip()
    clock.tick(fps)

terminate()

import pygame
import os
import sys
import random

pygame.init()

FPS = 50
WIDTH = 850
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    # image = image.convert_alpha()

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
    def __init__(self, width, height, left=10, top=10, cell_size=20):
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
        self.score = 0
        self.apple = 0

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
                    pygame.draw.rect(
                        screen,
                        pygame.Color('black'),
                        (self.left + x * self.cell_size,
                         self.top + y * self.cell_size,
                         self.cell_size,
                         self.cell_size),
                        1
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
                elif 3 <= self.board[y][x] <= 5:
                    pygame.draw.circle(
                        screen,
                        pygame.Color("black"),
                        (self.left + x * self.cell_size + self.cell_size // 2,
                         self.top + y * self.cell_size + self.cell_size // 2),
                        self.cell_size // 2,
                        1
                    )
                    if self.board[y][x] == 3:
                        pygame.draw.circle(
                            screen,
                            (255, 45, 71),
                            (self.left + x * self.cell_size + self.cell_size // 2,
                             self.top + y * self.cell_size + self.cell_size // 2),
                            self.cell_size // 2
                        )
                    elif self.board[y][x] == 4:
                        pygame.draw.circle(
                            screen,
                            (255, 111, 139),
                            (self.left + x * self.cell_size + self.cell_size // 2,
                             self.top + y * self.cell_size + self.cell_size // 2),
                            self.cell_size // 2
                        )
                    elif self.board[y][x] == 5:
                        pygame.draw.circle(
                            screen,
                            (255, 147, 5),
                            (self.left + x * self.cell_size + self.cell_size // 2,
                             self.top + y * self.cell_size + self.cell_size // 2),
                            self.cell_size // 2
                        )

    def move(self, direction):
        head = self.list[len(self.list) - 1]
        add = False
        if direction == 2:
            if self.check_wall((head[0], (head[1] + 1) % self.width)):
                game_over()
                return False, self.score
            if self.check_food((head[0], (head[1] + 1) % self.width)):
                add = True
                point = self.board[head[0]][(head[1] + 1) % self.width]
            self.list.append((head[0], (head[1] + 1) % self.width))
            self.board[head[0]][(head[1] + 1) % self.width] = 1
        elif direction == 1:
            if head[0] > 0:
                if self.check_wall((head[0] - 1, head[1])):
                    game_over()
                    return False, self.score
                if self.check_food((head[0] - 1, head[1])):
                    add = True
                    point = self.board[head[0] - 1][head[1]]
                self.list.append((head[0] - 1, head[1]))
                self.board[head[0] - 1][head[1]] = 1
            else:
                if self.check_wall((head[0] - 1 + self.height, head[1])):
                    game_over()
                    return False, self.score
                if self.check_food((head[0] - 1 + self.height, head[1])):
                    add = True
                    point = self.board[head[0] - 1 + self.height][head[1]]
                self.list.append((head[0] - 1 + self.height, head[1]))
                self.board[head[0] - 1 + self.height][head[1]] = 1
        elif direction == 4:
            if head[1] > 0:
                if self.check_wall((head[0], head[1] - 1)):
                    game_over()
                    return False, self.score
                if self.check_food((head[0], head[1] - 1)):
                    add = True
                    point = self.board[head[0]][head[1] - 1]
                self.list.append((head[0], head[1] - 1))
                self.board[head[0]][head[1] - 1] = 1
            else:
                if self.check_wall((head[0], head[1] - 1 + self.width)):
                    game_over()
                    return False, self.score
                if self.check_food((head[0], head[1] - 1 + self.width)):
                    add = True
                    point = self.board[head[0]][head[1] - 1 + self.width]
                self.list.append((head[0], head[1] - 1 + self.width))
                self.board[head[0]][head[1] - 1 + self.width] = 1
        elif direction == 3:
            if self.check_wall(((head[0] + 1) % self.height, head[1])):
                game_over()
                return False, self.score
            if self.check_food(((head[0] + 1) % self.height, head[1])):
                add = True
                point = self.board[(head[0] + 1) % self.height][head[1]]
            self.list.append(((head[0] + 1) % self.height, head[1]))
            self.board[(head[0] + 1) % self.height][head[1]] = 1
        if not add:
            self.board[self.list[0][0]][self.list[0][1]] = 0
            del self.list[0]
        else:
            if point == 3:
                self.score += 10
            elif point == 4:
                self.score += 15
            elif point == 5:
                self.score += 20
            self.add_food()
        return True, self.score

    def check_wall(self, cell_coords):
        if self.board[cell_coords[0]][cell_coords[1]] == -1 or \
                self.board[cell_coords[0]][cell_coords[1]] == 1:
            return True
        return False

    def check_food(self, cell_coords):
        if 3 <= self.board[cell_coords[0]][cell_coords[1]] <= 5:
            return True
        return False

    def food(self):
        count = 0
        while count < 2:
            x = random.randint(1, self.width - 1)
            y = random.randint(1, self.height - 1)
            if self.board[y][x] == 0:
                self.board[y][x] = 3
                count += 1
                self.apple += 1

    def add_food(self):
        flag = True
        while flag:
            x = random.randint(1, self.width - 1)
            y = random.randint(1, self.height - 1)
            if self.board[y][x] == 0:
                self.board[y][x] = 3
                flag = False
        self.apple += 1
        if self.apple % 7 == 0:
            self.board[y][x] = 4
        if self.apple % 22 == 0:
            self.board[y][x] = 5


def terminate():
    pygame.quit()
    sys.exit()


def game_over():
    fon = pygame.transform.scale(load_image('game_over.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    button_size = (201, 65)
    button_menu = load_image('button_menu.png')
    screen.blit(button_menu, ((WIDTH - button_size[0]) / 2, 450))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (WIDTH - button_size[0]) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0]) / 2 + button_size[0] and \
                        450 <= event.pos[1] <= 450 + button_size[1]:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    size = (420, 84)
    name = load_image('name.png')
    screen.blit(name, ((WIDTH - size[0]) / 2, 50))
    button_size = (201, 65)
    button_play = load_image('button_play.png')
    screen.blit(button_play, ((WIDTH - button_size[0]) / 2, 210))
    button_levels = load_image('button_levels.png')
    screen.blit(button_levels, ((WIDTH - button_size[0]) / 2, 310))
    button_rules = load_image('button_rules.png')
    screen.blit(button_rules, ((WIDTH - button_size[0]) / 2, 410))
    button_exit = load_image('exit.png')
    screen.blit(button_exit, ((WIDTH - button_size[0]) / 2, 510))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (WIDTH - button_size[0]) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0]) / 2 + button_size[0] and \
                        210 <= event.pos[1] <= 210 + button_size[1]:
                    return 0  # начинаем игру
                elif (WIDTH - button_size[0]) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0]) / 2 + button_size[0] and \
                        310 <= event.pos[1] <= 310 + button_size[1]:
                    return 1
                elif (WIDTH - button_size[0]) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0]) / 2 + button_size[0] and \
                        510 <= event.pos[1] <= 510 + button_size[1]:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


def levels_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    button_size = (65, 65)
    button_level = load_image('level1.png')
    screen.blit(button_level, ((WIDTH - button_size[0] - 400) / 2, 310))
    button_level = load_image('level2.png')
    screen.blit(button_level, ((WIDTH - button_size[0] - 200) / 2, 310))
    button_level = load_image('level3.png')
    screen.blit(button_level, ((WIDTH - button_size[0]) / 2, 310))
    button_level = load_image('level4.png')
    screen.blit(button_level, ((WIDTH - button_size[0] + 200) / 2, 310))
    button_level = load_image('level5.png')
    screen.blit(button_level, ((WIDTH - button_size[0] + 400) / 2, 310))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (WIDTH - button_size[0] - 400) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0] - 400) / 2 + button_size[0]:
                    return 1
                elif (WIDTH - button_size[0] - 200) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0] - 200) / 2 + button_size[0]:
                    return 2
                elif (WIDTH - button_size[0]) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0]) / 2 + button_size[0]:
                    return 3
                elif (WIDTH - button_size[0] + 200) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0] + 200) / 2 + button_size[0]:
                    return 4
                elif (WIDTH - button_size[0] + 400) / 2 <= event.pos[0] <= \
                        (WIDTH - button_size[0] + 400) / 2 + button_size[0]:
                    return 5
        pygame.display.flip()
        clock.tick(FPS)


def draw():
    screen.blit(fon, (0, 0))
    pygame.draw.line(screen, pygame.Color('white'),
                     (620, 0), (620, HEIGHT - 100), 2)
    pygame.draw.line(screen, pygame.Color('white'),
                     (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)
    button_exit = load_image('button_exit.png')
    button_exit = pygame.transform.scale(button_exit, (85, 35))
    screen.blit(button_exit, (750, 15))
    button_menu = load_image('menu.png')
    button_menu = pygame.transform.scale(button_menu, (85, 35))
    screen.blit(button_menu, (750, 55))


def print_score():
    font = pygame.font.SysFont(None, 50)
    message = 'SCORE: '
    text = font.render(message, True, pygame.Color('lightgreen'))
    text_rect = text.get_rect()
    text_rect.center = (700, 150)
    screen.blit(text, text_rect)
    message = str(score)
    text = font.render(message, True, pygame.Color('lightgreen'))
    text_rect = text.get_rect()
    text_rect.center = (800, 150)
    screen.blit(text, text_rect)
    message = 'LEVEL: '
    text = font.render(message, True, pygame.Color('lightgreen'))
    text_rect = text.get_rect()
    text_rect.center = (700, 200)
    screen.blit(text, text_rect)
    message = str(level)
    text = font.render(message, True, pygame.Color('lightgreen'))
    text_rect = text.get_rect()
    text_rect.center = (800, 200)
    screen.blit(text, text_rect)


def notification():
    font = pygame.font.Font(None, 70)
    message = 'PRESS ANY KEY TO BEGIN GAME'
    text = font.render(message, True, (255, 119, 89))
    text_rect = text.get_rect()
    text_rect.center = (WIDTH / 2, HEIGHT - 50)
    screen.blit(text, text_rect)


cycle = True
level = 1
while cycle:
    pygame.display.set_caption('SNAKE')
    number = start_screen()
    if number == 1:
        level = levels_screen()
    running = True
    width, height = 30, 30
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    fps = 10
    snake = Snake(generate_level(load_level("level" + str(level) + ".txt")))
    snake.food()
    direction = 2
    score = 0
    running = True
    pointer = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                cycle = False
            if event.type == pygame.KEYDOWN:
                if pointer:
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
                else:
                    pointer = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 750 <= event.pos[0] <= 835 and 15 <= event.pos[1] <= 50:
                    terminate()
                elif 750 <= event.pos[0] <= 835 and 55 <= event.pos[1] <= 90:
                    running = False
        draw()
        if pointer:
            game, score = snake.move(direction)
            if not game:
                running = False
            else:
                snake.render()
                print_score()
        else:
            snake.render()
            print_score()
            notification()
        pygame.display.flip()
        clock.tick(fps)

terminate()

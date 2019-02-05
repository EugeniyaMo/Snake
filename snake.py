import os
import sys
import pygame

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 50
WIDTH = 800
HEIGHT = 600
STEP = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

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

head = load_image('head2_clear.png')
head = pygame.transform.scale(head, (80, 40))
wall = load_image('wall.png')
wall = pygame.transform.scale(wall, (40, 40))
grass = load_image('grass.png')
grass = pygame.transform.scale(grass, (40, 40))
tail = load_image('tail2_clear.png')
tail = pygame.transform.scale(tail, (80, 40))
body = load_image('body_clear.png')
body = pygame.transform.scale(body, (40, 40))
tile_images = {'wall': wall, 'empty':  grass}

tile_width = tile_height = 40

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, player_image):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        v = 20
        fps = 60
        self.rect.x += v * clock.tick(fps) / 100

def generate_level(level):
    new_player, x, y = [], None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player.append(Player(x, y, head))
            elif level[y][x] == '>':
                Tile('empty', x, y)
                new_player.append(Player(x, y, tail))
            elif level[y][x] == '-':
                Tile('empty', x, y)
                new_player.append(Player(x, y, body))
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


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


start_screen()
player, level_x, level_y = generate_level(load_level("level1.txt"))
direction = 2
running = True
v = 200
pos_x = level_x
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                direction = 4
                for i in player:
                    i.rect.x -= STEP
            if event.key == pygame.K_RIGHT:
                direction = 2
                for i in player:
                    i.rect.x += STEP
            if event.key == pygame.K_UP:
                direction = 1
                for i in player:
                    i.rect.y -= STEP
            if event.key == pygame.K_DOWN:
                direction = 3
                for i in player:
                    i.rect.y += STEP
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    player_group.update()
    pygame.display.flip()

    clock.tick(FPS)

terminate()
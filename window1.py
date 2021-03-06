import pygame
import os
import sys
import random
import sqlite3
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QLineEdit, QPushButton, QLCDNumber, \
    QInputDialog, QTableWidgetItem

FPS = 50
STEP = 50
size = WIDTH, HEIGHT = 450, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # прозрачный цвет
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ВТОРЖЕНИЕ", "",
                  "Выберите уровень",
                  "Легкий: нажмите вниз",
                  "Средний: нажмите вверх",
                  "Сложный: нажмите влево",
                  "Выстрел: нажмите W"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 30
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 30
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    return 1  # начинаем игру
                if event.key == pygame.K_LEFT:
                    return 3
                if event.key == pygame.K_UP:
                    return 2
        pygame.display.flip()
        clock.tick(FPS)


def close_screen(vin_ships):
    intro_text = ['Набранные очки:',
                  f'{vin_ships}',
                  'Просмотр таблицы лучших: нажмите X']
    fon = pygame.transform.scale(load_image('end.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 30
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    return 1
                else:
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('hero.png')
pule_image = load_image('pula.png')

tile_width = tile_height = 50


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class DBSample(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('результаты.ui', self)
        self.connection = sqlite3.connect("data/results.db")

        query = 'SELECT name, vin_ships FROM results'
        res = self.connection.cursor().execute(query).fetchall()
        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(2)

        self.tableWidget.setRowCount(0)
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))


class Tilewall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(wales_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self):
        if not pygame.sprite.spritecollide(self, ships_group, True):
            return 0
        else:
            return 1


class Tilegreen(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 5, tile_height * pos_y + 5)


class Ship(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(ships_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        pass


class Pule(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(pules_group, all_sprites)
        self.image = pule_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y

    def update(self):
        if not pygame.sprite.spritecollide(self, ships_group, True):
            return 0
        else:
            return 1


player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
ships_group = pygame.sprite.Group()
pules_group = pygame.sprite.Group()
wales_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tilegreen('empty', x, y)
            elif level[y][x] == '#':
                Tilewall('wall', x, y)
            elif level[y][x] == '@':
                Tilegreen('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    print(new_player)
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map.txt'))

pygame.init()
level = start_screen()

ship = False
pule = False
v = 50
vin_ships = 0
life = 3
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            ship = True
            Ship(random.choice([50, 100, 150, 200, 250, 300, 350]), 0)
            if event.key == pygame.K_RIGHT:
                if player.rect.x + STEP <= WIDTH - 80:
                    player.rect.x += STEP
            if event.key == pygame.K_LEFT:
                if player.rect.x - STEP >= 50:
                    player.rect.x -= STEP
            if event.key == pygame.K_w:
                pule = True
                Pule(player.rect.x + 15, 350)
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    wales_group.draw(screen)
    for i in wales_group:
        life -= i.update()
        if life == 0:
            running = False
    player_group.draw(screen)
    if ship:
        ships_group.draw(screen)
        ships_group.update()
    for i in ships_group:
        i.rect.y += v / FPS * level
    if pule:
        pules_group.draw(screen)
        for i in pules_group:
            vin_ships += i.update()
    for i in pules_group:
        i.rect.y -= v / FPS * level

    clock.tick(FPS)
    pygame.display.flip()
a = close_screen(vin_ships)
if a:
    pass

terminate()

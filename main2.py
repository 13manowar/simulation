# подключаем библиотеку pygame для графики и симуляции
import pygame

# генерация случайных чисел
import random

# математические функции (sin, cos, sqrt и т.д.)
import math


# -------------------------
# НАСТРОЙКИ СИМУЛЯЦИИ
# -------------------------

# ширина окна
WIDTH, HEIGHT = 900, 600

# количество частиц в начале
NUM_PARTICLES = 25

# базовая скорость атомов
BASE_SPEED = 2.0

# радиус атома (размер кружка)
RADIUS = 10


# -------------------------
# ПОЛЗУНОК СКОРОСТИ
# -------------------------

# X-координата начала ползунка
SLIDER_X = 120

# Y-координата ползунка (внизу экрана)
SLIDER_Y = HEIGHT - 30

# ширина ползунка
SLIDER_W = 520

# толщина ползунка
SLIDER_H = 10


# -------------------------
# КНОПКИ UI
# -------------------------

# ширина кнопки
BUTTON_W, BUTTON_H = 110, 36

# Y-координата кнопок (внизу)
BUTTON_Y = HEIGHT - BUTTON_H - 20

# кнопка restart справа
BUTTON_X_RESTART = WIDTH - BUTTON_W - 10

# кнопка pause левее restart
BUTTON_X_PAUSE = BUTTON_X_RESTART - BUTTON_W - 10


# -------------------------
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# -------------------------

# множитель скорости (изменяется ползунком)
speed_multiplier = 1.0

# состояние паузы
paused = False

# флаг перетаскивания ползунка
dragging_slider = False


# -------------------------
# ХИМИЧЕСКИЕ ВАЛЕНТНОСТИ
# -------------------------

# сколько связей может иметь каждый атом
VALENCE = {
    "H": 1,   # водород = 1 связь
    "O": 2    # кислород = 2 связи
}


# список всех связей между атомами
bonds = []

# счётчик связей для каждого атома
bond_count = {}

# хранение структуры воды (O → [H, H])
water_pairs = {}


# -------------------------
# ЦВЕТА АТОМОВ
# -------------------------

COLORS = {
    "H": (255, 255, 255),  # белый водород
    "O": (255, 0, 0),      # красный кислород
}


# -------------------------
# КЛАСС АТОМА
# -------------------------

class Particle:

    # создание атома
    def __init__(self, kind):

        # тип атома (H или O)
        self.kind = kind

        # случайная позиция X
        self.x = random.uniform(50, WIDTH - 50)

        # случайная позиция Y
        self.y = random.uniform(50, HEIGHT - 80)

        # случайное направление движения
        angle = random.uniform(0, 2 * math.pi)

        # скорость по X
        self.vx = math.cos(angle) * BASE_SPEED

        # скорость по Y
        self.vy = math.sin(angle) * BASE_SPEED


    # движение атома
    def move(self):

        # обновляем позицию X
        self.x += self.vx * speed_multiplier

        # обновляем позицию Y
        self.y += self.vy * speed_multiplier

        # отражение от левой границы
        if self.x <= RADIUS:
            self.x = RADIUS
            self.vx *= -1

        # отражение от правой границы
        if self.x >= WIDTH - RADIUS:
            self.x = WIDTH - RADIUS
            self.vx *= -1

        # отражение от верхней границы
        if self.y <= RADIUS:
            self.y = RADIUS
            self.vy *= -1

        # отражение от нижней границы
        if self.y >= HEIGHT - 60:
            self.y = HEIGHT - 60
            self.vy *= -1

        # нормализация скорости
        self.normalize_speed()


    # нормализация скорости (чтобы не ускорялись)
    def normalize_speed(self):

        # длина вектора скорости
        mag = math.hypot(self.vx, self.vy)

        # защита от деления на 0
        if mag == 0:
            return

        # нормализуем vx
        self.vx = self.vx / mag * BASE_SPEED

        # нормализуем vy
        self.vy = self.vy / mag * BASE_SPEED


    # отрисовка атома
    def draw(self, screen, font):

        # рисуем круг атома
        pygame.draw.circle(screen, COLORS[self.kind],
                           (int(self.x), int(self.y)), RADIUS)

        # текст метки атома
        label = font.render(self.kind, True, (0, 0, 0))

        # вывод текста рядом с атомом
        screen.blit(label, (self.x + 10, self.y + 10))


# -------------------------
# СТОЛКНОВЕНИЯ АТОМОВ
# -------------------------

def handle_collisions(particles):

    # перебор всех пар атомов
    for i in range(len(particles)):

        for j in range(i + 1, len(particles)):

            # первый атом
            p1 = particles[i]

            # второй атом
            p2 = particles[j]

            # разница по X
            dx = p2.x - p1.x

            # разница по Y
            dy = p2.y - p1.y

            # расстояние между атомами
            dist = math.hypot(dx, dy)

            # если пересекаются
            if dist < 2 * RADIUS and dist > 0:

                # нормаль по X
                nx = dx / dist

                # нормаль по Y
                ny = dy / dist

                # глубина пересечения
                overlap = 2 * RADIUS - dist

                # раздвигаем p1
                p1.x -= nx * overlap / 2
                p1.y -= ny * overlap / 2

                # раздвигаем p2
                p2.x += nx * overlap / 2
                p2.y += ny * overlap / 2

                # обмен скоростей X
                p1.vx, p2.vx = p2.vx, p1.vx

                # обмен скоростей Y
                p1.vy, p2.vy = p2.vy, p1.vy


# -------------------------
# ОБРАЗОВАНИЕ СВЯЗЕЙ
# -------------------------

def try_bonding(particles):

    # доступ к глобальным структурам
    global bonds, bond_count, water_pairs

    # перебор атомов
    for i in range(len(particles)):

        for j in range(len(particles)):

            # пропуск самого себя
            if i == j:
                continue

            # атом A
            a = particles[i]

            # атом B
            b = particles[j]

            # проверка типа (O + H)
            if a.kind == "O" and b.kind == "H":

                # проверка валентности кислорода
                if bond_count.get(i, 0) >= 2:
                    continue

                # проверка валентности водорода
                if bond_count.get(j, 0) >= 1:
                    continue

                # расстояние
                dx = b.x - a.x
                dy = b.y - a.y
                dist = math.hypot(dx, dy)

                # если рядом
                if dist < 35:

                    # связь
                    pair = (i, j)

                    # если ещё нет связи
                    if pair not in bonds:

                        # добавляем связь
                        bonds.append(pair)

                        # увеличиваем счётчики
                        bond_count[i] = bond_count.get(i, 0) + 1
                        bond_count[j] = 1

                        # сохраняем структуру воды
                        water_pairs.setdefault(i, []).append(j)


# -------------------------
# ЖЁСТКИЕ СВЯЗИ
# -------------------------

def enforce_bonds(particles):

    # длина связи
    target = 25

    # перебор связей
    for i, j in bonds:

        # защита от выхода за массив
        if i >= len(particles) or j >= len(particles):
            continue

        # атомы
        p1 = particles[i]
        p2 = particles[j]

        # разница координат
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        # расстояние
        dist = math.hypot(dx, dy)

        # защита
        if dist == 0:
            continue

        # корректировка расстояния
        diff = (dist - target) / dist

        # корректируем p1
        p1.x += dx * diff * 0.5
        p1.y += dy * diff * 0.5

        # корректируем p2
        p2.x -= dx * diff * 0.5
        p2.y -= dy * diff * 0.5


# -------------------------
# УГОЛ ВОДЫ 104.5°
# -------------------------

def enforce_water_angle(particles):

    # угол воды в радианах
    WATER_ANGLE = math.radians(104.5)

    # перебор молекул воды
    for o, hs in water_pairs.items():

        # проверка существования атомов
        if len(hs) < 2:
            continue

        # кислород
        O = particles[o]

        # два водорода
        H1 = particles[hs[0]]
        H2 = particles[hs[1]]

        # векторы
        v1 = (H1.x - O.x, H1.y - O.y)
        v2 = (H2.x - O.x, H2.y - O.y)

        # углы
        a1 = math.atan2(v1[1], v1[0])
        a2 = math.atan2(v2[1], v2[0])

        # текущий угол
        angle = abs(a2 - a1)

        # нормализация
        if angle > math.pi:
            angle = 2 * math.pi - angle

        # ошибка
        error = angle - WATER_ANGLE

        # сила коррекции
        correction = error * 0.02

        # корректировка H1
        H1.x = O.x + math.cos(a1 - correction) * 25
        H1.y = O.y + math.sin(a1 - correction) * 25

        # корректировка H2
        H2.x = O.x + math.cos(a2 + correction) * 25
        H2.y = O.y + math.sin(a2 + correction) * 25


# -------------------------
# UI
# -------------------------

def handle_slider(mx, my):

    global speed_multiplier

    if SLIDER_Y - 10 <= my <= SLIDER_Y + 20 and SLIDER_X <= mx <= SLIDER_X + SLIDER_W:

        rel = (mx - SLIDER_X) / SLIDER_W

        speed_multiplier = max(0.1, min(10.0, rel * 10))


def draw_slider(screen, font):

    pygame.draw.rect(screen, (180, 180, 180),
                     (SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H))

    knob = SLIDER_X + int((speed_multiplier / 10) * SLIDER_W)

    pygame.draw.circle(screen, (50, 50, 50),
                       (knob, SLIDER_Y + 5), 8)

    txt = font.render(f"Speed: {speed_multiplier:.2f}x", True, (0, 0, 0))

    screen.blit(txt, (20, HEIGHT - 40))


def draw_button(screen, font, x, text):

    pygame.draw.rect(screen, (200, 200, 200),
                     (x, BUTTON_Y, BUTTON_W, BUTTON_H))

    pygame.draw.rect(screen, (0, 0, 0),
                     (x, BUTTON_Y, BUTTON_W, BUTTON_H), 2)

    screen.blit(font.render(text, True, (0, 0, 0)),
                (x + 15, BUTTON_Y + 8))


# -------------------------
# RESET
# -------------------------

def reset():

    global bonds, bond_count, water_pairs

    bonds = []
    bond_count = {}
    water_pairs = {}

    return [Particle(random.choice(["H", "O"])) for _ in range(NUM_PARTICLES)]


# -------------------------
# MAIN LOOP
# -------------------------

def main():

    global paused, dragging_slider

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 14)

    particles = reset()

    running = True

    while running:

        screen.fill((230, 230, 230))

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if BUTTON_X_RESTART <= mx <= BUTTON_X_RESTART + BUTTON_W:
                    if BUTTON_Y <= my <= BUTTON_Y + BUTTON_H:
                        particles = reset()

                elif BUTTON_X_PAUSE <= mx <= BUTTON_X_PAUSE + BUTTON_W:
                    if BUTTON_Y <= my <= BUTTON_Y + BUTTON_H:
                        paused = not paused

                elif SLIDER_Y - 10 <= my <= SLIDER_Y + 20:
                    if SLIDER_X <= mx <= SLIDER_X + SLIDER_W:
                        dragging_slider = True
                        handle_slider(mx, my)

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                handle_slider(*event.pos)

        if not paused:

            for p in particles:
                p.move()

            handle_collisions(particles)
            try_bonding(particles)
            enforce_bonds(particles)
            enforce_water_angle(particles)

        for i, j in bonds:

            if i < len(particles) and j < len(particles):

                pygame.draw.line(screen, (50, 50, 50),
                                 (particles[i].x, particles[i].y),
                                 (particles[j].x, particles[j].y), 2)

        for p in particles:
            p.draw(screen, font)

        draw_slider(screen, font)

        draw_button(screen, font, BUTTON_X_PAUSE,
                    "Pause" if not paused else "Resume")

        draw_button(screen, font, BUTTON_X_RESTART, "Restart")

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
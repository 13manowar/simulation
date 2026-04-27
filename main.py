import pygame
import random
import math
import time
from collections import Counter

# -------------------
# НАСТРОЙКИ
# -------------------
WIDTH, HEIGHT = 900, 650
FPS = 60
ATOM_COUNT = 5
RADIUS = 6
BOND_LENGTH = 45

MAX_SPEED = 3.5
DAMPING = 0.999

LEGEND_HEIGHT = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 18)

# -------------------
# ЭЛЕМЕНТЫ
# -------------------
ELEMENTS = ["H","C","N","O","Na","Cl","Fe","S","Ca","Mg"]

COLORS = {
    "H": (200,200,255),
    "C": (100,255,100),
    "N": (150,150,255),
    "O": (255,100,100),
    "Na": (255,200,100),
    "Cl": (100,255,200),
    "Fe": (200,150,100),
    "S": (255,255,100),
    "Ca": (200,200,150),
    "Mg": (150,255,150),
}

# -------------------
# УТИЛИТЫ
# -------------------
def limit_speed(vx, vy):
    speed = math.hypot(vx, vy)
    if speed > MAX_SPEED:
        scale = MAX_SPEED / speed
        return vx * scale, vy * scale
    return vx, vy

# -------------------
# АТОМ
# -------------------
class Atom:
    def __init__(self, element):
        self.element = element
        self.x = random.randint(100, WIDTH-100)
        self.y = random.randint(100, HEIGHT-LEGEND_HEIGHT-50)
        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-2,2)
        self.molecule = None

    def update(self):
        self.vx *= DAMPING
        self.vy *= DAMPING
        self.vx, self.vy = limit_speed(self.vx, self.vy)

        self.x += self.vx
        self.y += self.vy

        # стены (учитываем нижнюю панель)
        if self.x <= RADIUS:
            self.x = RADIUS
            self.vx = abs(self.vx)

        elif self.x >= WIDTH - RADIUS:
            self.x = WIDTH - RADIUS
            self.vx = -abs(self.vx)

        if self.y <= RADIUS:
            self.y = RADIUS
            self.vy = abs(self.vy)

        elif self.y >= HEIGHT - LEGEND_HEIGHT - RADIUS:
            self.y = HEIGHT - LEGEND_HEIGHT - RADIUS
            self.vy = -abs(self.vy)

    def draw(self):
        pygame.draw.circle(screen, COLORS[self.element], (int(self.x), int(self.y)), RADIUS)

# -------------------
# МОЛЕКУЛА
# -------------------
class Molecule:
    def __init__(self, atoms):
        self.atoms = atoms
        self.created = time.time()
        self.lifetime = 30

        self.vx = random.uniform(-1.5,1.5)
        self.vy = random.uniform(-1.5,1.5)

        for a in atoms:
            a.molecule = self

    def center(self):
        cx = sum(a.x for a in self.atoms)/len(self.atoms)
        cy = sum(a.y for a in self.atoms)/len(self.atoms)
        return cx, cy

    def formula(self):
        counts = Counter(a.element for a in self.atoms)
        return "".join(f"{k}{v if v>1 else ''}" for k,v in sorted(counts.items()))

    def wall_collision(self):
        for a in self.atoms:
            if a.x <= RADIUS or a.x >= WIDTH - RADIUS:
                self.vx *= -1
            if a.y <= RADIUS or a.y >= HEIGHT - LEGEND_HEIGHT - RADIUS:
                self.vy *= -1

            a.x = max(RADIUS, min(WIDTH - RADIUS, a.x))
            a.y = max(RADIUS, min(HEIGHT - LEGEND_HEIGHT - RADIUS, a.y))

    def update(self):
        self.vx *= DAMPING
        self.vy *= DAMPING
        self.vx, self.vy = limit_speed(self.vx, self.vy)

        for a in self.atoms:
            a.x += self.vx
            a.y += self.vy

        self.wall_collision()

        # пружины
        for i in range(len(self.atoms)):
            for j in range(i+1, len(self.atoms)):
                a = self.atoms[i]
                b = self.atoms[j]

                dx = b.x - a.x
                dy = b.y - a.y
                dist = math.hypot(dx, dy) + 0.001

                diff = dist - BOND_LENGTH
                force = 0.02

                a.x += dx/dist * diff * force
                a.y += dy/dist * diff * force
                b.x -= dx/dist * diff * force
                b.y -= dy/dist * diff * force

        # распад
        if time.time() - self.created > self.lifetime:
            for a in self.atoms:
                a.molecule = None
                a.vx = random.uniform(-2,2)
                a.vy = random.uniform(-2,2)
            return True

        return False

    def draw(self):
        for i in range(len(self.atoms)):
            for j in range(i+1, len(self.atoms)):
                pygame.draw.line(
                    screen,
                    (220,220,220),
                    (self.atoms[i].x, self.atoms[i].y),
                    (self.atoms[j].x, self.atoms[j].y),
                    2
                )

        for a in self.atoms:
            a.draw()

        cx, cy = self.center()
        txt = font.render(self.formula(), True, (255,255,255))
        screen.blit(txt, (cx, cy))

# -------------------
# СТОЛКНОВЕНИЯ
# -------------------
def collide(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)

    if dist == 0 or dist > 2*RADIUS:
        return

    nx = dx / dist
    ny = dy / dist

    dvx = a.vx - b.vx
    dvy = a.vy - b.vy

    rel = dvx * nx + dvy * ny
    if rel > 0:
        return

    impulse = -1.2 * rel

    a.vx += impulse * nx
    a.vy += impulse * ny
    b.vx -= impulse * nx
    b.vy -= impulse * ny

    overlap = 2*RADIUS - dist
    a.x -= nx * overlap * 0.5
    a.y -= ny * overlap * 0.5
    b.x += nx * overlap * 0.5
    b.y += ny * overlap * 0.5

    try_bond(a, b)

# -------------------
# СВЯЗЬ
# -------------------
def try_bond(a, b):
    if a.molecule or b.molecule:
        return

    if random.random() < 0.12:
        molecules.append(Molecule([a,b]))

# -------------------
# ЛЕГЕНДА
# -------------------
def draw_legend():
    y = HEIGHT - LEGEND_HEIGHT + 20
    x = 20

    for e in ELEMENTS:
        pygame.draw.circle(screen, COLORS[e], (x, y), 6)
        txt = font.render(e, True, (255,255,255))
        screen.blit(txt, (x+10, y-8))
        x += 70

# -------------------
# СОЗДАНИЕ
# -------------------
atoms = []
for e in ELEMENTS:
    for _ in range(ATOM_COUNT):
        atoms.append(Atom(e))

molecules = []

# -------------------
# MAIN LOOP
# -------------------
running = True
while running:
    screen.fill((10,10,20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for a in atoms:
        if not a.molecule:
            a.update()

    for i in range(len(atoms)):
        for j in range(i+1, len(atoms)):
            collide(atoms[i], atoms[j])

    for m in molecules[:]:
        if m.update():
            molecules.remove(m)

    for m in molecules:
        m.draw()

    for a in atoms:
        if not a.molecule:
            a.draw()

    draw_legend()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
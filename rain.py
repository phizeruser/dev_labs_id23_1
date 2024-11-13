import json
import random
import math
import pygame

with open('file/config.json', 'r') as config_file:
    config = json.load(config_file)

width, height = 600, 600

min_drops = config['min_drops']
max_drops = config['max_drops']
min_speed = config['min_speed']
max_speed = config['max_speed']
min_angle = config['min_angle']
max_angle = config['max_angle']
min_length = config['min_length']
max_length = config['max_length']
drop_color = config['drop_color']
background_color = config['background_color']


class Drop:
    def __init__(self):
        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)
        self.speed = random.uniform(min_speed, max_speed)
        self.angle = random.uniform(min_angle, max_angle)
        self.length = random.uniform(min_length, max_length)

    def update(self, dt):
        rad_angle = math.radians(self.angle)
        self.y += self.speed * dt * math.cos(rad_angle)
        self.x += self.speed * dt * math.sin(rad_angle)

        if self.y > height:
            self.y = 0
            self.x = random.uniform(0, width)
            self.speed = random.uniform(min_speed, max_speed)
            self.angle = random.uniform(min_angle, max_angle)
            self.length = random.uniform(min_length, max_length)


num_drops = random.randint(min_drops, max_drops)
drops = [Drop() for _ in range(num_drops)]


def update_drops():
    global drops
    if random.random() < 0.05 and len(drops) < max_drops:
        drops.append(Drop())
    if random.random() < 0.05 and len(drops) > min_drops:
        drops.pop()


def simulate_rain(dt):
    update_drops()
    for drop in drops:
        drop.update(dt)


pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()


def render():
    screen.fill(background_color)
    for drop in drops:
        pygame.draw.line(screen, drop_color, (drop.x, drop.y),
                         (drop.x + drop.length * math.sin(math.radians(drop.angle)),
                          drop.y + drop.length * math.cos(math.radians(drop.angle))), 2)
    pygame.display.flip()


running = True
while running:
    dt = clock.tick(60) / 1000
    simulate_rain(dt)
    render()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

import json
import random
import math
import pygame

# Загрузка конфигурации
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

width, height = 800, 600  # Увеличим размер окна для UI

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


class Cloud:
    def __init__(self, x, y, shape='rect', width=100, height=50):
        self.x = x
        self.y = y
        self.shape = shape
        self.width = width
        self.height = height
        self.drops = []
        self.density = 0.1
        self.speed_multiplier = 1.0

    def generate_drop(self):
        if self.shape == 'rect':
            x = random.uniform(self.x, self.x + self.width)
            y = self.y + self.height
        elif self.shape == 'oval':
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, 1)
            x = self.x + self.width / 2 + r * self.width / 2 * math.cos(angle)
            y = self.y + self.height / 2 + r * self.height / 2 * math.sin(angle)
        elif self.shape == 'winnie':
            # Упрощенная форма Винни-Пуха (круг с ушками)
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, 1)
            x = self.x + self.width / 2 + r * self.width / 2 * math.cos(angle)
            y = self.y + self.height / 2 + r * self.height / 2 * math.sin(angle)
            # Добавляем "ушки"
            if random.random() < 0.2:
                x += random.uniform(-self.width / 4, self.width / 4)
                y -= self.height / 4

        return Drop(x, y, self.speed_multiplier)

    def update(self, dt):
        # Генерируем новые капли в зависимости от плотности
        if random.random() < self.density:
            self.drops.append(self.generate_drop())

        # Обновляем существующие капли
        for drop in self.drops:
            drop.update(dt)

        # Удаляем капли, вышедшие за пределы экрана
        self.drops = [drop for drop in self.drops if drop.y < height]

    def draw(self, screen):
        if self.shape == 'rect':
            pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))
        elif self.shape == 'oval':
            pygame.draw.ellipse(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))
        elif self.shape == 'winnie':
            # Рисуем основное "тело"
            pygame.draw.ellipse(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))
            # Рисуем "ушки"
            ear_size = self.width // 4
            pygame.draw.ellipse(screen, (200, 200, 200),
                                (self.x - ear_size // 2, self.y - ear_size // 2, ear_size, ear_size))
            pygame.draw.ellipse(screen, (200, 200, 200),
                                (self.x + self.width - ear_size // 2, self.y - ear_size // 2, ear_size, ear_size))

        for drop in self.drops:
            drop.draw(screen)


class Drop:
    def __init__(self, x, y, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.speed = random.uniform(min_speed, max_speed) * speed_multiplier
        self.angle = random.uniform(min_angle, max_angle)
        self.length = random.uniform(min_length, max_length)

    def update(self, dt):
        rad_angle = math.radians(self.angle)
        self.y += self.speed * dt * math.cos(rad_angle)
        self.x += self.speed * dt * math.sin(rad_angle)

    def draw(self, screen):
        pygame.draw.line(screen, drop_color, (self.x, self.y),
                         (self.x + self.length * math.sin(math.radians(self.angle)),
                          self.y + self.length * math.cos(math.radians(self.angle))), 2)


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 30)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

clouds = []
selected_cloud = None

add_cloud_button = Button(10, 10, 150, 40, "Add Cloud", (0, 255, 0))
shape_button = Button(170, 10, 150, 40, "Change Shape", (255, 255, 0))
increase_density_button = Button(330, 10, 150, 40, "Increase Density", (0, 255, 255))
decrease_density_button = Button(490, 10, 150, 40, "Decrease Density", (255, 0, 255))
increase_speed_button = Button(650, 10, 150, 40, "Increase Speed", (255, 128, 0))
decrease_speed_button = Button(10, 60, 150, 40, "Decrease Speed", (128, 255, 0))


def handle_events():
    global selected_cloud
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if add_cloud_button.is_clicked(pos):
                clouds.append(Cloud(random.randint(0, width - 100), random.randint(100, height // 2)))
            elif shape_button.is_clicked(pos) and selected_cloud:
                shapes = ['rect', 'oval', 'winnie']
                selected_cloud.shape = shapes[(shapes.index(selected_cloud.shape) + 1) % len(shapes)]
            elif increase_density_button.is_clicked(pos) and selected_cloud:
                selected_cloud.density = min(1.0, selected_cloud.density + 0.1)
            elif decrease_density_button.is_clicked(pos) and selected_cloud:
                selected_cloud.density = max(0.0, selected_cloud.density - 0.1)
            elif increase_speed_button.is_clicked(pos) and selected_cloud:
                selected_cloud.speed_multiplier *= 1.2
            elif decrease_speed_button.is_clicked(pos) and selected_cloud:
                selected_cloud.speed_multiplier /= 1.2
            else:
                selected_cloud = None
                for cloud in clouds:
                    if cloud.x <= pos[0] <= cloud.x + cloud.width and cloud.y <= pos[1] <= cloud.y + cloud.height:
                        selected_cloud = cloud
                        break
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] and selected_cloud:  # Left mouse button
                selected_cloud.x += event.rel[0]
                selected_cloud.y += event.rel[1]
    return True


def update(dt):
    for cloud in clouds:
        cloud.update(dt)


def render():
    screen.fill(background_color)
    for cloud in clouds:
        cloud.draw(screen)
    add_cloud_button.draw(screen)
    shape_button.draw(screen)
    increase_density_button.draw(screen)
    decrease_density_button.draw(screen)
    increase_speed_button.draw(screen)
    decrease_speed_button.draw(screen)
    if selected_cloud:
        pygame.draw.rect(screen, (255, 0, 0),
                         (selected_cloud.x, selected_cloud.y, selected_cloud.width, selected_cloud.height), 2)
    pygame.display.flip()


running = True
while running:
    dt = clock.tick(60) / 1000
    running = handle_events()
    update(dt)
    render()

pygame.quit()
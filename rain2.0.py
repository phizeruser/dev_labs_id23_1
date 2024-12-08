import json
import random
import math
import pygame as pg
import time


def load_settings(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


config = load_settings('config.json')

SCREEN_SIZE = (800, 600)
DROP_PARAMS = {k: config[k] for k in
               ['min_drops', 'max_drops', 'min_speed', 'max_speed', 'min_angle', 'max_angle', 'min_length',
                'max_length']}
COLORS = {'drop': config['drop_color'], 'bg': config['background_color']}


class RainCloud:
    def __init__(self, position, dimensions, form='rectangle'):
        self.pos = list(position)
        self.size = dimensions
        self.form = form
        self.raindrops = []
        self.rain_intensity = 0.1
        self.velocity_factor = 1.0

    def create_raindrop(self):
        if self.form == 'rectangle':
            x = random.uniform(self.pos[0], self.pos[0] + self.size[0])
            y = self.pos[1] + self.size[1]
        elif self.form == 'ellipse':
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, 1)
            x = self.pos[0] + self.size[0] / 2 + r * self.size[0] / 2 * math.cos(angle)
            y = self.pos[1] + self.size[1] / 2 + r * self.size[1] / 2 * math.sin(angle)
        else:  # 'custom'
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, 1)
            x = self.pos[0] + self.size[0] / 2 + r * self.size[0] / 2 * math.cos(angle)
            y = self.pos[1] + self.size[1] / 2 + r * self.size[1] / 2 * math.sin(angle)
            if random.random() < 0.2:
                x += random.uniform(-self.size[0] / 4, self.size[0] / 4)
                y -= self.size[1] / 4

        return Raindrop(x, y, self.velocity_factor)

    def update(self, delta_time):
        if random.random() < self.rain_intensity:
            self.raindrops.append(self.create_raindrop())

        for drop in self.raindrops:
            drop.update(delta_time)

        self.raindrops = [drop for drop in self.raindrops if drop.pos[1] < SCREEN_SIZE[1]]

    def render(self, surface):
        if self.form == 'rectangle':
            pg.draw.rect(surface, (200, 200, 200), (*self.pos, *self.size))
        elif self.form == 'ellipse':
            pg.draw.ellipse(surface, (200, 200, 200), (*self.pos, *self.size))
        else:  # 'custom'
            pg.draw.ellipse(surface, (200, 200, 200), (*self.pos, *self.size))
            ear_size = self.size[0] // 4
            pg.draw.ellipse(surface, (200, 200, 200),
                            (self.pos[0] - ear_size // 2, self.pos[1] - ear_size // 2, ear_size, ear_size))
            pg.draw.ellipse(surface, (200, 200, 200),
                            (self.pos[0] + self.size[0] - ear_size // 2, self.pos[1] - ear_size // 2, ear_size,
                             ear_size))

        for drop in self.raindrops:
            drop.render(surface)


class Raindrop:
    def __init__(self, x, y, speed_factor=1.0):
        self.pos = [x, y]
        self.velocity = random.uniform(DROP_PARAMS['min_speed'], DROP_PARAMS['max_speed']) * speed_factor
        self.angle = random.uniform(DROP_PARAMS['min_angle'], DROP_PARAMS['max_angle'])
        self.length = random.uniform(DROP_PARAMS['min_length'], DROP_PARAMS['max_length'])

    def update(self, delta_time):
        rad_angle = math.radians(self.angle)
        self.pos[1] += self.velocity * delta_time * math.cos(rad_angle)
        self.pos[0] += self.velocity * delta_time * math.sin(rad_angle)

    def render(self, surface):
        end_pos = (self.pos[0] + self.length * math.sin(math.radians(self.angle)),
                   self.pos[1] + self.length * math.cos(math.radians(self.angle)))
        pg.draw.line(surface, COLORS['drop'], self.pos, end_pos, 2)


class UIElement:
    def __init__(self, rect, text, color):
        self.rect = pg.Rect(rect)
        self.text = text
        self.color = color

    def render(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        font = pg.font.Font(None, 30)
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def main():
    pg.init()
    screen = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()

    clouds = []
    active_cloud = None

    ui_elements = [
        UIElement((10, 10, 150, 40), "Add Cloud", (0, 255, 0)),
        UIElement((170, 10, 150, 40), "Change Shape", (255, 255, 0)),
        UIElement((330, 10, 150, 40), "More Rain", (0, 255, 255)),
        UIElement((490, 10, 150, 40), "Less Rain", (255, 0, 255)),
        UIElement((650, 10, 150, 40), "Speed Up", (255, 128, 0)),
        UIElement((10, 60, 150, 40), "Slow Down", (128, 255, 0)),
        UIElement((170, 60, 150, 40), "Pause", (255, 165, 0)),
        UIElement((330, 60, 150, 40), "Delete Cloud", (255, 0, 0))
    ]

    paused = False
    last_click_time = 0
    last_click_pos = None
    double_click_interval = 0.5  # 500 milliseconds

    running = True
    while running:
        delta_time = clock.tick(60) / 1000

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    current_time = time.time()
                    mouse_pos = pg.mouse.get_pos()

                    if (current_time - last_click_time < double_click_interval and
                            last_click_pos == mouse_pos):
                        # Double click detected
                        for cloud in clouds[:]:
                            if pg.Rect(*cloud.pos, *cloud.size).collidepoint(mouse_pos):
                                clouds.remove(cloud)
                                if cloud == active_cloud:
                                    active_cloud = None
                                break

                    last_click_time = current_time
                    last_click_pos = mouse_pos

                for idx, element in enumerate(ui_elements):
                    if element.is_clicked(mouse_pos):
                        if idx == 0:
                            clouds.append(RainCloud(
                                (random.randint(0, SCREEN_SIZE[0] - 100), random.randint(100, SCREEN_SIZE[1] // 2)),
                                (100, 50)))
                        elif idx == 1 and active_cloud:
                            forms = ['rectangle', 'ellipse', 'custom']
                            active_cloud.form = forms[(forms.index(active_cloud.form) + 1) % len(forms)]
                        elif idx == 2 and active_cloud:
                            active_cloud.rain_intensity = min(1.0, active_cloud.rain_intensity + 0.1)
                        elif idx == 3 and active_cloud:
                            active_cloud.rain_intensity = max(0.0, active_cloud.rain_intensity - 0.1)
                        elif idx == 4 and active_cloud:
                            active_cloud.velocity_factor *= 1.2
                        elif idx == 5 and active_cloud:
                            active_cloud.velocity_factor /= 1.2
                        elif idx == 6:
                            paused = not paused
                            ui_elements[6].text = "Resume" if paused else "Pause"
                        elif idx == 7 and active_cloud:
                            clouds.remove(active_cloud)
                            active_cloud = None
                        break
                else:
                    active_cloud = next(
                        (cloud for cloud in clouds if pg.Rect(*cloud.pos, *cloud.size).collidepoint(mouse_pos)), None)

            elif event.type == pg.MOUSEMOTION:
                if event.buttons[0] and active_cloud:
                    active_cloud.pos[0] += event.rel[0]
                    active_cloud.pos[1] += event.rel[1]

        if not paused:
            for cloud in clouds:
                cloud.update(delta_time)

        screen.fill(COLORS['bg'])
        for cloud in clouds:
            cloud.render(screen)
        for element in ui_elements:
            element.render(screen)
        if active_cloud:
            pg.draw.rect(screen, (255, 0, 0), (*active_cloud.pos, *active_cloud.size), 2)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
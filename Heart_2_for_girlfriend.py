import random
from math import sin, cos, pi, log
from tkinter import *

HEART_HEIGHT = 640
HEART_WIDTH = 980

CENTER_X_COORD = HEART_WIDTH / 2
CENTER_Y_COORD = HEART_HEIGHT / 2

HEART_COLOR = "#ff8a3d"      # orange principal
HEART_ENLARGE_RATIO = 11

def heart_function(t, shrink_ratio: float = HEART_ENLARGE_RATIO):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
    x *= shrink_ratio
    y *= shrink_ratio
    x += CENTER_X_COORD
    y += CENTER_Y_COORD
    return int(x), int(y)

def scatter_inside(x, y, beta=0.15):
    ratio_x = -beta * log(random.random())
    ratio_y = -beta * log(random.random())
    dx = ratio_x * (x - CENTER_X_COORD)
    dy = ratio_y * (y - CENTER_Y_COORD)
    return x - dx, y - dy

def shrink(x, y, ratio):
    force = -1 / (((x - CENTER_X_COORD) ** 2 + (y - CENTER_Y_COORD) ** 2) ** 0.6)
    dx = ratio * force * (x - CENTER_X_COORD)
    dy = ratio * force * (y - CENTER_Y_COORD)
    return x - dx, y - dy

def curve(p):
    return 2 * (3 * sin(4 * p)) / (2 * pi)

def lerp_color(c1, c2, t):
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

class Heart:
    def __init__(self, generate_frame=20):
        self._points = set()
        self._edge_diffusion_points = set()
        self._center_diffusion_points = set()
        self._bg_particles = []
        self.all_points = {}
        self.build(2200)
        self.random_halo = 1000
        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)
        for _ in range(120):
            x = random.randint(0, HEART_WIDTH)
            y = random.randint(0, HEART_HEIGHT)
            self._bg_particles.append((x, y, random.randint(1, 2)))

    def build(self, number):
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))
        point_list = list(self._points)
        for _ in range(4500):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CENTER_X_COORD) ** 2 + (y - CENTER_Y_COORD) ** 2) ** 0.520)
        dx = ratio * force * (x - CENTER_X_COORD) + random.randint(-1, 1)
        dy = ratio * force * (y - CENTER_Y_COORD) + random.randint(-1, 1)
        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(2800 + 4200 * abs(curve(generate_frame / 10 * pi) ** 2))
        all_points = []
        heart_halo_point = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=11.7)
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                heart_halo_point.add((x, y))
                x += random.randint(-10, 10)
                y += random.randint(-10, 10)
                size = random.choice((1, 1, 2))
                all_points.append((x, y, size, 0))
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size, 1))
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size, 2))
        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size, 3))
        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        pts = self.all_points[render_frame % self.generate_frame]
        pulse = (sin(render_frame * 0.4) + 1) / 2
        base_color = lerp_color("#b54711", HEART_COLOR, pulse)
        halo_color = lerp_color("#ffe0c2", "#ff9d50", pulse)
        for x, y, size, kind in pts:
            if kind == 0:
                render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=halo_color)
            elif kind == 1:
                render_canvas.create_rectangle(x, y, x + size + 1, y + size + 1, width=0, fill=base_color)
            elif kind == 2:
                render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=lerp_color(base_color, "#ffd7b0", 0.3))
            else:
                render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=lerp_color(base_color, "#ffffff", 0.1))
        for i, (bx, by, bs) in enumerate(self._bg_particles):
            tw = (sin(render_frame * 0.3 + i) + 1) / 2
            c = lerp_color("#251000", "#ff9d50", tw * 0.25)
            render_canvas.create_oval(bx, by, bx + bs, by + bs, width=0, fill=c)

def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(120, draw, main, render_canvas, render_heart, render_frame + 1)

def main():
    root = Tk()
    root.title('Heart for Girlfriend, again...')
    canvas = Canvas(root, bg='black', height=HEART_HEIGHT, width=HEART_WIDTH, highlightthickness=0)
    canvas.pack()
    heart = Heart()
    draw(root, canvas, heart)
    root.mainloop()

main()

import random
from math import sin, cos, pi, log
from tkinter import *

HEART_HEIGHT = 640
HEART_WIDTH = 980

CENTER_X_COORD = HEART_WIDTH / 2
CENTER_Y_COORD = HEART_HEIGHT / 2

HEART_COLOR = "#e77c8e" 

HEART_ENLARGE_RATIO = 11 

"""
Creates the heart shape

:param t: parameter for shape calculation
:param shrink_ratio: enlarge ratio
:return: x and y coordinates 
"""
def heart_function(t, shrink_ratio: float = HEART_ENLARGE_RATIO):
    # Basic Calculation
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) -5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # Enlarge
    x *= shrink_ratio
    y *= shrink_ratio

    # Shift to center
    x += CENTER_X_COORD
    y += CENTER_Y_COORD

    return int(x), int(y)


"""
Randomly scatters the small dots within the circumference of the shape

:param x: x-coordinate
:param y: y-coordinate
:param beta: tensile strength
:return: new x,y coordinates
"""
def scatter_inside(x, y, beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CENTER_X_COORD)
    dy = ratio_y * (y - CENTER_Y_COORD)

    return x - dx, y - dy


"""
Jitters the particles

:param x: x-coordinate
:param y: y-coordinate
:param ratio: ratio
:return: new x,y coordinates
"""
def shrink(x, y, ratio):
    force = -1 / (((x - CENTER_X_COORD) ** 2 + (y - CENTER_Y_COORD) ** 2) ** 0.6)

    dx = ratio * force * (x - CENTER_X_COORD)
    dy = ratio * force * (y - CENTER_Y_COORD)

    return x - dx, y - dy

"""
Customize the curve function and adjust the beating period
"""
def curve(p):
    return 2 * (3 * sin(4 * p)) / (2 * pi)



class Heart: 
    
    def __init__(self, generate_frame=20):
        self._points = set()  # Original Coordinate Location
        self._edge_diffusion_points = set()  # Edge Diffusion Effect Coordinate
        self._center_diffusion_points = set()  # Center Diffusion Effect Coordinate
        self.all_points = {}  # Coordinates per frame
        self.build(2000)
 
        self.random_halo = 1000
 
        self.generate_frame = generate_frame

        for frame in range(generate_frame):
            self.calc(frame)
    

    def build(self, number):
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  
            x, y = heart_function(t)
            self._points.add((x, y))
 
        # Spread inner particles
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))
 
        # Spread inner particles again
        point_list = list(self._points)

        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))
    

    @staticmethod
    def calc_position(x, y, ratio):
        # Adjust enlarge/shrink ratio
        force = 1 / (((x - CENTER_X_COORD) ** 2 + (y - CENTER_Y_COORD) ** 2) ** 0.520)  
 
        dx = ratio * force * (x - CENTER_X_COORD) + random.randint(-1, 1)
        dy = ratio * force * (y - CENTER_Y_COORD) + random.randint(-1, 1)
 
        return x - dx, y - dy
    

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)  # Periodic Scaling
 
        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))
 
        all_points = []

        # Halo
        heart_halo_point = set()  # Point Coordinates

        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # 
            x, y = heart_function(t, shrink_ratio=11.6)  
            x, y = shrink(x, y, halo_radius)

            if (x, y) not in heart_halo_point:
                # Handle New Points
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))
 
        # Contour
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))
 
        # Content (Particles)
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
 
        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
 
        self.all_points[generate_frame] = all_points
    

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()  
    root.title('H.E.A.R.T')
    canvas = Canvas(root, bg='black', height=HEART_HEIGHT, width=HEART_WIDTH)
    canvas.pack()
    heart = Heart()  
    draw(root, canvas, heart)  # Draws the Heart
    root.mainloop()
import pygame as pg
from math import floor
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon as pol


def get_code(x, y):
    return [x < border.x1, y < border.y1, x > border.x2, y > border.y2]


def rotate(A, B, C):
    return (B[0] - A[0]) * (C[1] - B[1]) - (B[1] - A[1]) * (C[0] - B[0])


def jarvismarch(A):
    n = len(A)
    P = list(range(n))
    # start point
    for i in range(1, n):
        if A[P[i]][0] < A[P[0]][0]:
            P[i], P[0] = P[0], P[i]
    H = [P[0]]
    del P[0]
    P.append(H[0])
    while True:
        right = 0
        for i in range(1, len(P)):
            if rotate(A[H[-1]], A[P[right]], A[P[i]]) < 0:
                right = i
        if P[right] == H[0]:
            break
        else:
            H.append(P[right])
            del P[right]
    return H


def checkCode(x, y):
    code = get_code(x, y)
    for i in range(4):
        if code[i]:
            return False
    return True


def get_border(x, y):
    if x == border.x1:
        return 1
    if x == border.x2:
        return 2
    if y == border.y1:
        return 3
    if y == border.y2:
        return 4
    return -1


def remove_duplicates(lst):
    counts = {}
    for item in reversed(lst):
        counts[item] = counts.get(item, 0) + 1

    result = [item for item in lst if counts[item] == 1]

    return result


class Polygon:
    def __init__(self, points, color):
        self.points = points
        self.color = color

    def add_point(self, x, y):
        self.points.append((x, y))

    def remove_point(self):
        self.points.pop(-1)

    def draw_border(self, window):
        ans = []
        self.points.append(self.points[0])
        for i in range(len(self.points) - 1):
            a = self.points[i + 1][1] - self.points[i][1]
            b = -(self.points[i + 1][0] - self.points[i][0])
            c = - a * self.points[i][0] - b * self.points[i][1]
            fCode = get_code(self.points[i][0], self.points[i][1])
            sCode = get_code(self.points[i + 1][0], self.points[i + 1][1])
            checkAnd = False

            for j in range(4):
                checkAnd |= (fCode[j] and sCode[j])

            if checkAnd:
                continue

            check_in1 = True
            check_in2 = True

            for j in fCode:
                check_in1 &= not j

            if check_in1:
                ans.append((self.points[i][0], self.points[i][1]))

            for j in range(4):
                if fCode[j] or sCode[j]:
                    if j == 0:
                        x = border.x1
                        y = (-a * x - c) / b
                        if checkCode(x, y):
                            ans.append((x, y))
                    elif j == 1:
                        y = border.y1
                        x = (-b * y - c) / a
                        if checkCode(x, y):
                            ans.append((x, y))
                    elif j == 2:
                        x = border.x2
                        y = (-a * x - c) / b
                        if checkCode(x, y):
                            ans.append((x, y))
                    elif j == 3:
                        y = border.y2
                        x = (-b * y - c) / a
                        if checkCode(x, y):
                            ans.append((x, y))
            for j in sCode:
                check_in2 &= not j

            if check_in2:
                ans.append((self.points[i + 1][0], self.points[i + 1][1]))
        self.points.pop(-1)
        li = []
        ans.reverse()
        for i in ans:
            if i not in li:
                li.append(i)
        ans = li
        ans.reverse()
        corner1 = Point(border.x1, border.y1)
        corner2 = Point(border.x1, border.y2)
        corner3 = Point(border.x2, border.y2)
        corner4 = Point(border.x2, border.y1)
        corners = [corner1, corner2, corner3, corner4]
        p = pol(self.points)

        for corner in corners:
            if p.contains(corner):
                ans.append(corner)

        if len(ans) > 2:
            ans = [point if type(point) == tuple else (point.x, point.y) for point in ans]
            order = jarvismarch(ans)
            new_ans = []
            for j in order:
                new_ans.append(ans[j])
            pg.draw.polygon(window, self.color, new_ans)
            for point in new_ans:
                pg.draw.circle(window, point_color, point, 3)

    def draw(self, window):
        if len(self.points) > 2:
            pg.draw.polygon(window, self.color, self.points)


class Border:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def change(self, m, val):
        if val == UP:
            self.y1 = min(self.y2, self.y1 - m)
        elif val == DOWN:
            self.y2 = max(self.y1, self.y2 + m)
        elif val == LEFT:
            self.x1 = min(self.x2, self.x1 - m)
        elif val == RIGHT:
            self.x2 = max(self.x1, self.x2 + m)

    def draw(self, window):
        pg.draw.rect(window, border_color, (self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1), 1)


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, window, color):
        pg.draw.rect(window, color, (self.x, self.y, size, size))


class Circle:
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.radius = r
        self.color = color
        self.tiles = []

    def calc(self):
        self.tiles = []
        self.x = floor(self.x)
        self.y = floor(self.y)
        self.x -= self.x % size
        self.y -= self.y % size
        self.radius = floor(self.radius)
        x = self.radius // size
        y = 0
        t1 = self.radius // 16
        while x >= y:
            self.symmetric_add(x * size, y * size, self.x, self.y)
            y += 1
            t1 += y
            t2 = t1 - x
            if t2 >= 0:
                t1 = t2
                x -= 1

    def symmetric_add(self, x, y, shift_x, shift_y):
        tiles = [Tile(x, y), Tile(-x, y), Tile(x, -y), Tile(-x, -y)]

        temp_tiles = [Tile(t.y, t.x) for t in tiles]

        tiles.extend(temp_tiles)

        for i in range(8):
            tiles[i].x += shift_x
            tiles[i].y += shift_y

        self.tiles.extend(tiles)

    def draw(self, window):
        for tile in self.tiles:
            tile.draw(window, self.color)


def draw_field(window):

    for i in range(width // size):
        pg.draw.line(window, color_grid, (i * size, 0), (i * size, height))
    for i in range(height // size):
        pg.draw.line(window, color_grid, (0, i * size), (width, i * size))

    f1 = pg.font.Font(None, 25)
    text1 = f1.render('X', 1, (0, 0, 0))
    w.blit(text1, (width - 10, 1))

    text1 = f1.render('Y', 1, (0, 0, 0))
    w.blit(text1, (5, height - 15))


def restore():
    global clicked, cur_circle, cur_polygon
    clicked = False
    cur_circle = None
    cur_polygon = None


pg.init()
width = 800
height = 450
size = 5

color_grid = (0, 0, 200)
bg_color = (255, 255, 255)
predraw_color = (255, 50, 50, 50)
draw_color = (0, 0, 0)
border_color = (255, 255, 0)
point_color = (0, 255, 0)

UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

w = pg.display.set_mode((width, height))

run = True
clicked = False

try:
    t = open("input.txt", "r").read().split('\n')

    cords = list(map(float, t[0].split()))

    border = Border(cords[0], cords[1], cords[2], cords[3])

    i = 2

    circles = []
    polygons = []

    while t[i] != "":
        cords = t[i].split()
        circles.append(Circle(float(cords[0]), float(cords[1]), float(cords[2]), draw_color))
        circles[-1].calc()
        i += 1

    i += 1

    while i != len(t):
        if t[i] == "":
            break
        cords = t[i].strip().split()
        p = []
        for j in range(len(cords) // 2):
            p.append((float(cords[j * 2]), float(cords[j * 2 + 1])))
        polygons.append(Polygon(p, draw_color))
        i += 1
except Exception as e:
    print(e)
    border = Border(0, 0, 100, 100)
    circles = []
    polygons = []

mode = "c"
# mode = "b"
# mode = "p"
# mode = "d"

while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_c:
                mode = "c"
                restore()
            elif event.key == pg.K_b:
                mode = "b"
                restore()
            elif event.key == pg.K_p:
                mode = "p"
                restore()
            elif event.key == pg.K_z:
                circles = []
                polygons = []
                border = Border(0, 0, 100, 100)
        if mode == "c":
            if event.type == pg.MOUSEBUTTONDOWN:
                clicked = True
                cur_circle = Circle(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 0, predraw_color)
            if event.type == pg.MOUSEBUTTONUP and clicked:
                cur_circle.color = draw_color
                circles.append(cur_circle)
                clicked = False
        if mode == "p":
            if event.type == pg.MOUSEBUTTONDOWN and not clicked:
                clicked = True
                cur_polygon = Polygon([(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])], predraw_color)
            elif event.type == pg.MOUSEBUTTONDOWN:
                cur_polygon.add_point(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and clicked:
                    cur_polygon.color = draw_color
                    polygons.append(cur_polygon)
                    clicked = False
    if mode == "b":
        keys = pg.key.get_pressed()
        mult = 1
        if keys[pg.K_LSHIFT]:
            mult = -1
        if keys[pg.K_UP]:
            border.change(mult, UP)
        if keys[pg.K_DOWN]:
            border.change(mult, DOWN)
        if keys[pg.K_LEFT]:
            border.change(mult, LEFT)
        if keys[pg.K_RIGHT]:
            border.change(mult, RIGHT)

    draw_field(w)
    if mode == "c":
        for circle in circles:
            circle.draw(w)

    if clicked and mode == "c":
        cur_x, cur_y = pg.mouse.get_pos()
        cur_circle.radius = ((cur_circle.x - cur_x) ** 2 + (cur_circle.y - cur_y) ** 2) ** 0.5
        cur_circle.calc()
        cur_circle.draw(w)

    if clicked and mode == "p":
        cur_polygon.draw(w)
    if mode == "p":
        for polygon in polygons:
            polygon.draw(w)

    if mode == "b":
        border.draw(w)

    if mode == "b":
        for polygon in polygons:
            polygon.draw_border(w)

    pg.display.update()
    pg.time.wait(20)
    w.fill(bg_color)

try:
    file = open("input.txt", "w")

    file.write(f"{border.x1} {border.y1} {border.x2} {border.y2}\n\n")

    for circle in circles:
        file.write(f"{circle.x} {circle.y} {circle.radius}\n")
    file.write("\n")

    for polygon in polygons:
        p = polygon.points
        new_p = []

        for a in p:
            new_p.extend(a)

        new_p = list(map(str, new_p))

        file.write(" ".join(new_p) + "\n")

    file.close()
except Exception as e:
    print(e)
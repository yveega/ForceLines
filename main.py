from tkinter import *
from PIL import Image, ImageDraw, ImageTk
import math
import random
X1, Y1, Q1 = 250, 500, 100
X2, Y2, Q2 = 750, 500, -200
STEP = 10
FONT = ('Comic Sans', 14, 'bold')
R_POINT = 10
W, H = 1000, 1000
points = []
lines = []
LINES_FROM_POINT = 10
GRID_SPACE = 25

EPS = 0.0000001

buffer = dict()
tool = 'line'


def dekahex2(n):
    n = round(n)
    lc = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    return lc[(n % 256) // 16] + lc[n % 16]


def rgb(red, green, blue):
    return '#' + dekahex2(red) + dekahex2(green) + dekahex2(blue)


def end_asking(event):
    global res
    res = en.get()
    r_ask.destroy()
    return


def askquestion(title, question):
    global r_ask, en
    r_ask = Toplevel()
    r_ask.title(title)
    l_que = Label(r_ask, text=question, fg='blue', font=FONT)
    en = Entry(r_ask, width=20)
    l_que.pack(padx=20, pady=20)
    en.pack(padx=20, pady=10)
    en.bind('<Return>', end_asking)
    main.wait_window(r_ask)
    return res


def draw_line(x, y):
    x1, y1 = x, y
    while True:
        end = False
        for i in points:
            if i.distance(x1, y1) < STEP:
                end = True
                break
        for i in lines:
            if i.distance(x1, y1) < STEP / 2 and \
                    min(i.x1, i.x2) - STEP < x1 < max(i.x1, i.x2) + STEP:
                end = True
                break
        if end:
            break
        x_shift = 0
        y_shift = 0
        for i in points:
            x_plus, y_plus = i.force(x1, y1)
            x_shift += x_plus
            y_shift += y_plus
        for i in lines:
            x_plus, y_plus = i.force(x1, y1)
            x_shift += x_plus
            y_shift += y_plus
        module = math.sqrt(x_shift ** 2 + y_shift ** 2)
        if module < 0.001:
            break
        x_shift *= STEP / module
        y_shift *= STEP / module
        x2, y2 = x1 + x_shift, y1 + y_shift
        if not (0 < x2 < W and 0 < y2 < H):
            break
        draw.line([int(x1), int(y1), int(x2), int(y2)], (0, 0, 255), 2)
        x1, y1 = x2, y2
    global photo_im
    photo_im = ImageTk.PhotoImage(img)
    c.itemconfig(im, image=photo_im)


def click(event):
    global tool
    if tool == 'point':
        QPoint(event.x, event.y)
    elif tool == 'line':
        buffer['x1'], buffer['y1'] = event.x, event.y
        tool = 'line_wait'
    elif tool == 'line_wait':
        tool = 'line'
        QLine(buffer['x1'], buffer['y1'], event.x, event.y)


class QPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        draw.ellipse([x - R_POINT, y - R_POINT, x + R_POINT, y + R_POINT],
                     (random.randint(0, 7) * 32, random.randint(0, 7) * 32, random.randint(0, 7) * 32))
        global photo_im
        photo_im = ImageTk.PhotoImage(img)
        c.itemconfig(im, image=photo_im)
        self.q = int(askquestion('Ввод данных', 'Введите заряд точки'))
        points.append(self)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def force(self, x, y):
        dist = self.distance(x, y) ** 3
        return (x - self.x) * self.q / dist, (y - self.y) * self.q / dist


class QLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.line_a = y2 - y1
        self.line_b = x1 - x2
        self.line_c = -(self.line_a * x1 + self.line_b * y1)
        self.length = math.sqrt(self.line_a ** 2 + self.line_b ** 2)
        self.normal_x = self.line_a * R_POINT / self.length
        self.normal_y = self.line_b * R_POINT / self.length
        draw.line([x1, y1, x2, y2], (random.randint(0, 5) * 32, random.randint(0, 5) * 32, random.randint(0, 5) * 32), 5)
        global photo_im
        photo_im = ImageTk.PhotoImage(img)
        c.itemconfig(im, image=photo_im)
        self.q = int(askquestion('Ввод данных', 'Введите заряд линии'))
        lines.append(self)

    def distance(self, x, y):
        k = math.sqrt(self.line_a ** 2 + self.line_b ** 2)
        return abs(self.line_a * x + self.line_b * y + self.line_c) / k

    def force(self, x, y):
        module1 = math.sqrt((x - self.x1) ** 2 + (y - self.y1) ** 2)
        module2 = math.sqrt((x - self.x2) ** 2 + (y - self.y2) ** 2)
        bis_b = -((x - self.x1) / module1 + (x - self.x2) / module2)
        bis_a = (y - self.y1) / module1 + (y - self.y2) / module2
        bis_c = - (bis_a * x + bis_b * y)
        k = bis_a * self.line_b - bis_b * self.line_a
        if abs(k) < EPS:
            gx = math.sqrt((self.x1 ** 2 + self.x2 ** 2) / 2)
            gy = math.sqrt((self.y1 ** 2 + self.y2 ** 2) / 2)
        else:
            gx = -(bis_c * self.line_b - bis_b * self.line_c) / k
            gy = -(bis_a * self.line_c - bis_c * self.line_a) / k
        # draw.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], (255, 0, 0))
        # draw.line([x, y, gx, gy], (0, 255, 0))
        dist = math.sqrt((x - gx) ** 2 + (y - gy) ** 2) ** 3
        return (x - gx) * self.q / dist, (y - gy) * self.q / dist


def draw_from_plus():
    for p in points:
        if p.q <= 0:
            continue
        for i in range(LINES_FROM_POINT):
            angle = math.pi * 2 / LINES_FROM_POINT
            x = p.x + math.cos(angle * i) * (R_POINT + 1)
            y = p.y + math.sin(angle * i) * (R_POINT + 1)
            draw_line(x, y)
    for line in lines:
        if line.q <= 0:
            continue
        for i in range(LINES_FROM_POINT + 1):
            px = line.x1 - line.line_b * i / LINES_FROM_POINT
            py = line.y1 + line.line_a * i / LINES_FROM_POINT
            draw_line(px + line.normal_x, py + line.normal_y)
            draw_line(px - line.normal_x, py - line.normal_y)
        draw_line(line.x1 + line.normal_x, line.y1 + line.normal_y)
        draw_line(line.x2 - line.normal_x, line.y2 - line.normal_y)


def make_grid():
    for j in range(1, W // GRID_SPACE):
        draw.line([j * GRID_SPACE, 0, j * GRID_SPACE, H], (0, 0, 0), 0)
    for j in range(1, H // GRID_SPACE):
        draw.line([0, j * GRID_SPACE, W, j * GRID_SPACE], (0, 0, 0), 0)


img = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(img)

main = Tk()
photo_im = ImageTk.PhotoImage(img)
b_draw = Button(main, text='Draw', width=15, height=2, font=FONT,
                command=draw_from_plus)
c = Canvas(main, width=W, height=H)
c.bind('<Button-1>', click)
im = c.create_image(0, 0, image=photo_im, anchor=NW)
b_draw.pack()
c.pack()
main.mainloop()
from tkinter import *
from PIL import Image, ImageDraw, ImageTk
import math
import random
STEP = 5
FONT = ('Comic Sans', 14, 'bold')
R_POINT = 10
W, H = 1000, 1000
points = []
lines = []
LINES_FROM_POINT = 8
GRID_SPACE = 25
LINE_WIDTH = 7
ACCURACY = 20
ARR_SIZE = 15
ARR_SPACE = 150
COLOR_LINE = (0, 0, 255)

EPS = 0.0000001

buffer = dict()
tool = 'point'


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
    global r_ask, en, res
    r_ask = Toplevel(main)
    r_ask.title(title)
    l_que = Label(r_ask, text=question, fg='blue', font=FONT)
    en = Entry(r_ask, width=20)
    l_que.pack(padx=20, pady=20)
    en.pack(padx=20, pady=10)
    en.bind('<Return>', end_asking)
    main.wait_window(r_ask)
    ans = res
    del res, r_ask, en
    return ans


def update():
    global photo_im
    photo_im = ImageTk.PhotoImage(img)
    c.itemconfig(im, image=photo_im)


def draw_arrow(x1, y1, x2, y2):
    vx = x1 - x2
    vy = y1 - y2
    a = vx + vy
    b = vx - vy
    lv = math.sqrt(a * a + b * b)
    a *= ARR_SIZE / lv
    b *= ARR_SIZE / lv
    draw.line([x2, y2, x2 + b, y2 + a], COLOR_LINE, 3)
    draw.line([x2, y2, x2 + a, y2 - b], COLOR_LINE, 3)


def draw_line(x, y, minus=False):
    x1, y1 = x, y
    length = 0
    while True:
        end = False
        for i in points:
            if i.distance(x1, y1) < STEP:
                end = True
                if x1 == i.x:
                    angle = math.pi / 2
                else:
                    angle = math.atan((y1 - i.y) / (x1 - i.x))
                if x1 > i.x:
                    i.ends.append(angle % (2 * math.pi))
                else:
                    i.ends.append((angle + math.pi) % (2 * math.pi))
                break
        for i in lines:
            if i.distance(x1, y1) < LINE_WIDTH - 1 and \
                    min(i.x1, i.x2) - STEP < x1 < max(i.x1, i.x2) + STEP and \
                    min(i.y1, i.y2) - STEP < y1 < max(i.y1, i.y2) + STEP:
                end = True
                if min(i.x1, i.x2) <= x1 <= max(i.x1, i.x2):
                    c1 = i.line_a * y1 - i.line_b * x1
                    k = i.line_a * i.line_a + i.line_b * i.line_b
                    xh = -(i.line_c * i.line_a + c1 * i.line_b) / k
                    yh = (c1 * i.line_a - i.line_b * i.line_b) / k
                    l1 = math.sqrt((xh - i.x1) ** 2 + (yh - i.y1) ** 2)
                    if x1 * i.line_a + y1 * i.line_b + i.line_c < 0:
                        i.ends1.append(int(round(l1)))
                    else:
                        i.ends2.append(int(round(l1)))
                elif (x1 - i.x1) ** 2 + (y1 - i.y1) ** 2 < (x1 - i.x2) ** 2 + (y1 - i.y2) ** 2:
                    i.end_on1 = False
                else:
                    i.end_on2 = False
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
        if length > W + H:
            break
        x_shift *= STEP / module
        y_shift *= STEP / module
        if minus:
            x_shift = -x_shift
            y_shift = -y_shift
        x2, y2 = x1 + x_shift, y1 + y_shift
        if not (0 < x2 < W and 0 < y2 < H):
            break
        draw.line([int(x1), int(y1), int(x2), int(y2)], COLOR_LINE, 2)
        if length % ARR_SPACE < STEP:
            if minus:
                draw_arrow(x2, y2, x1, y1)
            else:
                draw_arrow(x1, y1, x2, y2)
        x1, y1 = x2, y2
        length += STEP


def draw_objects():
    for i in points:
        i.paint()
    for i in lines:
        i.paint()


def delete_obj(obj):
    if type(obj) == QPoint:
        del points[points.index(obj)]
    else:
        del lines[lines.index(obj)]
    clear_lines()
    w_config.destroy()


def config_obj(obj):
    obj.q = int(en_q.get())
    if type(obj) == QLine:
        obj.set_points()
    clear_lines()
    w_config.destroy()


def delete_config(obj):
    global w_config, en_q
    w_config = Toplevel(main)
    if type(obj) == QPoint:
        w_config.title('Изменить/удалить точку')
        l_q = Label(w_config, text='Заряд точки', font=FONT)
    else:
        w_config.title('Изменить/удалить отрезок')
        l_q = Label(w_config, text='Заряд отрезка', font=FONT)
    en_q = Entry(w_config, text=str(obj.q), width=20)
    b_delete = Button(w_config, text='Удалить', font=FONT, bg='red', activebackground='#ffaaaa',
                      command=lambda: delete_obj(obj))
    b_config = Button(w_config, text='Изменить', font=FONT, command=lambda: config_obj(obj))
    l_q.pack(padx=20, side=TOP)
    en_q.pack(padx=20, side=TOP)
    b_delete.pack(padx=20, side=LEFT)
    b_config.pack(padx=20, side=LEFT)
    main.wait_window(w_config)


def click(event):
    global tool
    if tool == 'point':
        QPoint(event.x, event.y)
    elif tool == 'line':
        buffer['x1'], buffer['y1'] = event.x, event.y
        buffer['color'] = (random.randint(0, 5) * 32, random.randint(0, 5) * 32, random.randint(0, 5) * 32)
        draw.ellipse([event.x - LINE_WIDTH, event.y - LINE_WIDTH, event.x + LINE_WIDTH, event.y + LINE_WIDTH], buffer['color'])
        global photo_im
        photo_im = ImageTk.PhotoImage(img)
        c.itemconfig(im, image=photo_im)
        tool = 'line_wait'
    elif tool == 'line_wait':
        tool = 'line'
        QLine(buffer['x1'], buffer['y1'], event.x, event.y, buffer['color'])
    elif tool == 'delconf':
        for p in points:
            if p.distance(event.x, event.y) <= R_POINT:
                delete_config(p)
                return
        for line in lines:
            if (line.distance(event.x, event.y) <= LINE_WIDTH and min(line.x1, line.x2) <= event.x <= max(line.x1, line.x2)
                    and min(line.y1, line.y2) <= event.y <= max(line.y1, line.y2)) or \
                    (line.x1 - event.x) ** 2 + (line.y1 - event.y) ** 2 <= LINE_WIDTH ** 2 or \
                    (line.x2 - event.x) ** 2 + (line.y2 - event.y) ** 2 <= LINE_WIDTH ** 2:
                delete_config(line)
                return


class QPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (random.randint(0, 7) * 32, random.randint(0, 7) * 32, random.randint(0, 7) * 32)
        self.paint()
        self.ends = []
        self.q = int(askquestion('Ввод данных', 'Введите заряд точки'))
        points.append(self)

    def paint(self):
        self.ends = []
        draw.ellipse([self.x - R_POINT, self.y - R_POINT, self.x + R_POINT, self.y + R_POINT], self.color)
        update()

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def start_points(self):
        if len(self.ends) < 2:
            space = 2 * math.pi / LINES_FROM_POINT
            return [(self.x + math.cos(i * space) * (R_POINT + 1), self.y + math.sin(i * space) * (R_POINT + 1))\
                    for i in range(LINES_FROM_POINT)]
        res = []
        self.ends.sort()
        space = round(2 * math.pi / LINES_FROM_POINT * 100)
        for i, angle in enumerate(self.ends):
            ang1 = round(angle * 100)
            if i < len(self.ends) - 1:
                ang2 = round(self.ends[i + 1] * 100)
            else:
                ang2 = round((self.ends[0] + 2 * math.pi) * 100)
            res += [j / 100 - (space - (ang2 - ang1) % space) / 200 for j in range(ang1 + space, ang2, space)]
        for i, ang in enumerate(res):
            res[i] = (self.x + math.cos(ang) * (R_POINT + 1), self.y + math.sin(ang) * (R_POINT + 1))
        return res

    def force(self, x, y):
        dist = self.distance(x, y) ** 3
        return (x - self.x) * self.q / dist, (y - self.y) * self.q / dist


class LinePoint:
    def __init__(self, x, y, q):
        self.x = x
        self.y = y
        self.q = q

    def force(self, x, y):
        dist = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2) ** 3
        return (x - self.x) * self.q / dist, (y - self.y) * self.q / dist


class QLine:
    def __init__(self, x1, y1, x2, y2, color):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.line_a = y2 - y1
        self.line_b = x1 - x2
        self.line_c = -(self.line_a * x1 + self.line_b * y1)
        self.length = math.sqrt(self.line_a ** 2 + self.line_b ** 2)
        self.normal_x = self.line_a * LINE_WIDTH / self.length
        self.normal_y = self.line_b * LINE_WIDTH / self.length
        self.points = []
        self.ends1 = [0, round(self.length)]
        self.ends2 = [0, round(self.length)]
        self.end_on1 = True
        self.end_on2 = True
        self.paint()
        self.q = int(askquestion('Ввод данных', 'Введите заряд линии'))
        self.set_points()
        lines.append(self)

    def set_points(self):
        sin = (self.y2 - self.y1) / self.length
        cos = (self.x2 - self.x1) / self.length
        qp = self.q / (self.length // ACCURACY + 2)
        space = self.length / (self.length // ACCURACY + 1)
        for i in range(int(self.length // ACCURACY + 2)):
            self.points.append(LinePoint(self.x1 + cos * i * space, self.y1 + sin * i * space, qp))

    def start_points(self):
        res1 = []
        res2 = []
        sin = (self.y2 - self.y1) / self.length
        cos = (self.x2 - self.x1) / self.length
        self.ends1.sort()
        self.ends2.sort()
        space = round(self.length / LINES_FROM_POINT)
        for i, point in enumerate(self.ends1[:-1]):
            if (self.ends1[i + 1] - point) % space == 0:
                move = 0
            else:
                move = (space - (self.ends1[i + 1] - point) % space) // 2
            res1 += [j - move for j in range(point + space, self.ends1[i + 1], space)]
        for i in range(len(res1)):
            res1[i] = (self.x1 + cos * res1[i] - self.normal_x, self.y1 + sin * res1[i] - self.normal_y)
        for i, point in enumerate(self.ends2[:-1]):
            if (self.ends2[i + 1] - point) % space == 0:
                move = 0
            else:
                move = (space - (self.ends2[i + 1] - point) % space) // 2
            res2 += [j - move for j in range(point + space, self.ends2[i + 1], space)]
        for i in range(len(res2)):
            res2[i] = (self.x1 + cos * res2[i] + self.normal_x, self.y1 + sin * res2[i] + self.normal_y)
        sides = [(self.x1 + self.normal_x, self.y1 + self.normal_y),
                 (self.x1 - self.normal_x, self.y1 - self.normal_y),
                 (self.x2 + self.normal_x, self.y2 + self.normal_y),
                 (self.x2 - self.normal_x, self.y2 - self.normal_y)]
        if self.end_on1:
            sides.append((self.x1 + self.normal_y, self.y1 - self.normal_x))
        if self.end_on2:
            sides.append((self.x2 - self.normal_y, self.y2 + self.normal_x))
        return res1 + res2 + sides

    def paint(self):
        self.ends1 = [0, round(self.length)]
        self.ends2 = [0, round(self.length)]
        draw.line([self.x1, self.y1, self.x2, self.y2], self.color, LINE_WIDTH)
        draw.ellipse([self.x1 - LINE_WIDTH, self.y1 - LINE_WIDTH, self.x1 + LINE_WIDTH, self.y1 + LINE_WIDTH], self.color)
        draw.ellipse([self.x2 - LINE_WIDTH, self.y2 - LINE_WIDTH, self.x2 + LINE_WIDTH, self.y2 + LINE_WIDTH], self.color)
        update()

    def distance(self, x, y):
        k = math.sqrt(self.line_a ** 2 + self.line_b ** 2)
        return abs(self.line_a * x + self.line_b * y + self.line_c) / k

    def force(self, x, y):
        fx_all = 0
        fy_all = 0
        for p in self.points:
            fx_all_plus, fy_all_plus = p.force(x, y)
            fx_all += fx_all_plus
            fy_all += fy_all_plus
        return fx_all, fy_all


def draw_from_plus():
    clear_lines()
    for p in points:
        if p.q <= 0:
            continue
        for i in p.start_points():
            draw_line(i[0], i[1])
    for line in lines:
        if line.q <= 0:
            continue
        for i in line.start_points():
            draw_line(i[0], i[1])
    for p in points:
        if p.q >= 0:
            continue
        for i in p.start_points():
            draw_line(i[0], i[1], True)
    for line in lines:
        if line.q >= 0:
            continue
        for i in line.start_points():
            draw_line(i[0], i[1], True)
    draw_objects()


def set_tool_point():
    global tool
    b_point['bg'] = 'lightblue'
    b_point['activebackground'] = 'lightblue'
    b_line['bg'] = 'gray60'
    b_line['activebackground'] = 'gray60'
    b_delete_config['bg'] = 'gray60'
    b_delete_config['activebackground'] = 'gray60'
    tool = 'point'


def set_tool_line():
    global tool
    b_line['bg'] = 'lightblue'
    b_line['activebackground'] = 'lightblue'
    b_point['bg'] = 'gray60'
    b_point['activebackground'] = 'gray60'
    b_delete_config['bg'] = 'gray60'
    b_delete_config['activebackground'] = 'gray60'
    tool = 'line'


def set_tool_delconf():
    global tool
    b_line['bg'] = 'gray60'
    b_line['activebackground'] = 'gray60'
    b_delete_config['bg'] = 'lightblue'
    b_delete_config['activebackground'] = 'lightblue'
    b_point['bg'] = 'gray60'
    b_point['activebackground'] = 'gray60'
    tool = 'delconf'


def clear_lines():
    draw.rectangle([0, 0, W, H], (255, 255, 255), (255, 255, 255))
    draw_objects()
    update()


def delete_all():
    draw.rectangle([0, 0, W, H], (255, 255, 255), (255, 255, 255))
    global tool
    if tool == 'line1':
        tool = 'line'
    global points, lines
    for i in points:
        del i
    points = []
    for i in lines:
        del i
    lines = []
    update()


def make_grid():
    draw.rectangle([0, 0, W, H], (255, 255, 255), (255, 255, 255))
    for j in range(1, W // GRID_SPACE):
        draw.line([j * GRID_SPACE, 0, j * GRID_SPACE, H], (0, 0, 0), 0)
    for j in range(1, H // GRID_SPACE):
        draw.line([0, j * GRID_SPACE, W, j * GRID_SPACE], (0, 0, 0), 0)
    draw_objects()


def set_settings():
    global LINES_FROM_POINT, ARR_SIZE, ARR_SPACE, ACCURACY, STEP
    LINES_FROM_POINT = s_lines_from.get()
    STEP = s_step.get()
    ARR_SIZE = s_arr_size.get()
    ARR_SPACE = s_arr_space.get()
    ACCURACY = 100 // s_accuracy.get()
    w_settings.destroy()


def settings():
    global w_settings, s_lines_from, s_step, s_arr_size, s_arr_space, s_accuracy
    w_settings = Toplevel(main)
    w_settings.title('Параметры рисования линий')
    l_lines_from = Label(w_settings, text='Минимальное количество линий от точки', font=FONT, fg='darkgreen')
    s_lines_from = Scale(w_settings, orient=HORIZONTAL, from_=4, to=15, resolution=1, length=300)
    s_lines_from.set(LINES_FROM_POINT)
    l_step = Label(w_settings, text='Шаг рисования линий', font=FONT, fg='darkgreen')
    s_step = Scale(w_settings, orient=HORIZONTAL, from_=1, to=10, resolution=1, length=300)
    s_step.set(STEP)
    l_arr_size = Label(w_settings, text='Размер стрелок', font=FONT, fg='darkgreen')
    s_arr_size = Scale(w_settings, orient=HORIZONTAL, from_=10, to=25, resolution=1, length=300)
    s_arr_size.set(ARR_SIZE)
    l_arr_space = Label(w_settings, text='Промежуток между стрелками', font=FONT, fg='darkgreen')
    s_arr_space = Scale(w_settings, orient=HORIZONTAL, from_=60, to=250, resolution=10, length=300)
    s_arr_space.set(ARR_SPACE)
    l_accuracy = Label(w_settings, text='Точность подсчёта силы для отрезка', font=FONT, fg='darkgreen')
    s_accuracy = Scale(w_settings, orient=HORIZONTAL, from_=3, to=50, resolution=1, length=300)
    s_accuracy.set(100 // ACCURACY)
    b_ok = Button(w_settings, text='OK', font=FONT, bg='orange', activebackground='orange', command=set_settings)
    l_lines_from.pack(padx=20)
    s_lines_from.pack(padx=20)
    l_step.pack(padx=20)
    s_step.pack(padx=20)
    l_arr_size.pack(padx=20)
    s_arr_size.pack(padx=20)
    l_arr_space.pack(padx=20)
    s_arr_space.pack(padx=20)
    l_accuracy.pack(padx=20)
    s_accuracy.pack(padx=20)
    b_ok.pack()
    main.wait_window(w_settings)


img = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(img)

main = Tk()
main.title('Force Lines')
photo_im = ImageTk.PhotoImage(img)
button_frame_top = Frame(main)
button_frame_bottom = Frame(main)
b_point = Button(button_frame_bottom, text='Точка', font=FONT, command=set_tool_point)
b_line = Button(button_frame_bottom, text='Отрезок', font=FONT, command=set_tool_line)
b_draw = Button(button_frame_top, text='НАРИСОВАТЬ', width=15, height=1, font=FONT, fg='orange', activeforeground='orange',
                command=draw_from_plus)
b_settings = Button(button_frame_bottom, text='Параметры', font=FONT, command=settings)
b_clear = Button(button_frame_top, text='Очистить', width=15, height=1, font=FONT, command=clear_lines)
b_delete_all = Button(button_frame_top, text='Удалить всё', width=15, height=1, font=FONT, command=delete_all)
b_delete_config = Button(button_frame_bottom, text='Удалить/изменить', font=FONT, command=set_tool_delconf)
c = Canvas(main, width=W, height=H)
c.bind('<Button-1>', click)
b_point['bg'] = 'lightblue'
b_point['activebackground'] = 'lightblue'
b_line['bg'] = 'gray60'
b_line['activebackground'] = 'gray60'
b_delete_config['bg'] = 'gray60'
b_delete_config['activebackground'] = 'gray60'
im = c.create_image(0, 0, image=photo_im, anchor=NW)
button_frame_top.pack()
button_frame_bottom.pack()
b_draw.pack(side=LEFT, padx=10)
b_point.pack(side=LEFT, padx=10)
b_line.pack(side=LEFT, padx=10)
b_delete_config.pack(side=LEFT, padx=10)
b_settings.pack(side=LEFT, padx=10)
b_clear.pack(side=LEFT, padx=10)
b_delete_all.pack(side=LEFT, padx=10)
c.pack()
main.mainloop()

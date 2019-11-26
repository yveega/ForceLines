from PIL import Image, ImageDraw
import math
Xa, Ya = 250, 500
Xb, Yb = 750, 500
Q = 100
STEP = 2
W, H = 1000, 1000


def force(x, y):
    module_a = math.sqrt((x - Xa) ** 2 + (y - Ya) ** 2)
    module_b = math.sqrt((x - Xb) ** 2 + (y - Yb) ** 2)
    return (x - Xa) / module_a + (x - Xb) / module_b, (y - Ya) / module_a + (y - Yb) / module_b


def draw_line(x0, y0):
    x1, y1 = x0, y0
    while True:
        x_shift, y_shift = force(x1, y1)
        module = math.sqrt(x_shift ** 2 + y_shift ** 2)
        x_shift *= STEP / module
        y_shift *= STEP / module
        x2, y2 = x1 + x_shift, y1 + y_shift
        if not (0 < x2 < W and 0 < y2 < H):
            break
        draw.line([int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))], (0, 0, 255), 2)
        x1, y1 = x2, y2


img = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(img)
draw.line([Xa, Ya, Xb, Yb], (255, 0, 0), 5)
for i in range(Xa, Xb + 1, 20):
    draw_line(i, Ya + 5)
    draw_line(i, Ya - 5)
img.show()

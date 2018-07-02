from PIL import Image, ImageDraw
import cv2

TARGET_SHAPE = [416, 416]
PICTURE_PATH = './img/000509.jpg'
GRID_NUM = [13, 26, 52]
COLOR = [100, 200, 150]
GRID_LEN = [TARGET_SHAPE[0] / g for g in GRID_NUM]

image = Image.open(PICTURE_PATH)
iw, ih = image.size
w, h = TARGET_SHAPE
scale = min(w / iw, h / ih)
nw = int(iw * scale)
nh = int(ih * scale)

image = image.resize((nw, nh), Image.BICUBIC)
new_image = Image.new('RGB', TARGET_SHAPE, (128, 128, 128))
new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))

for j in range(len(GRID_NUM)):
    new_image_cur = new_image.copy()
    for i in range(1, GRID_NUM[j]):
        draw = ImageDraw.Draw(new_image_cur)
        draw.line((GRID_LEN[j] * i, 0, GRID_LEN[j] * i, 416), COLOR[j])
        draw.line((0, GRID_LEN[j] * i, 416, GRID_LEN[j] * i), COLOR[j])
    new_image_cur.show()



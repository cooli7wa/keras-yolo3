from yolo import *
import os, time
from PIL import Image, ImageDraw, ImageFile
import math
import cv2
import numpy as np
import subprocess

ImageFile.LOAD_TRUNCATED_IMAGES = True

WAIT_AFTER_JUMP = 3000
WAIT_AFTER_PULL = 2
CAPTURE_FOLDER = '/home/cooli7wa/Desktop/tmp_image/'
CAPTURE_FILE = CAPTURE_FOLDER + 'screen.png'
IMG_PATH = '/home/cooli7wa/project/pycharm/tiaotiao/img/'
PRESS_PARAM = 1.375
CHESS_CENTER_CORRECT = 22
INVALID_BOX_DISTANCE = 20
RESTORE_NUM = 50
RESTART_GAME_POS = [600, 1700]

screen_param = {'width': 0, 'height': 0}
restore_counter = 0


def image_open(path):
    img = Image.open(path)
    return img


def get_screen_parameter():
    screen_capture_download()
    img = image_open(CAPTURE_FILE)
    shape = img.size
    screen_param['width'] = shape[0]
    screen_param['height'] = shape[1]
    print('screen parameter:', screen_param)


def screen_capture_download():
    # process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    # screenshot = process.stdout.read()
    # f = open('{}'.format(CAPTURE_FILE), 'wb')
    # f.write(screenshot)
    # f.close()

    process = subprocess.Popen('adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()
    screenshot = screenshot.replace(b'\r\n', b'\n')
    f = open('{}'.format(CAPTURE_FILE), 'wb')
    f.write(screenshot)
    f.close()
    # binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
    # return Image.open(StringIO(binary_screenshot))


def jump(distance):
    press_time = round(distance * PRESS_PARAM)
    cmd = 'adb shell input swipe {x1} {y1} {x2} {y2} {duration}'.format(
        x1=screen_param['width'] // 2,
        y1=screen_param['height'] // 2,
        x2=screen_param['width'] // 2,
        y2=screen_param['height'] // 2,
        duration=press_time
    )
    print('distance: {}, press_time: {}ms'.format(distance, press_time))
    os.popen(cmd)


def cal_center_point(box):
    x = (box[2] + box[0]) / 2
    y = (box[3] + box[1]) / 2
    return [x, y]


def is_invalid_box(chess_center, box_center):
    if box_center[1] >= chess_center[1]:
        return True
    if cal_distance(box_center, chess_center) <= INVALID_BOX_DISTANCE:
        return True
    return False


def cal_distance(point1, point2):
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]
    return math.sqrt((x ** 2) + (y ** 2))


def draw_points(image, points):
    draw = ImageDraw.Draw(image)
    for point in points:
        draw.ellipse((point[0] - 10, point[1] - 10, point[0] + 10, point[1] + 10), 'seagreen', 'skyblue')
    return image


def change_box_xy(boxes):
    for i, box in enumerate(boxes):
        boxes[i] = [box[j] for j in [1, 0, 3, 2]]


def restore_image(img_a, img):
    global restore_counter
    cv2.imwrite('{}/{}_a.jpg'.format(CAPTURE_FOLDER, restore_counter), img_a)
    cv2.imwrite('{}/{}.jpg'.format(CAPTURE_FOLDER, restore_counter), img)
    restore_counter = (restore_counter + 1) % RESTORE_NUM


def add_mismatch_image(image):
    jpg_list = list(filter(lambda i: i.rsplit('.')[1] == 'jpg', os.listdir(IMG_PATH)))
    next_number = int(sorted(jpg_list)[-1].rsplit('.')[0]) + 1
    cv2.imwrite(IMG_PATH + '%06d.jpg' % next_number, image)


def restart_game():
    jump(2000)
    time.sleep(8)
    os.popen('adb shell input tap {} {}'.format(RESTART_GAME_POS[0], RESTART_GAME_POS[1]))
    time.sleep(2)


def main_loop(model):
    while True:
        screen_capture_download()
        image_origin = image_open(CAPTURE_FILE)
        image = image_origin.copy()
        boxes, classes = model.detect_image(image)
        image_origin = np.array(image_origin)
        image_origin = cv2.cvtColor(image_origin, cv2.COLOR_RGB2BGR)
        boxes = boxes.tolist()
        classes = classes.tolist()
        change_box_xy(boxes)
        target_box, chessman_box = [], []

        for i in range(len(boxes)):
            if classes[i] == 2:
                chessman_box = boxes[i]
            else:
                if not target_box:
                    target_box = boxes[i]
                else:
                    center_cur = cal_center_point(boxes[i])
                    center_tar = cal_center_point(target_box)
                    if center_cur[1] < center_tar[1]:
                        target_box = boxes[i]
        if not chessman_box or not target_box:
            print('no chessman or target box')
            add_mismatch_image(image_origin)
            restart_game()
            continue
        chessman_center = [(chessman_box[2] + chessman_box[0]) / 2, chessman_box[3] - CHESS_CENTER_CORRECT]
        target_center = cal_center_point(target_box)
        image = draw_points(image, [chessman_center, target_center])
        image = image.resize((screen_param['width'] // 3, screen_param['height'] // 3), Image.ANTIALIAS)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow('', image)
        if is_invalid_box(chessman_center, target_center):
            print('no possible target box')
            add_mismatch_image(image_origin)
            restart_game()
            continue
        restore_image(image, image_origin)
        distance = cal_distance(target_center, chessman_center)
        jump(distance)
        cv2.waitKey(WAIT_AFTER_JUMP)


if __name__ == '__main__':
    get_screen_parameter()
    restore_counter = 0
    main_loop(YOLO())
    # screen_capture_download()

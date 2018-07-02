import cv2
import os

PRE_FRAME_KEY = 44 # ','
NEXT_FRAME_KEY = 46 # '.'
PAUSE_KEY = 32 # ' '
SAVE_IMG_KEY =  47 # '/'
EXIT_KEY = 27 # 'esc'

save_image_path = os.path.abspath('./') + '/img/'
video = '/home/cooli7wa/project/pycharm/tiaotiao/video/20180617123132.mp4'


cv2.namedWindow('video')
capture = cv2.VideoCapture(video)
frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
cv2.createTrackbar('time', 'video', 0, frames, lambda a:None)
video_pos, bar_pos = 0, 0
img_cnt = 0
if not os.path.exists(save_image_path):
    os.mkdir(save_image_path)
cur_img_list = os.listdir(save_image_path)
if cur_img_list:
    img_cnt = int(sorted(os.listdir(save_image_path))[-1].rsplit('.')[0]) + 1

while True:
    bar_pos = cv2.getTrackbarPos('time', 'video')
    if video_pos != bar_pos:
        video_pos = bar_pos
        capture.set(cv2.CAP_PROP_POS_FRAMES, video_pos)
    ret, img_origin = capture.read()
    if ret == True:
        img_show = cv2.resize(img_origin, (0,0), fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('video', img_show)
        video_pos += 1
        bar_pos = video_pos
        cv2.setTrackbarPos('time', 'video', bar_pos)
    else:
        break

    key = cv2.waitKey(10)
    if key == PAUSE_KEY:
        while True:
            key = cv2.waitKey(0)
            if key == PAUSE_KEY:
                break
            if key == EXIT_KEY:
                break
            if key == SAVE_IMG_KEY:
                path = '%s%06d.jpg' % (save_image_path, img_cnt)
                print("save img to %s" % path)
                cv2.imwrite(path, img_origin)
                img_cnt += 1
                continue
            if key == PRE_FRAME_KEY:
                video_pos -= 1
            elif key == NEXT_FRAME_KEY:
                video_pos += 1

            bar_pos = video_pos
            cv2.setTrackbarPos('time', 'video', bar_pos)
            capture.set(cv2.CAP_PROP_POS_FRAMES, video_pos)
            ret, img_origin = capture.read()
            img_show = cv2.resize(img_origin, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
            cv2.imshow('video', img_show)
    if key == EXIT_KEY:
        break

capture.release()
cv2.destroyAllWindows()

import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join
import sys
import re
import random

classes = ["box_normal", "box_score", "chessman"]
prop = 1.0

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(folder, image_id):
    in_file = open('%s/%s.xml'%(folder, image_id))
    out_file = open('%s/%s.txt'%(folder, image_id), 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

folder = os.path.abspath(sys.argv[1])

folder_list = os.listdir(folder)
image_ids = []
for name in folder_list:
    if re.match(r'.*\.jpg', name):
        image_ids.append(name.rsplit('.')[0])

list_file = open('%s/total.txt'%(folder), 'w')
for image_id in image_ids:
    list_file.write('%s/%s.jpg\n'%(folder, image_id))
    convert_annotation(folder, image_id)
list_file.close()

with open('%s/total.txt'%(folder), 'r') as f:
    lines = f.readlines()

random.shuffle(lines)
train_lines = lines[:int(round(len(lines)*prop))]
test_lines = lines[int(round(len(lines)*prop)):]

with open('%s/train.txt'%(folder), 'w') as f:
    for line in train_lines:
        f.write(line)

with open('%s/test.txt'%(folder), 'w') as f:
    for line in test_lines:
        f.write(line)





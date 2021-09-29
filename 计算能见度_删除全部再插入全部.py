#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cv2
import numpy as np
import csv
from math import sqrt
import os
import psycopg2

#颜色是http://www.nmc.cn/publish/sea/seaplatform1.html图例,RGB顺序的值
COLORS = [
    (110, 39, 9),  # 0~0.2
    (151, 2, 244),  # 0.2~0.5
    (236, 7, 14),  # 0.5~1
    (244, 87, 6),  # 1~2
    (247, 182, 78),  # 2~3
    (251, 254, 17),  # 3~5
    (113, 255, 39),  # 5~10
    (147, 221, 246),  # 10~20
    (198, 236, 255),  # 20~30
    (255, 255, 255),  # ≥30
]


#[(x1,y1),(x2,y2),……,(x10,y10)],大连的坐标
coordinate_list = [(694,290),
                   (695,290),
                   (695,289),
                   (694,289),
                   (696,289),
                   (698,288),
                   (697,288),
                   (696,288),
                   (697,287),
                   (698,287)]

visibility_list = ['0~0.2','0.2~0.5','0.5~1','1~2','2~3','3~5','5~10','10~20','20~30','≥30']

def cv_imread(filePath):
    '''
    读取中文路径下的图片
    :param filePath:图片路径
    :return:图片对象
    '''
    cv_img=cv2.imdecode(np.fromfile(filePath,dtype=np.uint8),-1)
    # imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
    cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
    return cv_img

def closest_color(rgb):
    '''
    获取颜色最接近COLORS的颜色
    :param rgb:
    :return:
    '''
    r, g, b = rgb
    color_diffs = []
    for color in COLORS:
        cr, cg, cb = color
        color_diff = sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2) #方差
        # color_diff = abs(r - cr) + abs(g - cg) + abs(b - cb) #绝对值差
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


def outputVisibilityValue(para_image_list):
    if para_image_list:
        para_image_list = [ item for item in para_image_list if item.endswith('jpg') ]
        title = [['date', 'visibility', 'label']]
        result_list = []
        for image_path in para_image_list:
            try:
                img = cv_imread(image_path)
                blue_list = []
                green_list = []
                red_list = []
                # 循环大连所在地图上的坐标点
                for x,y in coordinate_list:
                    blue_list.append(img[y,x,0])
                    green_list.append(img[y,x,1])
                    red_list.append(img[y,x,2])
                #获取一张图片上coordinate_list中的像素对应的三通道的平均值
                blue_mean = np.mean(blue_list)
                green_mean = np.mean(green_list)
                red_mean = np.mean(red_list)
                # print(image_path,closest_color((red_mean, green_mean, blue_mean)))
                index = COLORS.index(closest_color((red_mean, green_mean, blue_mean)))
                date = image_path.split(os.sep)[-1].split('.')[0]
                result_list.append([date+':00:00', visibility_list[index],int(index)+1])
            except Exception as ex:
                print(image_path)
                continue

        # with open(r'D:/pythonProjects/image_recognition/opencv_calculate_visibility.csv', 'w', newline='', encoding='utf-8') as f:
        with open(r'./opencv_calculate_visibility.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(title)
            writer.writerows(result_list)
        delete_sql = 'delete from computer_vision_visibility'
        insert_sql = ' insert into computer_vision_visibility  ' \
              ' values (%s,%s,%s) '
        conn = psycopg2.connect("host=x.x.x.x dbname=aaa user=postgres password=bbb")
        cur = conn.cursor()
        cur.execute(delete_sql, result_list)
        conn.commit()
        cur.executemany(insert_sql, result_list)
        conn.commit()
        conn.close()

if __name__=='__main__':
    images_folder = r'D:/images'
    # images_folder = r'/home/images'
    image_list = [ os.path.join(images_folder, image_name) for image_name in os.listdir(images_folder) ]
    outputVisibilityValue(image_list)



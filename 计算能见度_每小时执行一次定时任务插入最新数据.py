#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cv2
import numpy as np
import csv
from math import sqrt
import os
import psycopg2
import schedule
from datetime import datetime

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


def outputVisibilityValue():
    now_time = datetime.today().strftime('%Y-%m-%d %H')
    now_time_image = os.path.join(images_folder, now_time + '.jpg')
    if os.path.exists(now_time_image):
        # title = [['date', 'visibility', 'label']]
        result_list = []
        try:
            img = cv_imread(now_time_image)
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
            date = now_time_image.split(os.sep)[-1].split('.')[0]
            result_list.append([date+':00:00', visibility_list[index],int(index)+1])
        except Exception as ex:
            print(now_time_image, ex)

        conn = psycopg2.connect("host=x.x.x.x dbname=aaa user=postgres password=bbb")
        cur = conn.cursor()
        my_date = date + ':00:00'
        select_sql = " select * from computer_vision_visibility  where date = '%s' " \
                    % (my_date)
        cur.execute(select_sql)
        rows = cur.fetchall()

        if not rows:
            insert_sql = " insert into computer_vision_visibility " \
                         " values ('%s','%s','%s') " \
                         % (my_date, visibility_list[index], int(index)+1 )
            cur.execute(insert_sql)
            conn.commit()
        conn.close()


if __name__=='__main__':
    images_folder = r'/home/images'
    # schedule.every().hour.do(outputVisibilityValue)
    schedule.every(10).minutes.do(outputVisibilityValue)
    while True:
        schedule.run_pending()



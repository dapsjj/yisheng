#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
import os
import json
import datetime

app = Flask(__name__)

# 请求例如
#视频
# http://192.168.1.186:8081/detectForCar?source=D:/202109101705.mp4
# http://192.168.1.186:8081/detectForCar?source=D:/ch01_00000000062000000_4second.mp4

#图片文件夹
# http://192.168.1.186:8081/detectForCar?source=D:/pythonProjects/yolov5-master/data/images


@app.route('/')
# def index():
#     return redirect(url_for('detectForCar'))

@app.route('/detectForCar', methods=['GET','POST'])
def detectForCar():
    source = request.args.get("source")
    ip = request.remote_addr #获取访问的ip
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('ip:'+ip,'now:'+now_time)
    print('source:' + source)
    if source:
        if os.path.exists(source):
            try:
                # cmd = 'python detect_for_all_plate_统计各种车的数量和车牌号.py --source %s' %source
                # print('cmd:'+ cmd)
                # os.system(cmd)
                str_response = {'message': '请求成功'}
                json_response = json.dumps(str_response,ensure_ascii=False)
                return json_response
            except Exception as ex:
                str_response = {'message': '请求失败'}
                json_response = json.dumps(str_response,ensure_ascii=False)
                return json_response
        else:
            str_response = {'message': '文件不存在'}
            json_response = json.dumps(str_response,ensure_ascii=False)
            return json_response
    else:
        str_response = {'message': '请求失败'}
        json_response = json.dumps(str_response,ensure_ascii=False)
        return json_response


if __name__ == '__main__':
    app.run(host='192.168.1.186' ,port=8081)



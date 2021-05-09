# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import json
import csv
from datetime import datetime
import werkzeug
import os

import matplotlib
matplotlib.use('Agg') #バックエンドを指定
import matplotlib.pyplot as plt
from flask import Flask, render_template, redirect, request, Markup, escape, session, url_for

application = Flask(__name__,static_folder='images')
#application.secret_key = 'secret'

DATA_FILE = 'data.json'
UPLOAD_DIR = "/Users/akiyamasayaka/Desktop/"
SAVE_DIR = "images"
FIG_FILE = "figure.png"

# 可視化機能
def visualize_data(condition, axis):
    """可視化
    :param condition:　可視化条件
    :type condition: str
    :param axis: [x軸に指定されたデータのヘッダ名, y軸に指定されたデータのヘッダ名]
    :type axis: list
    :type axis[]: str
    :return: None
    """

    json_open = open(DATA_FILE, 'r')
    json_load = json.load(json_open)

    # グラフの描画先
    fig = plt.figure()

    if condition == "hist":
        x = json_load[0][axis[0]]  # key指定によるvalueの取得
        plt.hist(x)
        plt.title("Histogram")
        plt.xlabel(axis[0])
        plt.ylabel("Count")

    elif condition == "series":
        x = json_load[0][axis[0]]
        y = json_load[0][axis[1]]
        plt.plot(x, y)
        plt.title("Series")
        plt.xlabel(axis[0])
        plt.ylabel(axis[1])

    elif condition == "scatter":
        x = json_load[0][axis[0]]
        y = json_load[0][axis[1]]
        plt.scatter(x, y)
        plt.title("Scatter plot")
        plt.xlabel(axis[0])
        plt.ylabel(axis[1])

    # save fig
    plt.savefig(os.path.join(SAVE_DIR, FIG_FILE))
    return os.path.join(SAVE_DIR, FIG_FILE)

# データ保存(読み込みデータの一時置き場として)
def save_data(filename):
    """対象データをJSON形式に変換し、header情報をkeyとしてカラム単位で保存します
    :param fileName: 入力データのファイルパス
    :type fileName: str
    :return: None
    """
    csv_input = pd.read_csv(filepath_or_buffer=filename, sep=",")
    keys = csv_input.columns.values

    text2json = "{"
    cnt = 0
    for k in keys:
        text2json += "\"" + k + "\": "+ str(list(csv_input[k]))
        
        # judge need ","
        cnt += 1
        if cnt != 0|len(keys):
            text2json += ","
        elif cnt == len(keys):
            text2json += "}"
    
    # データベースへ保存
    try:
        # jsonモジュールでデータベースファイルを開きます
        database = json.load(open(DATA_FILE, mode="r", encoding="utf-8"))

    except FileNotFoundError:
        database = []
            
    eval("database.insert(0,"+text2json+")")
    json.dump(database, open(DATA_FILE, mode="w", encoding="utf-8"), indent=4, ensure_ascii=False)

def get_axis(axis_x,axis_y):
    """formから取得したlistを元に軸情報を取得する
    :param axislist: [x軸に指定されたデータのヘッダ名リスト, y軸に指定されたデータのヘッダ名リスト]
    :type axislist: str
    :return: None
    """

    x_idx = [i for i, n in enumerate(axis_x) if n != '']
    x = axis_x[x_idx[0]]

    y_idx = [i for i, n in enumerate(axis_y) if n != '']
    if y_idx == []:
        y = ''
    else:
        y = axis_y[y_idx[0]]

    return [x, y]


def get_tags():
    """軸選択用のデータリストを作成する
    """

    json_open = open(DATA_FILE, 'r')
    json_load = json.load(json_open)
    tags = list(json_load[0].keys())

#    csv_input = pd.read_csv(filepath_or_buffer=filename, sep=",")
#    keys = csv_input.columns.values

#    list_text = "["
#    cnt = 0
#    for k in keys:
#        list_text += "{'name':'" + k + "'}"
#        if cnt != len(keys):
#            list_text += ","
#        if cnt == lrn(keys):
#            len_text += "]"

    return tags

def csv_to_html(filepath):
     # CSVファイル読み込み
    data = pd.read_csv(filepath, na_filter=False)

    # htmlファイル読み込み
    htmldata = ''
    with open('index.html',mode='r',encoding='utf-8') as htmlfile:
        htmldata = htmlfile.read()

    # CSVファイルをhtmlに変換
    rpdict = { "filename" : os.path.basename(data), "table" : data.to_html() }
    htmldata = htmldata.format(**rpdict)

    # htmlファイル出力
    with open('index.html',mode='w',encoding='utf-8') as outputhtml:
        outputhtml.write(htmldata)


@application.route('/')
def index():
    """トップページテンプレートを使用してページを表示します"""
    return render_template('index.html')

@application.route('/upload',  methods=["GET","POST"])
def load_data():
    # ボタン
    upload_b = request.form["upload"]

    if upload_b != "":
        if 'uploadFile' not in request.files:
            make_response(jsonify({'result':'uploadFile is required.'}))

        file = request.files['uploadFile']
        fileName = file.filename
        if '' == fileName:
            make_response(jsonify({'result':'filename must not empty.'}))

        # 下記のような情報がFileStorageからは取れる
        #application.logger.info('file_name={}'.format(fileName))
        #application.logger.info('content_type={} content_length={}, mimetype={}, mimetype_params={}'.format(
        #            file.content_type, file.content_length, file.mimetype, file.mimetype_params))
                
        # ファイルを保存
        savefilepath=os.path.join(UPLOAD_DIR,fileName)
        file.save(savefilepath)
        save_data(savefilepath)

        dataset = pd.read_csv(filepath_or_buffer=savefilepath, sep=",")
        tags = get_tags()

    return render_template('index.html', dataset=dataset, tags=tags)

@application.route('/visualize', methods=['POST'])
def upload_fig():
    visualize_b = request.form["visualize"]

    if visualize_b != "":
        condition = request.form["condition"]
        axis_x = request.form.getlist('x')
        axis_y = request.form.getlist('y')

        axis = get_axis(axis_x,axis_y)
        fig=visualize_data(condition, axis)

        return render_template('index.html', visualize_b=visualize_b,axis=axis,fig=fig)

if __name__ == '__main__':
    # IPアドレス0.0.0.0の8000番ポートでアプリケーションを実行します
    application.run('0.0.0.0', 8000, debug=True)
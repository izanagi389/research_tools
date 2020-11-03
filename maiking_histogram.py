import glob
import csv
import matplotlib.pyplot as plt
import math
import numpy as np
import matplotlib as mpl
import emoji
import re
from matplotlib.font_manager import FontProperties
import os
import shutil


def main():
    pi = math.pi  # mathモジュールのπを利用
    y = np.linspace(0, 2 * pi)
    cos_y = np.cos(y)

    files = glob.glob('./data/csv/doc2vec_result/*.csv')
    # フォントURL指定（ttc不可）
    font_path = '../../library/Fonts/ipaexm.ttf'
    font_prop = FontProperties(fname=font_path)

    # フォルダの初期化
    shutil.rmtree("histogram")
    os.mkdir("histogram")
    # 結果ファイル削除
    files.remove('./data/csv/doc2vec_result/result.csv')
    for i, file in enumerate(files):
        with open(file, 'r') as f:
            # カラムの値を抽出（ツイート内容）
            list = []
            for row in csv.reader(f):
                try:
                    if isinstance(float(row[0]), float):
                        list.append(float(row[0]))
                except ValueError:
                    continue

            fig = plt.figure()
            x = np.round(list, decimals=5)

            plt.xlabel("コサイン類似度", fontproperties=font_prop)
            plt.ylabel("ツイート、ニュース比較数", fontproperties=font_prop)
            plt.hist(x, bins=50)
            plt.grid()
            file_path_list = file.split('/')
            name = re.sub(r'.csv', '', file_path_list[-1])
            fig.savefig("histogram/" + name + ".png")


main()

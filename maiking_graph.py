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
from config import making_graph_config


def main():
    files = glob.glob(making_graph_config.SEARCHDIRECTORY)
    # フォントURL指定（ttc不可）
    font_path = making_graph_config.FONTPATH
    font_prop = FontProperties(fname=font_path)

    # フォルダの初期化
    try:
        shutil.rmtree(making_graph_config.SAVEPATH)
    except FileNotFoundError:
        pass

    os.mkdir(making_graph_config.SAVEPATH)

    # 結果ファイル削除
    for file in making_graph_config.REMOVEFILES:
        files.remove(file)

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
            result_list = np.round(list, decimals=5)

            plt.xlim(making_graph_config.XRANGEMIN, making_graph_config.XRANGEMAX)

            # ラベルを作成
            plt.xlabel(making_graph_config.LABELX, fontproperties=font_prop)
            plt.ylabel(making_graph_config.LABELY, fontproperties=font_prop)
            # ヒストグラムを作成
            plt.grid()
            plt.hist(result_list, bins=50)
            # ファイル名のみを取り出す
            file_path_list = file.split('/')
            name = re.sub(r'.csv', '', file_path_list[-1])
            # 画像ファイルとして保存
            fig.savefig(making_graph_config.SAVEPATH + "/" + name + ".png")


main()

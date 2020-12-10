#!/usr/bin/python
# -*- coding: utf-8 -*-

"""doc2vec.py

     * 「gensim.models.doc2vec」を利用し、
     *  テキストと類似性の高いWikipedia記事を参照する（modelがWikipediaを使用しているため）
     * 結果をcsvに保存
     *
     * 起動方法
     * $ Python text_most_similar_doc2vec.py

"""
from gensim.models.doc2vec import Doc2Vec
import MeCab
import emoji
import re
import csv
import numpy as np
import pandas as pd
import glob
import logging
from config import config
import statistics


model_path = config.doc2vec_config.MODELPATH
model = Doc2Vec.load(model_path)


def main():
    """main処理

    ロギングの設定
    定数、変数の初期設定を行なっている

    Note:
        ここで結果保存用csvファイルの初期化を行なっている

    """
    formatter = '%(levelname)s/%(asctime)s/%(filename)s(%(lineno)s)/%(message)s '
    logging.basicConfig(format=formatter)

    df = pd.DataFrame(columns=["id", "類似度", "比較テキスト"])
    df.to_csv("test/csv/result_most_similar.csv", index=None)
    # ツイートパス
    path_list = glob.glob("data/csv/tweet/random/" + "*.csv")
    # ニュース記事パス
    # path_list = glob.glob("data/csv/newsbynews/" + "*.csv")
    for path in path_list:
        execute(path)


def execute(text_file_path):
    """execute関数

    実行処理

    Arge:
        text_file_path String: テキストファイル（csv）のファイルパス

    """
    list = read_csv(text_file_path)
    if list:
        for l in list:
            actDoc2vec(l)
    else:
        logging.warning("「{}」は値が格納されていません！".format(tweet_csv_path))


def tokenize(text):
    """tokenize関数

    Mecabを用いて形態素解析を行う

    Arge:
        text String: 形態素解析を行うテキスト

    Returns:
        [String]: 形態素解析された単語リスト

    """
    tagger = MeCab.Tagger(config.NEOLOGDPATH)

    key = tagger.parse(text)
    corpus = []
    for row in key.split("\n"):
        word = row.split("\t")[0]
        if word == "EOS":
            break
        else:
            corpus.append(word)

    return corpus


def read_csv(path):
    """read_csv関数

    csvファイルの読み込みを行う
    tokenize関数の実行処理

    Arge:
        text String: 形態素解析を行うテキスト

    Returns:
        [String]: tokenize関数で得た結果をさらにリスト化

    """
    list = []
    file = path
    with open(file, 'r') as f:
        for row in csv.reader(f):
            text = "".join(row[0].splitlines())
            if not len(text) == 0:
                list.append(tokenize(text))

        return list


def actDoc2vec(text_list):
    """actDoc2vec関数

    Doc2Vecを実行(most_similar)
    結果をcsvに出力

    Arge:
        text_list [String]: 形態素解析を行うテキスト

    Note:
        model.infer_vector(text_list)にて検索文章のベクトル化を行なっている。
        ＊positive=にベクトル化した文章を格納しないとエラーが発生


    """
    result = []
    sim_value = model.docvecs.most_similar(
        positive=[model.infer_vector(text_list)], topn=1)
    print(sim_value[0][0])
    result.append([sim_value[0][0], sim_value[0][1], ''.join(text)])

    df_result = pd.DataFrame(result)
    df_result.to_csv("test/csv/result_most_similar.csv",
                     mode="a", index=None, header=None)


main()

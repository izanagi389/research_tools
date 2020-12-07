#!/usr/bin/python
# -*- coding: utf-8 -*-
"""doc2vec.py

     * 「gensim.models.doc2vec」を利用し、
     * ニュース記事とツイートのコサイン類似度を抽出する
     * 結果をcsvに保存
     *
     * 起動方法
     * $ Python doc2vec.py

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

    news_name = config.config_news.NEWSNAME
    news_csv_path = config.config_news.NEWSPATH + news_name + ".csv"
    news_list = read_csv(news_csv_path)
    tweet_csv_path_list = glob.glob(config.config_tweet.SAVEPATH + "*.csv")

    df_initialize = pd.DataFrame(
        columns=["アカウント名", "コサイン類似度平均", "コサイン類似度標準偏差", "コサイン類似度分散", "最頻値", "中央値",
                 "最大値", "最小値", "ツイート数", "ニュース数"])
    df_initialize.to_csv(config.doc2vec_config.SAVEPATH +
                         config.doc2vec_config.SAVEFILENAME, mode="w", index=None)

    execute(tweet_csv_path_list, news_list)


def execute(tweet_csv_path_list, news_list):
    """execute関数

    実行処理

    Arge:
        tweet_csv_path_list [String]: ツイートcsvのパスリスト
        news_list [String]: ニュース記事リスト
    """

    for tweet_csv_path in tweet_csv_path_list:
        tweet_list = read_csv(tweet_csv_path)
        if tweet_list:
            actDoc2vec(tweet_csv_path, tweet_list, news_list)
        else:
            logging.warning("「{}」は値が格納されていません！".format(tweet_csv_path))


def tokenize(text):
    """tokenize関数
    MeCabを用いた形態素解析

    Arge: text String: 形態素解析するテキスト

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
    csvからテキストを取得する

    Arge: path String: 形態素解析するテキスト

    Returns:
        [String]: csvから抽出したテキストリスト

    """
    list = []
    file = path
    with open(file, 'r') as f:
        for row in csv.reader(f):
            text = "".join(row[0].splitlines())
            if not len(text) == 0:
                list.append(tokenize(text))

        return list


def actDoc2vec(tweet_csv_path, tweet_list, news_list):
    """actDoc2vec関数

    Doc2vec実行処理

    Arge:　
        tweet_csv_path [String]: ツイートのcsvパス（アカウント名取得用）
        tweet_list [String]: ツイートリスト
        news_list [String]: ニュース記事リスト

    Note:
        csvファイルに保存も行なっている

    """
    sim_value_sum = []
    result = []
    tweet_num = len(tweet_list)
    news_num = len(news_list)

    for tweet_str in tweet_list:
        if not (len(tweet_str) == 0):
            for news_str in news_list:
                sim_value = model.docvecs.similarity_unseen_docs(
                    model, news_str, tweet_str, alpha=1, min_alpha=0.0001, steps=5)
                if sim_value < 0:
                    sim_value *= -1

                sim_value_sum.append(sim_value)

                result.append([sim_value,
                               ''.join(news_str), ''.join(tweet_str)])

    name = tweet_csv_path.split('/')[-1]
    df_result = pd.DataFrame(result, columns=["コサイン類似度", "ニュース記事", "ツイート"])
    df_result.round(4).to_csv(config.doc2vec_config.SAVEPATH +
                              name, mode="w", index=None)

    a = np.array(sim_value_sum)
    average = np.average(a)
    std = np.std(a)
    var = np.var(a)
    num_max = np.max(a)
    num_min = np.min(a)
    num_mode = min(statistics.multimode(a))
    num_median = np.median(a)

    name = re.sub(".csv", "", name)
    df_result_num = pd.DataFrame([[name,
                                   average,
                                   std,
                                   var,
                                   num_mode,
                                   num_median,
                                   num_max,
                                   num_min,
                                   tweet_num, news_num, ]],)

    df_result_num.round(4).to_csv(config.doc2vec_config.SAVEPATH +
                                  config.doc2vec_config.SAVEFILENAME, mode="a", header=None, index=None)

    print(name + " create OK!")


main()

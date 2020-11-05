from gensim.models.doc2vec import Doc2Vec
import MeCab
# 絵文字管理ライブラリ
import emoji
import re
# ファイル取得に利用
import csv
import numpy as np
import pandas as pd
from config import config

from config import doc2vec_config


# Wikipediaモデル読み込み
model_path = doc2vec_config.MODELPATH
model = Doc2Vec.load(model_path)


def main():
    # ニューステキストをリストに格納
    news_name = config.NEWSNAME
    news_csv_path = config.NEWSPATH + news_name + ".csv"
    news_list = shap_text(news_csv_path)

    # 分析対象アカウントツイートをリストに格納
    names = config.NAMES
    # csvファイルの初期化（カラム作成）
    df_initialize = pd.DataFrame(
        columns=["アカウント名", "コサイン類似度平均", "コサイン類似度標準偏差", "コサイン類似度分散", "最大値", "最小値"])
    df_initialize.to_csv(doc2vec_config.SAVEPATH + "result.csv", mode="w", index=None)

    # 実装処理
    for name in names:
        tweet_csv_path = "./data/csv/" + name + ".csv"
        tweet_list = shap_text(tweet_csv_path)
        actDoc2vec(name, tweet_list, news_list)


def tokenize(text):
    # MeCabでの形態素解析
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    key = tagger.parse(text)
    corpus = []
    for row in key.split("\n"):
        word = row.split("\t")[0]
        if word == "EOS":
            break
        else:
            corpus.append(word)

    return corpus


def shap_text(path):
    list = []
    file = path
    with open(file, 'r') as f:
        # カラムの値を抽出（ツイート内容）
        for row in csv.reader(f):
            # テキストを整形
            # 文字の整形（改行削除）
            # URL削除
            text = "".join(row[0].splitlines())
            if not len(text) == 0:
                # テキストを整形
                list.append(tokenize(text))

        return list


def actDoc2vec(name, tweet_list, news_list):

    # コサイン類似度合計
    sim_value_sum = []

    # csvに書き込む２次元配列
    result = []

    for tweet_str in tweet_list:
        # から文字（NULL）削除
        if not (len(tweet_str) == 0):
            for news_str in news_list:
                sim_value = model.docvecs.similarity_unseen_docs(
                    model, news_str, tweet_str, alpha=1, min_alpha=0.0001, steps=5)
                if sim_value < 0:
                    sim_value *= -1

                sim_value_sum.append(np.round(sim_value, decimals=4))

                result.append([np.round(sim_value, decimals=4),
                               ''.join(news_str), ''.join(tweet_str)])

    # 結果をcsvに保存
    df_result = pd.DataFrame(result, columns=["コサイン類似度", "ニュース記事", "ツイート"])
    df_result.round(4).to_csv(doc2vec_config.SAVEPATH + name + ".csv", mode="w", index=None)

    # 分散・標準偏差・最大値などをcsvに保存
    a = np.array(sim_value_sum)
    average = np.average(a)
    std = np.std(a)
    var = np.var(a)
    num_max = np.max(a)
    num_min = np.min(a)

    df_result_num = pd.DataFrame([[name,
                                   np.round(average, decimals=4),
                                   np.round(std, decimals=4),
                                   np.round(var, decimals=4),
                                   np.round(num_max, decimals=4),
                                   np.round(num_min, decimals=4)]],)

    df_result_num.round(4).to_csv(doc2vec_config.SAVEPATH +
                                  "result.csv", mode="a", header=None, index=None)

    print(name + " create OK!")


main()

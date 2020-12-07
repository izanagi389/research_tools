from gensim.models.word2vec import Word2Vec
import MeCab
# 絵文字管理ライブラリ
import emoji
import re
# ファイル取得に利用
import csv
import numpy as np
import pandas as pd
import glob

from config import config

# Wikipediaモデル読み込み
model_path = config.word2vec_config.MODELPATH
model = Word2Vec.load(model_path)


def main():
    # ニューステキストをリストに格納
    news_name = config.config_news.NEWSNAME
    news_csv_path = config.config_news.NEWSPATH + news_name + ".csv"
    news_list = shap_text(news_csv_path)
    # csvファイルの初期化（カラム作成）
    df_initialize = pd.DataFrame(
        columns=["アカウント名", "WMD類似度平均", "WMD類似度標準偏差", "WMD類似度分散", "最大値", "最小値"])
    df_initialize.to_csv(config.word2vec_config.SAVEPATH + "result.csv", mode="w", index=None)

    # 実装処理
    tweet_csv_path = glob.glob(config.config_tweet.SAVEPATH + "*.csv")
    for path in tweet_csv_path:
        tweet_list = shap_text(path)
        name = path.split('/')[-1]
        actWord2vec(name, tweet_list, news_list)


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
            text = "".join(row[0].splitlines())
            if not len(text) == 0:
                # テキストを整形
                list.append(tokenize(text))

        return list


def actWord2vec(name, tweet_list, news_list):

    # WMD類似度合計
    sim_value_sum = []
    # csvに書き込む２次元配列
    result = []
    for tweet_str in tweet_list:
        # から文字（NULL）削除
        if not (len(tweet_str) == 0):
            for news_str in news_list:

                sim_value = model.wv.wmdistance(news_str, tweet_str)
                if str(sim_value) == "inf":
                    # sim_value = 100
                    break

                sim_value_sum.append(np.round(sim_value, decimals=4))

                result.append([np.round(sim_value, decimals=4),
                               ''.join(news_str), ''.join(tweet_str)])

    # 結果をcsvに保存
    df_result = pd.DataFrame(result, columns=["WMD類似度", "ニュース記事", "ツイート"])
    df_result.to_csv(config.word2vec_config.SAVEPATH + name + ".csv", mode="w", index=None)

    # 分散・標準偏差・最大値などをcsvに保存
    a = np.array(sim_value_sum)

    df_result_num = pd.DataFrame([[name,
                                   np.round(np.average(a), decimals=4),
                                   np.round(np.std(a), decimals=4),
                                   np.round(np.var(a), decimals=4),
                                   np.round(np.max(a), decimals=4), np.round(np.min(a), decimals=4)]],)

    df_result_num.round(4).to_csv(config.word2vec_config.SAVEPATH +
                                  "result.csv", mode="a", header=None, index=None)
    print(name + " create OK!")


main()

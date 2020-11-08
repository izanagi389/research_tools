import csv
import requests
import json
import re
import emoji
import gensim
import MeCab
import pandas as pd

from config import config
from config import config_trend
from requests_oauthlib import OAuth1Session
from gensim.corpora.dictionary import Dictionary
from gensim import corpora
from gensim.models import LdaModel


CK = config.CK
CS = config.CS
AT = config.AT
AS = config.AS


def main():
    tweet_list = getTwitterData(
        config_trend.KEYWORD, config_trend.LIMIT, config_trend.SUBLIST)

    common_texts = []
    for content in tweet_list:
        common_texts.append(tokenize(content))

    result = latent_dirichlet_allocation(common_texts)
    df = pd.DataFrame(result)
    df.to_csv('data/csv/trend/tweet_result.csv', header=None, index=None)
    print(result)


def getTwitterData(key_word, repeat, sub_list):
    twitter = OAuth1Session(CK, CS, AT, AS)
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {'q': key_word, 'exclude': 'retweets', 'count': '100', 'lang': 'ja',
              'result_type': 'recent', "tweet_mode": "extended"}

    result_list = []
    break_flag = 0
    mid = -1
    for i in range(repeat):
        params['max_id'] = mid  # midよりも古いIDのツイートのみを取得する
        res = twitter.get(url, params=params)

        if res.status_code == 200:  # 正常通信出来た場合
            # limit = res.headers['x-rate-limit-remaining'] if 'x-rate-limit-remaining' in res.headers else 0
            # print("API残接続可能回数：%s" % len(limit))
            tweet_ids = []
            timelines = json.loads(res.text)  # レスポンスからタイムラインリストを取得
            for line in timelines['statuses']:
                tweet_ids.append(int(line['id']))
                text = shape_text(line['full_text'], sub_list)
                result_list.append(text)

            if len(tweet_ids) > 0:
                min_tweet_id = min(tweet_ids)
                mid = min_tweet_id - 1
            else:
                break_flag = 1
                break

            # 終了判定
            if break_flag == 1:
                break

        else:
            print("Failed: %d" % res.status_code)
            break_flag = 1

    print("ツイート取得数：%s" % len(list(set(result_list))))

    return list(set(result_list))


def latent_dirichlet_allocation(common_texts):
    dictionary = Dictionary(common_texts)
    # LdaModelが読み込めるBoW形式に変換
    corpus = [dictionary.doc2bow(text) for text in common_texts]

    num_topics = config_trend.COUNTTOPIC
    lda = LdaModel(corpus, num_topics=num_topics)

    topic_words = []
    for i in range(num_topics):
        tt = lda.get_topic_terms(i, config_trend.COUNTTOPICNUM)
        topic_words.append([dictionary[pair[0]] for pair in tt])

    result_topic = []
    for topic in topic_words:
        result_topic = result_topic + topic
    topics = list(dict.fromkeys(result_topic))

    result = []
    for topic in topics:
        if not bool(re.search(r'\d', topic)):
            result.append(topic)

    return result


def tokenize(text):
    # MeCabでの形態素解析
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    key = tagger.parse(text)
    output_words = []
    for row in key.split("\n"):
        word = row.split("\t")[0]
        if word == "EOS":
            break
        else:
            pos = row.split("\t")[1]
            slice = pos.split(",")
            if len(word) > 2:
                if slice[0] == "名詞":
                    if slice[1] == "固有名詞":
                        if slice[2] == "人名":
                            continue
                        elif slice[2] == "形容動詞語幹":
                            continue
                        else:
                            output_words.append(word)

    return output_words


def shape_text(line, result_list):
    text = "".join(line.splitlines())
    text = re.sub(r'[^ ]+\.[^ ]+', '', text)
    # 絵文字を削除
    text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)
    # 全角記号削除
    text = re.sub(r'[︰-＠]', '', text)
    # 半角記号削除
    text = re.sub(re.compile("[!-/:-@[-`{-~]"), '', text)
    for sub_text in result_list:
        text = re.sub(sub_text, '', text)

    return text


main()

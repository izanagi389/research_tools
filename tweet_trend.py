from config import config
import csv  # csv読み取り
import requests
from requests_oauthlib import OAuth1Session  # OAuthのライブラリの読み込み
import json
import csv
import re
import emoji
from gensim.corpora.dictionary import Dictionary
from gensim import corpora
import gensim
import MeCab
from gensim.models import LdaModel

CK = config.CK
CS = config.CS
AT = config.AT
AS = config.AS


def main():
    common_texts = []

    key_word = "コスメ"
    limit = 170
    tweet_list = getTwitterData(key_word, limit)

    for content in tweet_list:
        common_texts.append(tokenize(content))

    dictionary = Dictionary(common_texts)
    # LdaModelが読み込めるBoW形式に変換
    corpus = [dictionary.doc2bow(text) for text in common_texts]

    num_topics = 3
    lda = LdaModel(corpus, num_topics=num_topics)

    topic_words = []
    for i in range(num_topics):
        tt = lda.get_topic_terms(i, 20)
        topic_words.append([dictionary[pair[0]] for pair in tt])

    result_topic = []
    # result_topic = result_topic.extend(topic_words)
    for topic in topic_words:
        result_topic = result_topic + topic
    result_topic = list(dict.fromkeys(result_topic))
    result = []
    for topic in result_topic:
        if not bool(re.search(r'\d', topic)):
            result.append(topic)

    print(result)


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
                    output_words.append(word)

    return output_words


def getTwitterData(key_word, repeat):
    twitter = OAuth1Session(CK, CS, AT, AS)
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {'q': key_word, 'exclude': 'retweets', 'count': '100', 'lang': 'ja',
              'result_type': 'recent', "tweet_mode": "extended"}

    list = []
    break_flag = 0

    for i in range(repeat):
        res = twitter.get(url, params=params)

        if res.status_code == 200:  # 正常通信出来た場合
            # limit = res.headers['x-rate-limit-remaining'] if 'x-rate-limit-remaining' in res.headers else 0
            # print("API残接続可能回数：%s" % len(limit))
            timelines = json.loads(res.text)  # レスポンスからタイムラインリストを取得
            for line in timelines["statuses"]:
                text = shape_text(line['full_text'])
                list.append(text)

            if not len(list) > 0:
                break_flag = 1
                break

            # 終了判定
            if break_flag == 1:
                break

        else:
            print("Failed: %d" % res.status_code)
            break_flag = 1

    print("ツイート取得数：%s" % len(list))

    return list


def shape_text(line):
    text = "".join(line.splitlines())
    text = re.sub(r'[^ ]+\.[^ ]+', '', text)
    # 絵文字を削除
    text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)
    # 全角記号削除
    text = re.sub(r'[︰-＠]', '', text)
    # 半角記号削除
    text = re.sub(re.compile("[!-/:-@[-`{-~]"), '', text)

    return text


main()

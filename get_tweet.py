import json
from config import config
import csv  # csv読み取り
import requests
from requests_oauthlib import OAuth1Session  # OAuthのライブラリの読み込み
import pandas as pd
import re
import emoji
import os
import shutil
import logging

# 各種Key情報（config.pyに記入）
CK = config.config_tweet.CK
CS = config.config_tweet.CS
AT = config.config_tweet.AT
AS = config.config_tweet.AS


def main():
    formatter = '%(levelname)s/%(asctime)s/%(filename)s(%(lineno)s)/%(message)s '
    logging.basicConfig(format=formatter)
    twitter = OAuth1Session(CK, CS, AT, AS)  # 認証処理
    url_base = "https://api.twitter.com/1.1/statuses/user_timeline.json?tweet_mode=extended&user_id="  # タイムライン取得エンドポイント
    user_id_list = config.USER_ID_LIST

    for id in user_id_list:
        getTweet(id, url_base, twitter)


def getTweet(id, url_base, twitter):

    url = url_base + id
    params = {'include_rts': False, 'exclude_replies': True, 'count': 200, }  # 取得数,リプライを除く
    result_list = []
    break_flag = 0
    mid = -1
    text_list = []
    account_name = ""
    count = 0
    for i in range(config.RANGE):
        if not mid == -1:
            params['max_id'] = mid
        res = twitter.get(url, params=params)

        if res.status_code == 200:
            timelines = json.loads(res.text)
            if timelines == []:
                mid = -1
                break
            account_name = timelines[0]['user']['name'].replace('/', '')

            tweet_ids = []

            for line in timelines:
                text = "".join(line['full_text'].splitlines())
                tweet_ids.append(int(line['id']))
                text = shape_text(text)
                if len(text) >= 5:
                    text_list.append([text, line['created_at']])
                    count += 1
                if len(tweet_ids) > 0:
                    min_tweet_id = min(tweet_ids)
                    mid = min_tweet_id - 1
                else:
                    break_flag = 1
                    mid = -1
                    break
                # 終了判定
                if break_flag == 1:
                    mid = -1
                    break

        else:  # 正常通信出来なかった場合
            print("Failed: %d" % res.status_code)
            break_flag = 1
    print(account_name + "tweets get! " + str(count) + " piece")
    df = pd.DataFrame(get_unique_list(text_list))
    df.to_csv(config.config_tweet.SAVEPATH + account_name +
              '.csv', header=None, index=None, mode="w")


def select_news(text):

    result_list = []
    df = pd.read_csv(config.config_trend.SAVEPATH + config.config_trend.SAVEFILENAME, sep=',',
                     encoding='utf-8', index_col=False, header=None)
    trend_list = list(df[0])

    num_list = []
    for trend in trend_list:
        num_list.append(text.count(trend))

    if not sum(num_list) > 0:
        text = ""

    return text


def shape_text(text):

    text = re.sub(r'[^ ]+\.[^ ]+', '', text)
    text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text = re.sub('RT', "", text)
    text = re.sub('お気に入り', "", text)
    text = re.sub('まとめ', "", text)
    text = re.sub(r'[!-~]', "", text)  # 半角記号,数字,英字
    text = re.sub(r'[︰-＠]', "", text)  # 全角記号
    text = re.sub('\n', "", text)  # 改行文字
    text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)  # 絵文字を削除
    flag = config.config_tweet.FLAG
    if flag == 0:
        text = select_news(text)

    return text


def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]


main()

import json
from config import config
import csv # csv読み取り
import requests
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み
import os
import pandas as pd
import re
import emoji

# 各種Key情報（config.pyに記入）
CK = config.CK
CS = config.CS
AT = config.AT
AS = config.AS

def main():
    twitter = OAuth1Session(CK, CS, AT, AS) #認証処理
    url_base = "https://api.twitter.com/1.1/statuses/user_timeline.json?tweet_mode=extended&user_id="#タイムライン取得エンドポイント
    user_id_list = config.USER_ID_LIST

    for id in user_id_list:
        getTweet(id, url_base, twitter)


def getTweet(id, url_base, twitter):
    url = url_base + id
    params ={'include_rts' : False, 'exclude_replies' : True,'count' : 200, } #取得数,リプライを除く
    res = twitter.get(url, params = params)

    if res.status_code == 200: #正常通信出来た場合
        timelines = json.loads(res.text) #レスポンスからタイムラインリストを取得

        count = len(timelines)
        account_name = timelines[0]['user']['name'].replace('/', '') #アカウント名の取得
        with open('data/csv/' + account_name + '.csv', 'w') as f:
            writer = csv.writer(f)

            for line in timelines: #タイムラインリストをループ処理
                # csv書き込み
                text = "".join(line['full_text'].splitlines())
                text = re.sub(r'[^ ]+\.[^ ]+','',text)
                # 絵文字を削除
                text = ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)
                # 全角記号削除
                text = re.sub(r'[︰-＠]','',text)
                # 半角記号削除 + 半角数字
                text = re.sub(r'[!-@[-`{-~]','',text)
                writer.writerow([text, line['created_at']]) # result[0], result[1]

        print(account_name + "tweets get! " + str(count) + " piece")
    else: #正常通信出来なかった場合
        print("Failed: %d" % res.status_code)

main()



# gcp感情分析
# def emotion(text_emotion):
#     #APIキーを入力
#     key = config.gcp_api_key
#
#     #APIのURL
#     url = 'https://language.googleapis.com/v1/documents:analyzeSentiment?key=' + key
#
#     #基本情報の設定 JAをENにすれば英語のテキストを解析可能
#     header = {'Content-Type': 'application/json'}
#     body = {
#         "document": {
#             "type": "PLAIN_TEXT",
#             "language": "JA",
#             "content": text_emotion
#         },
#         "encodingType": "UTF8"
#     }
#
#     #json形式で結果を受け取る。
#     response = requests.post(url, headers=header, json=body).json()
#
#     #分析の結果をコンソール画面で見やすく表示
#     return [response["documentSentiment"]["magnitude"],response["documentSentiment"]["score"]]

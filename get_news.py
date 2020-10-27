import requests
import json
from config import config
import csv
import emoji
import re
import MeCab
import glob
import pandas as pd
import logging

from bs4 import BeautifulSoup

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer


def main():
    # ロギング設定
    formatter = '%(levelname)s/%(asctime)s/%(filename)s(%(lineno)s)/%(message)s '
    logging.basicConfig(format=formatter)
    # ニュースAPIの利用
    API_KEY = config.news_api
    # 検索キーワード・オプション
    keywords = "スキンケア"
    count = "100"
    sort = "publishedAt"
    # fashionsnap.com
    domains_fashionsnap = "fashionsnap.com"
    domains_yahoo = "yahoo.co.jp"
    news_api_url_fashionsnap = ("https://newsapi.org/v2/everything?" + "pageSize=" + count + "&q=" +
                                keywords + "&sortBy=" + sort + "&domains=" + domains_fashionsnap + '&apiKey=' + API_KEY)
    news_api_url_yahoo = ("https://newsapi.org/v2/everything?" + "pageSize=" + count + "&q=" +
                          keywords + "&sortBy=" + sort + "&domains=" + domains_yahoo + '&apiKey=' + API_KEY)
    # ニュースURLリストを取得
    url_list_fashionsnap = getNewsURl(news_api_url_fashionsnap)
    url_list_yahoo = getNewsURl(news_api_url_yahoo)

    result_news_fashionsnapcom_list = newsScrapingFashionsnapcom(
        url_list_fashionsnap)
    result_news_yahoo_list = newsScrapingYahoo(url_list_yahoo)
    save_list = result_news_fashionsnapcom_list + result_news_yahoo_list

    # 結果の保存
    save_result_csv(result_news_fashionsnapcom_list, "fashionsnapcom_news")
    save_result_csv(result_news_yahoo_list, "yahoo_news")
    save_result_csv(save_list, "result_news")


# ニュースAPIのリクエスト
def getNewsURl(url):
    urls = []
    response = requests.get(url)
    json_data = json.loads(response.text)

    # 正常に通信できた場合
    if json_data['status'] == "ok":
        for data in json_data["articles"]:
            if not (("collection" in data["url"]) or ("streetstyle" in data["url"])):
                urls.append(data["url"])
                logging.warning(data["url"])
    else:
        # リクエストステータス表示
        logging.warning("ニュースをリクエストできませんでした：「{}」", json_data['status'])

    return urls

# # Webスクレイピング(Yahooニュース)


def newsScrapingYahoo(urls):
    result_news = []
    # ニューステキストをスクレイピング
    for url in urls:
        # レスポンスを取得
        response = requests.get(url)
        # BeautifulSoupオブジェクト生成
        soup = BeautifulSoup(response.text, "html.parser")

        # スクレイピング結果を取得
        # テキストが存在しない場合以外の処理
        if soup.find(class_='article_body') is not None:
            news_content = soup.find(class_='article_body').text
            news_content = shap_text(news_content)
            result_news.append([news_content, url])
        else:
            logging.warning("「{}」の記事の内容が見つかりませんでした".format(url))

    return result_news


# Webスクレイピング(fashionsnap.comニュース)
def newsScrapingFashionsnapcom(urls):

    result_news = []
    # ニューステキストをスクレイピング
    for url in urls:
        # レスポンスを取得
        response = requests.get(url)
        # BeautifulSoupオブジェクト生成
        soup = BeautifulSoup(response.text, "html.parser")

        # スクレイピング結果を取得
        # テキストが存在しない場合以外の処理
        if soup.find('article') is not None:
            if soup.find('article').a is not None:
                soup.find('article').a.decompose()

            news_content = soup.find('article').text

            news_content = re.sub(r'全て表示する', '', news_content)
            news_content = re.sub(r'Update【年月日追加】', '', news_content)
            news_content = re.sub(r'Update【年月日続報】', '', news_content)
            news_content = shap_text(news_content)

            news_content.strip()

            result_news.append([news_content, url])
        else:
            logging.warning("「{}」の記事の内容が見つかりませんでした:".format(url))

    return result_news


def save_result_csv(list, name):
    lists = []
    for row in list:
        if row[0]:
            lists.append(row)

    df = pd.DataFrame(lists)
    df.to_csv('data/csv/news/' + name + '.csv', header=None, index=None)
    logging.warning("save OK! ： {}".format(name))


def summary(text):
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    # 入れないと安定しない（エラーが起こる）
    key = tagger.parse(text)
    corpus = []
    for row in key.split("\n"):
        word = row.split("\t")[0]
        if word == "EOS":
            break
        else:
            corpus.append(word)
    # 抽出された単語をスペースで連結
    # 末尾の'。'は、この後使うtinysegmenterで文として分離させるため。
    parser = PlaintextParser.from_string(text, Tokenizer('japanese'))

    summarizer = LexRankSummarizer()
    summarizer.stop_words = [' ']  # スペースも1単語として認識されるため、ストップワードにすることで除外する

    # sentencres_countに要約後の文の数を指定します。
    summary = summarizer(document=parser.document, sentences_count=3)
    b = []
    for sentence in summary:
        b.append(sentence.__str__())

    if str(''.join(b)) == "":
        b = ''.join(corpus)
    return ''.join(b)


def shap_text(content):
    news_content = re.sub(r'　', '', content)
    news_content = re.sub(r' ', '', news_content)
    # 文字の整形（改行削除）
    news_content = "".join(news_content.splitlines())
    # 絵文字を削除
    news_content = ''.join(
        c for c in news_content if c not in emoji.UNICODE_EMOJI)
    # URL削除
    if not len(re.sub(r'[^ ]+\.[^ ]+', '', news_content)) == 0:
        news_content = re.sub(r'[^ ]+\.[^ ]+', '', news_content)
    # 全角記号削除
    news_content = re.sub(r'[︰-＠]', '', news_content)
    # 半角記号削除 + 半角数字
    news_content = re.sub(r'[!-@[-`{-~]', '', news_content)
    news_content = summary(news_content)
    return news_content


main()
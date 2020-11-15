#!/usr/bin/python
# -*- coding: utf-8 -*-
"""get_news.py

     * NewsAPIを利用し、関連ニュース記事URLを取得
     * その後、URLごとにスクレイピングを行い、記事を要約
     * 結果をcsvに保存
     *
     * 起動方法
     * $ Python get_news.py

"""

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
    """main処理

    ロギングの設定
    定数、変数の初期設定を行なっている

    Note:
        API_KEY String: NewsAPIキー
        count String: ニュース取得数（最大：100）
        sort String: ニュースの取得順序
        domains [String]: ニュースドメインの指定（スクレイピングで利用）

    """

    formatter = '%(levelname)s/%(asctime)s/%(filename)s(%(lineno)s)/%(message)s '
    logging.basicConfig(format=formatter)

    API_KEY = config.config_news.news_api
    count = "100"
    sort = "publishedAt"
    domains = ["fashionsnap.com", "yahoo.co.jp", "vogue.co.jp", "livedoor.com"]

    execute(API_KEY, count, sort, domains)


def execute(API_KEY, count, sort, domains):
    """execute関数

    処理の実行

    Args:
        API_KEY String: NewsAPIキー
        count String: ニュース取得数（最大：100）
        sort String: ニュースの取得順序
        domains [String]: ニュースドメインの指定（スクレイピングで利用）

    """
    save_list = []

    trend_list = config.config_news.KEYWORDS
    for keywords in trend_list:
        news_api_urls = create_api_url(keywords, count, sort, domains, API_KEY)
        news_url_list = get_news_url(news_api_urls)
        loging.warning("「{}」のキーワードで以下のURLをスクレイピングします。".format(keywords))
        for url in news_url_list:
            loging.warning("{}".format(url))
        result_news_text_list = scraping(domains, news_url_list)

        flag = config.config_news.FLAG
        if flag == 0:
            save_list += select_news_text(result_news_text_list)
        else:
            save_list += result_news_text_list

    save_result_csv(save_list)


def create_api_url(keywords, count, sort, domains, API_KEY):
    """create_api_url関数

    NewsAPIにリクエストするURLを生成する

    Args:
        keywords　String: 検索キーワードa
        API_KEY String: NewsAPIキー
        count String: ニュース取得数（最大：100）
        sort String: ニュースの取得順序
        domains [String]: ニュースドメインの指定（スクレイピングで利用）

    Returns:
       [String]: NewsAPIにリクエストするURL
    """
    urls = []
    for domain in domains:
        urls.append("https://newsapi.org/v2/everything?" + "pageSize=" + count + "&q=" +
                    keywords + "&sortBy=" + sort + "&domains=" + domain + '&apiKey=' + API_KEY)
    return urls


def get_news_url(urls):
    """get_news_url関数

    ニュースサイトのURLを取得数する

    Args:
        urls [String]: NewsAPIURLのリスト
    Returns:
       [String]: ニュースサイトのURL

    """
    news_url = []
    for url in urls:
        response = requests.get(url)
        json_data = json.loads(response.text)

        if json_data['status'] == "ok":
            for data in json_data["articles"]:
                if not (("collection" in data["url"]) or ("streetstyle" in data["url"])):
                    news_url.append(data["url"])
        else:
            logging.warning(
                "ニュースをリクエストできませんでした：「{}」".format(json_data['status']))

    return news_url


def scraping(domains, news_url_list):
    """get_news_url関数

    ニュースサイトのURLを取得数する

    Args:
        domains [String]: ニュースドメイン配列
        news_url_list [String]: ニュース記事のURL配列
    Returns:
       [[String, String]]: 要約されたニュース記事＋URLのリスト

    """
    result_list = []
    for url in news_url_list:
        for domain in domains:
            if domain in url:
                if domain == "fashionsnap.com":
                    result_list += news_scraping_fashionsnapcom(url)
                elif domain == "yahoo.co.jp":
                    result_list += news_scraping_yahoo(url)
                elif domain == "vogue.co.jp":
                    result_list += news_scraping_vogue(url)
                elif domain == "livedoor.com":
                    result_list += news_scraping_livedoor(url)
                else:
                    logging.warning("スクレイピングできるurlではありませんでした。：{}".format(url))

    return result_list


def news_scraping_yahoo(url):
    """news_scraping_yahoo関数
    Yahooニュース記事のスクレイピング

    Args:
        url String: Yahooニュース記事のURL配列
    Returns:
        [[String, String]]: 要約されたYahooニュース記事＋URLのリスト
    Note:
        403 Forbidden回避するためユーザーエージェント情報を載せている
        headers = {
            "User-Agent": config.HEADER
        }
    """
    result_news = []

    headers = {
        "User-Agent": config.HEADER
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find(class_='article_body') is not None:
        news_content = soup.find(class_='article_body').text
        news_content = shap_text(news_content)
        if not news_content == "":
            result_news.append([news_content, url])
    else:
        logging.warning("「{}」の記事の内容が見つかりませんでした".format(url))

    return result_news


def news_scraping_fashionsnapcom(url):
    """news_scraping_fashionsnapcom関数
    fashionsnapcom記事のスクレイピング

    Args:
        url String: fashionsnapcom記事のURL
    Returns:
        [[String, String]]: 要約されたfashionsnapcom記事＋URLのリスト
    Note:
        403 Forbidden回避するためユーザーエージェント情報を載せている
        headers = {
            "User-Agent": config.HEADER
        }
    """
    result_news = []

    headers = {
        "User-Agent": config.HEADER
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find('article') is not None:
        if soup.find('article').a is not None:
            soup.find('article').a.decompose()

        news_content = soup.find('article').text
        news_content = re.sub(r'全て表示する', '', news_content)
        news_content = re.sub(r'Update【年月日追加】', '', news_content)
        news_content = re.sub(r'Update【年月日続報】', '', news_content)
        news_content = shap_text(news_content)

        if not news_content == "":
            news_content.strip()
            result_news.append([news_content, url])
    else:
        logging.warning("「{}」の記事の内容が見つかりませんでした:".format(url))

    return result_news


def news_scraping_vogue(url):
    """news_scraping_vogue関数
    vogue記事のスクレイピング

    Args:
        url String: vogue記事のURL
    Returns:
        [[String, String]]: 要約されたvogue記事＋URLのリスト
    Note:
        403 Forbidden回避するためユーザーエージェント情報を載せている
        headers = {
            "User-Agent": config.HEADER
        }
    """
    result_news = []

    headers = {
        "User-Agent": config.HEADER
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find(class_='MainContentWrapper-s89gjf-14') is not None:
        news_content = soup.find(
            class_='MainContentWrapper-s89gjf-14').text
        news_content = shap_text(news_content)
        if not news_content == "":
            result_news.append([news_content, url])
    else:
        logging.warning("「{}」の記事の内容が見つかりませんでした".format(url))
    return result_news


def news_scraping_livedoor(url):
    """news_scraping_livedoor関数
    livedoorニュース記事のスクレイピング

    Args:
        url String: livedoorニュース記事のURL配列
    Returns:
        [[String, String]]: 要約されたlivedoorニュース記事＋URLのリスト
    Note:
        403 Forbidden回避するためユーザーエージェント情報を載せている
        headers = {
            "User-Agent": config.HEADER
        }
    """
    result_news = []

    headers = {
        "User-Agent": config.HEADER
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        if soup.article.find(class_="articleBody") is not None:
            if soup.article.find(class_="articleBody").a is not None:
                soup.article.find(class_="articleBody").a.decompose()

            news_content = soup.article.find(class_="articleBody").text
            news_content = shap_text(news_content)
            if not news_content == "":
                result_news.append([news_content, url])
        else:
            logging.warning("「{}」の記事の内容が見つかりませんでした".format(url))
    except AttributeError:
        pass

    return result_news


def save_result_csv(list):
    """save_result_csv関数

    csvに結果を保存する

    Args:
        list [[String, String]]: 保存する内容
    """
    lists = []
    for row in list:
        lists.append(row)

    df = pd.DataFrame(get_unique_list(lists))
    df.to_csv(config.config_news.SAVEPATH + config.config_news.SAVEFILENAME, header=None, index=None)
    logging.warning("save OK! ： {}".format(config.config_news.SAVEFILENAME))


def summary(text):
    """summary関数

    summaryを利用した文章要約メソッド

    Args:
        text String: 要約するテキスト

    Returns:
        String: 要約されたテキスト

    Note:
        MeCabとneologd辞書を利用している
        変数「sentences_count」の値を変えることで文章の長さ「（。）の数」を変更可能
        要約出来なかった文章、またはからの文章はここで排除している
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

    parser = PlaintextParser.from_string(text, Tokenizer('japanese'))

    summarizer = LexRankSummarizer()
    summarizer.stop_words = [' ']

    summary = summarizer(document=parser.document, sentences_count=3)
    b = []
    for sentence in summary:
        b.append(sentence.__str__())

    if str(''.join(b)) == "":
        b = ""
    return ''.join(b)


def shap_text(content):
    """shap_text関数

    テキストを整形（絵文字や記号の削除等）

    Args:
        content String: 整形するテキスト

    Returns:
        String: 整形されたテキスト
    Note:
        re.compile("[!-/:-@[-`{-~]"): 半角記号削除 + 半角数字
        r'[︰-＠]': 全角記号
        r'[^ ]+\.[^ ]+': URL

    """
    news_content = summary(content)
    news_content = re.sub(r'　', '', news_content)
    news_content = re.sub(r' ', '', news_content)
    news_content = "".join(news_content.splitlines())
    news_content = ''.join(
        c for c in news_content if c not in emoji.UNICODE_EMOJI)
    if not len(re.sub(r'[^ ]+\.[^ ]+', '', news_content)) == 0:
        news_content = re.sub(r'[^ ]+\.[^ ]+', '', news_content)
    news_content = re.sub(r'[︰-＠]', '', news_content)
    news_content = re.sub(re.compile("[!-/:-@[-`{-~]"), '', news_content)
    return news_content


def select_news_text(news_list):
    """select_news_text関数

    取得したニュース記事をトレンドコーパスに合わせて選別する
    選別法：トレンドコーパス内の単語が使われているかどうか

    Args:
        news_list [String]: 選別するテキスト

    Returns:
        [String]: 選別されたテキストリスト

    """
    result_list = []

    trend_list = config.config_news.TREND
    for news in news_list:
        num_list = []
        for trend in trend_list:
            num_list.append(news[0].count(trend))

        if sum(num_list) > config.config_news.INCLUDEKEYWORDSNUM:
            result_list.append(news)

    return result_list


def get_unique_list(seq):
    """get_unique_list関数

    配列整形メソッド

    Args:
        seq [[String,String]]: 選別するテキスト＋URLのリスト

    Returns:
        [[String,String]]: 選別されたテキスト＋URLのリスト

    """
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]


main()

from gensim.corpora.dictionary import Dictionary
from gensim import corpora
import gensim
import MeCab
import csv
from gensim.models import LdaModel
import re
from config import config


def main():
    common_texts = []
    news_contents = get_csv_text(config.NEWSPATH + config.NEWSNAME + ".csv")
    for content in news_contents:
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


def get_csv_text(path):
    list = []
    file = path
    with open(file, 'r') as f:
        # カラムの値を抽出（ツイート内容）
        for row in csv.reader(f):
            text = "".join(row[0].splitlines())
            if not len(text) == 0:
                list.append(text)

    return list


main()

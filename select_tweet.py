import glob
import pandas as pd
from config import config


def main():
    tweet_csv_path_list = glob.glob(config.config_tweet.SAVEPATH + "*.csv")

    no_select_nums = []
    for tweet_csv_path in tweet_csv_path_list:
        no_select_nums.append(
            [read_csv_len(tweet_csv_path, 0), tweet_csv_path.split("/")[-1].replace(".csv", "")])

    select_nums = []
    for tweet_csv_path in tweet_csv_path_list:
        select_nums.append(
            [read_csv_len(tweet_csv_path, 1), tweet_csv_path.split("/")[-1].replace(".csv", "")])

    result_list = []
    for select in select_nums:
        for no_select in no_select_nums:
            if no_select[1] == select[1]:
                rate_of_change = (no_select[0] - select[0]) / no_select[0]
                probability = select[0] / no_select[0]
                result_list.append([rate_of_change, probability, select[1]])

    save_result_csv(result_list)
    print(result_list)


def select_key():

    result_list = []
    df = pd.read_csv(config.config_trend.SAVEPATH + config.config_trend.SAVEFILENAME, sep=',',
                     encoding='utf-8', index_col=False, header=None)
    trend_list = list(df[0])
    text = '|'.join(trend_list)

    return text


def read_csv_len(tweet_csv_path, flag):
    df = pd.read_csv(tweet_csv_path, header=None)
    num = 0
    if flag == 1:
        regix = select_key()
        num = len(df[df[0].str.contains(regix)])
    else:
        num = len(df)

    return num


def save_result_csv(list):
    """save_result_csv関数

    csvに結果を保存する

    Args:
        list [[String, String]]: 保存する内容
    """

    df = pd.DataFrame(list, columns=["変化率", "確率", "インフルエンサー名"])
    df.to_csv("data/csv/tweet/rate_of_change/rate_of_change.csv", index=None)


main()

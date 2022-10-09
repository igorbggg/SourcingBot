import json
import logging
import os
from pprint import pprint

import requests
from pymongo import MongoClient

url_filter = None


def connect_to_newsStream(db_string: str):
    client = MongoClient(db_string)
    return client['newsStream']['rssFeeds']


def insert_news_item_to_rssFeed(db_string: str, rss_feed_entryes):
    client = MongoClient(db_string)
    logging.info('Connected to db')
    for entry in rss_feed_entryes:
        client['newsStream']['rssFeeds'].update_one(filter=entry, update={'$set': entry}, upsert=True)
        logging.info('Added RSS feed')
    client.close()
    logging.info('Connection closed')


def call_cloud_url2text(cloud_url: str, url: str) -> [str, str]:
    req = requests.post(cloud_url, json={"kwargs": {"url": url}})
    if req.status_code == 200:
        return req.text
    raise Exception(f'Cloud function call failed!: {req.status_code}')


def get_empty_ds_summary_feed(db_string: str):
    client = MongoClient(db_string)
    logging.info('Connected to db')
    i = 0
    j = 0
    for x in client['newsStream']['rssFeeds'].find({"ds_summary": None, "summary": {"$exists": False}},
                                                   {"link": 1, "links": 1}):
        pprint(f'{i}: {x["_id"]}')
        if x['link']:
            j += 1
        i += 1
    pprint(f'{i}: {j}')
    client.close()
    logging.info('Connection closed')


def set_repost_cnt_from_ap_uid(db_string: str):
    client = MongoClient(db_string)
    logging.info('Connected to db')
    i = 0
    j = 0
    for x in client['newsStream']['rssFeeds'].find({"repost_cnt": None, "ap_uid": {"$exists": True}}, {"ap_uid": 1}):
        pprint(f'{i}: {x["ap_uid"]}')
        if x['ap_uid']:
            client['newsStream']['rssFeeds'].update_one({"_id": x["_id"]},
                                                        {"$set": {"repost_cnt": len(json.loads(get_ap_data_from_cloud(x['ap_uid'])['result_json'])['urls'])-1}})
            j += 1
        i += 1
    pprint(f'{i}: {j}')
    client.close()
    logging.info('Connection closed')


def set_ap_uid_from_summary_feed(db_string: str):
    client = MongoClient(db_string)
    logging.info('Connected to db')
    i = 0
    j = 0
    for x in client['newsStream']['rssFeeds'].find(
            {"repost_cnt": None, "summary": {"$exists": True}, "link": {"$exists": True}}, {"summary": 1, "link": 1}):
        pprint(f'{i}: {x["_id"]}')
        if x['summary'] and is_url_in_list(x['link']):
            client['newsStream']['rssFeeds'].update_one({"_id": x["_id"]},
                                                        {"$set": {"ap_uid": get_ap_uid_from_cloud(x['summary'])}})
            j += 1
        i += 1
    pprint(f'{i}: {j}')

    client.close()
    logging.info('Connection closed')


def is_url_in_list(url: str):
    global url_filter
    if not url_filter:
        with open('settings/urls_filter.list') as filter_list:
            url_filter = filter_list.readlines()
        url_filter = list(map(lambda x: x.replace('\n', ''), url_filter))
    result = False
    for uf in url_filter:
        if uf in url:
            return True
    return False


def get_ap_data_from_cloud(ap_uid: str) -> str | None:
    cloud_function_url = 'https://functions.yandexcloud.net/d4e7ecsptedpa99mnceh'

    response = requests.post(
        url=cloud_function_url,
        json=dict(
            kwargs=dict(
                text_uid=ap_uid,
                userkey=os.getenv('TEXTRU_USERKEY')
            )
        )
    )

    if response.status_code != 200:
        raise Exception(f'Не удалось обратиться к облачной функции; {cloud_function_url=}; {response.status_code=}')

    data = response.json()

    if data['result']['status'] != 200:
        raise Exception(f"Сервис text.ru вернул не 200; {cloud_function_url=}; {data['result']['status']=}")

    ap_data = data['result']['data']

    return ap_data


def get_ap_uid_from_cloud(text: str) -> str | None:
    cloud_function_url = 'https://functions.yandexcloud.net/d4eihgtjsqo0ejcekq2r'

    response = requests.get(
        url=cloud_function_url,
        json=dict(
            kwargs=dict(
                text=text,
                userkey=os.getenv('TEXTRU_USERKEY')
            )
        )
    )

    if response.status_code != 200:
        raise Exception(f'Не удалось обратиться к облачной функции; {cloud_function_url=}')

    data = response.json()

    if data['result']['status'] != 200:
        raise Exception(f"Сервис text.ru вернул не 200; {cloud_function_url=}; {data['result']['status']=}")

    return data['result']['text_uid']


def set_insight_from_ds(db_string: str):
    client = MongoClient(db_string)
    logging.info('Connected to db')
    i = 0
    j = 0
    for x in client['newsStream']['rssFeeds'].find(
            {"ds_insight": None, "summary": {"$exists": True}}, {"summary": 1, "ds_insight": 1}):
        pprint(f'{i}: {x["_id"]}')
        if x['summary']:
            client['newsStream']['rssFeeds'].update_one({"_id": x["_id"]},
                                                        {"$set": {"ds_insight": get_insight_from_ds(x['summary'])}})
            j += 1
        i += 1
    pprint(f'{i}: {j}')

    client.close()
    logging.info('Connection closed')


def get_insight_from_ds(text: str):
    url = 'http://0.0.0.0:8989/predict_insight'

    response = requests.post(
        url=url,
        json=dict(
            text=text
        )

    )

    if response.status_code != 200:
        return None

    data = response.json()

    return data

import os

from rss_tools.token_worker.tools import TokenService
from rss_tools.rss_loader.tools import get_rss_from_url
from db_tools.mongo_tools.crud import insert_news_item_to_rssFeed
from pprint import pprint

def main():
    pprint('Script started!')
    mongo_token = TokenService('tokens/mongodb.token').token
    textru_token = TokenService('tokens/textru.token').token
    os.environ['TEXTRU_USERKEY'] = textru_token

    with open('settings/sources.list', 'r') as source:
        sources = source.readlines()
        sources = list(map((lambda x: x.replace('\n', '')), sources))
    for source in sources:
        news = get_rss_from_url(source)
        insert_news_item_to_rssFeed(mongo_token, news.entries)
    pprint('Script finished successfully!')
    return 0


if __name__ == '__main__':
    main()

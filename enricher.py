import os

from rss_tools.token_worker.tools import TokenService
from rss_tools.rss_loader.tools import get_rss_from_url
from db_tools.mongo_tools.crud import set_repost_cnt_from_ap_uid, set_ap_uid_from_summary_feed, set_insight_from_ds
from pprint import pprint

def main():
    pprint('Script started!')
    mongo_token = TokenService('tokens/mongodb.token').token
    textru_token = TokenService('tokens/textru.token').token
    os.environ.get('TEXTRU_USERKEY',textru_token)
    set_ap_uid_from_summary_feed(mongo_token)
    set_repost_cnt_from_ap_uid(mongo_token)
    set_insight_from_ds(mongo_token)

    pprint('Script finished successfully!')
    return 0


if __name__ == '__main__':
    main()

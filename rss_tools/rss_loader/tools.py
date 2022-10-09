import feedparser

def get_rss_from_url(url:str) -> []:
    return feedparser.parse(url)


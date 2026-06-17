import feedparser
from datetime import datetime, timezone, timedelta
from time import mktime
from bs4 import BeautifulSoup
import extractor

def scrape_latest_rss_warnings(url="https://rss.mtsz.pl/gis-ostrzezenia.xml"):
    feed = feedparser.parse(url, agent="EatSafe-App/1.0")

    if not feed.entries:
        print("Error: No entries found.")
        return []

    warnings=[]

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        # converting to RMD HMS format, used in mysql
        # the rss may not contain a publication date
        # in such case, publication_date will be None
        publication_date=None
        if hasattr(entry, "published_parsed"):
            dt_utc=datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            pl_timezone=timezone(timedelta(hours=2))
            publication_date=dt_utc.astimezone(pl_timezone).strftime("%Y-%m-%d %H:%M:%S")


        if hasattr(entry, 'content') and isinstance(entry.content, list) and len(entry.content) > 0:
            raw_html = entry.content[0].value
        else:
            raw_html = ""

        ext_data=extractor.extract(raw_html)
        warnings.append({
            "title":title,
            "link":link,
            "publication_date":publication_date,
            "raw_html": raw_html,

            "cleared_html":ext_data.get('cleared_html'),
            "images":ext_data.get('images'),
            "danger": ext_data.get('danger'),
            "product": ext_data.get('product'),
            "brand": ext_data.get('brand'),
            "recommendations": ext_data.get('recommendations')
        })
    return warnings


if __name__ == "__main__":
    data=scrape_latest_rss_warnings()
    extractor.check_missing(data)
    # for d in data:
    #     print(d["title"])
    #     print()
    #     print(d["link"])
    #     print()
    #     print(d["publication_date"])
    #     print()
    #     print()
    #     print(d["images"])
    #     print()
    #     print(d["danger"])
    #     print()
    #     print(d["product"])
    #     print()
    #     print(d["brand"])
    #     print()
    #     print(d["recommendations"])
    #     print()
    #     # print(d["raw_html"])
    #     # print()
    #     # print(d["cleared_html"])
    #     print("=============")

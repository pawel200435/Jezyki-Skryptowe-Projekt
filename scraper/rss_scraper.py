import feedparser
from datetime import datetime
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
        publication_date = datetime.fromtimestamp(mktime(entry.published_parsed)).strftime('%Y-%m-%d %H:%M:%S') if hasattr(entry, 'published_parsed') else None


        if hasattr(entry, 'content') and isinstance(entry.content, list) and len(entry.content) > 0:
            raw_html = entry.content[0].value
        else:
            raw_html = ""

        if raw_html:
            soup = BeautifulSoup(raw_html, "html.parser")
            # we separate the gallery section to extract image links
            gallery_section=soup.find("div", class_="gallery")

            if gallery_section:
                images = gallery_section.find_all("img", src=True)
                # a set of tuples, first argument being imgs description, and second one being the link
                # also small check - GIS always includes their graphic, and it always ends in 1920x810
                img_urls = {(tag.get('alt',""), tag['src']) for tag in images if "resolution/1920x810" not in tag['src']}
                # we can destroy this section since we've already extracted our urls
                gallery_section.decompose()
            else:
                img_urls = []

            # There is always a small header telling the reader how many photos are there in the gallery
            # We must get rid of it
            photos_header = soup.find("h3", string=lambda t: t and "Zdjęcia" in t)
            if photos_header:
                photos_header.decompose()

            # also checking for text which is hidden in reader-view only
            for hidden_text in soup.find_all(class_="sr-only"):
                hidden_text.decompose()

            # clearing the html
            cleared_html = soup.get_text(separator="\n", strip=True)

        else:
            cleared_html = ""
            img_urls = []

        warnings.append({
            "title":title,
            "link":link,
            "publication_date":publication_date,
            "cleared_html":cleared_html,
            "images":img_urls,
            "raw_html":raw_html
        })
    return warnings


if __name__ == "__main__":
    data = scrape_latest_rss_warnings()
    for d in data:
        print(d["title"])
        print()
        print(d["publication_date"])
        print()
        print(d["link"])
        print()
        # print(d["cleared_html"])
        # print()
        print(d["images"])
        print()
        print(extractor.parse_data_from_html(d["raw_html"]))
        print("=================================================\n\n")

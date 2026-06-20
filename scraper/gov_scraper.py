from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import extractor
from fake_useragent import UserAgent


def scrape_gov_data(url="https://www.gov.pl/web/gis/ostrzezenia"):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    URL_BASE = "https://www.gov.pl"
    pg_count=0

    try:
        # checking connection
        initial_response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(initial_response.content, "html.parser")

        # extracting last page number
        pg_count_tag = soup.find("a", class_="pagination__total-count")
        pg_count = int(pg_count_tag.get_text()) if pg_count_tag else 1
        print(f"found {pg_count} pages")

    except Exception as e:
        print("Error while initialising")
        return []

    result=[]

    for i in range(1, 3):
        print(f"processing page {i}/{pg_count}")
        page_url=url if i==1 else f"{url}?page={i}"

        try:
            # load new page
            response = requests.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print("connection error")
                continue

            # soupify the response
            page_soup = BeautifulSoup(response.text, "html.parser")
            # the articles are stored as <li> blocks
            list_items = page_soup.find_all("li")

            for index, art in enumerate(list_items):
                # look for list item's title
                title_div = art.find("div", class_="title")
                # if you cant find one, the list item is not an article
                if not title_div:
                    continue

                # search for a link section
                link_tag = title_div.find("a")
                # if you cant find one, the list item is not an article
                # also link is in href
                if link_tag and 'href' in link_tag.attrs:
                    # the link is relative, we need to build it from base
                    full_link = URL_BASE + link_tag["href"]
                    title = link_tag.get_text()
                    # logging to lest user know of progress
                    print(f" Loading: {title[:50]}...")
                    date = None
                    # date extraction logic
                    event_div = art.find("div", class_="event")
                    if event_div:
                        date_span = event_div.find("span", class_="date")
                        if date_span:
                            date_raw = date_span.get_text(strip=True)
                            if date_raw:
                                date = datetime.strptime(date_raw, "%d.%m.%Y")
                    # looking for archives, last few <li> direct you to fe ostrzezenia-2019
                    if "ostrzezenia-20" in full_link:
                        print(f"scraping data from link: {full_link}")
                        scraped_data = scrape_gov_data(full_link)
                        result=result + scraped_data
                    # get article's raw html
                    else:
                        raw_html = get_raw_html(full_link)
                        # and extract it using extractor module
                        ext_data = extractor.extract(raw_html)
                        result.append({
                            "title": title,
                            "link": full_link,
                            "publication_date": date,
                            "raw_html": raw_html,

                            "cleared_html": ext_data.get("cleared_html"),
                            "images": ext_data.get("images"),
                            "danger": ext_data.get("danger"),
                            "product": ext_data.get("product"),
                            "brand": ext_data.get("brand"),
                            "recommendations": ext_data.get("recommendations"),
                        })
                        time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"error while paginating: {e}")
    return result
def get_raw_html(art_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) EatSafe-Projekt-Akademicki'}
    try:
        response = requests.get(art_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # look for <article> block
            article = soup.find("article")
            if article:
                return str(article)
        else:
            print(f" [!] Błąd pobierania artykułu: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f" [!] Błąd sieci przy pobieraniu artykułu: {e}")
    return ""



if __name__ == "__main__":
    # extractor.check_missing(scrape_gov_data())
    for d in scrape_gov_data():
        print(d["title"])
        print(d["product"])
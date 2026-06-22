from bs4 import BeautifulSoup
# base for images
URL_BASE = "https://www.gov.pl"
# keyword dictionaries
# for batches and brands we have two kinds of keywords dictionaries
# primary - those are the desirable ones
# secondary - if we didn't find any primary kws, secondary ones will do better than nothing
KW_BATCH_PRIMARY = ("partii", "partia", "partie", "numer", "ean", "referencyjny", "artykułu", "artykuł")
KW_BATCH_SECONDARY = ("kod", "kreskowy", "trwałości", "termin")
KW_BATCH_ALL = KW_BATCH_PRIMARY + KW_BATCH_SECONDARY

KW_PRODUCT = ("produkt", "nazwa", "produktu")

KW_BRAND_PRIMARY = ("firmy", "firma", "marka", "producent", "wyprodukowano")
KW_BRAND_SECONDARY = ("dystrybutor", "pakowano", "importer")
KW_BRAND_ALL = KW_BRAND_PRIMARY + KW_BRAND_SECONDARY

# those are words, that will be ignored
KW_IGNORE = (
    "szczegóły", "identyfikacja", "zdjęcia", "wycofywanych",
    "zalecenia dla konsumentów", "działania podjęte", "zagrożenie",
    "organy urzędowej", "oraz"
)

# strict product labels, used in part 3 of extract function
# they are used in the process of "gathering" batches
STRICT_PRODUCT_LABELS = {"nazwa produktu", "nazwa", "produkt", "nazwa produktu/ odmiana"}
STRICT_BATCH_LABELS = {
    "numer partii", "nr partii", "partia", "partie", "numery partii",
    "kod ean", "ean", "kod kreskowy", "numer serii", "nr serii",
    "artykuł", "nr artykułu", "numer artykułu", "data minimalnej trwałości", "termin przydatności"
}
STRICT_BRAND_LABELS = {"marka", "firma", "producent", "dystrybutor", "wyprodukowano dla", "importer"}


def format_img_src(src):
    # support function for cleaning img src
    if not src or "data:image/" in src:
        return "no image"
    else:
        if src.startswith("/photo/"):
            return URL_BASE + src
        return src


def extract(html_content):

    result={
        'danger': "",
        'product' : set(),
        'brand':"",
        'recommendations':"",
        'cleared_html':"",
        'images':set(),
    }

    soup = BeautifulSoup(html_content, "html.parser")
    # first part - lets check if there is a table containing product names and batch codes
    table=soup.find('table')
    if table:
        rows=table.find_all("tr")

        if rows:
            # we iterate the first row in hopes of finding the descriptions, which index contains what
            cols_raw=rows[0].find_all(["td", "th"])
            cols = [col.get_text(strip=True).lower() for col in cols_raw]
            img_idx, batch_idx, product_idx = -1, -1, -1

            for i, col_text in enumerate(cols):
                col = col_text.lower()
                # checking for product name, batch and photos
                if "zdjęci" in col:
                    img_idx = i

                elif batch_idx == -1 and any(k in col for k in KW_BATCH_ALL):
                    batch_idx = i

                elif product_idx == -1 and any(k in col for k in KW_PRODUCT) and "numer" not in col:
                    if not batch_idx == i:
                        product_idx = i

            # we remember the product's name so in case of
            # a few different batches share the same name
            # we can add them as separate products
            current_table_prod = ""

            # now we iterate on the remaining rows
            for row in rows[1:]:
                if row.find("th"):
                    continue

                cells_raw = row.find_all("td")

                # search for <img> blocks within these cols
                if img_idx != -1 and img_idx < len(cells_raw):
                    cell=cells_raw[img_idx]
                    imgs=cell.find_all("img", src=True)
                    if imgs:
                        # create a tuple of a description and src
                        img_final = {
                            (tag.get('alt', ""),format_img_src(tag.get('src', "")))for tag in imgs
                        }
                        # add newly found images to result
                        result['images'].update(img_final)

                if cells_raw:
                    # extracting text from cells
                    cells = [cell.get_text(strip=True) for cell in cells_raw]
                    prod_batch = ""
                    # we need to calculate an offset - sometimes the columns dont have the same
                    # amounts of cells, fe 1 product name on the left and 4 different serial numbers on the right
                    offset = len(cols) - len(cells)

                    # we try to assess the product's name
                    local_prod_idx = product_idx - offset
                    if 0 <= local_prod_idx < len(cells) and cells[local_prod_idx]:
                        current_table_prod = cells[local_prod_idx]

                    # we try to get the batch number minding the offset
                    local_batch_idx = batch_idx - offset
                    if 0 <= local_batch_idx < len(cells):
                        prod_batch = cells[local_batch_idx]

                    # we save the product data using current name and batch code
                    if current_table_prod and prod_batch:
                        result['product'].add((current_table_prod, prod_batch))



    # second part - the interesting data is usually in <strong> blocks
    prod_name, prod_batch = "", ""
    for strong in soup.find_all("strong"):
        # skip if currently in table, parsed before
        if strong.find_parent("table"):
            continue

        # list item logic
        if strong.parent and strong.parent.name == "li":
            parent_list = strong.find_parent(["ul", "ol"])
            prev_text = parent_list.find_previous(string=True) if parent_list else strong.find_previous(string=True)
        else:
            # we search for immediate text neighbor of label <strong>
            prev_text = strong.find_previous(string=True)

        # we skip spaces and enters
        while prev_text and not prev_text.strip():
            prev_text = prev_text.find_previous(string=True)

        # label and value
        txt = ""
        val = strong.get_text(separator=" | ", strip=True)

        # colon logic
        # if colon in prev_text, then prev_text is a label
        if prev_text and ":" in prev_text:
            txt=prev_text.strip().lower()
        # if colon in val then it's a formating mistake
        # or label is also bolded
        elif ":" in val:
            # split into two
            parts = val.split(":", 1)
            # if the label is lower than 30 sgns
            # then it's probably correct
            if len(parts[0])<30:
                txt=parts[0].strip().lower()
                val=parts[1].strip()
            else:
                # the label is in previous line
                txt=prev_text.strip().lower() if prev_text else ""
        else:
            txt = prev_text.strip().lower() if prev_text else ""

        # check for ignored keywords in current label
        if len(txt) > 60 or any(bad in txt for bad in KW_IGNORE):
            txt = ""

        if txt:
            # logical checks, for categorizing
            if any(k in txt for k in KW_BATCH_PRIMARY) or (any(k in txt for k in KW_BATCH_SECONDARY) and not result["product"]):
                prod_batch = val

            elif any(k in txt for k in KW_PRODUCT) and "numer" not in txt:
                prod_name = val

            elif any(k in txt for k in KW_BRAND_PRIMARY) or (any(k in txt for k in KW_BRAND_SECONDARY) and not result["brand"]):
                result['brand']=val

        # appending product lists - sometimes one warning contains more than one product
        if prod_name and prod_batch:
            result["product"].add((prod_name,prod_batch))
            # we reset only the batch - if we have few different batches we need to save the product's name
            prod_batch = ""

    # search for danger and recommendations sections - those are
    # usually in <h3> blocks
    # but for older articles they will be stored in <p> blocks
    h3_danger=find_in_h3("Zagrożenie", soup)
    h3_recommendation=find_in_h3("Zalecenia", soup)
    result['danger']=find_in_p("Zagrożenie", soup) if not h3_danger else h3_danger
    result['recommendations']= find_in_p("Zalecenia", soup) if not h3_recommendation else h3_recommendation


    # we separate the gallery section to extract image links
    gallery_section = soup.find("div", class_="gallery")
    if gallery_section:
        images = gallery_section.find_all("img", src=True)
        # a set of tuples, first argument being imgs description, and second one being the link
        img_urls={(tag.get('alt', ""), format_img_src(tag['src'])) for tag in images }
        result['images'].update(img_urls)
        # we can destroy this section since we've already extracted our urls
        gallery_section.decompose()

    # if we didn't find any images, we have to take anything the article has to offer
    if not result.get('images'):
        article=soup.find("article")
        if article:
            img=article.find_all("img", src=True)
            img_urls={(tag.get('alt', ""), format_img_src(tag['src'])) for tag in img}
            result['images'].update(img_urls)

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
    result['cleared_html'] = cleared_html


    # part 3 - plain text check, used when no <strong> labels found,

    # split html into lines
    lines=cleared_html.split("\n")
    current_product_name=""
    gathering_batches=False


    for i, line in enumerate(lines):
        line_clean = line.strip()
        # if current line is empty we stop gathering batches
        if not line_clean:
            gathering_batches = False
            continue

        # get rid of unnecessary list symbols in value
        clean_val = line_clean.lstrip("•-*▪ ").strip()
        # if we found any of the ignored keywords in value, we've must have hit regular article content,\
        # stop gathering
        if any(bad in clean_val.lower() for bad in KW_IGNORE):
            gathering_batches = False
            continue

        # split around the colon
        parts = line_clean.split(":", 1)

        # checking for irregularities in first part
        if len(parts) < 2 or len(parts[0])>60:
            # if currently gathering and found sth interesting, add it to result else stop gahtering
            if gathering_batches and clean_val and current_product_name:
                if len(clean_val) < 30:
                    result['product'].add((current_product_name, clean_val))
                else:
                    gathering_batches = False
            continue

        raw_label = parts[0].lower().strip()
        value = parts[1].strip()
        # clean the label of numbering
        label = raw_label.lstrip("0123456789.- ")

        # again ignore keywords from the label
        if len(label) > 60 or any(bad in label for bad in KW_IGNORE):
            continue

        # check for exact labels
        is_product_label = label in STRICT_PRODUCT_LABELS
        is_batch_label = label in STRICT_BATCH_LABELS
        is_brand_label = label in STRICT_BRAND_LABELS


        if not (is_product_label or is_batch_label or is_brand_label):
            gathering_batches = False
            continue

        gathering_batches = False

        # lookahead logic
        # sometimes the data for our label is hidden few lines lower
        if not value:
            # look in 5 next lines
            for j in range(i+1, min(i+4, len(lines))):
                next_line = lines[j].strip()
                if next_line and next_line != ":":
                    if ":" in next_line and len(next_line.split(":", 1)[0]) <= 60:
                        break
                # if there is a valid value in next line then clean it and save it
                value = next_line.lstrip("•-*▪ ").strip()
                break

        # if didn't find anything just skip
        if not value:
            continue

        # we look for brands if it's still empty
        if not result['brand'] and is_brand_label:
            result['brand'] = value



        if is_product_label:
            current_product_name = value

        elif is_batch_label:
            gathering_batches = True
            batch_nr = value
            # if we have a name and a batch, then just save it
            if current_product_name:
                result['product'].add((current_product_name, batch_nr))

    return result



def find_in_h3(word:str, soup):
    # we search for given word
    header = soup.find("h3", string=lambda t: t and word in t)
    if header:
        # info is usually stored in a paragraph
        paragraph = header.find_next_sibling("p")

        if paragraph:
            return paragraph.get_text(strip=True, separator=" ")
        # however sometimes, the data is surrounded by a div
        else:
            paragraph = header.find_next_sibling("div").find("p")

            if paragraph:
                return paragraph.get_text(strip=True, separator=" ")

    return None


def find_in_p(word: str, soup):
    for p in soup.find_all("p"):
        # extract the text and separate it in lines
        text = p.get_text(separator="\n", strip=True)

        if word.lower() in text.lower():
            # if the word we are looking for is within 20 first signs it usually means it's
            # the label that we are looking for
            if text.lower().find(word.lower()) < 20:
                # we check if the paragraph contained <br> separating our data
                # separate the text and remove empty lines
                lines = [line.strip() for line in text.split("\n") if line.strip()]

                if len(lines) > 1:
                    # extract content from text
                    content = " ".join(lines[1:]).strip(" :")
                    if content:
                        return content

                # there was no <br>, meaning that data is stored with the label
                if ":" in text:
                    content = text.split(":", 1)[1].strip()
                    # if there is still some text left:
                    if content:
                        return content

                # there was no <br> or ':', meaning the data is within the next <p>
                next_p = p.find_next_sibling("p")
                if next_p:
                    return next_p.get_text(separator=" ", strip=True)

    return None

def check_missing(data):
    for d in data:
        key_list = d.keys()
        # check for missing keys
        missing_data = [key for key in key_list if not d.get(key)]
        print(f"Title: {d.get('title')}")
        if missing_data:
            print("missing data:")
            for i in missing_data:
                print(i)
        else:
            print("all data extracted successfully")
        print("=================================================\n\n")

if __name__ == "__main__":
    f=open("test.txt", "r", encoding="utf-8")
    html = f.read()
    print(extract(html)['product'])
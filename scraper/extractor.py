from bs4 import BeautifulSoup, NavigableString

def extract(html_content):
    URL_BASE = "https://www.gov.pl"
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
        # we iterate the first row in hopes of finding the descriptions, which index contains what
        cols_raw=rows[0].find_all(["td", "th"])
        cols = [col.get_text(strip=True) for col in cols_raw]
        imgIdx, batchIdx, productIdx = -1, -1, -1
        for i, col_text in enumerate(cols):
            col = col_text.lower()
            # checking for product name, batch and photos
            if "zdjęcie" in col or "zdjęcia" in col:
                imgIdx = i

            elif ("partii" in col or "partia" in col or "trwałości" in col or "partie" in col or "ean" in col) and (batchIdx == -1):
                batchIdx = i

            elif ("produkt" in col or "nazwa" in col or "produktu" in col) and "numer" not in col:
                productIdx = i
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
            if imgIdx != -1 and imgIdx < len(cells_raw):
                cell=cells_raw[imgIdx]
                imgs=cell.find_all("img", src=True)
                if imgs:
                    # create a tuple of a description and src
                    # this list comprehension allows us to analyze few different pictures in the same cell
                    img_final = {
                        (
                            tag.get('alt', ""),
                            "No Image" if "data:image" in tag.get('src', "")
                            else URL_BASE + tag.get('src', "") if tag.get('src', "").startswith("/photo/")
                            else tag.get('src', "")
                        )
                        for tag in imgs
                    }# add newly found images to result
                    result['images'].update(img_final)

            if len(cells_raw) > 0:
                # extracting text from cells
                cells = [cell.get_text(strip=True) for cell in cells_raw]
                prod_batch = ""

                # we need to calculate an offset - sometimes the columns dont have the same
                # amounts of cells, fe 1 product name on the left and 4 different serial numbers on the right
                expected_cols = len(cols)
                actual_cols = len(cells)
                offset = expected_cols - actual_cols

                # we try to assess the product's name
                local_prod_idx = productIdx - offset
                if 0 <= local_prod_idx < actual_cols:
                    name_text = cells[local_prod_idx]
                    # we update the name only if its not empty
                    if name_text:
                        current_table_prod = name_text

                # we try to get the batch number minding the offset
                local_batch_idx = batchIdx - offset
                if 0 <= local_batch_idx < actual_cols:
                    prod_batch = cells[local_batch_idx]

                # we save the product data using current name and batch code
                if current_table_prod and prod_batch:
                    result['product'].add((current_table_prod, prod_batch))



    # second part - the interesting data is usually in <strong> blocks
    prod_name, prod_batch = "", ""
    for strong in soup.find_all("strong"):
        if strong.find_parent("table"):
            continue

        if strong.parent and strong.parent.name == "li":
            parent_list = strong.find_parent(["ul", "ol"])
            if parent_list:
                prev_text = parent_list.find_previous(string=True)
            else:
                prev_text = strong.find_previous(string=True)
        else:
            # we search for immediate text neighbor of label <strong>
            prev_text = strong.find_previous(string=True)

        # we skip spaces and enters
        while prev_text and not prev_text.strip():
            prev_text = prev_text.find_previous(string=True)

        txt = ""
        if prev_text:
            txt = prev_text.strip().lower()

        if txt:
            # getting text from strong
            val=strong.get_text(separator=" | ", strip=True)
            if prev_text and ":" in prev_text:
                txt=prev_text.strip().lower()
            # colon in val means that the person in GIS made an input mistake
            elif ":" in val:
                parts = val.split(":", 1)
                if len(parts[0])<30:
                    txt = parts[0].strip().lower()
                    val = parts[1].strip()
                else:
                    txt=prev_text.strip().lower() if prev_text else ""
            else:
                txt=prev_text.strip().lower() if prev_text else ""
            if len(txt)>60:
                txt=""

            # print(txt)
            # logical checks, for categorizing
            if "numer" in txt or "partii" in txt or "partia" in txt or "partie" in txt or "ean" in txt or "referencyjny" in txt or  (("kod" in txt or "trwałości" in txt or "kreskowy" in txt) and not result["product"]):
                # print("Batch")
                prod_batch = val

            elif ("produkt" in txt or "nazwa" in txt or "produktu" in txt) and "numer" not in txt:
                # print("Nazwa")
                prod_name = val

            elif "firmy" in txt or "firma" in txt or "marka" in txt or "dystrybutor" in txt:
                result['brand']=val

            elif not result['brand'] and ("producent" in txt or "wyprodukowano" in txt or "pakowano" in txt or "importer" in txt):
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
        # also small check - GIS always includes their graphic, and it always ends in 1920x810
        img_urls={
            (
                tag.get('alt', ""),
                "No Image" if "data:image/png" in tag['src'] else
                URL_BASE + tag['src'] if tag['src'].startswith("/photo/") else
                tag['src']
            )
            for tag in images
        }
        result['images'].update(img_urls)
        # we can destroy this section since we've already extracted our urls
        gallery_section.decompose()

    # if we didn't find any images, we have to take anything the article has to offer
    if not result.get('images'):
        images=soup.find("article").find_all("img", src=True)
        img_urls={
            (
                tag.get('alt', ""),
                "No Image" if "data:image/png" in tag['src'] else
                URL_BASE + tag['src'] if tag['src'].startswith("/photo/") else
                tag['src']
            )
            for tag in images
        }
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
    # part 3 - if we still didn't find any brands or products,
    # we need to look for them in plaintext
    if not result['brand'] or not result['product']:
        lines=soup.get_text(separator="\n", strip=True).split("\n")
        product_name, batch_nr="",""
        for i, line in enumerate(lines):
            line_low=line.lower()
            parts=line_low.split(":", 1)

            if len(parts) > 1:
                # label is on the left of the colon
                # value is on the right
                label = parts[0].lower()
                value = parts[1].strip()

                if len(label) > 60:
                    continue

                is_valid_label = any(k in label for k in [
                    "firm", "mark", "dystrybutor", "producent", "wyprodukowano",
                    "parti", "trwał", "kreskow", "termin", "ean", "artykuł", "kod",
                    "produkt", "nazw"
                ])


                if is_valid_label and not value:
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and next_line != ":":
                            value = next_line
                            break

                if not value:
                    continue


                # we look for brands if it's still empty
                if not result['brand'] and any(
                        word in label for word in ["firmy", "firma", "marka", "dystrybutor", "producent", "wyprodukowano"]):
                    result['brand'] = value

                # we look for product if we still don't have any
                if not result['product']:

                    # if we have both name and batch we can clear the batch allowing different batches to share same name
                    if any(word in label for word in
                           ["partii", "partia", "trwałości", "partie", "kreskowy", "termin", "ean", "artykułu", "kod"]):
                        batch_nr = value
                    elif any(word in label for word in ["produkt", "nazwa", "produktu"]) and not "numer" in label:
                        product_name = value

                    if product_name and batch_nr:
                        result['product'].add((product_name, batch_nr))
                        batch_nr = ""
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
from bs4 import BeautifulSoup, NavigableString

# this data extractor module seems to work fine for the rss feed part
# obviously it will change when the gov data get imported
def parse_data_from_html(html_content):

    result={
        'danger': "",
        'product' : set(),
        'brand':"",
        'recommendations':"",
    }

    soup = BeautifulSoup(html_content, "html.parser")
    # first part - lets check if there is a table containing product names and batch codes
    table=soup.find('table')

    if table:
        rows=table.find_all("tr")
        # we iterate the first row in hopes of finding the descriptions, which index contains what
        cols_raw=rows[0].find_all(["td", "th"])
        cols = [col.get_text(strip=True) for col in cols_raw]
        batchIdx, productIdx = -1, -1

        for i, col_text in enumerate(cols):
            col = col_text.lower()
            # checking for product name and batch
            if "partii" in col or "partia" in col or "trwałości" in col or "partie" in col:
                batchIdx = i

            elif "produkt" in col or "nazwa" in col:
                productIdx = i
        # now we iterate on the remaining rows
        for row in rows[1:]:
            cells_raw = row.find_all("td")

            if len(cells_raw) > 1:
                # extracting text from cells
                cells = [cell.get_text(strip=True) for cell in cells_raw]
                prod_name, prod_batch = "", ""

                if productIdx != -1 and productIdx < len(cells):
                    prod_name = cells[productIdx]

                if batchIdx != -1 and batchIdx < len(cells):
                    prod_batch = cells[batchIdx]
                # creating new entry - a "product" tuple
                if prod_name and prod_batch:
                    result['product'].add((prod_name,prod_batch))
                    prod_batch, prod_name = "", ""

    # second part - the interesting data is usually in <strong> blocks
    prod_name, prod_batch = "", ""
    for strong in soup.find_all("strong"):
        # we check the previous sibling in hopes of finding what kind of data we are looking at
        prev=strong.previous_sibling
        # skipping lines to get to the description
        while prev and (prev.name == "br" or (isinstance(prev, NavigableString) and not prev.strip())):
            prev=prev.previous_sibling
        txt = ""

        # check if sth found
        if isinstance(prev, NavigableString) and prev.strip():
            txt=prev.strip().lower()

        # list logic
        elif strong.parent and strong.parent.name == "li":
            # search for <ul> or <ol> blocks
            lst=strong.parent.find_parent(['ul', 'ol'])


            if lst:
                lst_prev=lst.previous_sibling
                # skipping lines to get to the description
                while lst_prev and (isinstance(lst_prev, NavigableString) and not lst_prev.strip()):
                    lst_prev=lst_prev.previous_sibling
                # extracting desc
                if lst_prev:
                    txt=lst_prev.get_text(strip=True).lower()

        if txt:
            # getting text from strong
            val=strong.get_text(separator=" | ", strip=True)

            # logical checks, for categorizing
            if "partii" in txt or "partia" in txt or "trwałości" in txt or "partie" in txt:
                prod_batch = val

            elif "produkt" in txt or "nazwa" in txt:
                prod_name = val

            elif "firmy" in txt or "firma" in txt or "marka" in txt or "dystrybutor"  in txt:
                result['brand']=val

            elif not result['brand'] and ("producent" in txt or "wyprodukowano" in txt):
                result['brand']=val
        # appending product lists - sometimes one warning contains more than one product
        if prod_name and prod_batch:
            result["product"].add((prod_name,prod_batch))
            prod_batch, prod_name = "", ""

    # search for danger and recommendations sections - those are
    # usually in <h3> blocks
    result['danger']=find_in_h3("Zagrożenie", soup)
    result['recommendations']=find_in_h3("Zalecenia", soup)


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

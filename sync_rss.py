from app.models import db, Warning, Product, Image
from scraper.rss_scraper import scrape_latest_rss_warnings
from scraper import extractor
from datetime import datetime
import os
from flask import Flask
from dotenv import load_dotenv


def sync_warnings_to_db():
    """
    Fetches the latest warnings from the GIS RSS feed, parses the HTML,
    and inserts new records into the database.
    """
    print("Fetching latest warnings from GIS RSS feed...")

    scraped_data = scrape_latest_rss_warnings()
    if not scraped_data:
        print("No data from scraper")
        return
    
    new_records_count=0

    for data in scraped_data:
        #check for duplicates
        existing_warning = Warning.query.filter_by(link=data['link']).first()

        if existing_warning:
            continue
        
        #extract info from raw HTML
        extracted_info = extractor.extract(data['raw_html'])

        #datetime conversion
        pub_date = None
        if data['publication_date']:
            pub_date = datetime.strptime(data['publication_date'], '%Y-%m-%d %H:%M:%S')

        #create Warning object
        new_warning = Warning(
            title=data['title'],
            link=data['link'],
            publication_date=pub_date,
            danger=extracted_info.get('danger', ''),
            brand=extracted_info.get('brand', ''),
            recommendations=extracted_info.get('recommendations', '')
        )

        db.session.add(new_warning)
        db.session.flush() #flush pushes the object to DB to get wID, but keep transaction open in case of error

        #create Product object (extractor returns set of tuples contains products and batch)
        for prod_name, prod_batch in extracted_info.get('product', []):
            new_product = Product(
                wID=new_warning.wID,
                product_name=prod_name,
                batch=prod_batch
            )
            db.session.add(new_product)


        #create Image object, scraper returns set of tuples (alt_desc, img_url)
        for alt_desc, img_url in data.get('images', []):
            new_image = Image(
                wID=new_warning.wID,
                img_url=img_url,
                alt_desc=alt_desc
            )
            db.session.add(new_image)
        
        db.session.commit()
        new_records_count+=1
    
    print(f"\nSynchronization complete. Added {new_records_count} new warnings to the database.")


if __name__ == "__main__":
    load_dotenv()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        sync_warnings_to_db()
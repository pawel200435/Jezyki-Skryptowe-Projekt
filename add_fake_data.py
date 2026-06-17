from datetime import datetime
from app.models import db, Warning, Product, Image
from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()

def add_fake_data():
    """
    Seeds the database with initial fake data for testing purposes.
    """

    warnings_data = [
        {
            "link": "https://www.gov.pl/web/gis/ostrzezenie-publiczne-dotyczace-zywnosci-wysoki-poziom-akryloamidu-w-okreslonych-partiach-herbatnikow",
            "title": "Ostrzeżenie publiczne dotyczące żywności: wysoki poziom akryloamidu w określonych partiach herbatników",
            "publication_date": datetime(2026, 6, 11, 0, 0, 0),
            "danger": "W wyniku badań przeprowadzonych przez Państwową Inspekcję Sanitarną stwierdzono wysoki poziom akryloamidu w herbatnikach Petit Beurre określonych poniżej. Na podstawie oceny ryzyka Narodowego Instytutu Zdrowia Publicznego PZH – Państwowego Instytutu Badawczego należy uznać, że produkt ten stanowi zagrożenie dla zdrowia konsumentów.",
            "brand": "Apetitki",
            "recommendations": "Nie należy spożywać partii produktu określonej w tym komunikacie.",
    
            "product_name": "Herbatniki Petit Beurre",
            "batch": "10.05.2027.B - 10/05/2027, 20.05.2027.A - 20/05/2027",
            
            "images": [
                {"url": "https://www.gov.pl/photo/c677fc60-c186-4e56-a7a0-b507def87307", "alt": "Opakowanie herbatników Petit Beurre Apetitki przód opakowania"},
                {"url": "https://www.gov.pl/photo/64c224d2-1836-45e1-96ed-b5e6d92fd20b", "alt": "Opakowanie herbatników Petit Beurre Apetitki tył opakowania"}
            ]
        },
        {
            "link": "https://www.gov.pl/web/gis/ostrzezenie-publiczne-dotyczace-zywnosci-wysoki-poziom-alkaloidow-pirolizydynowych-w-produkcie-pn-pylek-kwiatowy2",
            "title": "Ostrzeżenie publiczne dotyczące żywności: wysoki poziom alkaloidów pirolizydynowych w produkcie pn. Pyłek kwiatowy",
            "publication_date": datetime(2026, 6, 8, 0, 0, 0),
            "danger": "W badaniach Państwowej Inspekcji Sanitarnej stwierdzono przekroczenie dopuszczalnego poziomu alkaloidów pirolizydynowych w przedmiotowym produkcie. Na podstawie oceny ryzyka Narodowego Instytutu Zdrowia Publicznego PZH – Państwowego Instytutu Badawczego uznano, że spożycie produktu zanieczyszczonego alkaloidami pirolizydynowymi na wykrytym poziomie może stanowić ryzyko dla zdrowia konsumentów.",
            "brand": "Sądecki Bartnik",
            "recommendations": "Nie należy spożywać wskazanej w komunikacie partii produktu.",
            
            "product_name": "Pyłek kwiatowy, Sądecki Bartnik, 200 g",
            "batch": "20/01/2028 7/4",
            
            "images": [
                {"url": "https://www.gov.pl/photo/314f41cb-94bb-4ea2-b01a-e6f9d6ab472d", "alt": "Opakowanie produktu Pyłek kwiatowy Sądecki Bartnik 200 g przód opakowania"},
                {"url": "https://www.gov.pl/photo/5ccc047d-3049-47b9-a9e5-0357d60d6c6b", "alt": "Opakowanie produktu Pyłek kwiatowy Sądecki Bartnik tył opakowania"}
            ]
        }
    ]

    for item in warnings_data:
        #Anti-duplication protection
        warnings_exist = Warning.query.filter_by(link=item["link"]).first()
        
        if not warnings_exist:
            new_warning = Warning(
                title=item["title"],
                link=item["link"],
                publication_date=item["publication_date"],
                danger=item["danger"],
                brand=item["brand"],
                recommendations=item["recommendations"]
            )
            db.session.add(new_warning)
            db.session.commit()

            new_product = Product(
                wID=new_warning.wID,
                product_name=item["product_name"],
                batch=item["batch"]
            )
            db.session.add(new_product)

            for img in item["images"]:
                new_image = Image(
                    wID = new_warning.wID,
                    img_url=img["url"],
                    alt_desc=img["alt"]
                )
                db.session.add(new_image)
            
            db.session.commit()

    print("Adding example data - completed")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        add_fake_data()

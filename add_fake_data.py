from datetime import datetime
from app.models import db, Ostrzezenie, Zdjecie
from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()

def add_fake_data():
    ostrzezenia_data = [
        {
            "gis_id": "https://www.gov.pl/web/gis/ostrzezenie-publiczne-dotyczace-zywnosci-wysoki-poziom-akryloamidu-w-okreslonych-partiach-herbatnikow",
            "tytul": "Ostrzeżenie publiczne dotyczące żywności: wysoki poziom akryloamidu w określonych partiach herbatników",
            "link_zrodlowy": "https://www.gov.pl/web/gis/ostrzezenie-publiczne-dotyczace-zywnosci-wysoki-poziom-akryloamidu-w-okreslonych-partiach-herbatnikow",
            "data_publikacji": datetime(2026, 6, 11, 0, 0, 0),
            "zagrozenie": "W wyniku badań przeprowadzonych przez Państwową Inspekcję Sanitarną stwierdzono wysoki poziom akryloamidu w herbatnikach Petit Beurre określonych poniżej. Na podstawie oceny ryzyka Narodowego Instytutu Zdrowia Publicznego PZH – Państwowego Instytutu Badawczego należy uznać, że produkt ten stanowi zagrożenie dla zdrowia konsumentów.",
            "produkt": "Herbatniki Petit Beurre",
            "marka": "Apetitki",
            "numer_partii": "10.05.2027.B - 10/05/2027, 20.05.2027.A - 20/05/2027",
            "producent": "Eurobrand Sp. z o.o. Płochocińska 111/114, 03-044 Warszawa",
            "zalecenia": "Nie należy spożywać partii produktu określonej w tym komunikacie.",
            "zdjecia": [
                {"url": "https://www.gov.pl/photo/c677fc60-c186-4e56-a7a0-b507def87307", "alt": "Opakowanie herbatników Petit Beurre Apetitki przód opakowania"},
                {"url": "https://www.gov.pl/photo/64c224d2-1836-45e1-96ed-b5e6d92fd20b", "alt": "Opakowanie herbatników Petit Beurre Apetitki tył opakowania"}
            ]
        },
        {
            "gis_id": "https://www.gov.pl/web/gis/ostrzezenie-publiczne-dotyczace-zywnosci-wysoki-poziom-alkaloidow-pirolizydynowych-w-produkcie-pn-pylek-kwiatowy2",
            "tytul": "Ostrzeżenie publiczne dotyczące żywności: wysoki poziom alkaloidów pirolizydynowych w produkcie pn. Pyłek kwiatowy",
            "link_zrodlowy": "https://www.gov.pl/web/gis/ostrzezenie-publiczne-dotyczace-zywnosci-wysoki-poziom-alkaloidow-pirolizydynowych-w-produkcie-pn-pylek-kwiatowy2",
            "data_publikacji": datetime(2026, 6, 8, 0, 0, 0),
            "zagrozenie": "W badaniach Państwowej Inspekcji Sanitarnej stwierdzono przekroczenie dopuszczalnego poziomu alkaloidów pirolizydynowych w przedmiotowym produkcie. Na podstawie oceny ryzyka Narodowego Instytutu Zdrowia Publicznego PZH – Państwowego Instytutu Badawczego uznano, że spożycie produktu zanieczyszczonego alkaloidami pirolizydynowymi na wykrytym poziomie może stanowić ryzyko dla zdrowia konsumentów.",
            "produkt": "Pyłek kwiatowy, Sądecki Bartnik, 200 g",
            "marka": "Sądecki Bartnik",
            "numer_partii": "20/01/2028 7/4",
            "producent": "Gospodarstwo Pasieczne ,,Sądecki Bartnik” Sp. z o.o., Stróże 235, 33-331 Stróże.",
            "zalecenia": "Nie należy spożywać wskazanej w komunikacie partii produktu.",
            "zdjecia": [
                {"url": "https://www.gov.pl/photo/314f41cb-94bb-4ea2-b01a-e6f9d6ab472d", "alt": "Opakowanie produktu Pyłek kwiatowy Sądecki Bartnik 200 g przód opakowania"},
                {"url": "https://www.gov.pl/photo/5ccc047d-3049-47b9-a9e5-0357d60d6c6b", "alt": "Opakowanie produktu Pyłek kwiatowy Sądecki Bartnik tył opakowania"}
            ]
        }
    ]

    for item in ostrzezenia_data:
        #Anti-duplication protection (check the unique gis_id)
        ostrzezenie_exist = Ostrzezenie.query.filter_by(gis_id=item["gis_id"]).first()
        
        if not ostrzezenie_exist:
            new_o = Ostrzezenie(
                gis_id=item["gis_id"],
                tytul=item["tytul"],
                link_zrodlowy=item["link_zrodlowy"],
                data_publikacji=item["data_publikacji"],
                zagrozenie=item["zagrozenie"],
                produkt=item["produkt"],
                marka=item["marka"],
                numer_partii=item["numer_partii"],
                producent=item["producent"],
                zalecenia=item["zalecenia"]
            )
            db.session.add(new_o)
            db.session.commit()

            #Adding photos
            for img in item["zdjecia"]:
                new_foto = Zdjecie(
                    ostrzezenie_id=new_o.idO,
                    url_zdjecia=img["url"],
                    opis_alternatywny=img["alt"]
                )
                db.session.add(new_foto)
            
            db.session.commit()

    print("Adding example data - completed")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        add_fake_data()

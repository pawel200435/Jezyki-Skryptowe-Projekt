PL
# EatSafe - Monitor Ostrzeżeń GIS

<br>

## 📖 Cel i Opis Projektu
<div style="text-align: justify">
EatSafe to aplikacja desktopowa (oparta na architekturze webowej), której głównym celem jest ułatwienie obywatelom dostępu do kluczowych informacji o bezpieczeństwie żywności. Aplikacja automatycznie pobiera i przetwarza oficjalne ostrzeżenia z Głównego Inspektoratu Sanitarnego (GIS), prezentując je w czytelnym, przyjaznym dla użytkownika interfejsie. 
<br><br>
Projekt rozwiązuje realny problem rozproszonych i trudnych w nawigacji danych rządowych, integrując je w jednym, zautomatyzowanym systemie. Ponadto, integralną częścią rozwiązania jest autorskie REST API, które otwiera system dla deweloperów i zewnętrznych usług, umożliwiając im łatwe pobieranie, filtrowanie i wykorzystywanie ustrukturyzowanych danych o zagrożeniach we własnych projektach.
</div>
<br>

![Ekran główny aplikacji EatSafe](/docs/images/app.png)
*Zrzut ekranu przedstawiający główny interfejs aplikacji.*

---
<br>

## 🛠️ Technologie

* **Backend:** Python 3.8+, Flask, SQLAlchemy
* **Frontend:** HTML5, CSS3 (Bootstrap 5), HTMX (dla asynchronicznego UI), FontAwesome
* **Baza Danych:** MySQL (obsługiwana przez ORM SQLAlchemy)
* **Desktop Wrapper:** pywebview
* **Narzędzia:** Git, GitHub

---
<br>

## 🎯 Realizacja Wymagań Projektowych

Projekt został zaprojektowany tak, aby spełniać wszystkie techniczne i funkcjonalne kryteria oceny:

<div style="text-align: justify">

### 1. Wymagania Podstawowe i Interfejs
* **Interfejs Użytkownika:** Aplikacja wykorzystuje framework **Flask** do stworzenia responsywnej architektury SPA (Single Page Application), która została opakowana w natywne okno systemowe za pomocą biblioteki `pywebview`. Interfejs umożliwia pełną interakcję: wprowadzanie danych, filtrowanie, wizualizację w formie tabel oraz komunikację za pomocą alertów.
* **Architektura Obiektowa:** System bazuje na klasach (modele bazy danych SQLAlchemy) oraz dedykowanych funkcjach modułowych.
* **Obsługa Błędów:** Zaimplementowano bezpieczną walidację danych wejściowych (m.in. weryfikację formatu e-mail) oraz zabezpieczenia przed konfliktami w bazie danych (np. blokowanie prób zapisu duplikatów). Zapytania API posiadają pełną obsługę błędów, zwracając spójne komunikaty oraz odpowiednie kody statusów HTTP
* **Zewnętrzne Biblioteki:** Wykorzystano m.in. `Flask`, `SQLAlchemy`, `pywebview`, `requests` / narzędzia do parsowania RSS.

### 2. Baza Danych i Operacje CRUD (Ocena 5.0)
Zaimplementowano relacyjną bazę danych z wykorzystaniem **SQLAlchemy** (obsługa MySQL). System realizuje pełen cykl operacji CRUD:
* **Create:** Dodawanie nowych ostrzeżeń ze scrapera oraz rejestracja subskrybentów newslettera.
* **Read:** Zaawansowane zapytania do bazy, w tym asynchroniczne wyszukiwanie i filtrowanie.
* **Update:** Aktualizacja adresów email subskrybentów.
* **Delete:** Zaimplementowano mechanizmy dezaktywacji oraz usuwania maila z bazy dla subskrybentów.

<br>

![Schemat bazy danych](/docs/eatsafe_db.png) <br>
*Struktura relacyjnej bazy danych.*

### 3. Dodatkowe funkcjonalności
* **Modularność:** Kod został podzielony na logiczne pakiety (np. `app/routes/`, `app/utils/`, `scraper/`), co zapewnia wysoką czytelność struktury.
* **Architektura API:** Aplikacja posiada wbudowane REST API udokumentowane w języku angielskim, umożliwiające zewnętrzny dostęp do ustrukturyzowanych danych o ostrzeżeniach.
* **Wielowątkowość i Zarządzanie Procesami:** Integracja frameworka webowego z natywnym interfejsem desktopowym (`pywebview`) została zrealizowana przy użyciu wielowątkowości. Serwer Flask uruchamiany jest w wydzielonym wątku w trybie *daemon*, co zapewnia asynchroniczną i płynną pracę interfejsu bez blokowania głównego wątku, a także gwarantuje bezpieczne, automatyczne zamknięcie serwera w momencie wyłączenia okna aplikacji.

</div>

---

<br>

## ✨ Kluczowe Funkcjonalności

System oferuje szereg interaktywnych modułów zasilanych przez bibliotekę HTMX, co pozwala na asynchroniczne odświeżanie danych bez przeładowania strony:

### 1.  Wyszukiwanie, Filtrowanie i Sortowanie
Błyskawiczna wyszukiwarka przeszukująca nazwy produktów, producentów oraz typy zagrożeń w czasie rzeczywistym.
<br>
![Menu sortowania i filtrowania](sciezka/do/filtrowanie.png)

### 2. Szczegóły Ostrzeżenia
Wyświetlanie pełnych informacji o wycofanym produkcie (partia, zagrożenie) wraz ze zdjęciami w formie wyskakującego okienka modalnego.

![Pop-up z informacjami o ostrzeżeniu](/docs/images/warning_info.png)

### 3. System Subskrypcji (Newsletter)
Moduł umożliwiający zapisanie się na powiadomienia o nowych ostrzeżeniach. 
<br>

![Pop-up Newslettera](/docs/images/newsletter.png)

---
<br>

## 🚀 Instrukcja Uruchomienia

```
1. Uruchom MySQL (otwórz XAMPP Control Panel i włącz moduły Apache oraz MySQL).
2. Otwórz przeglądarkę i przejdź pod adres: http://localhost/phpmyadmin.
3. Kliknij zakładkę "Nowa" (w lewym panelu) i utwórz pustą bazę danych o nazwie: eatsafe_db
4. Upewnij się, że w głównym katalogu projektu znajduje się plik .env z poprawnym ciągiem połączeniowym (domyślny użytkownik w XAMPP to root z pustym hasłem).
   Zawartość pliku .env:
   DATABASE_URL=mysql+pymysql://root:@localhost:3306/eatsafe_db

5. Stwórz i aktywuj środowisko wirtualne (venv).
6. Zainstaluj wymagane pakiety komendą: uv pip install -r requirements.txt
7. Wygeneruj tabele w bazie danych, uruchamiając skrypt: 
   python create_db.py
8. Załaduj wstępne dane RSS do bazy danych, uruchamiając:
   python sync_rss.py

```
---
<br>

<div style="text-align: justify">

## 📊 Źródła Danych

System wykorzystuje zoptymalizowane, hybrydowe podejście do gromadzenia danych, zapewniając zarówno natychmiastowy dostęp do najnowszych komunikatów, jak i utrzymanie pełnej bazy historycznej:

* **Bieżące Ostrzeżenia (Strumień RSS):** Najświeższe komunikaty pobierane są asynchronicznie z dedykowanego kanału informacyjnego: [https://rss.mtsz.pl/](https://rss.mtsz.pl/). Zapewnia to błyskawiczną synchronizację i natychmiastowe aktualizowanie systemu o nowo pojawiających się zagrożeniach.
* **Dane Historyczne (Web Scraper):** Starsze ostrzeżenia oraz archiwalna baza danych zasilane są za pomocą autorskiego modułu skrapującego. Skraper bezpośrednio analizuje strukturę oficjalnej strony Głównego Inspektoratu Sanitarnego (GIS), wyciągając ustrukturyzowane informacje i uzupełniając relacyjną bazę danych o starsze wpisy.

---
<br>

## 🗃️ Dokumentacja
### API:
- https://documenter.getpostman.com/view/48536390/2sBXwvJUAb#intro [POSTMAN]
- [docs/API_documentation.pdf](docs\EatSafe_API_Documentation.pdf)


### RSS scraper:
- [docs/EatSafe_RSS_scraper_and_extractor.docx](docs/EatSafe_RSS_scraper_and_extractor.docx)

</div>

---

<br>

## 👥 Autorzy
 - Goliński Paweł
 - Kamiński Antoni
 - Karaśkiewicz Jakub
 - Zadrożny Mateusz 

Projekt zrealizowany w ramach zajęć na Politechnice Wrocławskiej.

<br>
<Br>
<hr style="border: 2px solid">
<br>
<br>

ENG
# EatSafe - GIS Warnings Monitor

<br>

## 📖 Project Goal and Description
<div style="text-align: justify">
EatSafe is a desktop application (based on web architecture) whose main goal is to facilitate citizens' access to key food safety information. The application automatically retrieves and processes official warnings from the Chief Sanitary Inspectorate (GIS), presenting them in a clear, user-friendly interface. 
<br><br>
The project solves the real problem of scattered and difficult-to-navigate government data by integrating it into a single, automated system. Furthermore, an integral part of the solution is a custom REST API, which opens the system to developers and external services, allowing them to easily retrieve, filter, and utilize structured hazard data in their own projects.
</div>
<br>

![Main EatSafe application screen](/docs/images/app.png)
*Screenshot showing the main application interface.*

---
<br>

## 🛠️ Technologies

* **Backend:** Python 3.8+, Flask, SQLAlchemy
* **Frontend:** HTML5, CSS3 (Bootstrap 5), HTMX (for asynchronous UI), FontAwesome
* **Database:** MySQL (supported by SQLAlchemy ORM)
* **Desktop Wrapper:** pywebview
* **Tools:** Git, GitHub

---
<br>

## 🎯 Fulfillment of Project Requirements

The project was designed to meet all technical and functional evaluation criteria:

<div style="text-align: justify">

### 1. Basic Requirements and Interface
* **User Interface:** The application uses the **Flask** framework to create a responsive SPA (Single Page Application) architecture, which has been wrapped in a native system window using the `pywebview` library. The interface allows full interaction: data entry, filtering, table-based visualization, and communication via alerts.
* **Object-Oriented Architecture:** The system is based on classes (SQLAlchemy database models) and dedicated modular functions.
* **Error Handling:** Secure input data validation has been implemented (e.g., e-mail format verification) alongside database conflict safeguards (e.g., blocking duplicate entry attempts). API requests feature full error handling, returning consistent messages and appropriate HTTP status codes.
* **External Libraries:** Libraries utilized include `Flask`, `SQLAlchemy`, `pywebview`, and `requests` / RSS parsing tools, among others.

### 2. Database and CRUD Operations (Grade 5.0)
A relational database has been implemented using **SQLAlchemy** (MySQL support). The system executes the full cycle of CRUD operations:
* **Create:** Adding new warnings from the scraper and registering newsletter subscribers.
* **Read:** Advanced database queries, including asynchronous searching and filtering.
* **Update:** Updating subscriber email addresses.
* **Delete:** Implementing mechanisms for deactivating and removing emails from the subscriber database.

<br>

![Database schema](/docs/eatsafe_db.png) <br>
*Relational database structure.*

### 3. Additional Features
* **Modularity:** The code has been divided into logical packages (e.g., `app/routes/`, `app/utils/`, `scraper/`), ensuring high structural readability.
* **API Architecture:** The application features a built-in REST API documented in English, enabling external access to structured warning data.
* **Multithreading and Process Management:** The integration of the web framework with the native desktop interface (`pywebview`) was achieved using multithreading. The Flask server runs in a dedicated thread in *daemon* mode, ensuring asynchronous and smooth interface operation without blocking the main thread, and guaranteeing a safe, automatic shutdown of the server when the application window is closed.

</div>

---

<br>

## ✨ Key Features

The system offers a range of interactive modules powered by the HTMX library, allowing for asynchronous data refresh without page reloads:

### 1.  Search, Filtering, and Sorting
A lightning-fast search engine that queries product names, manufacturers, and hazard types in real-time.
<br>
![Sorting and filtering menu](sciezka/do/filtrowanie.png)

### 2. Warning Details
Displaying full information about the recalled product (batch, hazard) along with photos in the form of a pop-up modal window.

![Warning info pop-up](/docs/images/warning_info.png)

### 3. Subscription System (Newsletter)
A module that allows users to subscribe to notifications about new warnings. 
<br>

![Newsletter Pop-up](/docs/images/newsletter.png)

---
<br>

## 🚀 Setup Instructions

```text
1. Start MySQL (open XAMPP Control Panel and enable the Apache and MySQL modules).
2. Open a browser and navigate to: http://localhost/phpmyadmin.
3. Click the "New" tab (in the left panel) and create an empty database named: eatsafe_db
4. Ensure that there is a .env file in the project's root directory with the correct connection string (the default user in XAMPP is root with an empty password).
   .env file content:
   DATABASE_URL=mysql+pymysql://root:@localhost:3306/eatsafe_db
5. Create and activate a virtual environment (venv).
6. Install the required packages with the command: uv pip install -r requirements.txt
7. Generate tables in the database by running the script: 
   python create_db.py
8. Load initial RSS data into the database by running:
   python sync_rss.py
```

---

<br>

<div style="text-align: justify">

## 📊 Data Sources

The system utilizes an optimized, hybrid approach to data collection, ensuring both immediate access to the latest alerts and the maintenance of a comprehensive historical database:

* **Current Warnings (RSS Stream):** The latest communications are fetched asynchronously from a dedicated information channel: https://rss.mtsz.pl/. This ensures lightning-fast synchronization and immediate system updates regarding newly emerging hazards.
* **Historical Data (Web Scraper):** Older warnings and the archival database are populated using a custom scraping module. The scraper directly analyzes the structure of the official Chief Sanitary Inspectorate (GIS) website, extracting structured information and populating the relational database with older entries.

---

<br>

## 🗃️ Documentation
### API:
- https://documenter.getpostman.com/view/48536390/2sBXwvJUAb#intro [POSTMAN]
- [docs/API_documentation.pdf](docs\EatSafe_API_Documentation.pdf)


### RSS scraper:
- [docs/EatSafe_RSS_scraper_and_extractor.docx](docs/EatSafe_RSS_scraper_and_extractor.docx)

</div>

---

<br>

## 👥 Authors
 - Goliński Paweł
 - Kamiński Antoni
 - Karaśkiewicz Jakub
 - Zadrożny Mateusz 

Project realized as part of classes at the Wrocław University of Science and Technology.
# 🍽️ EatSafe – GIS Food Warning Monitoring System

## 📌 Overview

**EatSafe** is a lightweight web application designed to make food safety alerts published by the Polish Chief Sanitary Inspectorate (GIS) more accessible and user-friendly.

GIS publishes warnings in a raw and difficult-to-use format (RSS/Atom feeds with embedded HTML and no proper API).  
This project aims to transform that data into a clean, searchable and structured interface.

The system automatically fetches, processes, and presents food safety alerts in a readable way, allowing users to easily browse, filter, and stay informed about potential food-related hazards.

---

## 🎯 Problem Statement

The official GIS data sources are:
- hard to read (raw RSS/Atom feeds),
- not user-friendly,
- lacking a structured API,
- limited to recent entries only.

As a result, accessing historical or structured information is difficult for end users.

---

## 💡 Proposed Solution

We are building a **Single Page Web Application (SPA-like)** that:

- automatically fetches GIS alerts,
- cleans and normalizes data,
- stores it in a database,
- exposes a custom API,
- provides a simple and readable UI for users,
- supports filtering, reporting, and notifications.

---

## 🧰 Tech Stack

- **Python**
- **Flask** (backend framework)
- **PostgreSQL** (database)
- **Jinja2** (templating)
- **HTMX** (dynamic UI interactions)
- **HTML / CSS**
- **Bootstrap** (UI framework – optional / planned)

---

## ⚙️ Planned Features & Architecture

### 1. Data ingestion
- Initial data source: RSS feed  
  `https://rss.mtsz.pl/`
- Fetch latest 9–10 alerts as a starting point
- Future extension: scraper to retrieve historical data *(subject to legal verification)*

---

### 2. Data storage
- PostgreSQL database
- Structured storage of GIS alerts
- Support for historical records and metadata

---

### 3. Custom API
- REST-like API built with Flask
- Filtering capabilities (e.g. date, category, severity)
- JSON responses for frontend usage

---

### 4. Web interface
- Simple and clean UI for browsing alerts
- Filtering and search functionality
- Built using Flask + Jinja2 + HTMX

---

### 5. Backend logic
- RSS parsing and data processing
- Database integration
- HTTP request handling
- Internal API layer

---

### 6. Data export & file handling (requirement)
- Generate files for email sharing (e.g. reports)
- Support exporting selected alerts into shareable formats

---

### 7. Newsletter system (requirement)
- Database table for user emails
- Basic CRUD operations:
  - create subscription
  - read subscribers
  - update subscription
  - delete subscription

---

## 📊 Data Source

Primary source:
- https://rss.mtsz.pl/

Additional GIS-related official channels (to be integrated later) may include government-published RSS/Atom feeds containing food safety alerts.

---

## Setup and Running
```
1. Run MySQL (open XAMPP Control Panel and start Apache and MySQL modules)
2. Open your browser and navigate to: http://localhost/phpmyadmin.
3. Click on the New tab (on the left panel) and create a blank database named: eatsafe_db

4. Ensure you have a .env file in the root directory of the project with the correct connection string (default XAMPP user is root with an empty password)
  .env file content:
  DATABASE_URL=mysql+pymysql://root:@localhost:3306/eatsafe_db

5. Create and activate venv
6. Install required packages: uv pip install -r requirements.txt

7. Generate database tables by running: 
  python create_db.py
8. Seed the database with test data
  python add_fake_data.py

```

---

## 👥 Team & Purpose

This project is developed as part of an academic assignment with the goal of practicing:
- backend development
- database design
- API creation
- web application architecture
- team collaboration using Git & GitHub workflows

---

## 📌 Future Improvements (planned)

- authentication system
- email notification system
- advanced filtering (severity, category)
- better data normalization
- UI improvements (dashboard-style view)

---

## Authors
 - Goliński Paweł
 - Kamiński Antoni
 - Karaśkiewicz Jakub
 - Zadrożny Mateusz 

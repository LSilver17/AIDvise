Folder Structure
data_pipeline/
├── saved_pages/
│   └── registration_page.html        # Manually saved HTML from QCC course offerings page
├── scrape_registration_sections.py   # Parses HTML and extracts course data
├── registration_sections.json        # Scraped course data (1,227 sections)
├── create_registration_db.py         # Initializes the SQLite database from JSON
├── update_registration_db.py         # Updates the database with fresh scraped data
├── view_registration_db.py           # Query and inspect the database
└── README_registration_pipeline.md   # This file

How It Works
QCC Course Offerings Page
        ↓  (manual HTML save)
saved_pages/registration_page.html
        ↓  (scrape_registration_sections.py)
registration_sections.json
        ↓  (create_registration_db.py)
registration.db
        ↓
Backend API → AI Advising Agent → Frontend

Install dependencies:
pip install beautifulsoup4

Scrape the page
python scrape_registration_sections.py
Outputs registration_sections.json with all course sections.

Initialize the database (run once)
python create_registration_db.py
Creates registration.db with a fully indexed schema.

Update the database (run after every re-scrape)
python update_registration_db.py
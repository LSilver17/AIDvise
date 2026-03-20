Folder Structure
data_pipeline/
├── saved_pages/                        # gitignored — not needed anymore
├── scrape_registration_sections.py     # legacy scraper (manual HTML save)
├── refresh_registration.py             # main script — scrapes + updates DB
├── create_registration_db.py           # run once to initialize DB
├── view_registration_db.py             # inspect and query the DB
├── registration_sections.json          # scraped course data (committed to repo)
├── registration.db                     # gitignored — generated locally
└── README_registration_pipeline.md     # this file

How It Works
QCC Course Offerings Page (Jenzabar Portal)
        ↓  scrape_registration_sections.py
registration_page.html
        ↓  refresh_registration.py (automated via Playwright)
registration_sections.json
        ↓  create_registration_db.py (run once)
registration.db
        ↓
Backend API → AI Advising Agent → Frontend

Install dependencies:
pip install beautifulsoup4 playwright
playwright install chromium

Scrape the page
python scrape_registration_sections.py
Outputs registration_sections.json with all course sections.

Initialize the database (run once)
python create_registration_db.py
Creates registration.db with a fully indexed schema.

Update the database (run after every re-scrape)
python refresh_registration.py

Inspect the database
python view_registration_db.py
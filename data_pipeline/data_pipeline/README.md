# Academic Advising Platform — Data Pipeline

**CSC 212 | Quinsigamond Community College**  
**Role:** Data Pipeline  
**Repository:** [https://github.com/LSilver17/CSC212---AI-Agent](https://github.com/LSilver17/CSC212---AI-Agent)  

---

## Overview

This directory contains the data pipeline for the Academic Advising Platform. The pipeline is responsible for scraping, cleaning, structuring, and maintaining all course and program data consumed by the LangGraph advising agent. It produces four JSON files that the backend team queries at runtime to answer student advising questions.

> **Note:** This implementation uses Quinsigamond Community College (QCC) as a proof of concept. The pipeline architecture is institution-agnostic and can be adapted to any college or university by updating the scraper target URLs, field mappings, and parsing logic to match the target institution's web systems and student portal. The JSON output schema and backend integration remain the same regardless of institution.

---

## Responsibility

All code in the `data_pipeline/` directory was written by the =team member with the Data Pipeline role. This includes:

- All web scrapers (`scraping/`)
- Database utilities (`database/`)
- Data conversion scripts
- JSON output files (`jsons/`)
- Unit tests (`test_data_pipeline.py`)
- This documentation

The backend team (`lg_agent/`) consumes the JSON outputs produced by this pipeline. The frontend team (`frontend/`) displays the results. No data pipeline code appears in those directories.

---

## Project Structure

```
data_pipeline/
├── scraping/
│   ├── scrape_registration_sections.py   # Parses saved HTML from The Q portal
│   ├── refresh_registration.py           # Live Playwright scraper for registration data
│   ├── scrape_catalog.py                 # Scrapes course catalog from The Q portal
│   ├── scrape_classes_page.py            # Scrapes public QCC course listing
│   └── scrape_programs.py               # Scrapes public QCC programs listing
├── database/
│   ├── create_registration_db.py         # Initializes SQLite database from JSON
│   └── view_registration_db.py           # Interactive database query utility
├── jsons/
│   ├── registration_sections.json        # Live registration data (1,227 sections)
│   ├── term_data.json                    # Registration data in backend schema
│   ├── course_catalog.json               # 286 unique courses with full details
│   ├── qcc_classes.json                  # Public course listing with prereqs/credits
│   └── qcc_programs.json                # 103 programs with requirements
├── docs/                                 # Auto-generated HTML documentation (pdoc)
├── convert_to_term_structure.py          # Converts registration JSON to backend schema
├── test_data_pipeline.py                 # Unit tests
└── README.md                            # This file
```

---

## Platform Setup

### Requirements

- Python 3.11+
- Windows, macOS, or Linux
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/LSilver17/CSC212---AI-Agent.git
cd CSC212---AI-Agent
```

### Step 2 — Create and Activate Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:

```bash
pip install playwright beautifulsoup4 requests
playwright install chromium
```

---

## Instructions — Running the Pipeline

All commands should be run from the `data_pipeline/` directory:

```bash
cd data_pipeline
```

### 1. Scrape Live Registration Data (The Q Portal)

Scrapes all departments from The Q portal, saves to JSON, and updates the database:

```bash
python scraping/refresh_registration.py
```

**Output:** `jsons/registration_sections.json`, `registration.db`  
**Runtime:** ~10–15 minutes (73 departments)

---

### 2. Scrape Course Catalog (The Q Portal)

Scrapes unique course details (description, credits, prerequisites, semesters offered):

```bash
python scraping/scrape_catalog.py
```

**Output:** `jsons/course_catalog.json`  
**Runtime:** ~30–45 minutes (286 courses)

---

### 3. Scrape Public Course Listing

Scrapes the full credit course list from the public institution website:

```bash
python scraping/scrape_classes_page.py
```

**Output:** `jsons/qcc_classes.json`  
**Runtime:** ~10–15 minutes

---

### 4. Scrape Programs of Study

Scrapes all academic programs and certificates:

```bash
python scraping/scrape_programs.py
```

**Output:** `jsons/qcc_programs.json`  
**Runtime:** ~5–10 minutes

---

### 5. Convert Registration Data to Backend Schema

Converts `registration_sections.json` into the term structure required by the backend team:

```bash
python convert_to_term_structure.py
```

**Input:** `jsons/registration_sections.json`  
**Output:** `jsons/term_data.json`  
**Runtime:** Seconds

---

### 6. Initialize the Database (First Time Only)

Creates `registration.db` from the JSON file:

```bash
python database/create_registration_db.py
```

**Note:** Use `refresh_registration.py` for subsequent updates — it upserts automatically.

---

### 7. Query the Database (Optional)

Interactive menu for exploring registration data:

```bash
python database/view_registration_db.py
```

---

## JSON Output Files

| File | Contents | Records | Refresh Frequency |
|------|----------|---------|-------------------|
| `registration_sections.json` | Live course sections | 1,227 | Each semester |
| `term_data.json` | Backend-formatted term data | 1,227 | Each semester |
| `course_catalog.json` | Course details from The Q | 286 | Annually |
| `qcc_classes.json` | Public course listing | ~300 | Annually |
| `qcc_programs.json` | Programs of study | 103 | Annually |

---

## HTML Documentation

Full API documentation generated with pdoc is available in the `docs/` folder.

Open in browser:
```
data_pipeline/docs/index.html
```

Or view individual module docs:
- `docs/scraping/refresh_registration.html`
- `docs/scraping/scrape_catalog.html`
- `docs/scraping/scrape_classes_page.html`
- `docs/scraping/scrape_programs.html`
- `docs/scraping/scrape_registration_sections.html`
- `docs/database/create_registration_db.html`
- `docs/database/view_registration_db.html`
- `docs/convert_to_term_structure.html`

---

## How the Pipeline Connects to the Backend

The backend team's LangGraph agent reads from the JSON files at runtime. The Planner node routes each student query to the appropriate data source:

| Student Query | Data Source | File |
|---------------|-------------|------|
| Course availability this semester | Registration sections | `term_data.json` |
| Prerequisites for a course | Course catalog | `course_catalog.json` |
| Credits for a course | Course catalog / classes | `course_catalog.json` |
| Program requirements | Programs | `qcc_programs.json` |
| Course description | Public listing | `qcc_classes.json` |

---

## Running Tests

```bash
cd data_pipeline
python -m pytest test_data_pipeline.py -v
```

---

## Notes

- The student portal (Jenzabar) requires Playwright because it renders content dynamically via JavaScript. Standard HTTP requests will not work.
- Public website scrapers use Requests + BeautifulSoup (no browser needed).
- A 0.3 second delay is applied between requests to avoid overloading the server.
- `course_catalog.json` should be regenerated each semester to pick up curriculum changes.
- To adapt this pipeline to a different institution, update the target URLs in each scraper and adjust the field parsing logic to match that institution's page structure.
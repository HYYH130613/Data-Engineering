# Countries by GDP: ETL Pipeline

A Python ETL (Extract, Transform, Load) pipeline that scrapes GDP figures for the world's economies from Wikipedia, cleans and converts them, and loads the result into both a CSV file and a SQLite database, with progress logging at every stage.

Built as the final project of the **Python Project for Data Engineering** course in the [IBM Data Engineering Professional Certificate](https://www.coursera.org/professional-certificates/ibm-data-engineer) on Coursera.

---

## What it does

| Stage | Description |
|-------|-------------|
| **Extract** | Downloads an archived copy of Wikipedia's *List of countries by GDP (nominal)* and parses the GDP table with BeautifulSoup. |
| **Transform** | Cleans the raw text (removes commas, spaces, `$`), converts it to numeric values, converts **million USD → billion USD**, and rounds to 2 decimals. Unparseable values become `NaN` instead of crashing the run. |
| **Load** | Saves the final table to a CSV file and to a SQLite table (`Countries_by_GDP`). |
| **Query** | Runs a SQL query against the database to filter economies above a GDP threshold. |
| **Log** | Writes a timestamped entry to `etl_project_log.txt` at each stage. |

```
Wikipedia (archived page)
        │
        ▼
   Extract (requests + BeautifulSoup)
        │
        ▼
   Transform (pandas: clean, convert, round)
        │
        ├──► CSV file
        └──► SQLite database ──► SQL query
```

## Tech stack

- **Python 3**
- **requests**: fetching the web page
- **BeautifulSoup4**: HTML parsing / web scraping
- **pandas**: data cleaning and transformation
- **SQLite3**: lightweight relational storage
- **datetime**: timestamped logging

## Data source

GDP (nominal) estimates by country, from Wikipedia's [List of countries by GDP (nominal)](https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)). The pipeline uses a fixed [Internet Archive snapshot (September 2023)](https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29) so results are reproducible even if the live page changes.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/HYYH130613/Data-Engineering.git
cd Data-Engineering
```

### 2. Install dependencies

```bash
pip install requests beautifulsoup4 pandas
```

`sqlite3` and `datetime` are part of the Python standard library.

### 3. Run the pipeline

```bash
python etl_project.py
```

## Output

| File | Contents |
|------|----------|
| `Countries_by_GDP.csv` | Cleaned GDP table (country, GDP in billion USD) |
| `World_Economies.db` | SQLite database with the table `Countries_by_GDP` |
| `etl_project_log.txt` | Timestamped log of each pipeline stage |

Example log format:

```
2026-Nov-11-14:05:32 : Preliminaries complete. Initiating ETL process
2026-Nov-11-14:05:34 : Data extraction complete. Initiating Transformation process
...
```

## Project structure

```
.
├── etl_project.py          # Full ETL pipeline
├── README.md
├── Countries_by_GDP.csv    # Generated on run
├── World_Economies.db      # Generated on run
└── etl_project_log.txt     # Generated on run
```

## Design notes

- **Separation of concerns:** each stage is its own function (`extract`, `transform`, `load_to_csv`, `load_to_db`, `run_query`, `log_progress`), which makes the pipeline easy to test and extend.
- **Defensive cleaning:** `safe_to_float` handles missing or malformed values without stopping the pipeline.
- **Reproducibility:** using an archived page snapshot keeps the extracted data stable between runs.
- **Observability:** logging at every stage makes it easy to see where a run succeeded or failed.

## Known limitations and planned improvements

- [ ] Locate the table by its headers instead of a fixed index, so layout changes on the page don't break extraction
- [ ] Add error handling for network failures (timeouts, retries, HTTP status checks)
- [ ] Move configuration (URL, paths, thresholds) into a config file or command-line arguments
- [ ] Add unit tests for `transform` (`pytest`) and a GitHub Actions workflow
- [ ] Add data-quality checks (duplicate countries, negative or missing GDP values)
- [ ] Containerize with Docker and schedule runs with Airflow
- [ ] Load into a cloud warehouse (e.g. BigQuery) and add a simple dashboard

## Author

**HYYH130613**: [GitHub profile](https://github.com/HYYH130613)

## Acknowledgements

Project structure and task requirements come from the IBM *Python Project for Data Engineering* course on Coursera.

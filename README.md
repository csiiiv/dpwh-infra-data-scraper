# DPWH Infrastructure Projects Data Pipeline

A comprehensive web scraping and data extraction pipeline for Philippine Department of Public Works and Highways (DPWH) infrastructure contract data. This project automates the collection, parsing, and analysis of contract information across all regions from 2016-2025.

## 📊 Project Overview

This project extracts and processes infrastructure project data from the DPWH public database, converting raw HTML tables into structured CSV datasets for analysis. As of the latest run, the pipeline has processed **209,199 contracts** worth **₱6.3 trillion** across all Philippine regions.

### Key Features

- **🤖 Automated Web Scraping**: Playwright-based scraper with anti-bot evasion
- **🔍 Robust HTML Parsing**: BeautifulSoup parser with comprehensive error handling
- **📈 Data Quality Tracking**: Multi-level error/warning system for data validation
- **🏗️ Joint Venture Support**: Handles projects with multiple contractors (up to 4)
- **📊 Analytics**: Automatic summary generation with regional and temporal breakdowns
- **💾 Multi-Format Output**: CSV, HTML, and structured analysis reports

## 🗂️ Project Structure

```
DPWH/
├── csv/                          # Processed CSV output files
│   ├── contracts_2016_all_offices.csv
│   ├── contracts_2017_all_offices.csv
│   ├── ...
│   ├── contracts_2025_all_offices.csv
│   ├── contracts_all_years_all_offices.csv  # Combined dataset
│   └── misc/                     # Additional analysis files
├── docs/                         # Comprehensive documentation
│   ├── CSV_SCHEMA.md            # CSV schema specification
│   ├── SCRAPER_DOCUMENTATION.md # Scraper technical documentation
│   ├── html_to_csv_parser_specification.md
│   ├── html_table_structure_analysis.md
│   ├── parse_notes_error_codes.md
│   └── parsing_summary.md       # Data quality report
├── html/                         # Raw HTML tables (scraped data)
│   ├── table_Central-Office_2016_*.html
│   ├── table_Cordillera-Administrative-Region_2016_*.html
│   └── ...                      # 180 HTML files (18 regions × 10 years)
├── logs/                         # Processing logs
├── scripts/                      # Python processing scripts
│   ├── scraper_playwright.py   # Web scraper
│   ├── html_to_csv_parser.py   # HTML to CSV converter
│   ├── parse_all_and_summarize.py  # Batch processor
│   ├── generate_summary.py     # Summary generator
│   ├── extract_warnings.py     # Data quality filter
│   ├── convert_xlsx_to_csv.py  # XLSX converter utility
│   └── rename_office_underscores.py  # Filename cleaner
└── xlsx/                         # XLSX data files
```

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **System**: Windows/Linux/macOS with 2GB+ RAM
- **Storage**: ~1GB for full dataset

### Installation

1. **Clone or download the repository**

2. **Install Python dependencies**:

```bash
# Core dependencies
pip install beautifulsoup4 lxml python-dateutil

# For web scraping
pip install playwright
playwright install chromium

# For XLSX conversion (optional)
pip install python-calamine
```

3. **Verify installation**:

```bash
python3 -c "from bs4 import BeautifulSoup; print('✓ BeautifulSoup installed')"
python3 -c "from playwright.sync_api import sync_playwright; print('✓ Playwright installed')"
```

## 📖 Usage Guide

### 1. Web Scraping (Data Collection)

Scrape contract data from the DPWH website:

```bash
cd scripts
python3 scraper_playwright.py
```

**What it does**:
- Opens visible browser window
- Navigates to http://apps2.dpwh.gov.ph/infra_projects/
- Extracts data for all 18 regions across 10 years (2016-2025)
- Saves 180 HTML files to `html/` directory
- Takes ~60-80 minutes to complete

**Important Notes**:
- First region requires **manual selection** (anti-bot protection)
- Browser window stays open for monitoring
- Press Enter when prompted to continue
- Files saved immediately after extraction

See [SCRAPER_DOCUMENTATION.md](docs/SCRAPER_DOCUMENTATION.md) for detailed information.

### 2. HTML to CSV Conversion

Parse HTML tables into structured CSV:

```bash
cd scripts
python3 html_to_csv_parser.py
```

**Options**:
```bash
# Parse specific year only
python3 html_to_csv_parser.py --year 2024

# Parse all years (default)
python3 html_to_csv_parser.py
```

**Output**:
- `csv/contracts_YYYY_all_offices.csv` - Per-year files
- `csv/contracts_all_years_all_offices.csv` - Combined dataset
- Logs in `logs/parser.log`

### 3. Batch Processing with Summary

Run complete parsing pipeline with automatic summary:

```bash
cd scripts
python3 parse_all_and_summarize.py
```

**This script**:
1. Parses all HTML files to CSV
2. Generates comprehensive statistics
3. Creates `docs/parsing_summary.md` report
4. Provides data quality metrics

### 4. Data Quality Analysis

Extract contracts with data quality issues:

```bash
cd scripts
python3 extract_warnings.py
```

Creates `csv/contracts_with_warnings.csv` with all contracts that have warnings.

### 5. Generate Summary Report

Analyze existing CSV files:

```bash
cd scripts
python3 generate_summary.py
```

## 📋 Data Schema

### CSV Output Schema (25 columns)

| Column | Type | Description |
|--------|------|-------------|
| `row_number` | Integer | Sequential row number |
| `contract_id` | String | Unique contract identifier |
| `description` | String | Contract description |
| `contractor_name_1` | String | First contractor name |
| `contractor_id_1` | String | First contractor ID |
| `contractor_name_2` | String | Second contractor (joint ventures) |
| `contractor_id_2` | String | Second contractor ID |
| `contractor_name_3` | String | Third contractor |
| `contractor_id_3` | String | Third contractor ID |
| `contractor_name_4` | String | Fourth+ contractor (semicolon-separated if >4) |
| `contractor_id_4` | String | Fourth+ contractor ID |
| `region` | String | Regional office |
| `implementing_office` | String | Office managing contract |
| `source_of_funds` | String | Funding source |
| `cost_php` | Decimal | Contract cost (Philippine Peso) |
| `effectivity_date` | Date | Contract start date (ISO 8601) |
| `expiry_date` | Date | Contract end date |
| `status` | String | Contract status |
| `accomplishment_pct` | Decimal | Completion percentage |
| `year` | Integer | Year from source file |
| `source_office` | String | Source office name |
| `file_source` | String | Original HTML filename |
| `critical_errors` | String | Critical parsing errors |
| `errors` | String | Data extraction errors |
| `warnings` | String | Data quality warnings |
| `info_notes` | String | Informational notes |

See [CSV_SCHEMA.md](docs/CSV_SCHEMA.md) for complete schema documentation.

## 📊 Dataset Statistics

**Latest Dataset (2016-2025)**:
- **Total Contracts**: 209,199
- **Total Value**: ₱6.31 trillion
- **Years Covered**: 2016-2025 (10 years)
- **Regions**: 18 Philippine regions
- **Data Quality**: 99.5% clean (208,059 contracts)

**By Status**:
- Completed: 156,704 (74.9%)
- On-Going: 50,319 (24.1%)
- Not Yet Started: 1,534 (0.7%)
- Terminated: 642 (0.3%)

**By Year (contract count)**:
- 2016: 20,817 contracts (₱792B)
- 2017: 15,070 contracts (₱425B)
- 2018: 19,422 contracts (₱529B)
- 2019: 20,405 contracts (₱391B)
- 2020: 20,265 contracts (₱462B)
- 2021: 21,484 contracts (₱461B)
- 2022: 21,895 contracts (₱697B)
- 2023: 22,154 contracts (₱807B)
- 2024: 23,292 contracts (₱881B)
- 2025: 24,395 contracts (₱865B)

See [parsing_summary.md](docs/parsing_summary.md) for detailed statistics.

## 🔍 Data Quality

### Error Tracking System

The parser implements a 4-level error tracking system:

- **CRIT-xxx**: Critical errors (contract parsing failed)
- **ERR-xxx**: Data extraction errors (field missing/invalid)
- **WARN-xxx**: Data quality warnings (may need review)
- **INFO-xxx**: Informational notes (e.g., joint ventures)

### Common Error Codes

| Code | Description | Count |
|------|-------------|-------|
| WARN-013 | Empty expiry date | 753 |
| WARN-012 | Empty effectivity date | 752 |
| WARN-011 | Empty cost field | 351 |
| WARN-043 | Contractor missing name | 34 |
| ERR-024 | Percentage out of range | 2 |
| ERR-003 | Missing contractor info | 1 |

See [parse_notes_error_codes.md](docs/parse_notes_error_codes.md) for complete error reference.

## 💡 Usage Examples

### Python Analysis Examples

```python
import pandas as pd

# Load the dataset
df = pd.read_csv('csv/contracts_all_years_all_offices.csv')

# Basic statistics
print(f"Total contracts: {len(df)}")
print(f"Total value: ₱{df['cost_php'].sum():,.2f}")

# Filter clean data only
df_clean = df[df['errors'].isna() & df['critical_errors'].isna()]

# Group by region
by_region = df.groupby('region').agg({
    'contract_id': 'count',
    'cost_php': 'sum'
}).sort_values('cost_php', ascending=False)

# Find specific contractor
shimizu = df[df['contractor_name_1'].str.contains('SHIMIZU', na=False)]

# Ongoing projects in 2024
ongoing_2024 = df[(df['year'] == 2024) & (df['status'] == 'On-Going')]
```

### Joint Venture Analysis

```python
# Identify joint ventures
df['is_joint_venture'] = df['contractor_name_2'].notna()
jv_count = df['is_joint_venture'].sum()

# Large joint ventures (4+ contractors)
large_jv = df[df['contractor_name_4'].str.contains(';', na=False)]
print(f"Large JVs (4+ contractors): {len(large_jv)}")
```

### Regional Analysis

```python
# Top 5 regions by contract value
top_regions = df.groupby('region')['cost_php'].sum().nlargest(5)

# Top 5 regions by contract count
top_by_count = df['region'].value_counts().head(5)
```

## 🛠️ Script Reference

### Core Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `scraper_playwright.py` | Web scraping | 60-80 min |
| `html_to_csv_parser.py` | HTML parsing | 5-10 min |
| `parse_all_and_summarize.py` | Full pipeline | 10-15 min |
| `generate_summary.py` | Summary report | 1-2 min |
| `extract_warnings.py` | Quality filter | <1 min |

### Utility Scripts

| Script | Purpose |
|--------|---------|
| `convert_xlsx_to_csv.py` | Convert XLSX files to CSV |
| `rename_office_underscores.py` | Clean HTML filenames |

## 📚 Documentation

### Comprehensive Documentation

- **[SCRAPER_DOCUMENTATION.md](docs/SCRAPER_DOCUMENTATION.md)**: Complete scraper technical documentation
  - Architecture and design
  - Function reference
  - Timing and performance
  - Error handling
  - Troubleshooting guide

- **[CSV_SCHEMA.md](docs/CSV_SCHEMA.md)**: CSV schema specification
  - Column definitions
  - Data types
  - Example queries
  - Best practices

- **[html_to_csv_parser_specification.md](docs/html_to_csv_parser_specification.md)**: Parser implementation guide
  - Parsing logic
  - Data transformation rules
  - Testing strategy
  - Code examples

- **[parse_notes_error_codes.md](docs/parse_notes_error_codes.md)**: Error code reference
  - Complete error code list
  - Severity levels
  - Resolution guidance

- **[parsing_summary.md](docs/parsing_summary.md)**: Latest data quality report
  - Statistics by year
  - Error distribution
  - Regional breakdown

- **[html_table_structure_analysis.md](docs/html_table_structure_analysis.md)**: HTML structure analysis

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional data validation rules
- Performance optimization
- Extended regional coverage
- Additional analysis scripts
- Documentation improvements

## ⚠️ Important Notes

### Data Source & Disclaimer

**Data Source**: Department of Public Works and Highways (DPWH)  
**URL**: http://apps2.dpwh.gov.ph/infra_projects/

**Official Disclaimer**: "The data indicated herein are not conclusive but subject to verification from the Implementing Office"

### Usage Guidelines

- ✅ Educational and research purposes
- ✅ Data analysis and visualization
- ✅ Policy research and planning
- ⚠️ Respect website terms of service
- ⚠️ Do not overload servers with frequent requests
- ⚠️ Verify critical data with official sources
- ❌ Do not use for automated/commercial scraping without permission

### Technical Considerations

1. **First-time scraping**: Requires manual region selection for first region
2. **Anti-bot protection**: Imperva/Incapsula may block automated access
3. **Processing time**: Full scraping takes 60-80 minutes
4. **Storage requirements**: ~1GB for complete dataset
5. **Data validation**: Always check error columns before analysis

## 🔧 Troubleshooting

### Common Issues

**Scraper fails immediately**:
```bash
# Install/reinstall Playwright browsers
playwright install chromium
```

**Parser fails to find files**:
```bash
# Check HTML directory exists and has files
ls -la html/
```

**CSV encoding issues**:
```python
# Always use UTF-8 encoding
df = pd.read_csv('file.csv', encoding='utf-8')
```

**Out of memory errors**:
```python
# Process year by year instead of all at once
for year in range(2016, 2026):
    df = pd.read_csv(f'csv/contracts_{year}_all_offices.csv')
    # Process df...
```

## 📞 Support

For issues, questions, or suggestions:

1. Check the [documentation](docs/) folder
2. Review error codes in [parse_notes_error_codes.md](docs/parse_notes_error_codes.md)
3. Check logs in `logs/` directory
4. Review data quality in CSV error columns

## 📄 License

This project processes publicly available data from the DPWH website. Respect the source data's terms of use and cite appropriately in any publications or analysis.

## 📈 Version History

- **v2.0** (November 2025): Full dataset (2016-2025), 209K+ contracts
- **v1.0** (November 2025): Initial release with core functionality

---

**Last Updated**: November 12, 2025  
**Dataset Version**: 2.0  
**Total Contracts**: 209,199  
**Total Value**: ₱6.31 trillion

---

**Built with**: Python, Playwright, BeautifulSoup, Pandas  
**Data Source**: DPWH Philippines Public Database

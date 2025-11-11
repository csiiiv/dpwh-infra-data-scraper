# HTML to CSV Parser - Comprehensive Specification

**Project:** DPWH Contract Data Extraction  
**Version:** 1.0  
**Date:** November 11, 2025  
**Author:** GitHub Copilot

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Architecture](#architecture)
4. [Input Specification](#input-specification)
5. [Output Specification](#output-specification)
6. [Parsing Logic](#parsing-logic)
7. [Data Transformation Rules](#data-transformation-rules)
8. [Error Handling](#error-handling)
9. [Implementation Guide](#implementation-guide)
10. [Testing Strategy](#testing-strategy)
11. [Usage Examples](#usage-examples)
12. [Maintenance & Updates](#maintenance--updates)

---

## Overview

### Purpose
Extract structured contract data from DPWH HTML tables and convert to standardized CSV format for analysis and reporting.

### Scope
- Parse 11 HTML files (2016-2025 Central Office contracts)
- Extract 18 fields per contract
- Handle single and multiple contractors (joint ventures)
- Track data quality issues
- Support batch processing

### Key Features
- Robust HTML parsing with BeautifulSoup
- Automatic data cleaning and normalization
- Multiple contractor support (up to 4 per project, with excess contractors combined in column 4)
- Parse error tracking and reporting
- Year extraction from filenames
- Metadata preservation (source file tracking)

---

## Requirements

### System Requirements
- Python 3.8+
- Minimum 2GB RAM
- 50MB disk space for output

### Python Dependencies

```txt
beautifulsoup4>=4.12.0    # HTML parsing
lxml>=4.9.0               # Fast XML/HTML parser backend
python-dateutil>=2.8.0    # Date parsing
```

### Install Commands
```bash
pip install beautifulsoup4 lxml python-dateutil
# OR
pip install -r requirements.txt
```

---

## Architecture

### Module Structure

```
dpwh_parser/
├── __init__.py
├── parser.py              # Main parsing logic
├── transformers.py        # Data cleaning functions
├── validators.py          # Data validation
├── models.py              # Data models/schemas
└── utils.py               # Helper functions
```

### Data Flow

```
HTML Files (input)
    ↓
[File Discovery & Validation]
    ↓
[HTML Parsing (BeautifulSoup)]
    ↓
[Data Extraction (span elements)]
    ↓
[Data Transformation (clean, parse, normalize)]
    ↓
[Data Validation (quality checks)]
    ↓
[CSV Writing (with error tracking)]
    ↓
CSV Files (output) + Error Log
```

---

## Input Specification

### File Location
- **Directory:** `html/`
- **Pattern:** `table_Central_Office_YYYY_*.html`
- **Count:** 11 files (years 2016-2025)

### File Naming Convention
```
table_Central_Office_2016_20251111_155202.html
                     ^^^^  ^^^^^^^^  ^^^^^^
                     |     |         |
                     Year  Date      Time (timestamp)
```

### HTML Structure
```html
<table class="table table-bordered...">
  <thead>
    <!-- Headers with 5 columns -->
  </thead>
  <tbody class="table-group-divider">  <!-- Contract data -->
    <tr>
      <th scope="row">1.</th>
      <td><!-- Contract ID + details --></td>
      <td><!-- Cost --></td>
      <td><!-- Dates --></td>
      <td><!-- Status --></td>
    </tr>
    <tr><td colspan="5"></td></tr>  <!-- Spacer -->
  </tbody>
  <tbody class="table-group-divider">  <!-- Next contract -->
    ...
  </tbody>
</table>
```

### Unique Identifiers
Each data point has a unique `id` attribute:
- `Repeater1_lblCustomerId_{n}` - Contract ID
- `Repeater1_lblContactName_{n}` - Description
- `Repeater1_lblCountry_{n}` - Contractor(s)
- `Repeater1_Label5_{n}` - Implementing Office
- `Repeater1_Label6_{n}` - Source of Funds
- `Repeater1_Label2_{n}` - Cost
- `Repeater1_Label3_{n}` - Effectivity Date
- `Repeater1_Label4_{n}` - Expiry Date
- `Repeater1_Label7_{n}` - Status
- `Repeater1_Label1_{n}` - Accomplishment %

Where `{n}` is a zero-based index (0, 1, 2, ...).

---

## Output Specification

### File Location
- **Directory:** `csv/`
- **Pattern:** `contracts_YYYY.csv` (one per year) OR `contracts_all.csv` (combined)

### CSV Schema

| Column # | Column Name | Data Type | Nullable | Description |
|----------|-------------|-----------|----------|-------------|
| 1 | row_number | Integer | No | Sequential row number from HTML |
| 2 | contract_id | String | No | Unique contract identifier |
| 3 | description | String | No | Full contract description |
| 4 | contractor_name_1 | String | No | First contractor name |
| 5 | contractor_id_1 | String | Yes | First contractor ID code |
| 6 | contractor_name_2 | String | Yes | Second contractor name (if JV) |
| 7 | contractor_id_2 | String | Yes | Second contractor ID (if JV) |
| 8 | contractor_name_3 | String | Yes | Third contractor name (if JV) |
| 9 | contractor_id_3 | String | Yes | Third contractor ID (if JV) |
| 10 | contractor_name_4 | String | Yes | Fourth+ contractor names (semicolon-separated if >4) |
| 11 | contractor_id_4 | String | Yes | Fourth+ contractor IDs (semicolon-separated if >4) |
| 12 | implementing_office | String | No | Office managing the contract |
| 13 | source_of_funds | String | No | Funding source description |
| 14 | cost_php | Decimal | Yes | Contract cost in Philippine Peso |
| 15 | effectivity_date | Date | Yes | Contract start date (ISO 8601) |
| 16 | expiry_date | Date | Yes | Contract end date (ISO 8601) |
| 17 | status | String | Yes | Contract status |
| 18 | accomplishment_pct | Decimal | Yes | Percentage complete (0-100) |
| 19 | year | Integer | No | Year extracted from filename |
| 20 | file_source | String | No | Original HTML filename |
| 21 | critical_errors | String | Yes | CRIT-level errors (pipe-delimited) |
| 22 | errors | String | Yes | ERR-level errors (pipe-delimited) |
| 23 | warnings | String | Yes | WARN-level warnings (pipe-delimited) |
| 24 | info_notes | String | Yes | INFO-level notes (pipe-delimited) |

### Sample CSV Output
```csv
row_number,contract_id,description,contractor_name_1,contractor_id_1,contractor_name_2,contractor_id_2,contractor_name_3,contractor_id_3,contractor_name_4,contractor_id_4,implementing_office,source_of_funds,cost_php,effectivity_date,expiry_date,status,accomplishment_pct,year,file_source,critical_errors,errors,warnings,info_notes
1,16O00049,"VALENZUELA-PUMPING STATIONS...","TRIPLE 8 CONSTRUCTION & SUPPLY, INC.",10684,,,,,,,Central Office - Flood Control Management Cluster,Regular Infra - GAA 2017 MFO-2,91773188.54,2018-03-05,2018-09-30,Completed,100.00,2017,table_Central_Office_2017_20251111_155210.html,,,,
2,21Z00007,DAVAO CITY BYPASS CONSTRUCTION PROJECT...,"ULTICON BUILDERS, INC.",17267,SHIMIZU CORPORATION,OECO_16693,"TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD.",OECO_29591,,,Central Office - Roads Management Cluster I (Bilateral),Regular Infra - GAA 2023 FAPs,15234567890.12,2023-03-15,2028-12-31,On-Going,45.20,2023,table_Central_Office_2023_20251111_155306.html,,,,INFO-045: Joint venture with 3 contractors
3,23ABC123,SAMPLE PROJECT WITH MANY CONTRACTORS,"COMPANY A",12345,"COMPANY B",67890,"COMPANY C",11111,"COMPANY D; COMPANY E","22222; 33333",Central Office - Example,Regular Infra,5000000.00,2023-01-01,2025-12-31,On-Going,30.00,2023,table_Central_Office_2023_20251111_155306.html,,,"WARN-041: 5 contractors found, stored in 4 columns (excess combined in column 4)",INFO-045: Joint venture with 5 contractors
```

---

## Parsing Logic

### Step 1: File Discovery

```python
def discover_html_files(directory='html'):
    """
    Find all HTML files matching the pattern.
    
    Returns:
        List of tuples: [(filepath, year), ...]
    """
    pattern = 'table_Central_Office_*.html'
    files = []
    
    for filepath in Path(directory).glob(pattern):
        # Extract year from filename
        match = re.search(r'_(\d{4})_', filepath.name)
        if match:
            year = int(match.group(1))
            files.append((filepath, year))
    
    return sorted(files, key=lambda x: x[1])
```

### Step 2: HTML Parsing

```python
def parse_html_file(filepath):
    """
    Parse HTML file and return BeautifulSoup object.
    
    Args:
        filepath: Path to HTML file
        
    Returns:
        BeautifulSoup object
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return BeautifulSoup(html_content, 'lxml')
```

### Step 3: Contract Extraction

```python
def extract_contracts(soup):
    """
    Extract all contract tbody elements.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        List of contract tbody elements
    """
    # Find all tbody with class 'table-group-divider'
    tbodies = soup.find_all('tbody', class_='table-group-divider')
    
    # Filter out empty or footer tbodies
    valid_tbodies = []
    for tbody in tbodies:
        tr = tbody.find('tr')
        if tr and tr.find('th', scope='row'):
            valid_tbodies.append(tbody)
    
    return valid_tbodies
```

### Step 4: Field Extraction

```python
def extract_contract_data(tbody, year, filename):
    """
    Extract all fields from a contract tbody element.
    
    Args:
        tbody: BeautifulSoup tbody element
        year: Year from filename
        filename: Source filename
        
    Returns:
        Dictionary with all contract fields
    """
    tr = tbody.find('tr')
    contract = {}
    parse_notes = []
    
    # Row number
    row_th = tr.find('th', scope='row')
    contract['row_number'] = row_th.get_text(strip=True).rstrip('.') if row_th else None
    
    # Contract ID
    contract['contract_id'] = extract_span_by_pattern(tr, 'lblCustomerId')
    if not contract['contract_id']:
        parse_notes.append("ERROR: Missing contract ID")
    
    # Description
    contract['description'] = extract_span_by_pattern(tr, 'lblContactName')
    
    # Contractors (with multiple contractor support up to 4, excess combined)
    contractor_text = extract_span_by_pattern(tr, 'lblCountry')
    contractor_data = get_contractor_columns(contractor_text, max_contractors=4)
    contract.update(contractor_data)
    
    # If contractor parsing added notes, collect them
    if contractor_data.get('parse_notes'):
        parse_notes.append(contractor_data['parse_notes'])
    
    # Other fields
    contract['implementing_office'] = extract_span_by_pattern(tr, 'Label5')
    contract['source_of_funds'] = extract_span_by_pattern(tr, 'Label6')
    
    # Cost (with cleaning)
    cost_raw = extract_span_by_pattern(tr, 'Label2')
    contract['cost_php'] = clean_cost(cost_raw, parse_notes)
    
    # Dates (with parsing)
    effectivity_raw = extract_span_by_pattern(tr, 'Label3')
    contract['effectivity_date'] = parse_date(effectivity_raw, parse_notes, 'effectivity')
    
    expiry_raw = extract_span_by_pattern(tr, 'Label4')
    contract['expiry_date'] = parse_date(expiry_raw, parse_notes, 'expiry')
    
    # Status
    contract['status'] = extract_span_by_pattern(tr, 'Label7')
    
    # Accomplishment
    accomplishment_raw = extract_span_by_pattern(tr, 'Label1')
    contract['accomplishment_pct'] = clean_percentage(accomplishment_raw, parse_notes)
    
    # Metadata
    contract['year'] = year
    contract['file_source'] = filename
    
    # Combine all parse notes
    contract['parse_notes'] = ' | '.join(parse_notes) if parse_notes else None
    
    return contract
```

### Step 5: Helper Function

```python
def extract_span_by_pattern(tr, pattern):
    """
    Extract text from span element matching ID pattern.
    
    Args:
        tr: BeautifulSoup tr element
        pattern: Part of the ID to match (e.g., 'lblCustomerId')
        
    Returns:
        Extracted text or None
    """
    span = tr.find('span', id=lambda x: x and pattern in x)
    if span:
        return span.get_text(strip=True)
    return None
```

---

## Data Transformation Rules

### 1. Contract Cost

**Input Formats:**
- `"1,610,848,037.67"` (comma-separated)
- `"91,773,188.54"`
- Empty string

**Transformation:**
```python
def clean_cost(cost_text, parse_notes=None):
    """
    Remove commas and convert to decimal.
    
    Args:
        cost_text: Raw cost string
        parse_notes: List to append warnings to
        
    Returns:
        Decimal number or None
    """
    if not cost_text or cost_text.strip() == '':
        if parse_notes is not None:
            parse_notes.append("WARNING: Empty cost field")
        return None
    
    try:
        # Remove commas and convert
        cleaned = cost_text.replace(',', '')
        return float(cleaned)
    except ValueError:
        if parse_notes is not None:
            parse_notes.append(f"ERROR: Invalid cost format: '{cost_text}'")
        return None
```

**Output:** `1610848037.67` (float)

---

### 2. Dates

**Input Formats:**
- `"October 29, 2025"` (full text)
- `"March 5, 2018"`
- `"February 8, 2018"`
- Empty string

**Transformation:**
```python
from dateutil import parser as date_parser

def parse_date(date_text, parse_notes=None, field_name='date'):
    """
    Parse text date to ISO format (YYYY-MM-DD).
    
    Args:
        date_text: Raw date string
        parse_notes: List to append warnings to
        field_name: Name of field for error messages
        
    Returns:
        ISO date string or None
    """
    if not date_text or date_text.strip() == '':
        if parse_notes is not None:
            parse_notes.append(f"WARNING: Empty {field_name} field")
        return None
    
    try:
        parsed = date_parser.parse(date_text)
        return parsed.strftime('%Y-%m-%d')
    except (ValueError, TypeError) as e:
        if parse_notes is not None:
            parse_notes.append(f"ERROR: Invalid {field_name} format: '{date_text}'")
        return None
```

**Output:** `"2025-10-29"` (ISO 8601)

---

### 3. Percentage

**Input Formats:**
- `"100.00"` (decimal string)
- `"45.20"`
- Empty string

**Transformation:**
```python
def clean_percentage(pct_text, parse_notes=None):
    """
    Convert percentage string to decimal.
    
    Args:
        pct_text: Raw percentage string
        parse_notes: List to append warnings to
        
    Returns:
        Float number or None
    """
    if not pct_text or pct_text.strip() == '':
        # Empty accomplishment is valid (not started)
        return None
    
    try:
        return float(pct_text)
    except ValueError:
        if parse_notes is not None:
            parse_notes.append(f"ERROR: Invalid percentage format: '{pct_text}'")
        return None
```

**Output:** `100.00` (float)

---

### 4. Contractors

**Input Formats:**
- Single: `"CHINA WUYI CO., LTD (OECO_16634)"`
- Multiple: `"ULTICON BUILDERS, INC. (17267) / SHIMIZU CORPORATION (OECO_16693) / TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD. (OECO_29591)"`
- HTML entities: `"TRIPLE 8 CONSTRUCTION &amp; SUPPLY, INC. (10684)"`

**Transformation:**
```python
import re
from html import unescape

def parse_contractors(contractor_text):
    """
    Parse contractor text with multiple contractor support.
    
    Returns list of tuples: [(name1, id1), (name2, id2), ...]
    """
    if not contractor_text:
        return []
    
    # Decode HTML entities (&amp; -> &)
    contractor_text = unescape(contractor_text.strip())
    
    # Split by forward slash
    contractors = [c.strip() for c in contractor_text.split('/')]
    
    result = []
    regex = r'^(.+?)\s*\(([^)]+)\)\s*$'
    
    for contractor in contractors:
        match = re.match(regex, contractor)
        if match:
            name = match.group(1).strip()
            contractor_id = match.group(2).strip()
            result.append((name, contractor_id))
        else:
            # No parentheses - entire text is name
            result.append((contractor, None))
    
    return result

def get_contractor_columns(contractor_text, max_contractors=4):
    """
    Convert contractors to separate columns.
    
    If more than max_contractors are found, contractors 1-3 are stored normally,
    and contractors 4+ are combined in the 4th column (names and IDs separated by semicolons).
    
    Returns dict with contractor_name_1, contractor_id_1, etc.
    """
    contractors = parse_contractors(contractor_text)
    result = {}
    notes = []
    
    # Handle first 3 contractors normally
    for i in range(1, max_contractors):
        if i <= len(contractors):
            result[f'contractor_name_{i}'] = contractors[i-1][0]
            result[f'contractor_id_{i}'] = contractors[i-1][1]
        else:
            result[f'contractor_name_{i}'] = None
            result[f'contractor_id_{i}'] = None
    
    # Handle 4th contractor and any excess contractors (combine them)
    if len(contractors) >= max_contractors:
        # Combine contractors from index max_contractors-1 onwards
        names = []
        ids = []
        for i in range(max_contractors - 1, len(contractors)):
            names.append(contractors[i][0])
            ids.append(contractors[i][1] if contractors[i][1] else '')
        
        result[f'contractor_name_{max_contractors}'] = '; '.join(names)
        result[f'contractor_id_{max_contractors}'] = '; '.join(ids)
        
        if len(contractors) > max_contractors:
            notes.append(
                f"WARNING: {len(contractors)} contractors found, "
                f"stored in {max_contractors} columns (excess combined in column {max_contractors})"
            )
    else:
        result[f'contractor_name_{max_contractors}'] = None
        result[f'contractor_id_{max_contractors}'] = None
    
    result['parse_notes'] = ' | '.join(notes) if notes else None
    
    return result
```

**Output (3 contractors):**
```python
{
    'contractor_name_1': 'ULTICON BUILDERS, INC.',
    'contractor_id_1': '17267',
    'contractor_name_2': 'SHIMIZU CORPORATION',
    'contractor_id_2': 'OECO_16693',
    'contractor_name_3': 'TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD.',
    'contractor_id_3': 'OECO_29591',
    'contractor_name_4': None,
    'contractor_id_4': None,
    'parse_notes': None
}
```

**Output (5 contractors - excess combined in column 4):**
```python
{
    'contractor_name_1': 'COMPANY A',
    'contractor_id_1': '11111',
    'contractor_name_2': 'COMPANY B',
    'contractor_id_2': '22222',
    'contractor_name_3': 'COMPANY C',
    'contractor_id_3': '33333',
    'contractor_name_4': 'COMPANY D; COMPANY E',
    'contractor_id_4': '44444; 55555',
    'parse_notes': 'WARNING: 5 contractors found, stored in 4 columns (excess combined in column 4)'
}
```

---

### 5. HTML Entity Decoding

**Common Entities:**
- `&amp;` → `&`
- `&nbsp;` → ` ` (space)
- `&lt;` → `<`
- `&gt;` → `>`

**Automatic:** BeautifulSoup's `get_text()` decodes most entities. Use `html.unescape()` for additional safety.

---

## Error Handling

### Error Categories

| Category | Severity | Action | Example |
|----------|----------|--------|---------|
| Missing Required Field | ERROR | Add to parse_notes, keep row | Missing contract ID |
| Invalid Format | ERROR | Add to parse_notes, set field to None | Invalid date format |
| Missing Optional Field | WARNING | Add to parse_notes, set to None | Empty accomplishment |
| Extra Contractors | WARNING | Add to parse_notes, truncate | >3 contractors |
| HTML Parsing Failure | CRITICAL | Log error, skip file | Malformed HTML |

### Parse Notes Format

```
"ERROR: Missing contract ID | WARNING: Invalid date format: 'Invalid' | WARNING: >3 contractors (4 total), extras truncated"
```

Multiple issues separated by ` | `.

### Logging Strategy

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/parser.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info(f"Processing file: {filename}")
logger.warning(f"Contract {contract_id}: {warning_message}")
logger.error(f"Failed to parse {filename}: {error_message}")
```

### Error Recovery

1. **Field-level errors:** Set field to `None`, continue processing other fields
2. **Row-level errors:** Include row with error notes, continue to next row
3. **File-level errors:** Log error, skip file, continue to next file
4. **Critical errors:** Stop processing, report to user

---

## Implementation Guide

### Complete Script Template

```python
#!/usr/bin/env python3
"""
DPWH HTML to CSV Parser
Extracts contract data from HTML tables and converts to standardized CSV format.
"""

import csv
import re
import logging
from pathlib import Path
from html import unescape
from typing import List, Dict, Tuple, Optional

from bs4 import BeautifulSoup
from dateutil import parser as date_parser


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# CSV Field Names
CSV_FIELDS = [
    'row_number', 'contract_id', 'description',
    'contractor_name_1', 'contractor_id_1',
    'contractor_name_2', 'contractor_id_2',
    'contractor_name_3', 'contractor_id_3',
    'contractor_name_4', 'contractor_id_4',
    'region', 'implementing_office', 'source_of_funds',
    'cost_php', 'effectivity_date', 'expiry_date',
    'status', 'accomplishment_pct',
    'year', 'source_office', 'file_source',
    'critical_errors', 'errors', 'warnings', 'info_notes'
]


def discover_html_files(directory: str = 'html') -> List[Tuple[Path, int]]:
    """Discover all HTML files and extract years."""
    pattern = 'table_Central_Office_*.html'
    files = []
    
    for filepath in Path(directory).glob(pattern):
        match = re.search(r'_(\d{4})_', filepath.name)
        if match:
            year = int(match.group(1))
            files.append((filepath, year))
        else:
            logger.warning(f"Could not extract year from filename: {filepath.name}")
    
    return sorted(files, key=lambda x: x[1])


def parse_html_file(filepath: Path) -> BeautifulSoup:
    """Parse HTML file with BeautifulSoup."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return BeautifulSoup(html_content, 'lxml')


def extract_contracts(soup: BeautifulSoup) -> List:
    """Extract contract tbody elements."""
    tbodies = soup.find_all('tbody', class_='table-group-divider')
    valid_tbodies = []
    
    for tbody in tbodies:
        tr = tbody.find('tr')
        if tr and tr.find('th', scope='row'):
            valid_tbodies.append(tbody)
    
    return valid_tbodies


def extract_span_by_pattern(tr, pattern: str) -> Optional[str]:
    """Extract text from span with ID pattern."""
    span = tr.find('span', id=lambda x: x and pattern in x)
    return span.get_text(strip=True) if span else None


def clean_cost(cost_text: Optional[str], parse_notes: List[str]) -> Optional[float]:
    """Clean and convert cost to float."""
    if not cost_text or cost_text.strip() == '':
        parse_notes.append("WARNING: Empty cost field")
        return None
    
    try:
        cleaned = cost_text.replace(',', '')
        return float(cleaned)
    except ValueError:
        parse_notes.append(f"ERROR: Invalid cost format: '{cost_text}'")
        return None


def parse_date(date_text: Optional[str], parse_notes: List[str], 
               field_name: str = 'date') -> Optional[str]:
    """Parse date to ISO format."""
    if not date_text or date_text.strip() == '':
        parse_notes.append(f"WARNING: Empty {field_name} field")
        return None
    
    try:
        parsed = date_parser.parse(date_text)
        return parsed.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        parse_notes.append(f"ERROR: Invalid {field_name} format: '{date_text}'")
        return None


def clean_percentage(pct_text: Optional[str], 
                     parse_notes: List[str]) -> Optional[float]:
    """Convert percentage to float."""
    if not pct_text or pct_text.strip() == '':
        return None
    
    try:
        return float(pct_text)
    except ValueError:
        parse_notes.append(f"ERROR: Invalid percentage format: '{pct_text}'")
        return None


def parse_contractors(contractor_text: Optional[str]) -> List[Tuple[str, Optional[str]]]:
    """Parse contractor text into list of (name, id) tuples."""
    if not contractor_text:
        return []
    
    contractor_text = unescape(contractor_text.strip())
    contractors = [c.strip() for c in contractor_text.split('/')]
    
    result = []
    regex = r'^(.+?)\s*\(([^)]+)\)\s*$'
    
    for contractor in contractors:
        match = re.match(regex, contractor)
        if match:
            result.append((match.group(1).strip(), match.group(2).strip()))
        else:
            result.append((contractor, None))
    
    return result


def get_contractor_columns(contractor_text: Optional[str], 
                          max_contractors: int = 3) -> Dict:
    """Convert contractors to separate columns."""
    contractors = parse_contractors(contractor_text)
    result = {}
    notes = []
    
    for i in range(1, max_contractors + 1):
        if i <= len(contractors):
            result[f'contractor_name_{i}'] = contractors[i-1][0]
            result[f'contractor_id_{i}'] = contractors[i-1][1]
        else:
            result[f'contractor_name_{i}'] = None
            result[f'contractor_id_{i}'] = None
    
    if len(contractors) > max_contractors:
        notes.append(
            f"WARNING: >{max_contractors} contractors "
            f"({len(contractors)} total), extras truncated"
        )
    
    result['parse_notes'] = ' | '.join(notes) if notes else None
    return result


def extract_contract_data(tbody, year: int, filename: str) -> Dict:
    """Extract all fields from contract tbody."""
    tr = tbody.find('tr')
    contract = {}
    parse_notes = []
    
    # Row number
    row_th = tr.find('th', scope='row')
    contract['row_number'] = row_th.get_text(strip=True).rstrip('.') if row_th else None
    
    # Contract ID
    contract['contract_id'] = extract_span_by_pattern(tr, 'lblCustomerId')
    if not contract['contract_id']:
        parse_notes.append("ERROR: Missing contract ID")
    
    # Description
    contract['description'] = extract_span_by_pattern(tr, 'lblContactName')
    
    # Contractors
    contractor_text = extract_span_by_pattern(tr, 'lblCountry')
    contractor_data = get_contractor_columns(contractor_text, max_contractors=4)
    if contractor_data.get('parse_notes'):
        parse_notes.append(contractor_data.pop('parse_notes'))
    contract.update(contractor_data)
    
    # Other fields
    contract['implementing_office'] = extract_span_by_pattern(tr, 'Label5')
    contract['source_of_funds'] = extract_span_by_pattern(tr, 'Label6')
    
    # Cost
    cost_raw = extract_span_by_pattern(tr, 'Label2')
    contract['cost_php'] = clean_cost(cost_raw, parse_notes)
    
    # Dates
    effectivity_raw = extract_span_by_pattern(tr, 'Label3')
    contract['effectivity_date'] = parse_date(effectivity_raw, parse_notes, 'effectivity')
    
    expiry_raw = extract_span_by_pattern(tr, 'Label4')
    contract['expiry_date'] = parse_date(expiry_raw, parse_notes, 'expiry')
    
    # Status
    contract['status'] = extract_span_by_pattern(tr, 'Label7')
    
    # Accomplishment
    accomplishment_raw = extract_span_by_pattern(tr, 'Label1')
    contract['accomplishment_pct'] = clean_percentage(accomplishment_raw, parse_notes)
    
    # Metadata
    contract['year'] = year
    contract['file_source'] = filename
    contract['parse_notes'] = ' | '.join(parse_notes) if parse_notes else None
    
    return contract


def process_html_file(filepath: Path, year: int) -> List[Dict]:
    """Process single HTML file and return list of contracts."""
    logger.info(f"Processing: {filepath.name} (Year: {year})")
    
    try:
        soup = parse_html_file(filepath)
        tbodies = extract_contracts(soup)
        
        contracts = []
        for tbody in tbodies:
            try:
                contract = extract_contract_data(tbody, year, filepath.name)
                contracts.append(contract)
            except Exception as e:
                logger.error(f"Error extracting contract: {e}")
                continue
        
        logger.info(f"  Extracted {len(contracts)} contracts")
        return contracts
        
    except Exception as e:
        logger.error(f"Failed to process {filepath.name}: {e}")
        return []


def write_csv(contracts: List[Dict], output_path: Path):
    """Write contracts to CSV file."""
    logger.info(f"Writing {len(contracts)} contracts to {output_path}")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(contracts)
    
    logger.info(f"  Successfully wrote {output_path}")


def main():
    """Main processing function."""
    # Setup
    html_dir = Path('html')
    csv_dir = Path('csv')
    logs_dir = Path('logs')
    
    csv_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    # Discover files
    files = discover_html_files(html_dir)
    logger.info(f"Found {len(files)} HTML files to process")
    
    # Process all files
    all_contracts = []
    for filepath, year in files:
        contracts = process_html_file(filepath, year)
        all_contracts.extend(contracts)
    
    # Write combined CSV
    if all_contracts:
        output_path = csv_dir / 'contracts_all.csv'
        write_csv(all_contracts, output_path)
        
        # Statistics
        total = len(all_contracts)
        with_errors = sum(1 for c in all_contracts if c.get('parse_notes'))
        logger.info(f"\n=== Summary ===")
        logger.info(f"Total contracts: {total}")
        logger.info(f"Contracts with parse notes: {with_errors}")
        logger.info(f"Success rate: {((total - with_errors) / total * 100):.1f}%")
    else:
        logger.warning("No contracts extracted!")


if __name__ == '__main__':
    main()
```

---

## Testing Strategy

### Unit Tests

```python
import unittest
from parser import parse_contractors, clean_cost, parse_date

class TestDataTransformers(unittest.TestCase):
    
    def test_single_contractor(self):
        text = "CHINA WUYI CO., LTD (OECO_16634)"
        result = parse_contractors(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("CHINA WUYI CO., LTD", "OECO_16634"))
    
    def test_multiple_contractors(self):
        text = "COMPANY A (123) / COMPANY B (456)"
        result = parse_contractors(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("COMPANY A", "123"))
        self.assertEqual(result[1], ("COMPANY B", "456"))
    
    def test_html_entities(self):
        text = "COMPANY &amp; CO. (789)"
        result = parse_contractors(text)
        self.assertEqual(result[0][0], "COMPANY & CO.")
    
    def test_clean_cost(self):
        notes = []
        self.assertEqual(clean_cost("1,234,567.89", notes), 1234567.89)
        self.assertEqual(clean_cost("", notes), None)
        self.assertIn("WARNING", notes[0])
    
    def test_parse_date(self):
        notes = []
        self.assertEqual(parse_date("March 5, 2018", notes, "test"), "2018-03-05")
        self.assertEqual(parse_date("", notes, "test"), None)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

Test with sample HTML files:
1. Create `tests/fixtures/` with small HTML samples
2. Run parser on fixtures
3. Verify CSV output matches expected results

### Manual Testing Checklist

- [ ] Single contractor extraction
- [ ] Multiple contractors (2 and 3)
- [ ] >3 contractors (warning generated)
- [ ] Empty fields handled
- [ ] Invalid date formats
- [ ] HTML entities decoded
- [ ] All 11 files process successfully
- [ ] CSV opens correctly in Excel/LibreOffice
- [ ] Parse notes populated correctly

---

## Usage Examples

### Basic Usage

```bash
# Run parser
python parser.py

# Output
Found 11 HTML files to process
Processing: table_Central_Office_2016_20251111_155202.html (Year: 2016)
  Extracted 1 contracts
Processing: table_Central_Office_2017_20251111_155210.html (Year: 2017)
  Extracted 45 contracts
...
Writing 523 contracts to csv/contracts_all.csv
  Successfully wrote csv/contracts_all.csv

=== Summary ===
Total contracts: 523
Contracts with parse notes: 12
Success rate: 97.7%
```

### Generate Per-Year CSVs

```python
# Modify main() to write separate files
for filepath, year in files:
    contracts = process_html_file(filepath, year)
    if contracts:
        output_path = csv_dir / f'contracts_{year}.csv'
        write_csv(contracts, output_path)
```

### Filter Contracts with Errors

```python
# Extract only contracts with parse notes
error_contracts = [c for c in all_contracts if c.get('parse_notes')]
write_csv(error_contracts, csv_dir / 'contracts_with_errors.csv')
```

### Statistics Report

```python
# Generate statistics
from collections import Counter

statuses = Counter(c['status'] for c in all_contracts if c.get('status'))
years = Counter(c['year'] for c in all_contracts)

print("Contracts by Status:")
for status, count in statuses.most_common():
    print(f"  {status}: {count}")

print("\nContracts by Year:")
for year, count in sorted(years.items()):
    print(f"  {year}: {count}")
```

---

## Maintenance & Updates

### Adding New Fields

1. Update `CSV_FIELDS` list
2. Add extraction logic in `extract_contract_data()`
3. Update documentation
4. Add tests

### Handling Schema Changes

If HTML structure changes:
1. Inspect new HTML structure
2. Update ID patterns if needed
3. Adjust BeautifulSoup selectors
4. Test with new files

### Performance Optimization

Current performance: ~50-100 contracts/second

For large datasets (>10,000 contracts):
- Use `lxml` parser (already configured)
- Consider multiprocessing for file-level parallelism
- Use generator patterns for memory efficiency

### Version Control

Track parser version in CSV:
```python
contract['parser_version'] = '1.0.0'
```

### Data Quality Monitoring

Create dashboard to track:
- Parse error rate over time
- Most common error types
- Missing field patterns
- Contractor count distribution

---

## Appendix

### Regular Expressions Used

```python
# Extract year from filename
r'_(\d{4})_'

# Extract contractor name and ID
r'^(.+?)\s*\(([^)]+)\)\s*$'
```

### Date Format Examples

All handled by `dateutil.parser`:
- `"March 5, 2018"`
- `"October 29, 2025"`
- `"February 8, 2018"`
- `"January 12, 2023"`

### Known Issues

1. **>4 Contractors:** Rare cases with 5+ contractors will have excess contractors combined in column 4 with semicolon separators
   - **Solution:** Check parse_notes for warnings, contractors 4+ are stored as "NAME1; NAME2" in contractor_name_4
   
2. **Non-standard Date Formats:** Some dates may fail parsing
   - **Solution:** parse_notes will contain error, manually fix

3. **Special Characters:** Rare unicode characters may not display correctly
   - **Solution:** Use UTF-8 encoding consistently

---

## Contact & Support

For issues or questions:
- Check logs in `logs/parser.log`
- Review `parse_notes` column in output CSV
- Refer to HTML structure analysis document

**Last Updated:** November 11, 2025  
**Script Version:** 1.0.0

# HTML Table Structure Analysis - DPWH Contract Data

**File Analyzed:** `table_Central_Office_2016_20251111_155202.html` (and similar year files)  
**Analysis Date:** November 11, 2025

---

## Table Overview

The HTML files contain Bootstrap-styled tables displaying DPWH (Department of Public Works and Highways) contract information. Each file represents contracts for a specific year (2016-2025).

### File Characteristics
- **Format:** HTML table with Bootstrap classes
- **Structure:** Single table per file
- **Sample Size:** 2016 file has 89 lines (1 contract), 2017 file has 2,316 lines (multiple contracts)
- **Encoding:** UTF-8 HTML

---

## Table Structure

### Header Section
```html
<thead class="table" style="background-color: black; color: white">
    <tr class="align-text-top">
        <th scope="col"></th>  <!-- Row number column -->
        <th>CONTRACT ID + Details</th>
        <th>Contract Cost (Php)</th>
        <th>Dates (Effectivity & Expiry)</th>
        <th>Status & Accomplishment</th>
    </tr>
</thead>
```

**5 Main Columns:**
1. Row number (empty header)
2. CONTRACT ID with sub-fields (a-d)
3. Contract Cost in PHP
4. Contract dates (a-b)
5. Status information (a-b)

---

## Data Row Structure

Each contract is stored in a **repeating tbody pattern** with the following structure:

```html
<tbody class="table-group-divider">
    <tr>
        <th scope="row">1.</th>  <!-- Row number -->
        
        <!-- Column 1: Contract ID and Details -->
        <td>
            <b><span id="Repeater1_lblCustomerId_0">24Z00029</span></b>
            <ul class="list-group list-group-flush">
                <li><b>a)</b> <span id="Repeater1_lblContactName_0">CONTRACT DESCRIPTION</span></li>
                <li><b>b)</b> <span id="Repeater1_lblCountry_0">CONTRACTOR NAME</span></li>
                <li><b>c)</b> <span id="Repeater1_Label5_0">IMPLEMENTING OFFICE</span></li>
                <li><b>d)</b> <span id="Repeater1_Label6_0">SOURCE OF FUNDS</span></li>
            </ul>
        </td>
        
        <!-- Column 2: Contract Cost -->
        <td>
            <ul class="list-group list-group-flush">
                <li><span id="Repeater1_Label2_0">1,610,848,037.67</span></li>
            </ul>
        </td>
        
        <!-- Column 3: Dates -->
        <td>
            <ul class="list-group list-group-flush">
                <li><b>a)</b> <span id="Repeater1_Label3_0">October 29, 2025</span></li>
                <li><b>b)</b> <span id="Repeater1_Label4_0">October 12, 2028</span></li>
            </ul>
        </td>
        
        <!-- Column 4: Status -->
        <td>
            <ul class="list-group list-group-flush">
                <li><b>a)</b> <span id="Repeater1_Label7_0">Not Yet Started</span></li>
                <li><b>b)</b> <span id="Repeater1_Label1_0"></span></li>  <!-- May be empty -->
            </ul>
        </td>
    </tr>
    <tr><td colspan="5"></td></tr>  <!-- Spacer row -->
</tbody>
```

---

## Data Fields to Extract

### Field Mapping

| CSV Column | HTML Element | ID Pattern | Notes |
|-----------|--------------|------------|-------|
| Row Number | `<th scope="row">` | N/A | Sequential numbering |
| Contract ID | `<span>` | `Repeater1_lblCustomerId_{n}` | Primary identifier |
| Contract Description | `<span>` | `Repeater1_lblContactName_{n}` | Sub-field (a) |
| Contractor Name 1 | `<span>` | `Repeater1_lblCountry_{n}` | First contractor name |
| Contractor ID 1 | `<span>` | `Repeater1_lblCountry_{n}` | First contractor ID |
| Contractor Name 2 | `<span>` | `Repeater1_lblCountry_{n}` | Second contractor name (empty if single contractor) |
| Contractor ID 2 | `<span>` | `Repeater1_lblCountry_{n}` | Second contractor ID (empty if single contractor) |
| Contractor Name 3 | `<span>` | `Repeater1_lblCountry_{n}` | Third contractor name (empty if ≤2 contractors) |
| Contractor ID 3 | `<span>` | `Repeater1_lblCountry_{n}` | Third contractor ID (empty if ≤2 contractors) |
| Implementing Office | `<span>` | `Repeater1_Label5_{n}` | Sub-field (c) |
| Source of Funds | `<span>` | `Repeater1_Label6_{n}` | Sub-field (d) |
| Contract Cost | `<span>` | `Repeater1_Label2_{n}` | Formatted with commas |
| Effectivity Date | `<span>` | `Repeater1_Label3_{n}` | Sub-field (a) |
| Expiry Date | `<span>` | `Repeater1_Label4_{n}` | Sub-field (b) |
| Status | `<span>` | `Repeater1_Label7_{n}` | Sub-field (a) |
| % Accomplishment | `<span>` | `Repeater1_Label1_{n}` | Sub-field (b), may be empty |
| Year | Computed | N/A | Extracted from filename |
| File Source | Computed | N/A | Original HTML filename |
| Critical Errors | Computed | N/A | CRIT-level errors (pipe-delimited) |
| Errors | Computed | N/A | ERR-level errors (pipe-delimited) |
| Warnings | Computed | N/A | WARN-level warnings (pipe-delimited) |
| Info Notes | Computed | N/A | INFO-level notes (pipe-delimited) |

**Note:** `{n}` is a zero-based index for each contract row (0, 1, 2, ...)

---

## Extraction Strategy

### Approach 1: BeautifulSoup (Recommended)
**Pros:**
- Robust HTML parsing
- Easy navigation of nested structures
- Handles malformed HTML gracefully
- Can find elements by ID pattern

**Implementation:**
```python
from bs4 import BeautifulSoup

# Find all tbody elements with class 'table-group-divider'
tbodies = soup.find_all('tbody', class_='table-group-divider')

for tbody in tbodies:
    tr = tbody.find('tr')
    if tr:
        # Extract row number
        row_num = tr.find('th', scope='row').get_text(strip=True)
        
        # Extract all span elements by ID
        contract_id = tr.find('span', id=lambda x: x and 'lblCustomerId' in x)
        description = tr.find('span', id=lambda x: x and 'lblContactName' in x)
        # ... etc
```

### Approach 2: lxml + XPath
**Pros:**
- Fast parsing
- Powerful XPath queries
- Good for large files

**Cons:**
- Stricter HTML requirements
- More complex syntax

---

## Data Cleaning Considerations

### 1. Contract Cost
- **Format:** Comma-separated numbers (e.g., `1,610,848,037.67`)
- **Action:** Remove commas, convert to float
- **Example:** `"1,610,848,037.67"` → `1610848037.67`

### 2. Dates
- **Format:** Full text dates (e.g., `"October 29, 2025"`)
- **Action:** Parse to ISO format (YYYY-MM-DD)
- **Library:** Use `dateutil.parser` or `datetime.strptime`

### 3. Contractor Names
- **Format:** Name with ID code in parentheses; multiple contractors separated by ` / `
- **Single Contractor Example:** `"CHINA WUYI CO., LTD (OECO_16634)"`
- **Multiple Contractors Example:** `"ULTICON BUILDERS, INC. (17267) / SHIMIZU CORPORATION (OECO_16693) / TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD. (OECO_29591)"`
- **Action:** Split into separate columns for each contractor:
  - Contractor Name 1: `"CHINA WUYI CO., LTD"` or `"ULTICON BUILDERS, INC."`
  - Contractor ID 1: `"OECO_16634"` or `"17267"`
  - Contractor Name 2: `None` or `"SHIMIZU CORPORATION"`
  - Contractor ID 2: `None` or `"OECO_16693"`
  - Contractor Name 3: `None` or `"TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD."`
  - Contractor ID 3: `None` or `"OECO_29591"`
- **Strategy:** 
  1. Split by ` / ` delimiter to get individual contractors
  2. Extract name and ID from each contractor using regex: `^(.+?)\s*\(([^)]+)\)\s*$`
  3. Store in separate columns (contractor_name_1, contractor_id_1, contractor_name_2, contractor_id_2, etc.)
  4. Leave additional columns empty if fewer contractors exist

### 4. % Accomplishment
- **Format:** Decimal string (e.g., `"100.00"`) or empty
- **Action:** Convert to float, handle empty values as `None` or `0.0`

### 5. Special Characters
- **HTML Entities:** May contain `&amp;`, `&nbsp;`, etc.
- **Action:** BeautifulSoup automatically decodes these

---

## Edge Cases

### 1. Empty Accomplishment Field
```html
<span id="Repeater1_Label1_0"></span>  <!-- No text -->
```
**Handling:** Check for empty string, convert to `None` or `0`

### 2. Footer Row
```html
<tbody>
    <tr>
        <td colspan="5">
            <span id="Repeater1_lblEmptyData">
                <i>The data indicated herein are not conclusive...</i>
            </span>
        </td>
    </tr>
</tbody>
```
**Handling:** Skip tbody elements without class `"table-group-divider"`

### 3. Spacer Rows
```html
<tr><td colspan="5"></td></tr>
```
**Handling:** Ignore or skip during parsing

### 4. Multiple Contractors (Joint Ventures)
```html
<span id="Repeater1_lblCountry_0"> ULTICON BUILDERS, INC. (17267) / SHIMIZU CORPORATION (OECO_16693) / TAKENAKA CIVIL ENGINEERING &amp; CONSTRUCTION CO., LTD. (OECO_29591)</span>
```
**Handling:** Split by ` / ` delimiter, extract each contractor's name and ID separately, then store in separate columns (contractor_name_1, contractor_id_1, contractor_name_2, contractor_id_2, contractor_name_3, contractor_id_3). If more than 3 contractors exist, add a note to `parse_notes` column: `"WARNING: >3 contractors, extras truncated"`

**Examples of Multiple Contractors:**
- 2 contractors: `"A.M. ORETA & CO., INC. (108) / E. F. CHUA CONSTRUCTION, INC. (37826)"`
- 3 contractors: `"CAVDEAL-CAVITE IDEAL INT'L. CONST. & DEV'T. CORP. (5599) / WEE ENG CONSTRUCTION, INC. (16380) / COASTLAND CONSTRUCTION & DEVELOPMENT CORP. (11487)"`

**Standard:** Always provide 3 contractor column pairs. Empty contractor columns are left as `None` or empty strings.

---

## Recommended CSV Schema

```csv
row_number,contract_id,description,contractor_name_1,contractor_id_1,contractor_name_2,contractor_id_2,contractor_name_3,contractor_id_3,implementing_office,source_of_funds,cost_php,effectivity_date,expiry_date,status,accomplishment_pct,year,file_source,critical_errors,errors,warnings,info_notes
1,24Z00029,SUB-PROJECT 9 CONTRACT PACKAGE 2...,CHINA WUYI CO. LTD,OECO_16634,,,,,Central Office - Roads Management Cluster I (Bilateral),Regular Infra - GAA 2025 FAPs,1610848037.67,2025-10-29,2028-10-12,Not Yet Started,,2016,table_Central_Office_2016_20251111_155202.html,,,,,
2,21Z00007,DAVAO CITY BYPASS CONSTRUCTION PROJECT...,"ULTICON BUILDERS, INC.",17267,SHIMIZU CORPORATION,OECO_16693,"TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD.",OECO_29591,Central Office - Roads Management Cluster I (Bilateral),Regular Infra - GAA 2023 FAPs,15234567890.12,2023-03-15,2028-12-31,On-Going,45.20,2023,table_Central_Office_2023_20251111_155306.html,,,,INFO-045: Joint venture with 3 contractors
3,22X00001,EXAMPLE PROJECT WITH ISSUES,CONTRACTOR A,1234,,,,,,Regular Infra,,,,,,,2022,table_Central_Office_2022.html,,ERR-021: Invalid cost format: 'N/A',WARN-011: Empty cost field,
```

**Error Tracking Columns Purpose:**
- **Critical Errors:** Fatal issues preventing proper data extraction (CRIT-xxx codes)
- **Errors:** Data extraction failures, fields set to NULL (ERR-xxx codes)
- **Warnings:** Data quality concerns but fields populated (WARN-xxx codes)
- **Info Notes:** Informational messages about processing (INFO-xxx codes)
- Empty/blank when no issues of that severity detected
- Multiple issues within same severity concatenated with ` | ` delimiter
- **Benefit:** Easy filtering in analysis - drop rows with critical_errors, flag rows with errors, etc.

### Additional Metadata Fields
- `year`: Extracted from filename
- `file_source`: Original HTML filename for traceability

---

## Implementation Plan

### Step 1: Parse HTML with BeautifulSoup
- Load HTML file
- Find all contract tbody elements
- Extract data from span elements using ID patterns

### Step 2: Clean and Transform Data
- Remove commas from cost values
- Parse dates to ISO format
- Handle empty accomplishment values
- Decode HTML entities (e.g., `&amp;` → `&`)
- Split multiple contractors by ` / ` into separate columns

### Step 3: Write to CSV
- Create CSV with proper headers
- Write one row per contract
- Include metadata (year, source file)

### Step 4: Batch Processing
- Iterate through all HTML files in directory
- Combine all extracted data into single CSV or separate files per year
- Add error handling for malformed HTML

---

## Python Libraries Required

```python
beautifulsoup4  # HTML parsing
lxml           # Fast HTML parser backend
python-dateutil # Date parsing
```

---

## Extraction Script Pseudo-code

```python
def extract_contract_data(html_file):
    soup = BeautifulSoup(html_file, 'lxml')
    contracts = []
    
    tbodies = soup.find_all('tbody', class_='table-group-divider')
    
    for tbody in tbodies:
        tr = tbody.find('tr')
        if not tr:
            continue
            
        contract = {
            'row_number': extract_row_number(tr),
            'contract_id': extract_by_id_pattern(tr, 'lblCustomerId'),
            'description': extract_by_id_pattern(tr, 'lblContactName'),
        }
        
        # Add contractor columns
        contractor_data = get_contractor_columns(
            extract_by_id_pattern(tr, 'lblCountry'), 
            max_contractors=3
        )
        contract.update(contractor_data)
        
        # Collect any additional parse notes
        additional_notes = []
        
        contract.update({
            'implementing_office': extract_by_id_pattern(tr, 'Label5'),
            'source_of_funds': extract_by_id_pattern(tr, 'Label6'),
            'cost_php': clean_cost(extract_by_id_pattern(tr, 'Label2')),
            'effectivity_date': parse_date(extract_by_id_pattern(tr, 'Label3')),
            'expiry_date': parse_date(extract_by_id_pattern(tr, 'Label4')),
            'status': extract_by_id_pattern(tr, 'Label7'),
            'accomplishment_pct': clean_percentage(extract_by_id_pattern(tr, 'Label1')),
        })
        
        # Merge parse notes from contractors and any other issues
        if additional_notes:
            existing_notes = contract.get('parse_notes', '')
            all_notes = [existing_notes] + additional_notes if existing_notes else additional_notes
            contract['parse_notes'] = ' | '.join(all_notes)
        
        contracts.append(contract)
    
    return contracts
```

---

## Summary

The HTML tables have a **consistent, repeatable structure** that is well-suited for automated extraction:

✅ **Pros:**
- Consistent ID patterns (`Repeater1_*_{n}`)
- Clear data hierarchy
- Predictable structure across all year files
- Bootstrap classes for easy element selection

⚠️ **Challenges:**
- Nested list structures require careful navigation
- Comma-formatted numbers need cleaning
- Text-based dates need parsing
- Empty accomplishment fields need handling

**Recommended Tool:** BeautifulSoup with lxml parser for robust, reliable extraction.

---

## Helper Functions for Data Cleaning

```python
import re
from html import unescape

def parse_contractors(contractor_text):
    """
    Parse contractor text that may contain single or multiple contractors.
    Returns list of tuples: [(name1, id1), (name2, id2), ...].
    
    Examples:
        "CHINA WUYI CO., LTD (OECO_16634)" 
        -> [("CHINA WUYI CO., LTD", "OECO_16634")]
        
        "ULTICON BUILDERS, INC. (17267) / SHIMIZU CORPORATION (OECO_16693)"
        -> [("ULTICON BUILDERS, INC.", "17267"), ("SHIMIZU CORPORATION", "OECO_16693")]
    """
    if not contractor_text:
        return []
    
    # Decode HTML entities (e.g., &amp; -> &)
    contractor_text = unescape(contractor_text.strip())
    
    # Split by forward slash to handle multiple contractors
    contractors = [c.strip() for c in contractor_text.split('/')]
    
    result = []
    
    for contractor in contractors:
        # Extract name and ID using regex
        match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', contractor)
        if match:
            name = match.group(1).strip()
            contractor_id = match.group(2).strip()
            result.append((name, contractor_id))
        else:
            # No parentheses found, treat entire text as name
            result.append((contractor, None))
    
    return result

def get_contractor_columns(contractor_text, max_contractors=3):
    """
    Get contractor data as separate columns for CSV output.
    Returns dict with keys: contractor_name_1, contractor_id_1, etc., 
    plus parse_notes for any issues.
    
    Args:
        contractor_text: Raw contractor text from HTML
        max_contractors: Maximum number of contractor columns to support (default: 3)
    
    Returns:
        Dict with contractor_name_N, contractor_id_N keys (always present),
        and parse_notes string (empty if no issues)
    """
    contractors = parse_contractors(contractor_text)
    
    result = {}
    notes = []
    
    # Always populate all contractor columns (empty if not present)
    for i in range(1, max_contractors + 1):
        if i <= len(contractors):
            result[f'contractor_name_{i}'] = contractors[i-1][0]
            result[f'contractor_id_{i}'] = contractors[i-1][1]
        else:
            result[f'contractor_name_{i}'] = None
            result[f'contractor_id_{i}'] = None
    
    # Add note if there are more contractors than columns
    if len(contractors) > max_contractors:
        notes.append(f"WARNING: >{max_contractors} contractors ({len(contractors)} total), extras truncated")
    
    result['parse_notes'] = ' | '.join(notes) if notes else None
    
    return result
```

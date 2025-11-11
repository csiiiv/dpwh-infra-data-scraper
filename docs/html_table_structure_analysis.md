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

### 3. Contractor Names (revised)
**Problem:** Some contractor names include forward slashes (`/`) as part of the legal/business name (for example, "A / B Builders") while the joint-venture separator in the HTML is actually a `") /"` sequence (a closing parenthesis, space, slash). A naive split on `/` breaks contractor names that legitimately contain `/`.

**Updated strategy (implemented in `scripts/html_to_csv_parser.py`):**
- Split on the separator pattern `") /"` (implemented with the regex `r"\)\s*/\s*"`) so that we only split between contractor entries and not within names.
- After splitting, re-add the removed closing `)` for all but the last piece (the split removes the `)`), so each contractor string ends with the original `)` to ease regex extraction.
- Extract name and ID with the regex `^(.+?)\s*\(([^)]+)\)\s*$`.
- Preserve slashes inside contractor names and *flag* names that contain stray slashes for manual review.
- If more contractors are present than available columns (we store up to 4 contractor columns), combine the 4th+ contractors into the last contractor column using `; ` as a separator and emit a `WARN-041` warning.

**Single Contractor Example:**
`"CHINA WUYI CO., LTD (OECO_16634)"`

**Multiple Contractors Example (preserves slashes inside names):**
`"ULTICON BUILDERS, INC. (17267) / SHIMIZU CORPORATION (OECO_16693) / TAKENAKA CIVIL ENGINEERING & CONSTRUCTION CO., LTD. (OECO_29591)"`

**Outcome:** Contractor names that legitimately include `/` are preserved; true JV separators `") /"` split entries correctly; missing IDs are detected and flagged.

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

### 5. Multiple Contractors (Joint Ventures)
```html
<span id="Repeater1_lblCountry_0"> ULTICON BUILDERS, INC. (17267) / SHIMIZU CORPORATION (OECO_16693) / TAKENAKA CIVIL ENGINEERING &amp; CONSTRUCTION CO., LTD. (OECO_29591)</span>
```

**Handling (revised):**
- Split using the `") /"` separator (regex `r"\)\s*/\s*"`) to avoid breaking names that contain `/`.
- For each split piece, restore the closing parenthesis where necessary and extract name and ID via `^(.+?)\s*\(([^)]+)\)\s*$`.
- Flag any contractor name that still contains `/` (a stray slash) with `WARN-043` for manual review.
- If more contractors than supported columns are present, combine 4th+ names and IDs into the final contractor column (semicolon-separated) and emit `WARN-041`.

**Example behavior:**
- Input: `"A / B CONSTRUCTION (123) / C INC (456)"` → this will *not* split the `A / B` part because the separator is `") /"` (closing `)` required). The parser will produce two entries: `("A / B CONSTRUCTION", "123")` and `("C INC", "456")`.

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
    Parse contractor text into a list of (name, id, has_stray_slash) tuples.

    This function splits on the true JV separator `") /"` (implemented as
    the regex `r"\)\s*/\s*"`), which prevents splitting on slashes that
    are part of contractor names. For all but the last split piece the
    closing parenthesis is restored before applying the name/ID regex.

    Returns:
        List[Tuple[name, id_or_None, has_stray_slash_bool]]
    """
    if not contractor_text:
        return []

    contractor_text = unescape(contractor_text.strip())

    # Split on ") /" pattern which separates JV partners (preserves slashes in names)
    contractors = re.split(r'\)\s*/\s*', contractor_text)

    result = []
    regex = r'^(.+?)\s*\(([^)]+)\)\s*$'

    for i, contractor in enumerate(contractors):
        # For all but the last part, the split removed the closing paren — add it back
        if i < len(contractors) - 1:
            contractor = contractor + ')'

        contractor = contractor.strip()
        match = re.match(regex, contractor)

        if match:
            name = match.group(1).strip()
            contractor_id = match.group(2).strip()
            has_slash = '/' in name
            result.append((name, contractor_id, has_slash))
        else:
            # No ID found — keep text as name and mark stray slash if present
            has_slash = '/' in contractor
            result.append((contractor, None, has_slash))

    return result


def get_contractor_columns(contractor_text: str, max_contractors: int = 4):
    """
    Convert parsed contractors into CSV columns and error/warning notes.

    - First (max_contractors - 1) contractors stored in separate columns.
    - 4th column (index max_contractors) holds the 4th contractor or a semicolon-separated
      list when more than max_contractors contractors exist.
    - Missing IDs and stray slashes are flagged for parse notes.

    Returns:
        (result_dict, notes_dict) where notes_dict contains 'critical_errors', 'errors', 'warnings', 'info_notes'
    """
    # Note: in the real implementation the ParseNotes and ParseError helpers
    # are used to collect and format parse warnings/errors. This helper
    # returns a (result, notes) tuple similar to the script's behavior.
    
    from html import unescape as _unescape  # local reference (doc-only)
    
    # Use the parsing function above
    contractors = parse_contractors(contractor_text)
    result = {}
    notes = []

    # Fill first (max_contractors-1) columns
    for i in range(1, max_contractors):
        if i <= len(contractors):
            name, cid, has_slash = contractors[i-1]
            result[f'contractor_name_{i}'] = name
            result[f'contractor_id_{i}'] = cid
            if not cid:
                notes.append(f"ERR-042: Contractor missing ID code: '{name[:30]}'")
            if has_slash:
                notes.append(f"WARN-043: Contractor name contains slash: '{name[:50]}'")
        else:
            result[f'contractor_name_{i}'] = None
            result[f'contractor_id_{i}'] = None

    # Combine 4th+ contractors into the final contractor column
    if len(contractors) >= max_contractors:
        names = []
        ids = []
        for i in range(max_contractors - 1, len(contractors)):
            name, cid, has_slash = contractors[i]
            names.append(name)
            ids.append(cid if cid else '')
            if not cid:
                notes.append(f"ERR-042: Contractor missing ID code: '{name[:30]}'")
            if has_slash:
                notes.append(f"WARN-043: Contractor name contains slash: '{name[:50]}'")

        result[f'contractor_name_{max_contractors}'] = '; '.join(names)
        result[f'contractor_id_{max_contractors}'] = '; '.join(ids)
        if len(contractors) > max_contractors:
            notes.append(f"WARN-041: {len(contractors)} contractors found, combined into column {max_contractors}")
    else:
        result[f'contractor_name_{max_contractors}'] = None
        result[f'contractor_id_{max_contractors}'] = None

    if len(contractors) > 1:
        notes.append(f"INFO-045: Joint venture with {len(contractors)} contractors")

    notes_dict = {
        'critical_errors': None,
        'errors': ' | '.join([n for n in notes if n.startswith('ERR')]) or None,
        'warnings': ' | '.join([n for n in notes if n.startswith('WARN')]) or None,
        'info_notes': ' | '.join([n for n in notes if n.startswith('INFO')]) or None,
    }

    return result, notes_dict
```

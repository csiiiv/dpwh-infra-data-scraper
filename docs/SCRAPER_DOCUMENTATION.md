# DPWH Infrastructure Projects Scraper - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Functions](#functions)
4. [Configuration](#configuration)
5. [Data Flow](#data-flow)
6. [File Structure](#file-structure)
7. [Technical Specifications](#technical-specifications)
8. [Error Handling](#error-handling)

---

## Overview

### Purpose
`scraper_playwright.py` is a web scraper designed to extract infrastructure project data from the DPWH (Department of Public Works and Highways) website. It automates the process of collecting project information across all Philippine regions and years.

### Key Features
- **Automated Multi-Region Scraping**: Covers all 18 Philippine regions
- **Multi-Year Coverage**: Extracts data from 2016-2025 (10 years)
- **Anti-Bot Evasion**: Implements human-like behavior patterns
- **Progressive Saving**: Files saved immediately after extraction
- **ASP.NET Postback Handling**: Properly waits for server-side processing
- **Imperva Detection**: Identifies and reports anti-bot blocking

### Target Website
- **URL**: http://apps2.dpwh.gov.ph/infra_projects/
- **Technology**: ASP.NET Web Forms with ViewState
- **Data Control**: Repeater control with dynamic IDs
- **Anti-Bot**: Imperva/Incapsula protection

---

## Architecture

### Technology Stack

#### Core Dependencies
```python
playwright.sync_api    # Browser automation
beautifulsoup4        # HTML parsing
```

#### Python Standard Library
```python
time                  # Delays and timing
json                  # JSON serialization
random                # Random delays
os                    # File system operations
datetime              # Timestamps
```

### Design Pattern
- **Synchronous Execution**: Sequential region and year processing
- **Immediate Persistence**: Files saved as soon as extracted
- **Graceful Degradation**: Individual failures don't stop execution
- **Visible Browser**: Non-headless mode for monitoring

---

## Functions

### 1. `random_delay(min_sec=1.5, max_sec=3.5)`

**Purpose**: Simulate human-like timing between actions

**Parameters**:
- `min_sec` (float): Minimum delay in seconds (default: 1.5)
- `max_sec` (float): Maximum delay in seconds (default: 3.5)

**Returns**: None

**Behavior**:
```python
# Generates random delay between min and max
delay = random.uniform(min_sec, max_sec)
# Prints actual delay for visibility
print(f"    [Delay: {delay:.1f}s]")
# Pauses execution
time.sleep(delay)
```

**Usage Context**:
- After dropdown selections
- Between year iterations
- Before extraction operations
- Between region transitions

---

### 2. `extract_table_html(page)`

**Purpose**: Extract complete HTML table element from page

**Parameters**:
- `page` (playwright.sync_api.Page): Active browser page object

**Returns**: 
- `str`: Complete table HTML
- `None`: If extraction fails or blocked

**Process Flow**:
```
1. Get full page HTML content
2. Check for Imperva/Incapsula blocking
   └─> Return None if detected
3. Parse HTML with BeautifulSoup
4. Find table element by class 'table-bordered'
5. Count project spans (Repeater1_lblCustomerId_*)
6. Return raw table HTML string
```

**Anti-Bot Detection**:
```python
if 'incapsula' in html_content.lower() or 'imperva' in html_content.lower():
    print("⚠️ BLOCKED: Imperva/Incapsula detected!")
    return None
```

**Table Identification**:
```python
# Primary: Find by class
table = soup.find('table', class_='table-bordered')

# Fallback: Find by alternate class
if not table:
    table = soup.find('table', class_='caption-top')
```

**Output Sample**:
```html
<table class="table table-bordered caption-top shadow-lg...">
  <thead>...</thead>
  <tbody class="table-group-divider">
    <tr>
      <td>
        <span id="Repeater1_lblCustomerId_0">24A00678</span>
        <span id="Repeater1_lblContactName_0">PROJECT NAME</span>
        ...
      </td>
    </tr>
  </tbody>
</table>
```

---

### 3. `scrape_year(page, region, year, is_first_year=False)`

**Purpose**: Extract data for one year within a region

**Parameters**:
- `page` (playwright.sync_api.Page): Active browser page
- `region` (str): Region name (e.g., "Region I")
- `year` (str): Year to scrape (e.g., "2025")
- `is_first_year` (bool): Skip year selection if True

**Returns**:
```python
{
    'region': str,           # Region name
    'year': str,             # Year scraped
    'html_file': str,        # Filename only
    'html_path': str,        # Full path to file
    'html_size': int,        # Size in bytes
    'extracted_at': str      # ISO timestamp
}
# Returns None on failure
```

**Workflow**:

```
┌─────────────────────────────┐
│ is_first_year?              │
├─────────────────────────────┤
│ YES: Use current page state │
│ NO:  Select year dropdown   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Wait for ASP.NET postback   │
│ - random_delay(2, 4)        │
│ - wait_for_load_state()     │
│ - random_delay(1, 2)        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Extract table HTML          │
│ - extract_table_html(page)  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Save to file immediately    │
│ - Create filename           │
│ - Write to output/ folder   │
│ - Return metadata dict      │
└─────────────────────────────┘
```

**File Naming Convention**:
```
table_{Region_Name}_{Year}_{Timestamp}.html

Examples:
- table_Region_I_2025_20251111_154630.html
- table_Central_Office_2024_20251111_154645.html
- table_National_Capital_Region_2023_20251111_154700.html
```

**ASP.NET Postback Handling**:
```python
# Select year from dropdown
page.select_option('#ddlYear', value=year)

# Wait for server response
random_delay(2, 4)                           # Initial delay
page.wait_for_load_state('networkidle')      # Wait for network
random_delay(1, 2)                           # Stabilization delay
```

---

### 4. `scrape_region(page, region, is_first_region=False)`

**Purpose**: Scrape all years (2016-2025) for one region

**Parameters**:
- `page` (playwright.sync_api.Page): Active browser page
- `region` (str): Region name
- `is_first_region` (bool): Requires manual selection if True

**Returns**:
```python
[
    {metadata_dict_1},  # Year 2016
    {metadata_dict_2},  # Year 2017
    ...
    {metadata_dict_10}  # Year 2025
]
# Returns list even if partially successful
```

**First Region Handling**:

```
┌─────────────────────────────────────┐
│ FIRST REGION (Manual Selection)     │
├─────────────────────────────────────┤
│ 1. Display warning message          │
│ 2. Wait for user to select region   │
│ 3. User presses Enter to continue   │
│ 4. Wait for page to stabilize       │
└─────────────────────────────────────┘

Why Manual?
- Imperva anti-bot blocks first automated click
- Manual interaction establishes "human" session
- Subsequent regions can be automated safely
```

**Subsequent Regions Workflow**:

```
┌────────────────────────┐
│ Locate region dropdown │
│ #ddlRegion             │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Scroll into view       │
│ random_delay(0.5, 1)   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Click dropdown         │
│ random_delay(0.5, 1)   │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Select region option   │
│ by label text          │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Wait for postback      │
│ - delay(3, 5)          │
│ - networkidle          │
│ - delay(2, 3)          │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│ Loop through years     │
│ (call scrape_year)     │
└────────────────────────┘
```

**Year Iteration Logic**:
```python
for year_idx, year in enumerate(YEARS):
    is_first_year = (year_idx == 0)  # First year uses current state
    result = scrape_year(page, region, year, is_first_year)
    
    if result:
        region_results.append(result)
    
    # Delay between years (except after last)
    if year_idx < len(YEARS) - 1:
        random_delay(1, 2)
```

**Performance**:
- **Per Region**: ~2-4 minutes
- **10 Years**: ~1-2 minutes of scraping + 1-2 minutes of waits
- **Total per Region**: 10 extractions + postback waits

---

### 5. `main()`

**Purpose**: Orchestrate complete scraping workflow

**Parameters**: None

**Returns**: None (exits on completion)

**Execution Phases**:

#### Phase 1: Initialization
```python
# Display banner
print("DPWH Scraper - Playwright Version (Browser Visible)")

# Wait for user confirmation
input("Press Enter to start...")

# Launch browser
browser = p.chromium.launch(
    headless=False,      # Visible window
    slow_mo=500,         # 500ms between actions
    args=[...]           # Anti-detection flags
)
```

#### Phase 2: Browser Configuration
```python
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    locale='en-US',
    timezone_id='Asia/Manila',
    permissions=['geolocation'],
    color_scheme='light'
)

# Remove webdriver property
context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

#### Phase 3: Page Loading
```python
page.goto(BASE_URL, wait_until='domcontentloaded')
random_delay(3, 5)
page.wait_for_load_state('networkidle')
```

#### Phase 4: Region Loop
```python
for idx, region in enumerate(REGIONS):
    is_first_region = (idx == 0)
    
    # Scrape all years for this region
    region_results = scrape_region(page, region, is_first_region)
    
    # Accumulate results
    all_projects.extend(region_results)
    
    # Delay between regions
    if idx < len(REGIONS) - 1:
        random_delay(3, 6)
```

#### Phase 5: Summary Generation
```python
# Group results by region
by_region = defaultdict(list)
for item in all_projects:
    by_region[item['region']].append(item)

# Display statistics
for region_name, items in by_region.items():
    total_size = sum(item['html_size'] for item in items) / 1024
    years = [item['year'] for item in items]
    print(f"  • {region_name}: {len(items)} years - {total_size:.1f} KB")
```

#### Phase 6: JSON Index Creation
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
index_file = f'scrape_index_{timestamp}.json'
index_path = os.path.join(OUTPUT_DIR, index_file)

with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(all_projects, f, indent=2, ensure_ascii=False)
```

#### Phase 7: Cleanup
```python
# Wait for user before closing
input("Press Enter to close browser...")
browser.close()
```

---

## Configuration

### Constants

#### `BASE_URL`
```python
BASE_URL = "http://apps2.dpwh.gov.ph/infra_projects/"
```
- Target website URL
- ASP.NET Web Forms application
- Requires JavaScript and cookies

#### `OUTPUT_DIR`
```python
OUTPUT_DIR = "output"
```
- Directory for all output files
- Created automatically if missing
- Contains: HTML tables + JSON index

#### `REGIONS`
```python
REGIONS = [
    "Central Office",                      # Index 0 - Manual selection
    "Cordillera Administrative Region",    # Index 1 - Automated
    "National Capital Region",
    "Negros Island Region",
    "Region I", "Region II", "Region III",
    "Region IV-A", "Region IV-B",
    "Region V", "Region VI", "Region VII",
    "Region VIII", "Region IX", "Region X",
    "Region XI", "Region XII", "Region XIII"
]
```
- **Total**: 18 regions
- **Coverage**: All Philippine regions under DPWH
- **First Element**: Requires manual selection (Imperva blocking)

#### `YEARS`
```python
YEARS = [
    "2016", "2017", "2018", "2019", "2020",
    "2021", "2022", "2023", "2024", "2025"
]
```
- **Total**: 10 years
- **Range**: 2016-2025
- **Format**: String (matches dropdown values)
- **Selection**: Matches `<option value="2025">2025</option>`

---

## Data Flow

### Complete Scraping Cycle

```
START
  │
  ├─> Initialize Browser (Chromium, visible)
  │
  ├─> Load DPWH Website
  │   └─> Wait for networkidle
  │
  ├─> FOR EACH REGION (18 total)
  │   │
  │   ├─> [Region #1?]
  │   │   YES: Manual Selection Required
  │   │   │    ├─> Display instructions
  │   │   │    ├─> Wait for user input
  │   │   │    └─> Continue when Enter pressed
  │   │   NO:  Automated Selection
  │   │        ├─> Click dropdown
  │   │        ├─> Select region
  │   │        └─> Wait for postback
  │   │
  │   ├─> FOR EACH YEAR (10 total: 2016-2025)
  │   │   │
  │   │   ├─> [Year #1?]
  │   │   │   YES: Use current page (no selection)
  │   │   │   NO:  Select year from dropdown
  │   │   │        └─> Wait for postback
  │   │   │
  │   │   ├─> Extract Table HTML
  │   │   │   ├─> Get page.content()
  │   │   │   ├─> Check for Imperva blocking
  │   │   │   ├─> Parse with BeautifulSoup
  │   │   │   └─> Find <table> element
  │   │   │
  │   │   ├─> Save to File IMMEDIATELY
  │   │   │   ├─> Generate filename
  │   │   │   ├─> Write to output/ folder
  │   │   │   └─> Print confirmation
  │   │   │
  │   │   └─> Append to results list
  │   │
  │   └─> Delay before next region (3-6s)
  │
  ├─> Generate Summary Statistics
  │   ├─> Group by region
  │   ├─> Calculate sizes
  │   └─> Display to console
  │
  ├─> Create JSON Index File
  │   ├─> Timestamp filename
  │   ├─> Save to output/ folder
  │   └─> Include all metadata
  │
  └─> Close Browser & Exit
```

### File Creation Timeline

```
Time    Action                           Files Created
───────────────────────────────────────────────────────────
00:00   Start scraper
00:05   Manual region selection
00:10   Extract Year 2016                → table_Central_Office_2016_*.html
00:15   Extract Year 2017                → table_Central_Office_2017_*.html
00:20   Extract Year 2018                → table_Central_Office_2018_*.html
...     (Continue through years)
02:00   Extract Year 2025                → table_Central_Office_2025_*.html
02:05   Move to Region 2
02:10   Extract Year 2016                → table_CAR_2016_*.html
...     (Continue through all regions)
60:00   Generate summary
60:05   Create index                     → scrape_index_*.json
60:10   Close browser
```

---

## File Structure

### Output Directory Layout

```
output/
├── table_Central_Office_2016_20251111_154630.html
├── table_Central_Office_2017_20251111_154645.html
├── table_Central_Office_2018_20251111_154700.html
│   ... (10 files per region)
├── table_Central_Office_2025_20251111_155030.html
│
├── table_Cordillera_Administrative_Region_2016_20251111_155045.html
│   ... (10 files)
├── table_Cordillera_Administrative_Region_2025_20251111_155400.html
│
│   ... (Continue for all 18 regions)
│
├── table_Region_XIII_2016_20251111_163000.html
│   ... (10 files)
├── table_Region_XIII_2025_20251111_163330.html
│
└── scrape_index_20251111_163400.json

Total: 181 files (180 HTML + 1 JSON)
```

### HTML File Format

```html
<table class="table table-bordered caption-top shadow-lg p-3 mb-5 bg-body rounded">
    <caption>
        <div class="row">
            <div class="col-md-12">
                <p style="color:white">
                    <i>The data indicated herein are not conclusive...</i>
                </p>
            </div>
        </div>
    </caption>
    
    <thead class="table" style="background-color: black; color: white">
        <tr class="align-text-top">
            <th scope="col"></th>
            <th>CONTRACT ID...</th>
            <th>Contract Cost (Php)</th>
            <th>Contract Dates</th>
            <th>Status</th>
        </tr>
    </thead>
    
    <tbody class="table-group-divider">
        <tr>
            <th scope="row">1.</th>
            <td>
                <b><span id="Repeater1_lblCustomerId_0">24A00678</span></b>
                <ul class="list-group list-group-flush">
                    <li><b>a)</b> <span id="Repeater1_lblContactName_0">PROJECT NAME</span></li>
                    <li><b>b)</b> <span id="Repeater1_lblCountry_0">CONTRACTOR</span></li>
                    <li><b>c)</b> <span id="Repeater1_Label5_0">OFFICE</span></li>
                    <li><b>d)</b> <span id="Repeater1_Label6_0">FUND SOURCE</span></li>
                </ul>
            </td>
            <td>
                <ul><li><span id="Repeater1_Label2_0">1,234,567.89</span></li></ul>
            </td>
            <td>
                <ul>
                    <li><b>a)</b> <span id="Repeater1_Label3_0">January 1, 2025</span></li>
                    <li><b>b)</b> <span id="Repeater1_Label4_0">December 31, 2027</span></li>
                </ul>
            </td>
            <td>
                <ul>
                    <li><b>a)</b> <span id="Repeater1_Label7_0">On-going</span></li>
                    <li><b>b)</b> <span id="Repeater1_Label1_0">45.50%</span></li>
                </ul>
            </td>
        </tr>
        <tr><td colspan="5"></td></tr>
    </tbody>
    
    <!-- More rows... -->
</table>
```

### JSON Index Format

```json
[
  {
    "region": "Central Office",
    "year": "2016",
    "html_file": "table_Central_Office_2016_20251111_154630.html",
    "html_path": "output/table_Central_Office_2016_20251111_154630.html",
    "html_size": 1234567,
    "extracted_at": "2025-11-11T15:46:30.123456"
  },
  {
    "region": "Central Office",
    "year": "2017",
    "html_file": "table_Central_Office_2017_20251111_154645.html",
    "html_path": "output/table_Central_Office_2017_20251111_154645.html",
    "html_size": 987654,
    "extracted_at": "2025-11-11T15:46:45.789012"
  }
]
```

**Index Fields**:
- `region`: Region name (matches REGIONS constant)
- `year`: Year scraped (matches YEARS constant)
- `html_file`: Filename only (for portability)
- `html_path`: Full path relative to script location
- `html_size`: File size in bytes
- `extracted_at`: ISO 8601 timestamp with microseconds

---

## Technical Specifications

### Browser Configuration

```python
# Launch Parameters
headless=False              # Show browser window
slow_mo=500                 # 500ms delay between actions

# Anti-Detection Arguments
'--disable-blink-features=AutomationControlled'  # Hide automation
'--disable-dev-shm-usage'                        # Docker compatibility
'--no-sandbox'                                   # Permission handling
```

### Context Settings

```python
viewport = {'width': 1920, 'height': 1080}  # Standard desktop resolution
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
locale = 'en-US'                            # English interface
timezone_id = 'Asia/Manila'                 # Philippine timezone
permissions = ['geolocation']               # Location access
color_scheme = 'light'                      # Light mode preference
```

### Timing Parameters

| Action | Wait Type | Duration | Purpose |
|--------|-----------|----------|---------|
| Initial page load | `networkidle` | 3-5s + wait | Ensure complete load |
| Region selection | `networkidle` | 3-5s + 15s timeout + 2-3s | ASP.NET postback |
| Year selection | `networkidle` | 2-4s + 15s timeout + 1-2s | ASP.NET postback |
| Between years | `random_delay` | 1-2s | Human-like pacing |
| Between regions | `random_delay` | 3-6s | Rate limiting |
| Before extraction | `random_delay` | 1-2s | Ensure stability |

### Performance Metrics

#### Time Estimates
```
Per Year Extraction:    ~5-10 seconds
Per Region (10 years):  ~2-4 minutes
All Regions (18):       ~40-80 minutes
```

#### File Size Estimates
```
Per HTML File:          50 KB - 7 MB
Average:                1-2 MB
All HTML Files:         180-1000 MB
JSON Index:             10-50 KB
```

#### Network Statistics
```
Requests per Region:    11 requests (1 region + 10 years)
Total Requests:         198 requests (18 regions × 11)
Data Downloaded:        ~200-1000 MB total
```

---

## Error Handling

### Exception Hierarchy

```
┌─────────────────────────────┐
│ main() try/except           │
├─────────────────────────────┤
│ ├─> KeyboardInterrupt       │ User presses Ctrl+C
│ │   └─> Graceful shutdown   │
│ │                            │
│ ├─> Exception (general)     │ Any other error
│ │   └─> Print traceback     │
│ │                            │
│ └─> finally: browser.close()│ Always cleanup
└─────────────────────────────┘
         │
         ├─> scrape_region() try/except
         │   ├─> Exception
         │   │   └─> Return partial results
         │   └─> Continue to next region
         │
         └─> scrape_year() try/except
             ├─> Exception
             │   └─> Return None
             └─> Continue to next year
```

### Error Types and Responses

#### 1. Imperva/Incapsula Blocking
```python
# Detection
if 'incapsula' in html_content.lower() or 'imperva' in html_content.lower():
    print("⚠️ BLOCKED: Imperva/Incapsula detected!")
    return None

# Response
- Returns None from extract_table_html()
- Year marked as failed
- Continues to next year
- No file created for this year
```

#### 2. Network Timeout
```python
# Timeout configuration
page.wait_for_load_state('networkidle', timeout=15000)  # 15 seconds

# If timeout exceeded
- Exception raised
- Caught by scrape_year() or scrape_region()
- Error logged to console
- Returns None/empty list
- Continues execution
```

#### 3. Element Not Found
```python
# Dropdown not found
dropdown = page.locator('#ddlRegion')
# If element missing, Playwright raises TimeoutError

# Response
- Exception caught
- Error printed with traceback
- Function returns None/empty list
- Execution continues
```

#### 4. File Write Error
```python
# Disk full or permission denied
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(table_html)

# Response
- Exception raised (IOError, OSError)
- Caught by scrape_year()
- Error printed
- Metadata not added to results
- Continues to next year
```

#### 5. Keyboard Interrupt (Ctrl+C)
```python
except KeyboardInterrupt:
    print("\n\nStopped by user")
finally:
    browser.close()  # Always executed

# Response
- Immediate stop
- No summary generated
- Files already saved remain
- Browser closes gracefully
- Script exits
```

### Error Messages

```bash
# Success Indicators
✓ Initial page loaded
✓ Postback complete
✅ Table HTML extracted successfully
💾 Saved: output/table_Region_I_2025_*.html

# Warning Indicators
⚠️ BLOCKED: Imperva/Incapsula detected!
⚠️ No table HTML extracted
⚠️ Failed: 2025
⚠️ No data for region: Region X

# Error Indicators
✗ No table found
✗ Error extracting table HTML: [exception details]
✗ Error scraping year 2025: [exception details]
✗ Error: [exception details]

# Information Indicators
ℹ️ First year - using current page state
ℹ️ Table contains 45 project(s)
📄 Getting full page HTML...
📅 Year: 2025
```

### Graceful Degradation

#### Scenario 1: Single Year Fails
```
Region I - 2016: ✓ Success
Region I - 2017: ✗ Failed (timeout)
Region I - 2018: ✓ Success
...
Region I - 2025: ✓ Success

Result: 9 files created, 1 missing
Execution: Continues to next region
```

#### Scenario 2: Entire Region Fails
```
Region I: ✓ Success (10 years)
Region II: ✗ Failed (all years)
Region III: ✓ Success (10 years)

Result: 20 files created, 10 missing
Execution: Continues to next region
```

#### Scenario 3: User Interruption
```
Region I: ✓ Completed (10 files)
Region II: ✓ Completed (10 files)
Region III: Partial (3 files)
[Ctrl+C pressed]

Result: 23 files saved
         No JSON index
         Clean browser shutdown
```

---

## Logging and Monitoring

### Console Output Structure

```
[Section Header]
======================================================================
DPWH Scraper - Playwright Version (Browser Visible)
======================================================================

[Progress Indicators]
📄 Loading initial page...
    [Delay: 3.2s]
✓ Initial page loaded

[Region Level]
======================================================================
🌏 Region: Central Office (FIRST - Manual selection)
======================================================================

[Year Level]
  📅 Year: 2016
  ──────────────────────────────────────────────────────────
    ℹ️ First year - using current page state
    2️⃣ Extracting table HTML...
    [Delay: 1.8s]
    📄 Getting full page HTML...
    ✓ Table HTML extracted: 123456 characters
    💾 Saved: output/table_Central_Office_2016_*.html

[Summary]
======================================================================
SUMMARY
======================================================================
Total files scraped: 180
Regions collected: 18
  • Central Office: 10 years (2016-2025) - 12.3 MB total
  • Region I: 10 years (2016-2025) - 8.7 MB total
```

### Emoji Legend

| Emoji | Meaning | Usage |
|-------|---------|-------|
| 📄 | Document/Page | Page loading, HTML operations |
| 🌏 | Globe | Region indicator |
| 📅 | Calendar | Year indicator |
| ✓ | Checkmark | Success confirmation |
| ✅ | White Checkmark | Major success |
| ✗ | Cross | Error or failure |
| ⚠️ | Warning | Blocking or issues |
| ℹ️ | Information | Informational messages |
| 💾 | Floppy Disk | File saved |
| 👆 | Pointing Up | User action (click) |
| ⏳ | Hourglass | Waiting for process |
| 💤 | Sleeping | Delay/waiting |
| 📊 | Chart | Statistics/progress |
| 📁 | Folder | Output directory |

---

## Best Practices

### When to Use Manual Intervention
1. **First Region**: Always manual (Imperva blocking)
2. **After Blocking**: If Imperva detected, may need manual refresh
3. **Debugging**: Use visible browser to observe behavior

### Monitoring During Execution
1. **Watch Browser**: Ensure page loads correctly
2. **Check Console**: Look for error indicators (✗, ⚠️)
3. **Verify Files**: Check output/ folder for new files
4. **Monitor Size**: Ensure files are reasonable size (not 0 bytes)

### Optimization Guidelines
1. **Don't reduce delays too much**: May trigger blocking
2. **Don't run during peak hours**: Server may be slower
3. **Keep browser visible**: Easier to debug issues
4. **Check disk space**: Need ~1 GB free
5. **Stable network**: Avoid WiFi interruptions

### Troubleshooting Checklist
- [ ] Playwright installed: `playwright install chromium`
- [ ] Dependencies installed: `pip install beautifulsoup4 playwright`
- [ ] Network accessible: Can browse to DPWH site manually
- [ ] Disk space available: At least 1 GB
- [ ] No other Chromium instances: Close other browsers
- [ ] Output folder writable: Check permissions
- [ ] First region manual: User ready to interact

---

## Maintenance Notes

### Potential Breaking Changes
1. **Website redesign**: HTML structure may change
2. **Dropdown IDs**: `#ddlRegion`, `#ddlYear` may be renamed
3. **Table classes**: `table-bordered` may change
4. **Repeater IDs**: Pattern `Repeater1_*` may change
5. **Anti-bot updates**: Imperva may detect new patterns

### Update Checklist
- [ ] Verify BASE_URL still correct
- [ ] Check REGIONS list matches website dropdowns
- [ ] Check YEARS list matches website dropdowns
- [ ] Test `extract_table_html()` still finds table
- [ ] Verify timing delays still adequate
- [ ] Check file naming convention still works

---

## Performance Optimization

### Current Configuration (Safe)
```python
slow_mo = 500           # Very human-like
random_delay(3, 5)      # Conservative
timeout = 15000         # 15 seconds
```

### Faster Configuration (Risky)
```python
slow_mo = 100           # Minimal delay
random_delay(1, 2)      # Faster transitions
timeout = 10000         # 10 seconds
```

### Speed vs. Detection Trade-off
```
Speed ←──────────────────────────→ Stealth
  ↑                                    ↑
  │                                    │
More likely to be blocked       Less likely to be blocked
Faster completion               Slower completion
Lower delays                    Higher delays
Shorter timeouts                Longer timeouts
```

**Recommendation**: Keep current conservative settings unless necessary.

---

## Dependencies Version Compatibility

### Tested Versions
```
Python: 3.7+
Playwright: 1.40+
BeautifulSoup4: 4.12+
Chromium: 120+
```

### Installation Commands
```bash
# Install Python packages
pip install playwright==1.40.0 beautifulsoup4==4.12.0

# Install browser
playwright install chromium

# Verify installation
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

---

## License and Disclaimer

**Data Source**: Department of Public Works and Highways (DPWH)  
**Website Disclaimer**: "The data indicated herein are not conclusive but subject to verification from the Implementing Office"

**Scraper Usage**:
- Educational and research purposes
- Respect website terms of service
- Do not overload servers
- Verify data with official sources

---

## Support and Contact

**Documentation**: See README_SCRAPER.md for user guide  
**Code Location**: scraper_playwright.py  
**Output Location**: output/ folder  
**Issues**: Check console output for error messages

---

**Last Updated**: November 11, 2025  
**Version**: 1.0  
**Author**: GitHub Copilot

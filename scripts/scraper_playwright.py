#!/usr/bin/env python3
"""
DPWH Infrastructure Projects Web Scraper
==========================================

A Playwright-based web scraper for extracting infrastructure project data from the 
Department of Public Works and Highways (DPWH) website.

Website: http://apps2.dpwh.gov.ph/infra_projects/

Features:
---------
- Automated scraping of all 18 Philippine regions
- Multi-year data extraction (2016-2025)
- Human-like behavior to avoid anti-bot detection
- Immediate file saving after each extraction
- ASP.NET postback handling
- Imperva/Incapsula detection and avoidance

Output:
-------
- HTML files: table_{Region}_{Year}_{Timestamp}.html
- JSON index: scrape_index_{Timestamp}.json

Total Expected Files: 180 HTML files (18 regions × 10 years) + 1 JSON index

Dependencies:
-------------
- playwright (with chromium browser installed)
- beautifulsoup4
- Python 3.7+

Installation:
-------------
pip install playwright beautifulsoup4
playwright install chromium

Usage:
------
python3 scraper_playwright.py

Notes:
------
1. First region requires MANUAL selection to avoid Imperva blocking
2. Browser runs in visible mode (headless=False) for monitoring
3. Each table is saved immediately after extraction
4. ASP.NET postbacks are handled with appropriate wait times
5. Random delays simulate human behavior

Author: GitHub Copilot
Date: November 2025
"""

from playwright.sync_api import sync_playwright
import time
import json
import random
import os
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "http://apps2.dpwh.gov.ph/infra_projects/"
OUTPUT_DIR = "output"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def random_delay(min_sec=1.5, max_sec=3.5):
    """
    Introduce a random delay to simulate human behavior.
    
    This function helps avoid detection by anti-bot systems by introducing
    variable timing between actions, similar to how a human would interact
    with a website.
    
    Args:
        min_sec (float): Minimum delay in seconds (default: 1.5)
        max_sec (float): Maximum delay in seconds (default: 3.5)
    
    Returns:
        None
    
    Side Effects:
        - Prints the actual delay duration
        - Pauses execution for the random duration
    """
    delay = random.uniform(min_sec, max_sec)
    print(f"    [Delay: {delay:.1f}s]")
    time.sleep(delay)

# All Philippine regions covered by DPWH
REGIONS = [
    "Central Office",                      # National projects coordination
    "Cordillera Administrative Region",    # CAR - Baguio and mountain provinces
    "National Capital Region",             # NCR - Metro Manila
    "Negros Island Region",                # NIR - Negros Occidental & Oriental
    "Region I",                            # Ilocos Region
    "Region II",                           # Cagayan Valley
    "Region III",                          # Central Luzon
    "Region IV-A",                         # CALABARZON
    "Region IV-B",                         # MIMAROPA
    "Region V",                            # Bicol Region
    "Region VI",                           # Western Visayas
    "Region VII",                          # Central Visayas
    "Region VIII",                         # Eastern Visayas
    "Region IX",                           # Zamboanga Peninsula
    "Region X",                            # Northern Mindanao
    "Region XI",                           # Davao Region
    "Region XII",                          # SOCCSKSARGEN
    "Region XIII",                         # Caraga
]

# Infrastructure years available in the database
YEARS = [
    "2016", "2017", "2018", "2019", "2020",
    "2021", "2022", "2023", "2024", "2025"
]

def extract_table_html(page):
    """
    Extract the complete HTML table element from the current page.
    
    This function retrieves the entire page HTML, parses it with BeautifulSoup,
    and extracts the main data table without parsing individual rows. The raw
    HTML is returned for later processing by a separate parser.
    
    Args:
        page (playwright.sync_api.Page): Active Playwright page object
    
    Returns:
        str: Complete HTML table as string, or None if extraction fails
    
    Process:
        1. Fetch full page HTML content
        2. Check for anti-bot blocking (Imperva/Incapsula)
        3. Parse with BeautifulSoup
        4. Find table by class 'table-bordered'
        5. Count projects (Repeater1_lblCustomerId_* spans)
        6. Return raw table HTML
    
    Table Structure:
        - ASP.NET Repeater control with IDs like:
          * Repeater1_lblCustomerId_{n} - Project ID
          * Repeater1_lblContactName_{n} - Project name
          * Repeater1_lblCountry_{n} - Contractor
          * Repeater1_Label2_{n} - Contract amount
          * Repeater1_Label3_{n} - Start date
          * Repeater1_Label4_{n} - End date
          * Repeater1_Label5_{n} - Implementing office
          * Repeater1_Label6_{n} - Fund source
          * Repeater1_Label7_{n} - Status
          * Repeater1_Label1_{n} - Accomplishment %
    
    Anti-Bot Detection:
        - Checks for 'incapsula' or 'imperva' strings in HTML
        - Returns None if blocking detected
    """
    try:
        # Get the entire page HTML
        print("    📄 Getting full page HTML...")
        html_content = page.content()
        print(f"    📄 HTML length: {len(html_content)} characters")
        
        # Check for Imperva/Incapsula blocking first
        if 'incapsula' in html_content.lower() or 'imperva' in html_content.lower():
            print("    ⚠️  BLOCKED: Imperva/Incapsula detected!")
            return None
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the table element (it has multiple classes, so just look for table with "table-bordered")
        table = soup.find('table', class_='table-bordered')
        
        if not table:
            print("    ✗ No table found")
            # Try alternative: find any table with caption-top
            table = soup.find('table', class_='caption-top')
            if not table:
                print("    ✗ No table with caption-top found either")
                return None
        
        # Convert table to string
        table_html = str(table)
        print(f"    ✓ Table HTML extracted: {len(table_html)} characters")
        
        # Quick check for projects
        project_spans = table.find_all('span', id=lambda x: x and x.startswith('Repeater1_lblCustomerId_'))
        print(f"    ℹ️  Table contains {len(project_spans)} project(s)")
        
        return table_html
    
    except Exception as e:
        print(f"    ✗ Error extracting table HTML: {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_year(page, region, year, is_first_year=False):
    """
    Scrape infrastructure project data for a specific year within a region.
    
    This function handles the year selection dropdown, waits for ASP.NET postback,
    extracts the table HTML, and saves it immediately to disk.
    
    Args:
        page (playwright.sync_api.Page): Active Playwright page object
        region (str): Name of the Philippine region being scraped
        year (str): Year to scrape (e.g., "2025")
        is_first_year (bool): If True, skip year selection (use current state)
    
    Returns:
        dict: Metadata about the scraped file with keys:
            - region (str): Region name
            - year (str): Year scraped
            - html_file (str): Filename of saved HTML
            - html_size (int): Size of HTML content in bytes
            - extracted_at (str): ISO timestamp of extraction
        Returns None if extraction fails.
    
    File Naming:
        table_{Region_Name}_{Year}_{Timestamp}.html
        Example: table_Region_I_2025_20251111_143022.html
    
    ASP.NET Behavior:
        - Selecting a year triggers a postback (page reload)
        - Must wait for 'networkidle' state before extraction
        - First year uses current page state (already loaded)
    
    Process Flow:
        1. Select year from dropdown (if not first)
        2. Wait for ASP.NET postback (2-4s + networkidle)
        3. Extract table HTML
        4. Save immediately to file
        5. Return metadata
    """
    print(f"\n  📅 Year: {year}")
    print(f"  {'─'*60}")
    
    try:
        if not is_first_year:
            # Select year
            print(f"    1️⃣  Selecting year: {year}")
            year_dropdown = page.locator('#ddlYear')
            year_dropdown.scroll_into_view_if_needed()
            random_delay(0.3, 0.7)
            
            # Select year option
            page.select_option('#ddlYear', value=year)
            print("       ⏳ Waiting for ASP.NET postback...")
            
            # Wait for page to reload after year selection
            random_delay(2, 4)
            page.wait_for_load_state('networkidle', timeout=15000)
            print("       ✓ Postback complete")
            random_delay(1, 2)
        else:
            print(f"    ℹ️  First year - using current page state")
        
        # Extract table HTML
        print("    2️⃣  Extracting table HTML...")
        random_delay(1, 2)
        table_html = extract_table_html(page)
        
        if table_html:
            print(f"    ✅ Table HTML extracted successfully")
            
            # Save immediately
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            region_name = region.replace(' ', '-').replace('_', '-')
            html_file = f'table_{region_name}_{year}_{timestamp}.html'
            html_path = os.path.join(OUTPUT_DIR, html_file)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(table_html)
            
            print(f"    💾 Saved: {html_path}")
            
            return {
                'region': region,
                'year': year,
                'html_file': html_file,
                'html_path': html_path,
                'html_size': len(table_html),
                'extracted_at': datetime.now().isoformat()
            }
        else:
            print(f"    ⚠️  No table HTML extracted")
            return None
            
    except Exception as e:
        print(f"    ✗ Error scraping year {year}: {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_region(page, region, is_first_region=False):
    """
    Scrape all years (2016-2025) of infrastructure project data for one region.
    
    This is the main region-level scraping function that coordinates the extraction
    of data across all available years. It handles both manual (first region) and
    automated (subsequent regions) region selection.
    
    Args:
        page (playwright.sync_api.Page): Active Playwright page object
        region (str): Name of the Philippine region to scrape
        is_first_region (bool): If True, prompts user for manual selection
    
    Returns:
        list: List of metadata dictionaries (one per year successfully scraped)
              Each dict contains: region, year, html_file, html_size, extracted_at
              Returns empty list if region scraping fails completely.
    
    First Region Handling:
        - Imperva anti-bot blocks automated first dropdown interaction
        - Just refresh page by entering "https://apps2.dpwh.gov.ph/infra_projects/" in browser
        - After page loads again, User must MANUALLY select first region and year in visible browser 
        - If data loads properly, Script waits for user confirmation via Enter key
        - Press Enter to confirm and start extraction
        - Subsequent regions are fully automated
    
    Subsequent Regions:
        - Automated dropdown selection
        - Simulated human-like mouse movements and delays
        - ASP.NET postback handling (3-5s + networkidle wait)
    
    Year Iteration:
        - Loops through all years in YEARS list (2016-2025)
        - First year uses current page state (after region selection)
        - Subsequent years trigger dropdown selection + postback
        - 1-2 second delays between year transitions
    
    Output Files Per Region:
        - 10 HTML files (one per year)
        - Example: table_Region_I_2016_20251111_143022.html
                  table_Region_I_2017_20251111_143045.html
                  ... (through 2025)
    
    Error Handling:
        - Individual year failures don't stop region processing
        - Returns partial results if some years succeed
        - Prints detailed error messages for debugging
    
    Performance:
        - ~2-4 minutes per region (18 selections + 180 extractions)
        - Total runtime: ~40-80 minutes for all regions
    """
    print(f"\n{'='*70}")
    print(f"🌏 Region: {region} {'(FIRST - Manual selection)' if is_first_region else ''}")
    print('='*70)
    
    region_results = []
    
    try:
        if is_first_region:
            # First region: user manually selects
            print("  ⚠️  FIRST REGION: Please manually select a region in browser")
            print("  ⚠️  This avoids Imperva blocking the first automated click")
            input("  👉 Press Enter AFTER you've manually selected region...")
            
            # Wait for page to load
            random_delay(2, 4)
            page.wait_for_load_state('networkidle', timeout=30000)
            
        else:
            # Subsequent regions: automate
            print(f"  1️⃣  Selecting region: {region}")
            
            # Select region
            dropdown = page.locator('#ddlRegion')
            dropdown.scroll_into_view_if_needed()
            random_delay(0.5, 1)
            
            print("     👆 Clicking dropdown...")
            dropdown.click()
            random_delay(0.5, 1)
            
            print(f"     ✓ Selecting: {region}")
            page.select_option('#ddlRegion', label=region)
            print("     ⏳ Waiting for ASP.NET postback...")
            
            # Wait for region change postback
            random_delay(3, 5)
            page.wait_for_load_state('networkidle', timeout=15000)
            print("     ✓ Postback complete")
            random_delay(2, 3)
        
        # Now scrape all years for this region
        print(f"\n  🗓️  Scraping all years for {region}...")
        
        for year_idx, year in enumerate(YEARS):
            is_first_year = (year_idx == 0)
            result = scrape_year(page, region, year, is_first_year=is_first_year)
            
            if result:
                region_results.append(result)
                print(f"    ✓ Completed: {year}")
            else:
                print(f"    ⚠️  Failed: {year}")
            
            # Small delay between years
            if year_idx < len(YEARS) - 1:
                random_delay(1, 2)
        
        print(f"\n  📊 Completed {len(region_results)}/{len(YEARS)} years for {region}")
        return region_results
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return region_results

def main():
    """
    Main execution function for DPWH infrastructure projects scraper.
    
    This orchestrates the complete scraping workflow:
    1. Browser initialization with anti-detection settings
    2. Page navigation and initial load
    3. Sequential scraping of all 18 regions
    4. Each region scraped for all 10 years (2016-2025)
    5. Summary statistics and JSON index generation
    
    Browser Configuration:
        - Chromium engine (most reliable for ASP.NET sites)
        - Visible mode (headless=False) for monitoring
        - Slow motion: 500ms delays for human-like behavior
        - Anti-detection: Disabled automation flags
        - Realistic viewport: 1920x1080
        - User agent: Windows Chrome 120
        - Timezone: Asia/Manila (Philippines)
    
    Execution Flow:
        1. Launch browser with anti-bot evasion
        2. Load initial DPWH website
        3. For each region (18 total):
           a. Select region (manual first time, automated after)
           b. For each year (10 total):
              - Select year from dropdown
              - Wait for ASP.NET postback
              - Extract and save table HTML
           c. Move to next region
        4. Generate summary statistics
        5. Save JSON index file
    
    Output Files:
        - 180 HTML files: table_{Region}_{Year}_{Timestamp}.html
        - 1 JSON index: scrape_index_{Timestamp}.json
    
    JSON Index Structure:
        [
            {
                "region": "Region I",
                "year": "2025",
                "html_file": "table_Region_I_2025_20251111_143022.html",
                "html_size": 1234567,
                "extracted_at": "2025-11-11T14:30:22.123456"
            },
            ...
        ]
    
    User Interaction:
        - Initial: Press Enter to start
        - First region: Manually select region, then press Enter
        - Completion: Press Enter to close browser
    
    Error Handling:
        - Keyboard interrupt (Ctrl+C): Graceful shutdown
        - Individual failures: Logged but don't stop execution
        - Final: Browser always closes properly
    
    Performance:
        - Expected runtime: 40-80 minutes
        - Depends on: Network speed, server response, anti-bot delays
        - Files saved progressively (not all at end)
    
    Returns:
        None (exits after completion or error)
    """
    print("="*70)
    print("DPWH Scraper - Playwright Version (Browser Visible)")
    print("="*70)
    print("\nThis will open a browser window you can watch.")
    print("Press Ctrl+C to stop at any time.")
    print("="*70)
    
    input("\nPress Enter to start...")
    
    all_projects = []
    
    with sync_playwright() as p:
        # Launch browser with visible window and anti-detection
        print("\nLaunching browser...")
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,  # Slow down operations
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Asia/Manila',
            permissions=['geolocation'],
            color_scheme='light',
        )
        
        # Remove webdriver property
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        try:
            # Load initial page
            print("\n📄 Loading initial page...")
            page.goto(BASE_URL, wait_until='domcontentloaded', timeout=60000)
            random_delay(3, 5)
            page.wait_for_load_state('networkidle', timeout=30000)
            print("✓ Initial page loaded\n")
            
            for idx, region in enumerate(REGIONS):
                is_first_region = (idx == 0)
                region_results = scrape_region(page, region, is_first_region=is_first_region)
                
                if region_results:
                    all_projects.extend(region_results)
                    print(f"\n  ✅ Completed {region}: {len(region_results)} years scraped")
                else:
                    print(f"\n  ⚠️  No data for region: {region}")
                
                # Show progress
                print(f"\n  📊 Total files collected: {len(all_projects)}")
                
                # Random delay between regions
                if idx < len(REGIONS) - 1:
                    print(f"\n  💤 Waiting before next region...")
                    random_delay(3, 6)
            
            # Show summary
            print("\n" + "="*70)
            print("SUMMARY")
            print("="*70)
            print(f"Total files scraped: {len(all_projects)}")
            
            # Group by region
            if all_projects:
                from collections import defaultdict
                by_region = defaultdict(list)
                for item in all_projects:
                    by_region[item['region']].append(item)
                
                print(f"\nRegions collected: {len(by_region)}")
                for region_name, items in by_region.items():
                    total_size = sum(item['html_size'] for item in items) / 1024  # KB
                    years = [item['year'] for item in items]
                    print(f"  • {region_name}: {len(items)} years ({', '.join(years)}) - {total_size:.1f} KB total")
            
            # Save JSON index with metadata
            if all_projects:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                index_file = f'scrape_index_{timestamp}.json'
                index_path = os.path.join(OUTPUT_DIR, index_file)
                
                with open(index_path, 'w', encoding='utf-8') as f:
                    json.dump(all_projects, f, indent=2, ensure_ascii=False)
                
                print(f"\n✓ Saved index: {index_path}")
                print(f"\n📁 All files saved in: {os.path.abspath(OUTPUT_DIR)}/")
            
            else:
                print("\n⚠️  No data to save")
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n" + "="*70)
            input("Press Enter to close browser...")
            browser.close()
            print("Done!")

if __name__ == "__main__":
    main()

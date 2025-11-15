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


class ParseError:
    """Constants for parse error codes and messages."""
    
    # Missing Required Fields
    MISSING_CONTRACT_ID = ("ERR-001", "Missing contract ID")
    MISSING_DESCRIPTION = ("ERR-002", "Missing contract description")
    MISSING_CONTRACTOR = ("ERR-003", "Missing contractor information")
    MISSING_OFFICE = ("ERR-004", "Missing implementing office")
    MISSING_FUNDS = ("ERR-005", "Missing source of funds")
    
    # Empty Optional Fields
    EMPTY_COST = ("WARN-011", "Empty cost field")
    EMPTY_EFFECTIVITY = ("WARN-012", "Empty effectivity date")
    EMPTY_EXPIRY = ("WARN-013", "Empty expiry date")
    EMPTY_STATUS = ("WARN-014", "Empty status field")
    EMPTY_ACCOMPLISHMENT = ("WARN-015", "Empty accomplishment field")
    
    # Invalid Formats
    INVALID_COST = ("ERR-021", "Invalid cost format: '{value}'")
    NEGATIVE_COST = ("ERR-022", "Negative cost value: {value}")
    INVALID_PERCENTAGE = ("ERR-023", "Invalid percentage format: '{value}'")
    PERCENTAGE_OUT_RANGE = ("ERR-024", "Percentage out of range: {value}")
    
    INVALID_EFFECTIVITY = ("ERR-031", "Invalid effectivity date format: '{value}'")
    INVALID_EXPIRY = ("ERR-032", "Invalid expiry date format: '{value}'")
    
    # Contractor Issues
    EXTRA_CONTRACTORS = ("WARN-041", "{count} contractors found, stored in 4 columns (excess combined in column 4)")
    CONTRACTOR_MISSING_ID = ("ERR-042", "Contractor missing ID code: '{name}'")
    CONTRACTOR_NAME_HAS_SLASH = ("WARN-043", "Contractor name contains slash (/) - may need manual review: '{name}'")
    JOINT_VENTURE_INFO = ("INFO-045", "Joint venture with {count} contractors")
    
    # HTML Structure
    NO_TBODY = ("CRIT-051", "No contract tbody found")
    NO_TR = ("CRIT-052", "No tr element in tbody")


class ParseNotes:
    """Helper class for managing parse notes with severity separation."""
    
    def __init__(self):
        self.critical = []
        self.errors = []
        self.warnings = []
        self.info = []
    
    def add(self, error_tuple, **kwargs):
        """Add a parse note using error tuple."""
        code, message = error_tuple
        if kwargs:
            message = message.format(**kwargs)
        
        full_message = f"{code}: {message}"
        
        # Route to appropriate list based on code prefix
        if code.startswith("CRIT-"):
            self.critical.append(full_message)
        elif code.startswith("ERR-"):
            self.errors.append(full_message)
        elif code.startswith("WARN-"):
            self.warnings.append(full_message)
        elif code.startswith("INFO-"):
            self.info.append(full_message)
    
    def get_by_severity(self, severity, max_length=500):
        """Get notes for specific severity level."""
        notes_list = getattr(self, severity, [])
        
        if not notes_list:
            return None
        
        notes_str = " | ".join(notes_list)
        
        if len(notes_str) > max_length:
            notes_str = notes_str[:max_length-3] + "..."
        
        return notes_str
    
    def get_all_columns(self, max_length=500):
        """Get all notes as dict for CSV columns."""
        return {
            'critical_errors': self.get_by_severity('critical', max_length),
            'errors': self.get_by_severity('errors', max_length),
            'warnings': self.get_by_severity('warnings', max_length),
            'info_notes': self.get_by_severity('info', max_length)
        }
    
    def has_critical(self):
        """Check if any CRITICAL notes exist."""
        return len(self.critical) > 0
    
    def merge(self, other_columns):
        """Merge error columns from another source."""
        if other_columns.get('critical_errors'):
            self.critical.append(other_columns['critical_errors'])
        if other_columns.get('errors'):
            self.errors.append(other_columns['errors'])
        if other_columns.get('warnings'):
            self.warnings.append(other_columns['warnings'])
        if other_columns.get('info_notes'):
            self.info.append(other_columns['info_notes'])


def discover_html_files(directory: str = 'html', year_filter: Optional[int] = None) -> List[Tuple[Path, int, str]]:
    """Discover all HTML files and extract years and office names.
    
    Returns: List of (filepath, year, office_name) tuples
    """
    pattern = 'table_*.html'
    files = []
    
    for filepath in Path(directory).glob(pattern):
        # Extract office name from filename: table_{office_name}_{year}_{date}_{time}.html
        # The filename structure has timestamp split into date and time with underscore
        # Example: table_Central_Office_2016_20251111_155202.html
        # Split and work backwards: [...office_parts..., year, date, time]
        name_without_ext = filepath.stem  # Remove .html
        parts = name_without_ext.split('_')
        
        if len(parts) >= 4 and parts[-3].isdigit() and len(parts[-3]) == 4:
            # parts[-3] should be the year (4 digits)
            # parts[1:-3] should be the office name parts
            year = int(parts[-3])
            office_parts = parts[1:-3]  # Skip 'table' prefix and last 3 (year, date, time)
            office_name = ' '.join(office_parts)
            
            if year_filter is None or year == year_filter:
                files.append((filepath, year, office_name))
        else:
            logger.warning(f"Could not extract year/office from filename: {filepath.name}")
    
    return sorted(files, key=lambda x: (x[1], x[2]))


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


def clean_cost(cost_text: Optional[str]) -> Tuple[Optional[float], Dict]:
    """Clean and convert cost to float."""
    notes = ParseNotes()
    
    if not cost_text or cost_text.strip() == '':
        notes.add(ParseError.EMPTY_COST)
        return None, notes.get_all_columns()
    
    try:
        cleaned = cost_text.replace(',', '')
        value = float(cleaned)
        
        if value < 0:
            notes.add(ParseError.NEGATIVE_COST, value=value)
            return None, notes.get_all_columns()
        
        return value, notes.get_all_columns()
        
    except ValueError:
        notes.add(ParseError.INVALID_COST, value=cost_text)
        return None, notes.get_all_columns()


def parse_date(date_text: Optional[str], field_name: str = 'date') -> Tuple[Optional[str], Dict]:
    """Parse date to ISO format."""
    notes = ParseNotes()
    
    if not date_text or date_text.strip() == '':
        if field_name == 'effectivity':
            notes.add(ParseError.EMPTY_EFFECTIVITY)
        elif field_name == 'expiry':
            notes.add(ParseError.EMPTY_EXPIRY)
        return None, notes.get_all_columns()
    
    try:
        parsed = date_parser.parse(date_text)
        return parsed.strftime('%Y-%m-%d'), notes.get_all_columns()
    except (ValueError, TypeError):
        if field_name == 'effectivity':
            notes.add(ParseError.INVALID_EFFECTIVITY, value=date_text)
        elif field_name == 'expiry':
            notes.add(ParseError.INVALID_EXPIRY, value=date_text)
        return None, notes.get_all_columns()


def clean_percentage(pct_text: Optional[str]) -> Tuple[Optional[float], Dict]:
    """Convert percentage to float."""
    notes = ParseNotes()
    
    if not pct_text or pct_text.strip() == '':
        # Empty accomplishment is valid for not started
        return None, notes.get_all_columns()
    
    try:
        value = float(pct_text)
        if value < 0 or value > 100:
            notes.add(ParseError.PERCENTAGE_OUT_RANGE, value=value)
        return value, notes.get_all_columns()
    except ValueError:
        notes.add(ParseError.INVALID_PERCENTAGE, value=pct_text)
        return None, notes.get_all_columns()


def parse_contractors(contractor_text: Optional[str]) -> List[Tuple[str, Optional[str], bool]]:
    """Parse contractor text into list of (name, id, has_stray_slash) tuples.
    
    Handles both:
    - Single contractors: "COMPANY NAME (ID)"
    - Joint ventures: "COMPANY A (ID1) / COMPANY B (ID2)"
    
    Splits on ") /" pattern (closing paren, space, slash) which is the
    actual joint venture separator. Any remaining "/" in names are flagged
    as potentially needing manual review.
    
    Returns: List of (name, id, has_stray_slash) tuples
    """
    if not contractor_text:
        return []

    contractor_text = unescape(contractor_text.strip())

    # Improved splitting: split after (ID) pattern, keeping the ID with the contractor
    # This regex finds all occurrences of: NAME (FORMER NAME) (ID)
    # or NAME (ID), and is robust to missing parens in former name
    contractor_pattern = re.compile(r'(.*?\(.*?\))?\s*\((\d+)\)')
    matches = list(contractor_pattern.finditer(contractor_text))

    result = []
    last_end = 0
    for match in matches:
        full_contractor = contractor_text[last_end:match.end()].strip()
        last_end = match.end()
        id_match = re.search(r'\((\d+)\)\s*$', full_contractor)
        truncated = False
        if id_match:
            contractor_id = id_match.group(1)
            name = full_contractor[:id_match.start()].strip()
            # Remove any leading or trailing slash and whitespace
            name = name.lstrip('/').strip()
            # If unbalanced parens, replace with tilde
            if name.count('(') != name.count(')'):
                name = name.rstrip() + '~'
                truncated = True
            has_slash = '/' in name
            result.append((name, contractor_id, has_slash, truncated))
        else:
            fallback_id = None
            fallback_name = full_contractor.lstrip('/').strip()
            fallback_id_match = re.search(r'\((\d+)\)', full_contractor)
            if fallback_id_match:
                fallback_id = fallback_id_match.group(1)
                fallback_name = full_contractor[:fallback_id_match.start()].lstrip('/').strip()
            has_slash = '/' in fallback_name
            # Mark as truncated if fallback used
            truncated = True
            fallback_name = fallback_name.rstrip() + '~'
            result.append((fallback_name, fallback_id, has_slash, truncated))

    return result


def split_implementing_office(office_text: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Split implementing office into region and office name.
    
    Example: 'Central Office - Flood Control Management Cluster' 
    Returns: ('Central Office', 'Flood Control Management Cluster')
    """
    if not office_text:
        return None, None
    
    # Split on ' - ' delimiter
    parts = office_text.split(' - ', 1)
    
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        # No delimiter found, treat entire text as office
        return None, parts[0].strip()


def get_contractor_columns(contractor_text: Optional[str], max_contractors: int = 4) -> Tuple[Dict, Dict]:
    """Parse contractors and return data dict + error columns dict.
    
    If more than max_contractors are found, contractors 1-3 are stored normally,
    and contractors 4+ are combined in the 4th column (names and IDs separated by semicolons).
    """
    notes = ParseNotes()
    
    if not contractor_text:
        notes.add(ParseError.MISSING_CONTRACTOR)
        result = {}
        for i in range(1, max_contractors + 1):
            result[f'contractor_name_{i}'] = None
            result[f'contractor_id_{i}'] = None
        return result, notes.get_all_columns()
    
    contractors = parse_contractors(contractor_text)

    result = {}

    # Handle first 3 contractors normally
    for i in range(1, max_contractors):
        if i <= len(contractors):
            name, contractor_id, has_stray_slash, truncated = contractors[i-1]
            result[f'contractor_name_{i}'] = name
            result[f'contractor_id_{i}'] = contractor_id
            if not contractor_id:
                notes.add(ParseError.CONTRACTOR_MISSING_ID, name=name[:30] if name else 'Unknown')
            if has_stray_slash:
                notes.add(ParseError.CONTRACTOR_NAME_HAS_SLASH, name=name[:50] if name else 'Unknown')
            if truncated:
                notes.add(("WARN-044", "Contractor name appears truncated: '{name}'"), name=name[:50] if name else 'Unknown')
        else:
            result[f'contractor_name_{i}'] = None
            result[f'contractor_id_{i}'] = None

    # Handle 4th contractor and any excess contractors (combine them)
    if len(contractors) >= max_contractors:
        names = []
        ids = []
        for i in range(max_contractors - 1, len(contractors)):
            name, contractor_id, has_stray_slash, truncated = contractors[i]
            names.append(name)
            ids.append(contractor_id if contractor_id else '')
            if not contractor_id:
                notes.add(ParseError.CONTRACTOR_MISSING_ID, name=name[:30] if name else 'Unknown')
            if has_stray_slash:
                notes.add(ParseError.CONTRACTOR_NAME_HAS_SLASH, name=name[:50] if name else 'Unknown')
            if truncated:
                notes.add(("WARN-044", "Contractor name appears truncated: '{name}'"), name=name[:50] if name else 'Unknown')
        result[f'contractor_name_{max_contractors}'] = '; '.join(names)
        result[f'contractor_id_{max_contractors}'] = '; '.join(ids)
        if len(contractors) > max_contractors:
            notes.add(ParseError.EXTRA_CONTRACTORS, count=len(contractors))
    else:
        result[f'contractor_name_{max_contractors}'] = None
        result[f'contractor_id_{max_contractors}'] = None

    if len(contractors) > 1:
        notes.add(ParseError.JOINT_VENTURE_INFO, count=len(contractors))

    return result, notes.get_all_columns()


def extract_contract_data(tbody, year: int, office_name: str, filename: str) -> Dict:
    """Extract all fields from contract tbody."""
    tr = tbody.find('tr')
    if not tr:
        logger.error("No tr element found in tbody")
        return None
    
    contract = {}
    notes = ParseNotes()
    
    # Row number
    row_th = tr.find('th', scope='row')
    contract['row_number'] = row_th.get_text(strip=True).rstrip('.') if row_th else None
    
    # Contract ID
    contract['contract_id'] = extract_span_by_pattern(tr, 'lblCustomerId')
    if not contract['contract_id']:
        notes.add(ParseError.MISSING_CONTRACT_ID)
    
    # Description
    contract['description'] = extract_span_by_pattern(tr, 'lblContactName')
    if not contract['description']:
        notes.add(ParseError.MISSING_DESCRIPTION)
    
    # Contractors
    contractor_text = extract_span_by_pattern(tr, 'lblCountry')
    contractor_data, contractor_notes = get_contractor_columns(contractor_text, max_contractors=4)
    contract.update(contractor_data)
    notes.merge(contractor_notes)
    
    # Implementing office - split into region and office
    office_raw = extract_span_by_pattern(tr, 'Label5')
    if not office_raw:
        notes.add(ParseError.MISSING_OFFICE)
        contract['region'] = None
        contract['implementing_office'] = None
    else:
        region, office = split_implementing_office(office_raw)
        contract['region'] = region
        contract['implementing_office'] = office
    
    contract['source_of_funds'] = extract_span_by_pattern(tr, 'Label6')
    if not contract['source_of_funds']:
        notes.add(ParseError.MISSING_FUNDS)
    
    # Cost
    cost_raw = extract_span_by_pattern(tr, 'Label2')
    cost_value, cost_notes = clean_cost(cost_raw)
    contract['cost_php'] = cost_value
    notes.merge(cost_notes)
    
    # Dates
    effectivity_raw = extract_span_by_pattern(tr, 'Label3')
    effectivity_value, effectivity_notes = parse_date(effectivity_raw, 'effectivity')
    contract['effectivity_date'] = effectivity_value
    notes.merge(effectivity_notes)
    
    expiry_raw = extract_span_by_pattern(tr, 'Label4')
    expiry_value, expiry_notes = parse_date(expiry_raw, 'expiry')
    contract['expiry_date'] = expiry_value
    notes.merge(expiry_notes)
    
    # Status
    contract['status'] = extract_span_by_pattern(tr, 'Label7')
    if not contract['status']:
        notes.add(ParseError.EMPTY_STATUS)
    
    # Accomplishment
    accomplishment_raw = extract_span_by_pattern(tr, 'Label1')
    accomplishment_value, accomplishment_notes = clean_percentage(accomplishment_raw)
    contract['accomplishment_pct'] = accomplishment_value
    notes.merge(accomplishment_notes)
    
    # Metadata
    contract['year'] = year
    contract['source_office'] = office_name
    contract['file_source'] = filename
    
    # Add all error columns
    contract.update(notes.get_all_columns())
    
    return contract


def process_html_file(filepath: Path, year: int, office_name: str) -> List[Dict]:
    """Process single HTML file and return list of contracts."""
    logger.info(f"Processing: {filepath.name} (Year: {year}, Office: {office_name})")
    
    try:
        soup = parse_html_file(filepath)
        tbodies = extract_contracts(soup)
        
        contracts = []
        for tbody in tbodies:
            try:
                contract = extract_contract_data(tbody, year, office_name, filepath.name)
                if contract:
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


def main(year_filter: Optional[int] = None):
    """Main processing function."""
    # Setup
    html_dir = Path('html')
    csv_dir = Path('csv')
    logs_dir = Path('logs')
    
    csv_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    # Discover files
    files = discover_html_files(html_dir, year_filter)
    
    if not files:
        logger.warning(f"No HTML files found for year: {year_filter}")
        return
    
    logger.info(f"Found {len(files)} HTML file(s) to process")
    
    # Process all files
    all_contracts = []
    for filepath, year, office_name in files:
        contracts = process_html_file(filepath, year, office_name)
        all_contracts.extend(contracts)
    
    # Write CSV
    if all_contracts:
        if year_filter:
            output_path = csv_dir / f'contracts_{year_filter}_all_offices.csv'
        else:
            output_path = csv_dir / 'contracts_all_years_all_offices.csv'

        write_csv(all_contracts, output_path)

        # Statistics
        total = len(all_contracts)
        with_critical = sum(1 for c in all_contracts if c.get('critical_errors'))
        with_errors = sum(1 for c in all_contracts if c.get('errors'))
        with_warnings = sum(1 for c in all_contracts if c.get('warnings'))

        # Count all subtypes for errors, warnings, infos
        from collections import Counter
        def split_notes(contracts, col):
            notes = []
            for c in contracts:
                val = c.get(col)
                if val:
                    notes.extend([n.strip() for n in val.split('|')])
            return notes

        crit_counter = Counter()
        err_counter = Counter()
        warn_counter = Counter()
        info_counter = Counter()
        for c in all_contracts:
            for note in split_notes([c], 'critical_errors'):
                if note: crit_counter[note.split(':')[0]] += 1
            for note in split_notes([c], 'errors'):
                if note: err_counter[note.split(':')[0]] += 1
            for note in split_notes([c], 'warnings'):
                if note: warn_counter[note.split(':')[0]] += 1
            for note in split_notes([c], 'info_notes'):
                if note: info_counter[note.split(':')[0]] += 1

        # Message templates for each code (add new codes as needed)
        MESSAGE_TEMPLATES = {
            'WARN-041': '{count} contractors found, stored in 4 columns (excess combined in column 4)',
            'ERR-042': "Contractor missing ID code: '{name}'",
            'WARN-043': "Contractor missing name, only ID found: '{id}'",
            'WARN-044': "Contractor name appears truncated: '{name}'",
            'ERR-044': "Failed to parse contractor text: '{text}'",
            'INFO-045': 'Joint venture with {count} contractors',
            'ERR-001': 'Missing contract ID',
            'ERR-002': 'Missing contract description',
            'ERR-003': 'Missing contractor information',
            'ERR-004': 'Missing implementing office',
            'ERR-005': 'Missing source of funds',
            'WARN-011': 'Empty cost field',
            'WARN-012': 'Empty effectivity date',
            'WARN-013': 'Empty expiry date',
            'WARN-014': 'Empty status field',
            'WARN-015': 'Empty accomplishment field',
            'ERR-021': "Invalid cost format: '{value}'",
            'ERR-022': 'Negative cost value: {value}',
            'ERR-023': "Invalid percentage format: '{value}'",
            'ERR-024': 'Percentage out of range: {value}',
            'ERR-031': "Invalid effectivity date format: '{value}'",
            'ERR-032': "Invalid expiry date format: '{value}'",
            'ERR-033': 'Expiry date before effectivity date',
            'WARN-034': 'Future effectivity date: {date}',
            'WARN-035': 'Contract duration > 10 years',
            # Add more as needed
        }

        summary_lines = []
        summary_lines.append(f"# Parse Summary\n")
        summary_lines.append(f"**Total contracts:** {total}")
        summary_lines.append(f"**Contracts with CRITICAL errors:** {with_critical}")
        if crit_counter:
            summary_lines.append(f"\n## CRITICAL error subtypes:")
            summary_lines.append(f"| Code | Message Template | Count |")
            summary_lines.append(f"|------|------------------|-------|")
            for k, v in crit_counter.items():
                template = MESSAGE_TEMPLATES.get(k, '')
                summary_lines.append(f"| {k} | {template} | {v} |")
        summary_lines.append(f"**Contracts with ERRORs:** {with_errors}")
        if err_counter:
            summary_lines.append(f"\n## ERROR subtypes:")
            summary_lines.append(f"| Code | Message Template | Count |")
            summary_lines.append(f"|------|------------------|-------|")
            for k, v in err_counter.items():
                template = MESSAGE_TEMPLATES.get(k, '')
                summary_lines.append(f"| {k} | {template} | {v} |")
        summary_lines.append(f"**Contracts with WARNINGs:** {with_warnings}")
        if warn_counter:
            summary_lines.append(f"\n## WARNING subtypes:")
            summary_lines.append(f"| Code | Message Template | Count |")
            summary_lines.append(f"|------|------------------|-------|")
            for k, v in warn_counter.items():
                template = MESSAGE_TEMPLATES.get(k, '')
                summary_lines.append(f"| {k} | {template} | {v} |")
        if info_counter:
            summary_lines.append(f"\n## INFO subtypes:")
            summary_lines.append(f"| Code | Message Template | Count |")
            summary_lines.append(f"|------|------------------|-------|")
            for k, v in info_counter.items():
                template = MESSAGE_TEMPLATES.get(k, '')
                summary_lines.append(f"| {k} | {template} | {v} |")
        summary_lines.append(f"**Clean contracts:** {total - with_critical - with_errors - with_warnings}")

        # Write summary to markdown file
        summary_path = csv_dir / (f'parse_summary_{year_filter}.md' if year_filter else 'parse_summary_all_years.md')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))

        # Also log to console
        logger.info("\n" + '\n'.join(summary_lines))
    else:
        logger.warning("No contracts extracted!")


if __name__ == '__main__':
    import sys
    
    # Check for year argument
    year = None
    if len(sys.argv) > 1:
        try:
            year = int(sys.argv[1])
            logger.info(f"Filtering for year: {year}")
        except ValueError:
            logger.error(f"Invalid year: {sys.argv[1]}")
            sys.exit(1)
    
    main(year_filter=year)

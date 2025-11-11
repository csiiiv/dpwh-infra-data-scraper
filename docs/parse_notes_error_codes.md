# Parse Notes Error Codes and Messages

**Document:** Error Handling Specification for DPWH HTML Parser  
**Version:** 1.0  
**Date:** November 11, 2025

---

## Overview

This document defines all possible errors, warnings, and validation issues that can occur during HTML parsing. Each error is assigned a standardized code and message format for consistent tracking and reporting.

---

## Error Severity Levels

| Level | Code Prefix | Description | Impact |
|-------|------------|-------------|---------|
| **CRITICAL** | `CRIT-` | Fatal errors preventing data extraction | Row may be skipped entirely |
| **ERROR** | `ERR-` | Data extraction failed but row is preserved | Field set to NULL/None |
| **WARNING** | `WARN-` | Data extracted but may be incomplete/questionable | Field populated with best effort |
| **INFO** | `INFO-` | Informational notes about data processing | No data quality impact |

---

## Error Codes and Messages

### 1. Missing Required Fields (ERR-001 to ERR-010)

| Code | Field | Message Template | Example |
|------|-------|------------------|---------|
| `ERR-001` | Contract ID | `Missing contract ID` | `ERR-001: Missing contract ID` |
| `ERR-002` | Description | `Missing contract description` | `ERR-002: Missing contract description` |
| `ERR-003` | Contractor | `Missing contractor information` | `ERR-003: Missing contractor information` |
| `ERR-004` | Implementing Office | `Missing implementing office` | `ERR-004: Missing implementing office` |
| `ERR-005` | Source of Funds | `Missing source of funds` | `ERR-005: Missing source of funds` |

**Handling:** Set field to `None`, add error to parse_notes, continue processing

---

### 2. Empty Optional Fields (WARN-011 to WARN-020)

| Code | Field | Message Template | Example |
|------|-------|------------------|---------|
| `WARN-011` | Cost | `Empty cost field` | `WARN-011: Empty cost field` |
| `WARN-012` | Effectivity Date | `Empty effectivity date` | `WARN-012: Empty effectivity date` |
| `WARN-013` | Expiry Date | `Empty expiry date` | `WARN-013: Empty expiry date` |
| `WARN-014` | Status | `Empty status field` | `WARN-014: Empty status field` |
| `WARN-015` | Accomplishment % | `Empty accomplishment field` | `WARN-015: Empty accomplishment field` |

**Handling:** Set field to `None`, add warning to parse_notes, continue processing

**Note:** Empty accomplishment is expected for "Not Yet Started" contracts, so WARN-015 may be suppressed if status indicates not started.

---

### 3. Invalid Data Formats (ERR-021 to ERR-040)

#### Numeric Fields

| Code | Field | Message Template | Example |
|------|-------|------------------|---------|
| `ERR-021` | Cost | `Invalid cost format: '{value}'` | `ERR-021: Invalid cost format: 'N/A'` |
| `ERR-022` | Cost | `Negative cost value: {value}` | `ERR-022: Negative cost value: -1000` |
| `ERR-023` | Accomplishment % | `Invalid percentage format: '{value}'` | `ERR-023: Invalid percentage format: 'TBD'` |
| `ERR-024` | Accomplishment % | `Percentage out of range: {value}` | `ERR-024: Percentage out of range: 150.5` |

#### Date Fields

| Code | Field | Message Template | Example |
|------|-------|------------------|---------|
| `ERR-031` | Effectivity Date | `Invalid effectivity date format: '{value}'` | `ERR-031: Invalid effectivity date format: '2025-13-45'` |
| `ERR-032` | Expiry Date | `Invalid expiry date format: '{value}'` | `ERR-032: Invalid expiry date format: 'TBD'` |
| `ERR-033` | Dates | `Expiry date before effectivity date` | `ERR-033: Expiry date before effectivity date` |
| `WARN-034` | Effectivity Date | `Future effectivity date: {date}` | `WARN-034: Future effectivity date: 2030-01-01` |
| `WARN-035` | Dates | `Contract duration > 10 years` | `WARN-035: Contract duration > 10 years (12.5 years)` |

**Handling:** Set field to `None`, add error to parse_notes, continue processing

---

### 4. Contractor Parsing Issues (WARN-041 to ERR-050)

| Code | Issue | Message Template | Example |
|------|-------|------------------|---------|
| `WARN-041` | Multiple Contractors | `{count} contractors found, stored in 4 columns (excess combined in column 4)` | `WARN-041: 5 contractors found, stored in 4 columns (excess combined in column 4)` |
| `ERR-042` | Contractor Format | `Contractor missing ID code: '{name}'` | `ERR-042: Contractor missing ID code: 'ACME CORP'` |
| `WARN-043` | Contractor Format | `Contractor missing name, only ID found: '{id}'` | `WARN-043: Contractor missing name, only ID found: '12345'` |
| `ERR-044` | Contractor Parsing | `Failed to parse contractor text: '{text}'` | `ERR-044: Failed to parse contractor text: '((INVALID))'` |
| `INFO-045` | Joint Venture | `Joint venture with {count} contractors` | `INFO-045: Joint venture with 3 contractors` |

**Handling:** 
- WARN-041: Store first 3 contractors normally, combine contractors 4+ in column 4 with semicolons, add warning
- ERR-042/043: Store available data, add error
- ERR-044: Set contractor fields to None, add error
- INFO-045: Informational only (optional)

---

### 5. HTML Structure Issues (CRIT-051 to CRIT-060)

| Code | Issue | Message Template | Example |
|------|-------|------------------|---------|
| `CRIT-051` | Missing tbody | `No contract tbody found` | `CRIT-051: No contract tbody found` |
| `CRIT-052` | Missing tr | `No tr element in tbody` | `CRIT-052: No tr element in tbody` |
| `CRIT-053` | Missing Span | `Span element not found for pattern '{pattern}'` | `CRIT-053: Span element not found for pattern 'lblCustomerId'` |
| `CRIT-054` | Malformed HTML | `HTML parsing failed: {error}` | `CRIT-054: HTML parsing failed: unexpected end tag` |
| `CRIT-055` | Empty File | `HTML file is empty or unreadable` | `CRIT-055: HTML file is empty or unreadable` |

**Handling:** Critical errors may result in row being skipped or entire file failing

---

### 6. Data Validation Issues (WARN-061 to WARN-080)

#### Business Logic Validations

| Code | Validation | Message Template | Example |
|------|------------|------------------|---------|
| `WARN-061` | Status vs Accomplishment | `Status '{status}' but accomplishment is {pct}%` | `WARN-061: Status 'Completed' but accomplishment is 85%` |
| `WARN-062` | Status vs Dates | `Status '{status}' but expiry date is {date}` | `WARN-062: Status 'Completed' but expiry date is 2026-01-01` |
| `WARN-063` | Zero Cost | `Contract cost is zero` | `WARN-063: Contract cost is zero` |
| `WARN-064` | Unusually High Cost | `Cost exceeds 50 billion PHP: {cost}` | `WARN-064: Cost exceeds 50 billion PHP: 75000000000` |
| `WARN-065` | Duplicate Contract ID | `Contract ID already exists in dataset` | `WARN-065: Contract ID already exists in dataset` |
| `WARN-066` | Missing Row Number | `Row number not found or invalid` | `WARN-066: Row number not found or invalid` |
| `WARN-067` | Old Contract | `Contract from more than 20 years ago` | `WARN-067: Contract from more than 20 years ago (1998)` |

#### Text Field Validations

| Code | Field | Message Template | Example |
|------|-------|------------------|---------|
| `WARN-071` | Description | `Unusually short description: {length} chars` | `WARN-071: Unusually short description: 15 chars` |
| `WARN-072` | Description | `Description truncated or incomplete` | `WARN-072: Description truncated or incomplete` |
| `WARN-073` | Contractor Name | `Unusually short contractor name: '{name}'` | `WARN-073: Unusually short contractor name: 'ABC'` |
| `WARN-074` | Special Characters | `Field contains unusual characters: {field}` | `WARN-074: Field contains unusual characters: description` |

---

### 7. Data Cleaning Issues (INFO-081 to INFO-090)

| Code | Action | Message Template | Example |
|------|--------|------------------|---------|
| `INFO-081` | HTML Entities | `HTML entities decoded in {field}` | `INFO-081: HTML entities decoded in contractor_name` |
| `INFO-082` | Whitespace | `Extra whitespace trimmed from {field}` | `INFO-082: Extra whitespace trimmed from description` |
| `INFO-083` | Case Normalization | `Text case normalized in {field}` | `INFO-083: Text case normalized in status` |
| `INFO-084` | Number Formatting | `Number formatting cleaned: '{original}' -> {cleaned}` | `INFO-084: Number formatting cleaned: '1,234.56' -> 1234.56` |

**Handling:** Informational only, data successfully cleaned

---

### 8. File-Level Issues (CRIT-091 to CRIT-099)

| Code | Issue | Message Template | Example |
|------|-------|------------------|---------|
| `CRIT-091` | File Not Found | `HTML file not found: {filepath}` | `CRIT-091: HTML file not found: table_2026.html` |
| `CRIT-092` | Encoding Error | `File encoding error: {error}` | `CRIT-092: File encoding error: invalid UTF-8` |
| `CRIT-093` | Permission Error | `File permission denied: {filepath}` | `CRIT-093: File permission denied: table_2016.html` |
| `CRIT-094` | Year Extraction | `Cannot extract year from filename: {filename}` | `CRIT-094: Cannot extract year from filename: table.html` |
| `CRIT-095` | Empty Result | `No contracts found in file` | `CRIT-095: No contracts found in file` |

---

## Parse Notes Format

### Separate Columns by Severity

Instead of a single `parse_notes` column, errors are separated into 4 columns:

1. **critical_errors** - CRIT-xxx codes only
2. **errors** - ERR-xxx codes only  
3. **warnings** - WARN-xxx codes only
4. **info_notes** - INFO-xxx codes only

### Single Error Example
```csv
critical_errors,errors,warnings,info_notes
,ERR-021: Invalid cost format: 'N/A',,
```

### Multiple Errors in Same Severity (Pipe-Delimited)
```csv
critical_errors,errors,warnings,info_notes
,,WARN-011: Empty cost field | WARN-041: 4 contractors found | WARN-061: Status 'Completed' but accomplishment is 85%,
```

### Mixed Severities
```csv
critical_errors,errors,warnings,info_notes
,ERR-001: Missing contract ID | ERR-021: Invalid cost format: 'N/A',WARN-012: Empty effectivity date,INFO-045: Joint venture with 3 contractors
```

### Benefits of Separate Columns

**Easy Filtering:**
```python
# Drop rows with critical errors
df_clean = df[df['critical_errors'].isna()]

# Flag rows with any errors
df['has_errors'] = df['errors'].notna()

# Include only informational notes
df_info_only = df[df[['critical_errors', 'errors', 'warnings']].isna().all(axis=1)]

# Get all contracts with warnings but no errors
df_warnings = df[df['errors'].isna() & df['warnings'].notna()]
```

**Easy Severity Analysis:**
```python
# Count by severity
critical_count = df['critical_errors'].notna().sum()
error_count = df['errors'].notna().sum()
warning_count = df['warnings'].notna().sum()

print(f"Critical: {critical_count}, Errors: {error_count}, Warnings: {warning_count}")
```

**Selective Column Dropping:**
```python
# For production: drop info_notes, keep warnings for review
df_production = df.drop(columns=['info_notes'])

# For analysis: keep everything
df_analysis = df.copy()

# For clean dataset: drop all error columns
df_clean = df.drop(columns=['critical_errors', 'errors', 'warnings', 'info_notes'])
```

---

## Implementation Functions

### Error Helper Functions

```python
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
    DATE_ORDER_ERROR = ("ERR-033", "Expiry date before effectivity date")
    FUTURE_DATE_WARN = ("WARN-034", "Future effectivity date: {date}")
    LONG_DURATION_WARN = ("WARN-035", "Contract duration > 10 years ({duration:.1f} years)")
    
    # Contractor Issues
    EXTRA_CONTRACTORS = ("WARN-041", "{count} contractors found, stored in 4 columns (excess combined in column 4)")
    CONTRACTOR_MISSING_ID = ("ERR-042", "Contractor missing ID code: '{name}'")
    CONTRACTOR_MISSING_NAME = ("WARN-043", "Contractor missing name, only ID found: '{id}'")
    CONTRACTOR_PARSE_FAIL = ("ERR-044", "Failed to parse contractor text: '{text}'")
    JOINT_VENTURE_INFO = ("INFO-045", "Joint venture with {count} contractors")
    
    # HTML Structure
    NO_TBODY = ("CRIT-051", "No contract tbody found")
    NO_TR = ("CRIT-052", "No tr element in tbody")
    SPAN_NOT_FOUND = ("CRIT-053", "Span element not found for pattern '{pattern}'")
    HTML_PARSE_FAIL = ("CRIT-054", "HTML parsing failed: {error}")
    EMPTY_FILE = ("CRIT-055", "HTML file is empty or unreadable")
    
    # Data Validation
    STATUS_MISMATCH = ("WARN-061", "Status '{status}' but accomplishment is {pct}%")
    STATUS_DATE_MISMATCH = ("WARN-062", "Status '{status}' but expiry date is {date}")
    ZERO_COST = ("WARN-063", "Contract cost is zero")
    HIGH_COST = ("WARN-064", "Cost exceeds 50 billion PHP: {cost}")
    DUPLICATE_ID = ("WARN-065", "Contract ID already exists in dataset")
    MISSING_ROW_NUM = ("WARN-066", "Row number not found or invalid")
    OLD_CONTRACT = ("WARN-067", "Contract from more than 20 years ago ({year})")
    
    SHORT_DESCRIPTION = ("WARN-071", "Unusually short description: {length} chars")
    TRUNCATED_TEXT = ("WARN-072", "Description truncated or incomplete")
    SHORT_CONTRACTOR = ("WARN-073", "Unusually short contractor name: '{name}'")
    SPECIAL_CHARS = ("WARN-074", "Field contains unusual characters: {field}")
    
    # File-Level
    FILE_NOT_FOUND = ("CRIT-091", "HTML file not found: {filepath}")
    ENCODING_ERROR = ("CRIT-092", "File encoding error: {error}")
    PERMISSION_ERROR = ("CRIT-093", "File permission denied: {filepath}")
    YEAR_EXTRACT_FAIL = ("CRIT-094", "Cannot extract year from filename: {filename}")
    NO_CONTRACTS = ("CRIT-095", "No contracts found in file")


class ParseNotes:
    """Helper class for managing parse notes with severity separation."""
    
    def __init__(self):
        self.critical = []
        self.errors = []
        self.warnings = []
        self.info = []
    
    def add(self, error_tuple, **kwargs):
        """
        Add a parse note using error tuple.
        
        Args:
            error_tuple: Tuple of (code, message_template)
            **kwargs: Values to format into message template
        """
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
    
    def add_raw(self, code_prefix, message):
        """Add a raw message without code tuple."""
        if code_prefix == "CRIT":
            self.critical.append(message)
        elif code_prefix == "ERR":
            self.errors.append(message)
        elif code_prefix == "WARN":
            self.warnings.append(message)
        elif code_prefix == "INFO":
            self.info.append(message)
    
    def get_by_severity(self, severity, max_length=500):
        """
        Get notes for specific severity level.
        
        Args:
            severity: 'critical', 'errors', 'warnings', or 'info'
            max_length: Maximum length of notes string
            
        Returns:
            String of notes or None if empty
        """
        notes_list = getattr(self, severity, [])
        
        if not notes_list:
            return None
        
        notes_str = " | ".join(notes_list)
        
        if len(notes_str) > max_length:
            notes_str = notes_str[:max_length-3] + "..."
        
        return notes_str
    
    def get_all_columns(self, max_length=500):
        """
        Get all notes as dict for CSV columns.
        
        Returns:
            Dict with keys: critical_errors, errors, warnings, info_notes
        """
        return {
            'critical_errors': self.get_by_severity('critical', max_length),
            'errors': self.get_by_severity('errors', max_length),
            'warnings': self.get_by_severity('warnings', max_length),
            'info_notes': self.get_by_severity('info', max_length)
        }
    
    def has_critical(self):
        """Check if any CRITICAL notes exist."""
        return len(self.critical) > 0
    
    def has_errors(self):
        """Check if any ERROR notes exist."""
        return len(self.errors) > 0
    
    def has_warnings(self):
        """Check if any WARNING notes exist."""
        return len(self.warnings) > 0
    
    def has_any_issues(self):
        """Check if any notes exist (excluding INFO)."""
        return self.has_critical() or self.has_errors() or self.has_warnings()
    
    def get_summary(self):
        """Get summary count of issues."""
        return {
            'critical': len(self.critical),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'info': len(self.info)
        }


# Usage Example
def clean_cost(cost_text):
    """Clean cost with error tracking."""
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
        
        if value == 0:
            notes.add(ParseError.ZERO_COST)
        
        if value > 50_000_000_000:  # 50 billion
            notes.add(ParseError.HIGH_COST, cost=value)
        
        return value, notes.get_all_columns()
        
    except ValueError:
        notes.add(ParseError.INVALID_COST, value=cost_text)
        return None, notes.get_all_columns()


# Updated extract_contract_data function
def extract_contract_data(tbody, year: int, filename: str) -> Dict:
    """Extract all fields from contract tbody with separated error tracking."""
    tr = tbody.find('tr')
    contract = {}
    notes = ParseNotes()
    
    # Extract all fields...
    contract['contract_id'] = extract_span_by_pattern(tr, 'lblCustomerId')
    if not contract['contract_id']:
        notes.add(ParseError.MISSING_CONTRACT_ID)
    
    # ... more field extraction ...
    
    # Cost with error tracking
    cost_raw = extract_span_by_pattern(tr, 'Label2')
    cost_value, cost_notes = clean_cost(cost_raw)
    contract['cost_php'] = cost_value
    
    # Merge cost notes
    if cost_notes:
        for severity in ['critical_errors', 'errors', 'warnings', 'info_notes']:
            if cost_notes.get(severity):
                notes.add_raw(severity.split('_')[0].upper(), cost_notes[severity])
    
    # Metadata
    contract['year'] = year
    contract['file_source'] = filename
    
    # Add all error columns
    contract.update(notes.get_all_columns())
    
    return contract


def validate_dates(effectivity_date, expiry_date):
    """Validate date logic and return warnings."""
    notes = ParseNotes()
    
    if effectivity_date and expiry_date:
        from datetime import datetime
        
        eff = datetime.fromisoformat(effectivity_date)
        exp = datetime.fromisoformat(expiry_date)
        
        if exp < eff:
            notes.add(ParseError.DATE_ORDER_ERROR)
        
        duration_years = (exp - eff).days / 365.25
        if duration_years > 10:
            notes.add(ParseError.LONG_DURATION_WARN, duration=duration_years)
        
        now = datetime.now()
        if eff > now:
            notes.add(ParseError.FUTURE_DATE_WARN, date=effectivity_date)
    
    return notes.get_notes()


def get_contractor_columns_with_errors(contractor_text, max_contractors=4):
    """Parse contractors with comprehensive error tracking.
    
    Contractors 1-3 stored normally, contractors 4+ combined in column 4 with semicolons.
    """
    notes = ParseNotes()
    
    if not contractor_text:
        notes.add(ParseError.MISSING_CONTRACTOR)
        result = {f'contractor_name_{i}': None for i in range(1, max_contractors+1)}
        result.update({f'contractor_id_{i}': None for i in range(1, max_contractors+1)})
        return result, notes.get_notes()
    
    try:
        contractors = parse_contractors(contractor_text)
        
        if not contractors:
            notes.add(ParseError.CONTRACTOR_PARSE_FAIL, text=contractor_text[:50])
        
        result = {}
        
        for i in range(1, max_contractors + 1):
            if i <= len(contractors):
                name, contractor_id = contractors[i-1]
                result[f'contractor_name_{i}'] = name
                result[f'contractor_id_{i}'] = contractor_id
                
                # Validation
                if not contractor_id:
                    notes.add(ParseError.CONTRACTOR_MISSING_ID, name=name[:30])
                if not name or len(name) < 3:
                    notes.add(ParseError.SHORT_CONTRACTOR, name=name)
            else:
                result[f'contractor_name_{i}'] = None
                result[f'contractor_id_{i}'] = None
        
        if len(contractors) > max_contractors:
            notes.add(ParseError.EXTRA_CONTRACTORS, count=len(contractors))
        
        if len(contractors) > 1:
            notes.add(ParseError.JOINT_VENTURE_INFO, count=len(contractors))
        
        return result, notes.get_notes()
        
    except Exception as e:
        notes.add(ParseError.CONTRACTOR_PARSE_FAIL, text=str(e))
        result = {f'contractor_name_{i}': None for i in range(1, max_contractors+1)}
        result.update({f'contractor_id_{i}': None for i in range(1, max_contractors+1)})
        return result, notes.get_notes()
```

---

## Error Statistics Tracking

### Recommended Metrics

```python
from collections import Counter

class ErrorStats:
    """Track parsing error statistics."""
    
    def __init__(self):
        self.error_counts = Counter()
        self.total_rows = 0
        self.rows_with_errors = 0
    
    def record(self, parse_notes):
        """Record errors from a row's parse_notes."""
        self.total_rows += 1
        
        if parse_notes:
            self.rows_with_errors += 1
            
            # Extract error codes
            for note in parse_notes.split(" | "):
                code = note.split(":")[0].strip()
                self.error_counts[code] += 1
    
    def report(self):
        """Generate error statistics report."""
        print(f"\n=== Parse Error Statistics ===")
        print(f"Total rows processed: {self.total_rows}")
        print(f"Rows with errors/warnings: {self.rows_with_errors} ({self.rows_with_errors/self.total_rows*100:.1f}%)")
        print(f"\nTop 10 Most Common Issues:")
        
        for code, count in self.error_counts.most_common(10):
            print(f"  {code}: {count} occurrences")
        
        # Severity breakdown
        critical = sum(c for k, c in self.error_counts.items() if k.startswith("CRIT-"))
        errors = sum(c for k, c in self.error_counts.items() if k.startswith("ERR-"))
        warnings = sum(c for k, c in self.error_counts.items() if k.startswith("WARN-"))
        
        print(f"\nBy Severity:")
        print(f"  CRITICAL: {critical}")
        print(f"  ERROR: {errors}")
        print(f"  WARNING: {warnings}")
```

---

## Priority for Implementation

### Phase 1 (Critical)
1. ERR-001 to ERR-005: Missing required fields
2. ERR-021 to ERR-024: Invalid numeric formats
3. ERR-031 to ERR-033: Invalid date formats
4. WARN-041: Extra contractors

### Phase 2 (Important)
1. WARN-011 to WARN-015: Empty optional fields
2. WARN-061 to WARN-067: Business logic validations
3. CRIT-051 to CRIT-055: HTML structure issues

### Phase 3 (Nice to Have)
1. INFO-081 to INFO-084: Data cleaning info
2. WARN-071 to WARN-074: Text field validations
3. CRIT-091 to CRIT-095: File-level issues

---

## Testing Checklist

- [ ] Test each error code generates correct message
- [ ] Test multiple errors combine with ` | ` delimiter
- [ ] Test message truncation at 500 chars
- [ ] Test error statistics tracking
- [ ] Test severity filtering (CRITICAL only, ERROR+CRITICAL, etc.)
- [ ] Verify error codes don't overlap
- [ ] Test with real problematic HTML samples

---

**Last Updated:** November 11, 2025  
**Total Error Codes Defined:** 50+

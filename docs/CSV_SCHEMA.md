# DPWH Contracts CSV Schema Documentation

**Version:** 2.0  
**Last Updated:** November 11, 2025  
**Parser Version:** 2.0

---

## Overview

This document describes the CSV output schema for the DPWH contract data parser. The CSV file contains one row per contract with all extracted fields, metadata, and quality tracking columns.

---

## File Information

- **Output Directory:** `csv/`
- **Filename Patterns:** 
  - `contracts_all_years_all_offices.csv` - All contracts combined
  - `contracts_YYYY_all_offices.csv` - Single year (e.g., `contracts_2023_all_offices.csv`)
  - `contracts_with_warnings.csv` - Contracts with data quality warnings
- **Encoding:** UTF-8
- **Delimiter:** Comma (`,`)
- **Quote Character:** Double quote (`"`)
- **Line Endings:** LF (`\n`)

---

## Schema Details

Total: **25 columns**

### 1. Core Identification Fields

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `row_number` | Integer | No | Sequential row number from source HTML | `1` |
| `contract_id` | String | No | Unique contract identifier | `16O00049` |
| `description` | String | No | Full contract description | `VALENZUELA-PUMPING STATIONS...` |

---

### 2. Contractor Information (Joint Venture Support)

The parser supports up to **4 contractor columns**. For joint ventures with more than 4 contractors, contractors 1-3 are stored normally, and contractors 4+ are **combined in column 4** with semicolon separators.

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `contractor_name_1` | String | Yes | First contractor name | `TRIPLE 8 CONSTRUCTION & SUPPLY, INC.` |
| `contractor_id_1` | String | Yes | First contractor ID code | `10684` |
| `contractor_name_2` | String | Yes | Second contractor name (if joint venture) | `SHIMIZU CORPORATION` |
| `contractor_id_2` | String | Yes | Second contractor ID | `OECO_16693` |
| `contractor_name_3` | String | Yes | Third contractor name (if joint venture) | `TAKENAKA CIVIL ENGINEERING & CONSTRUCTION` |
| `contractor_id_3` | String | Yes | Third contractor ID | `OECO_29591` |
| `contractor_name_4` | String | Yes | Fourth+ contractor names (semicolon-separated) | `COMPANY D; COMPANY E` |
| `contractor_id_4` | String | Yes | Fourth+ contractor IDs (semicolon-separated) | `44444; 55555` |

**Examples:**

**Single contractor:**
```csv
contractor_name_1,contractor_id_1,contractor_name_2,contractor_id_2,contractor_name_3,contractor_id_3,contractor_name_4,contractor_id_4
"ABC COMPANY",12345,,,,,,
```

**Three contractors (typical joint venture):**
```csv
contractor_name_1,contractor_id_1,contractor_name_2,contractor_id_2,contractor_name_3,contractor_id_3,contractor_name_4,contractor_id_4
"COMPANY A",11111,"COMPANY B",22222,"COMPANY C",33333,,
```

**Five contractors (excess combined):**
```csv
contractor_name_1,contractor_id_1,contractor_name_2,contractor_id_2,contractor_name_3,contractor_id_3,contractor_name_4,contractor_id_4
"COMPANY A",11111,"COMPANY B",22222,"COMPANY C",33333,"COMPANY D; COMPANY E","44444; 55555"
```

---

### 3. Location & Office Information

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `region` | String | Yes | Regional office (extracted from implementing_office) | `Central Office` |
| `implementing_office` | String | No | Office managing the contract | `Flood Control Management Cluster` |
| `source_of_funds` | String | No | Funding source description | `Regular Infra - GAA 2017 MFO-2` |

**Note:** The `implementing_office` field in source HTML is formatted as "REGION - OFFICE". The parser splits this into:
- `region`: The part before " - "
- `implementing_office`: The part after " - "

---

### 4. Financial Information

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `cost_php` | Decimal | Yes | Contract cost in Philippine Peso | `91773188.54` |

**Notes:**
- Source format: `"1,610,848,037.67"` (comma-separated)
- Parsed format: `1610848037.67` (decimal number)
- Null if field is empty or invalid

---

### 5. Timeline Information

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `effectivity_date` | Date (ISO 8601) | Yes | Contract start date | `2018-03-05` |
| `expiry_date` | Date (ISO 8601) | Yes | Contract end date | `2018-09-30` |

**Notes:**
- Source format: `"March 5, 2018"` (text)
- Parsed format: `2018-03-05` (ISO 8601: YYYY-MM-DD)
- Null if field is empty or invalid

---

### 6. Status & Progress

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `status` | String | Yes | Contract status | `Completed`, `On-Going`, `Not Yet Started`, `Terminated` |
| `accomplishment_pct` | Decimal | Yes | Percentage complete (0-100) | `100.00` |

---

### 7. Metadata Fields

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `year` | Integer | No | Year extracted from source filename | `2017` |
| `source_office` | String | No | Office name extracted from filename | `Central Office` |
| `file_source` | String | No | Original HTML filename | `table_Central_Office_2017_20251111_155210.html` |

---

### 8. Data Quality Tracking

These columns track parsing errors, warnings, and data quality issues. Multiple issues are **pipe-delimited** (`|`).

| Column | Data Type | Nullable | Description | Example |
|--------|-----------|----------|-------------|---------|
| `critical_errors` | String | Yes | CRIT-level errors (fatal issues) | `CRIT-051: No contract tbody found` |
| `errors` | String | Yes | ERR-level errors (data extraction failed) | `ERR-001: Missing contract ID` |
| `warnings` | String | Yes | WARN-level warnings (data may be incomplete) | `WARN-041: 5 contractors found, stored in 4 columns (excess combined in column 4)` |
| `info_notes` | String | Yes | INFO-level notes (informational) | `INFO-045: Joint venture with 3 contractors` |

**Error Code Format:** `CODE: Message`

**Multiple Issues Example:**
```csv
warnings
"WARN-011: Empty cost field | WARN-041: 5 contractors found, stored in 4 columns (excess combined in column 4)"
```

---

## Common Error Codes

### Critical (CRIT-xxx)
- `CRIT-051`: No contract tbody found
- `CRIT-052`: No tr element in tbody

### Errors (ERR-xxx)
- `ERR-001`: Missing contract ID
- `ERR-002`: Missing contract description
- `ERR-003`: Missing contractor information
- `ERR-021`: Invalid cost format
- `ERR-031`: Invalid effectivity date format
- `ERR-042`: Contractor missing ID code

### Warnings (WARN-xxx)
- `WARN-011`: Empty cost field
- `WARN-012`: Empty effectivity date
- `WARN-013`: Empty expiry date
- `WARN-041`: Excess contractors (>4) combined in column 4
- `WARN-043`: Contractor name contains slash (may need review)

### Informational (INFO-xxx)
- `INFO-045`: Joint venture with N contractors

For complete error code documentation, see [`parse_notes_error_codes.md`](parse_notes_error_codes.md).

---

## Data Filtering Recommendations

### Clean Data Only
```python
# Remove all rows with critical errors
df_clean = df[df['critical_errors'].isna()]

# Remove rows with any errors (critical + errors)
df_clean = df[df['critical_errors'].isna() & df['errors'].isna()]
```

### Quality Analysis
```python
# Get contracts with warnings but no errors
df_review = df[df['errors'].isna() & df['warnings'].notna()]

# Count issues by severity
critical_count = df['critical_errors'].notna().sum()
error_count = df['errors'].notna().sum()
warning_count = df['warnings'].notna().sum()
```

### Contractor Analysis
```python
# Single contractor only
df_single = df[df['contractor_name_2'].isna()]

# Joint ventures (2+ contractors)
df_jv = df[df['contractor_name_2'].notna()]

# Large joint ventures (4+ contractors)
df_large_jv = df[df['contractor_name_4'].str.contains(';', na=False)]
```

---

## Usage Examples

### Loading CSV in Python

```python
import pandas as pd

# Load CSV
df = pd.read_csv('csv/contracts_all_years_all_offices.csv')

# Basic info
print(f"Total contracts: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"Memory usage: {df.memory_usage().sum() / 1024**2:.2f} MB")
```

### Filtering Contractors

```python
# Find all contracts with a specific contractor
df_contractor = df[
    df['contractor_name_1'].str.contains('SHIMIZU', case=False, na=False) |
    df['contractor_name_2'].str.contains('SHIMIZU', case=False, na=False) |
    df['contractor_name_3'].str.contains('SHIMIZU', case=False, na=False) |
    df['contractor_name_4'].str.contains('SHIMIZU', case=False, na=False)
]

# Handle semicolon-separated contractors in column 4
def has_contractor(row, name):
    for i in range(1, 5):
        contractor = row.get(f'contractor_name_{i}')
        if pd.notna(contractor) and name.lower() in contractor.lower():
            return True
    return False

df['has_acme'] = df.apply(lambda row: has_contractor(row, 'ACME'), axis=1)
```

### Financial Analysis

```python
# Total contract value by year
total_by_year = df.groupby('year')['cost_php'].sum()

# Average contract value by status
avg_by_status = df.groupby('status')['cost_php'].mean()

# Top 10 most expensive contracts
top_contracts = df.nlargest(10, 'cost_php')[['contract_id', 'description', 'cost_php']]
```

---

## Schema Changes

### Version 2.0 (November 11, 2025)
- **Added:** `contractor_name_4` and `contractor_id_4` columns
- **Changed:** Contractor handling - excess contractors (5+) now combined in column 4 with semicolons
- **Changed:** `WARN-041` message updated to reflect new handling
- **Added:** `region` and `source_office` columns for better location tracking

### Version 1.0 (Initial Release)
- Initial schema with 3 contractor columns
- Basic error tracking with separate severity columns

---

## Best Practices

### 1. Always Check Error Columns
Before analysis, review the distribution of errors/warnings:
```python
print("Data Quality Summary:")
print(f"Critical Errors: {df['critical_errors'].notna().sum()}")
print(f"Errors: {df['errors'].notna().sum()}")
print(f"Warnings: {df['warnings'].notna().sum()}")
print(f"Clean Rows: {df[df[['critical_errors','errors','warnings']].isna().all(axis=1)].shape[0]}")
```

### 2. Handle Missing Values
```python
# Fill missing costs with 0 or drop rows
df['cost_php'].fillna(0, inplace=True)
# OR
df = df[df['cost_php'].notna()]
```

### 3. Parse Semicolon-Separated Contractors
```python
# Split contractor_name_4 if it contains semicolons
df['contractors_4_list'] = df['contractor_name_4'].str.split('; ')
df['contractor_4_count'] = df['contractors_4_list'].str.len()
```

### 4. Date Range Filtering
```python
# Convert to datetime
df['effectivity_date'] = pd.to_datetime(df['effectivity_date'])
df['expiry_date'] = pd.to_datetime(df['expiry_date'])

# Filter by date range
df_2023 = df[(df['effectivity_date'] >= '2023-01-01') & 
             (df['effectivity_date'] < '2024-01-01')]
```

---

## Contact & Support

For schema questions or issues:
- See [`html_to_csv_parser_specification.md`](html_to_csv_parser_specification.md) for parser details
- See [`parse_notes_error_codes.md`](parse_notes_error_codes.md) for error codes

**Document Version:** 2.0  
**Last Updated:** November 11, 2025

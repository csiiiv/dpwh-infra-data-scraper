#!/usr/bin/env python3
"""
Parse all DPWH HTML files and generate per-year summaries.
"""

import csv
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def run_parser(year=None):
    """Run the HTML parser for a specific year or all years."""
    cmd = [sys.executable, 'scripts/html_to_csv_parser.py']
    if year:
        cmd.append(str(year))
    
    print(f"Running parser for year: {year if year else 'all years'}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running parser: {result.stderr}")
        return False
    
    return True


def analyze_csv(csv_path):
    """Analyze a CSV file and return statistics."""
    stats = {
        'total_contracts': 0,
        'critical_errors': 0,
        'errors': 0,
        'warnings': 0,
        'clean': 0,
        'by_office': defaultdict(int),
        'by_region': defaultdict(int),
        'by_status': defaultdict(int),
        'total_cost': 0.0,
        'contracts_with_cost': 0,
        'critical_error_types': defaultdict(int),
        'error_types': defaultdict(int),
        'warning_types': defaultdict(int),
    }

    def count_types(cell, dct):
        if cell:
            for note in cell.split('|'):
                note = note.strip()
                if note:
                    code = note.split(':')[0].strip()
                    dct[code] += 1

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['total_contracts'] += 1

            # Error tracking
            if row.get('critical_errors'):
                stats['critical_errors'] += 1
                count_types(row.get('critical_errors'), stats['critical_error_types'])
            if row.get('errors'):
                stats['errors'] += 1
                count_types(row.get('errors'), stats['error_types'])
            if row.get('warnings'):
                stats['warnings'] += 1
                count_types(row.get('warnings'), stats['warning_types'])
            if not any([row.get('critical_errors'), row.get('errors'), row.get('warnings')]):
                stats['clean'] += 1

            # Office/Region
            source_office = row.get('source_office', 'Unknown')
            stats['by_office'][source_office] += 1

            region = row.get('region', 'Unknown')
            stats['by_region'][region] += 1

            # Status
            status = row.get('status', 'Unknown')
            stats['by_status'][status] += 1

            # Cost
            cost_str = row.get('cost_php', '')
            if cost_str:
                try:
                    cost = float(cost_str)
                    stats['total_cost'] += cost
                    stats['contracts_with_cost'] += 1
                except ValueError:
                    pass

    return stats


def generate_summary_markdown(years_data, output_path):
    """Generate a markdown summary of all parsed data."""
    lines = []
    
    lines.append("# DPWH Contracts Data Summary")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("\n---\n")
    
    # Error code descriptions for breakdowns
    code_desc = {
        'ERR-001': 'Missing contract ID',
        'ERR-002': 'Missing contract description',
        'ERR-003': 'Missing contractor information',
        'ERR-004': 'Missing implementing office',
        'ERR-005': 'Missing source of funds',
        'ERR-021': 'Invalid cost format',
        'ERR-022': 'Negative cost value',
        'ERR-023': 'Invalid percentage format',
        'ERR-024': 'Percentage out of range',
        'ERR-031': 'Invalid effectivity date format',
        'ERR-032': 'Invalid expiry date format',
        'ERR-033': 'Expiry date before effectivity date',
        'ERR-042': 'Contractor missing ID code',
        'ERR-044': 'Failed to parse contractor text',
        'WARN-011': 'Empty cost field',
        'WARN-012': 'Empty effectivity date',
        'WARN-013': 'Empty expiry date',
        'WARN-041': 'Multiple contractors found, stored in 4 columns (excess combined in column 4)',
        'WARN-043': 'Contractor missing name, only ID found',
        'WARN-061': 'Status/accomplishment mismatch',
        'WARN-062': 'Status/expiry date mismatch',
        'WARN-063': 'Contract cost is zero',
        'WARN-064': 'Cost exceeds 50 billion PHP',
        'WARN-065': 'Duplicate contract ID',
        'WARN-066': 'Row number not found or invalid',
        'WARN-067': 'Contract from more than 20 years ago',
        'WARN-071': 'Unusually short description',
        'WARN-072': 'Description truncated or incomplete',
        'WARN-073': 'Unusually short contractor name',
        'WARN-074': 'Field contains unusual characters',
        'CRIT-051': 'No contract tbody found',
        'CRIT-052': 'No tr element in tbody',
        'CRIT-053': 'Span element not found for pattern',
        'CRIT-054': 'HTML parsing failed',
        'CRIT-055': 'HTML file is empty or unreadable',
        'CRIT-091': 'HTML file not found',
        'CRIT-092': 'File encoding error',
        'CRIT-093': 'File permission denied',
        'CRIT-094': 'Cannot extract year from filename',
        'CRIT-095': 'No contracts found in file',
    }
    
    # Overall summary
    lines.append("## Overall Summary\n")
    total_all = sum(data['total_contracts'] for data in years_data.values())
    total_cost_all = sum(data['total_cost'] for data in years_data.values())
    total_clean = sum(data['clean'] for data in years_data.values())
    total_critical = sum(data['critical_errors'] for data in years_data.values())
    total_errors = sum(data['errors'] for data in years_data.values())
    total_warnings = sum(data['warnings'] for data in years_data.values())

    # Aggregate status breakdown across all years
    total_status = defaultdict(int)
    for data in years_data.values():
        for status, count in data['by_status'].items():
            total_status[status] += count

    # Aggregate error/warning types across all years
    total_critical_types = defaultdict(int)
    total_error_types = defaultdict(int)
    total_warning_types = defaultdict(int)
    for data in years_data.values():
        for code, count in data['critical_error_types'].items():
            total_critical_types[code] += count
        for code, count in data['error_types'].items():
            total_error_types[code] += count
        for code, count in data['warning_types'].items():
            total_warning_types[code] += count

    lines.append(f"- **Total Contracts Parsed**: {total_all:,}")
    lines.append(f"- **Total Contract Value**: ₱{total_cost_all:,.2f}")
    lines.append(f"- **Years Covered**: {min(years_data.keys())} - {max(years_data.keys())}")
    lines.append(f"- **Number of Years**: {len(years_data)}")
    lines.append("")

    # Show total quality statistics
    lines.append("**Total Data Quality (All Years):**")
    lines.append(f"- Clean Contracts: {total_clean:,} ({total_clean/total_all*100:.1f}%)")
    lines.append(f"- Contracts with Critical Errors: {total_critical:,}")
    lines.append(f"- Contracts with Errors: {total_errors:,}")
    lines.append(f"- Contracts with Warnings: {total_warnings:,}")
    lines.append("")

    # Show total status breakdown
    lines.append("**Total Contract Status Breakdown (All Years):**")
    for status, count in sorted(total_status.items(), key=lambda x: -x[1]):
        pct = count / total_all * 100 if total_all else 0
        lines.append(f"- {status}: {count:,} ({pct:.1f}%)")
    lines.append("")

    # Show total error/warning breakdown
    if total_critical_types:
        lines.append("**Total Critical Error Breakdown (All Years):**")
        for code, count in sorted(total_critical_types.items(), key=lambda x: -x[1]):
            desc = code_desc.get(code, "")
            lines.append(f"  - {code}{' ('+desc+')' if desc else ''}: {count}")
        lines.append("")
    
    if total_error_types:
        lines.append("**Total Error Breakdown (All Years):**")
        for code, count in sorted(total_error_types.items(), key=lambda x: -x[1]):
            desc = code_desc.get(code, "")
            lines.append(f"  - {code}{' ('+desc+')' if desc else ''}: {count}")
        lines.append("")
    
    if total_warning_types:
        lines.append("**Total Warning Breakdown (All Years):**")
        for code, count in sorted(total_warning_types.items(), key=lambda x: -x[1]):
            desc = code_desc.get(code, "")
            lines.append(f"  - {code}{' ('+desc+')' if desc else ''}: {count}")
        lines.append("")
    
    # Per-year breakdown
    lines.append("## Per-Year Breakdown\n")

    for year in sorted(years_data.keys()):
        data = years_data[year]
        lines.append(f"### {year}\n")

        lines.append("**Contract Statistics:**")
        lines.append(f"- Total Contracts: {data['total_contracts']:,}")
        lines.append(f"- Clean Contracts: {data['clean']:,} ({data['clean']/data['total_contracts']*100:.1f}%)")
        lines.append(f"- Contracts with Critical Errors: {data['critical_errors']:,}")
        lines.append(f"- Contracts with Errors: {data['errors']:,}")
        lines.append(f"- Contracts with Warnings: {data['warnings']:,}")
        lines.append("")

        # Error/Warning breakdowns (with descriptions)
        if data['critical_error_types']:
            lines.append("**Critical Error Breakdown:**")
            for code, count in sorted(data['critical_error_types'].items(), key=lambda x: -x[1]):
                desc = code_desc.get(code, "")
                lines.append(f"  - {code}{' ('+desc+')' if desc else ''}: {count}")
            lines.append("")
        if data['error_types']:
            lines.append("**Error Breakdown:**")
            for code, count in sorted(data['error_types'].items(), key=lambda x: -x[1]):
                desc = code_desc.get(code, "")
                lines.append(f"  - {code}{' ('+desc+')' if desc else ''}: {count}")
            lines.append("")
        if data['warning_types']:
            lines.append("**Warning Breakdown:**")
            for code, count in sorted(data['warning_types'].items(), key=lambda x: -x[1]):
                desc = code_desc.get(code, "")
                lines.append(f"  - {code}{' ('+desc+')' if desc else ''}: {count}")
            lines.append("")

        lines.append("**Financial Statistics:**")
        if data['contracts_with_cost'] > 0:
            avg_cost = data['total_cost'] / data['contracts_with_cost']
            lines.append(f"- Total Contract Value: ₱{data['total_cost']:,.2f}")
            lines.append(f"- Contracts with Cost Data: {data['contracts_with_cost']:,} ({data['contracts_with_cost']/data['total_contracts']*100:.1f}%)")
            lines.append(f"- Average Contract Value: ₱{avg_cost:,.2f}")
        else:
            lines.append("- No cost data available")
        lines.append("")

        lines.append("**By Source Office:**")
        for office, count in sorted(data['by_office'].items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = count / data['total_contracts'] * 100
            lines.append(f"- {office}: {count:,} ({pct:.1f}%)")
        if len(data['by_office']) > 10:
            lines.append(f"- ... and {len(data['by_office']) - 10} more offices")
        lines.append("")

        lines.append("**By Contract Status:**")
        for status, count in sorted(data['by_status'].items(), key=lambda x: x[1], reverse=True):
            pct = count / data['total_contracts'] * 100
            lines.append(f"- {status}: {count:,} ({pct:.1f}%)")
        lines.append("")

        lines.append("---\n")
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Summary written to: {output_path}")


def main():
    """Main function to parse all data and generate summaries."""
    csv_dir = Path('csv')
    years = range(2016, 2026)  # 2016-2025
    
    years_data = {}
    
    # Parse each year
    for year in years:
        print(f"\n{'='*60}")
        print(f"Processing Year: {year}")
        print('='*60)
        
        # Run parser
        if not run_parser(year):
            print(f"Failed to parse {year}, skipping...")
            continue
        
        # Find the CSV file
        csv_path = csv_dir / f'contracts_{year}_all_offices.csv'
        if not csv_path.exists():
            print(f"CSV not found: {csv_path}")
            continue
        
        # Analyze CSV
        print(f"Analyzing {csv_path}...")
        stats = analyze_csv(csv_path)
        years_data[year] = stats
        
        print(f"✓ {year}: {stats['total_contracts']:,} contracts, {stats['clean']:,} clean")
    
    # Generate summary
    if years_data:
        summary_path = Path('docs/parsing_summary.md')
        print(f"\n{'='*60}")
        print("Generating Summary Markdown")
        print('='*60)
        generate_summary_markdown(years_data, summary_path)
        print(f"\n✓ All done! Summary: {summary_path}")
    else:
        print("\nNo data to summarize!")


if __name__ == '__main__':
    main()

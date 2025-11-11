#!/usr/bin/env python3
"""
Generate summary from existing CSV files.
"""

import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime


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
    }
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['total_contracts'] += 1
            
            # Error tracking
            if row.get('critical_errors'):
                stats['critical_errors'] += 1
            if row.get('errors'):
                stats['errors'] += 1
            if row.get('warnings'):
                stats['warnings'] += 1
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


def analyze_year_from_all_csv(csv_path):
    """Analyze CSV and group by year."""
    by_year = defaultdict(lambda: {
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
    })
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year_str = row.get('year', '')
            if not year_str:
                continue
            
            try:
                year = int(year_str)
            except ValueError:
                continue
            
            stats = by_year[year]
            stats['total_contracts'] += 1
            
            # Error tracking
            if row.get('critical_errors'):
                stats['critical_errors'] += 1
            if row.get('errors'):
                stats['errors'] += 1
            if row.get('warnings'):
                stats['warnings'] += 1
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
    
    return dict(by_year)


def generate_summary_markdown(years_data, output_path):
    """Generate a markdown summary of all parsed data."""
    lines = []
    
    lines.append("# DPWH Contracts Data Summary")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("\n---\n")
    
    # Overall summary
    lines.append("## Overall Summary\n")
    total_all = sum(data['total_contracts'] for data in years_data.values())
    total_cost_all = sum(data['total_cost'] for data in years_data.values())
    
    lines.append(f"- **Total Contracts Parsed**: {total_all:,}")
    lines.append(f"- **Total Contract Value**: ₱{total_cost_all:,.2f}")
    lines.append(f"- **Years Covered**: {min(years_data.keys())} - {max(years_data.keys())}")
    lines.append(f"- **Number of Years**: {len(years_data)}")
    lines.append("")
    
    # Collect all unique offices
    all_offices = set()
    for data in years_data.values():
        all_offices.update(data['by_office'].keys())
    lines.append(f"- **Offices Represented**: {len(all_offices)}")
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
        
        lines.append("**Financial Statistics:**")
        if data['contracts_with_cost'] > 0:
            avg_cost = data['total_cost'] / data['contracts_with_cost']
            lines.append(f"- Total Contract Value: ₱{data['total_cost']:,.2f}")
            lines.append(f"- Contracts with Cost Data: {data['contracts_with_cost']:,} ({data['contracts_with_cost']/data['total_contracts']*100:.1f}%)")
            lines.append(f"- Average Contract Value: ₱{avg_cost:,.2f}")
        else:
            lines.append("- No cost data available")
        lines.append("")
        
        lines.append("**By Source Office (Top 10):**")
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
    
    print(f"✓ Summary written to: {output_path}")


def main():
    """Main function."""
    csv_dir = Path('csv')
    
    # Check for all_years CSV
    all_csv = csv_dir / 'contracts_all_years_all_offices.csv'
    
    if all_csv.exists():
        print(f"Analyzing {all_csv}...")
        years_data = analyze_year_from_all_csv(all_csv)
    else:
        # Look for individual year CSVs
        print("Looking for individual year CSV files...")
        years_data = {}
        for year in range(2016, 2026):
            csv_path = csv_dir / f'contracts_{year}_all_offices.csv'
            if csv_path.exists():
                print(f"  Found {csv_path.name}")
                stats = analyze_csv(csv_path)
                years_data[year] = stats
    
    if years_data:
        summary_path = Path('docs/parsing_summary.md')
        print(f"\nGenerating summary for {len(years_data)} years...")
        generate_summary_markdown(years_data, summary_path)
        print(f"\n✓ Done! Summary saved to: {summary_path}")
    else:
        print("\n✗ No CSV files found to analyze!")


if __name__ == '__main__':
    main()

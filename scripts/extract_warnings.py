#!/usr/bin/env python3
"""
Extract all entries with warnings from contracts_all_years_all_offices.csv
"""
import csv

input_file = 'csv/contracts_all_years_all_offices.csv'
output_file = 'csv/contracts_with_warnings.csv'

with open(input_file, newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    count = 0
    for row in reader:
        if row.get('warnings') and row['warnings'].strip():
            writer.writerow(row)
            count += 1
print(f"Extracted {count} contracts with warnings to {output_file}")

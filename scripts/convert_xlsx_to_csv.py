#!/usr/bin/env python3
"""
Convert all XLSX files in the current directory to CSV format.
Uses python-calamine for fast XLSX processing.
"""

import os
from pathlib import Path
import csv
from python_calamine import CalamineWorkbook


def convert_xlsx_to_csv(xlsx_path, output_dir=None):
    """
    Convert an XLSX file to CSV format using calamine.
    
    Args:
        xlsx_path: Path to the XLSX file
        output_dir: Directory to save CSV files (default: same as XLSX)
    
    Returns:
        List of created CSV file paths
    """
    xlsx_path = Path(xlsx_path)
    
    if output_dir is None:
        output_dir = xlsx_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load workbook with calamine
    workbook = CalamineWorkbook.from_path(str(xlsx_path))
    
    csv_files = []
    sheet_names = workbook.sheet_names
    
    print(f"\nProcessing: {xlsx_path.name}")
    print(f"Found {len(sheet_names)} sheet(s)")
    
    for sheet_name in sheet_names:
        # Read sheet data
        data = workbook.get_sheet_by_name(sheet_name).to_python()
        
        # Create CSV filename
        if len(sheet_names) == 1:
            # Single sheet: use base filename
            csv_filename = xlsx_path.stem + ".csv"
        else:
            # Multiple sheets: append sheet name
            csv_filename = f"{xlsx_path.stem}_{sheet_name}.csv"
        
        csv_path = output_dir / csv_filename
        
        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in data:
                writer.writerow(row)
        
        csv_files.append(csv_path)
        print(f"  ✓ Exported sheet '{sheet_name}' to {csv_filename}")
    
    return csv_files


def main():
    """Convert all XLSX files in the xlsx directory to CSV in the csv directory."""
    # Get the project root directory (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    xlsx_dir = project_root / "xlsx"
    csv_dir = project_root / "csv"
    
    # Create csv directory if it doesn't exist
    csv_dir.mkdir(exist_ok=True)
    
    # Find all XLSX files in the xlsx directory
    xlsx_files = list(xlsx_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        print(f"No XLSX files found in {xlsx_dir}")
        return
    
    print(f"Found {len(xlsx_files)} XLSX file(s) to convert")
    print(f"Source: {xlsx_dir}")
    print(f"Output: {csv_dir}\n")
    
    total_csv_files = 0
    for xlsx_file in xlsx_files:
        try:
            csv_files = convert_xlsx_to_csv(xlsx_file, csv_dir)
            total_csv_files += len(csv_files)
        except Exception as e:
            print(f"  ✗ Error processing {xlsx_file.name}: {e}")
    
    print(f"\n✓ Conversion complete! Created {total_csv_files} CSV file(s).")


if __name__ == "__main__":
    main()

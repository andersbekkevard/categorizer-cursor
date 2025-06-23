#!/usr/bin/env python3
"""
Norwegian Company Categorization Tool

Main script for categorizing companies from CSV files.

USAGE:
    python categorize.py

INPUT:
    Place your CSV file in the 'input/' directory.
    CSV must contain columns: company_name, revenue (or similar variants)

OUTPUT:
    Results will be saved in the 'output/' directory.
    Output CSV contains: company_name, company_category, revenue
"""

import sys
import os
import glob
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.processor import process_csv_file
from src.config import PRODUCT_CATEGORIES, CSV_DELIMITER


def display_welcome():
    """Display welcome message and instructions"""
    print("🏢 Norwegian Company Categorization Tool")
    print("=" * 55)
    print()
    print("📁 INPUT:  Place your CSV file in the 'input/' directory")
    print("   Required columns: company_name, revenue")
    print()
    print("📁 OUTPUT: Results will be saved in the 'output/' directory")
    print("   Output format: company_name, company_category, revenue")
    print()
    print("🏷️  CATEGORIES:")
    for i, category in enumerate(PRODUCT_CATEGORIES.keys(), 1):
        print(f"   {i}. {category}")
    print()
    print("=" * 55)


def find_input_files():
    """Find CSV files in the input directory"""
    input_dir = Path("input")

    if not input_dir.exists():
        print("❌ 'input/' directory not found!")
        print("   Creating 'input/' directory...")
        input_dir.mkdir()
        return []

    csv_files = list(input_dir.glob("*.csv"))
    return csv_files


def select_input_file(csv_files):
    """Let user select which CSV file to process"""
    if len(csv_files) == 0:
        print("❌ No CSV files found in 'input/' directory!")
        print()
        print("📋 Please add your CSV file to the 'input/' directory with columns:")
        print("   - company_name (or 'company name', 'name', 'company')")
        print("   - revenue (or 'revenues', 'turnover', 'sales')")
        print()
        print("💡 Example CSV format:")
        print(f"   company_name{CSV_DELIMITER}revenue")
        print(f"   Equinor ASA{CSV_DELIMITER}500000000")
        print(f"   DNB Bank{CSV_DELIMITER}250000000")
        return None

    if len(csv_files) == 1:
        selected_file = csv_files[0]
        print(f"📄 Found 1 CSV file: {selected_file.name}")
        response = input("   Process this file? (y/n): ").lower().strip()
        if response in ["y", "yes", ""]:
            return selected_file
        else:
            return None

    # Multiple files - let user choose
    print(f"📄 Found {len(csv_files)} CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"   {i}. {file.name}")

    while True:
        try:
            choice = input(f"\nSelect file (1-{len(csv_files)}): ").strip()

            if not choice:
                return None

            index = int(choice) - 1
            if 0 <= index < len(csv_files):
                return csv_files[index]
            else:
                print(f"Please enter a number between 1 and {len(csv_files)}")
        except ValueError:
            print("Please enter a valid number")


def get_processing_options():
    """Get processing options from user"""
    print("\n⚙️  Processing Options:")

    # Include metadata option
    response = (
        input("   Include detailed metadata (subsegment, confidence, etc.)? (y/n): ")
        .lower()
        .strip()
    )
    include_metadata = response in ["y", "yes"]

    return {"include_metadata": include_metadata}


def ensure_directories():
    """Ensure required directories exist"""
    directories = ["input", "output"]

    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"📁 Creating '{dir_name}/' directory...")
            dir_path.mkdir()

            # Add placeholder files to help users understand structure
            if dir_name == "input":
                placeholder = dir_path / "README.txt"
                placeholder.write_text(
                    f"""Place your CSV files here for processing.

Required columns:
- company_name (or 'company name', 'name', 'company')
- revenue (or 'revenues', 'turnover', 'sales')

Example:
company_name{CSV_DELIMITER}revenue
Equinor ASA{CSV_DELIMITER}500000000
DNB Bank{CSV_DELIMITER}250000000
"""
                )


def main():
    """Main function"""
    try:
        display_welcome()
        ensure_directories()

        # Find input files
        csv_files = find_input_files()

        # Select file to process
        selected_file = select_input_file(csv_files)

        if not selected_file:
            print("\n👋 No file selected. Goodbye!")
            return

        # Get processing options
        options = get_processing_options()

        print(f"\n🚀 Starting categorization of {selected_file.name}...")

        # Process the file
        summary = process_csv_file(
            str(selected_file), include_metadata=options["include_metadata"]
        )

        if summary:
            print(f"\n🎉 Categorization completed successfully!")
            print(f"   📊 Processed {summary['total_companies']} companies")
            print(f"   📁 Results saved in 'output/' directory")

    except KeyboardInterrupt:
        print("\n\n⏸️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tips:")
        print("   - Ensure your CSV has the required columns")
        print("   - Check that company names are not empty")
        print("   - Verify file encoding is UTF-8")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

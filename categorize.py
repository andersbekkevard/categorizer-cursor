#!/usr/bin/env python3
"""
Norwegian Company Categorization Tool

Main script for categorizing companies from CSV files.

USAGE:
    python categorize.py

INPUT:
    Place your CSV file in the 'input/' directory.
    CSV must have at least 2 columns: first column is company name, second is revenue
    Additional columns are ignored. Handles quoted values with commas properly.

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
    print("   Required: At least 2 columns (company name, revenue)")
    print("   Additional columns are ignored")
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
        print("📋 Please add your CSV file to the 'input/' directory with:")
        print("   - First column: company name")
        print("   - Second column: revenue")
        print("   - Additional columns are ignored")
        print()
        print("💡 Example CSV format:")
        print(f"   company{CSV_DELIMITER}revenue{CSV_DELIMITER}other")
        print(f"   Equinor ASA{CSV_DELIMITER}500000000{CSV_DELIMITER}extra")
        print(f'   DNB Bank{CSV_DELIMITER}"250,000,000"{CSV_DELIMITER}ignored')
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

    # Excel compatibility option
    response = (
        input("   Optimize for Excel compatibility (UTF-8 with BOM)? (Y/n): ")
        .lower()
        .strip()
    )
    excel_compatible = response not in ["n", "no"]  # Default to yes

    # Concurrent processing option
    response = (
        input(
            "   Use concurrent processing for speed (recommended for large datasets)? (Y/n): "
        )
        .lower()
        .strip()
    )
    concurrent = response not in ["n", "no"]  # Default to yes

    # Workers option (only if concurrent is enabled)
    max_workers = 5  # Default
    if concurrent:
        response = input("   Maximum concurrent workers (2-10, default=5): ").strip()
        if response.isdigit() and 2 <= int(response) <= 10:
            max_workers = int(response)

    return {
        "include_metadata": include_metadata,
        "excel_compatible": excel_compatible,
        "concurrent": concurrent,
        "max_workers": max_workers,
    }


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

Required format:
- First column: company name
- Second column: revenue  
- Additional columns are ignored
- Handles quoted values with commas (e.g., "123,456,789")

Example:
company{CSV_DELIMITER}revenue{CSV_DELIMITER}other
Equinor ASA{CSV_DELIMITER}500000000{CSV_DELIMITER}extra
DNB Bank{CSV_DELIMITER}"250,000,000"{CSV_DELIMITER}ignored
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
            str(selected_file),
            include_metadata=options["include_metadata"],
            excel_compatible=options["excel_compatible"],
            concurrent=options["concurrent"],
            max_workers=options["max_workers"],
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
        print("   - Ensure your CSV has at least 2 columns")
        print("   - First column should be company name")
        print("   - Check that company names are not empty")
        print("   - Verify file encoding is UTF-8")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

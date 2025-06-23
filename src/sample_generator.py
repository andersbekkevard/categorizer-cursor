"""
Sample CSV File Generator

Generates sample CSV files using the configured delimiter from config.
"""

import csv
from .config import CSV_DELIMITER


def generate_sample_csv(output_path):
    """Generate a sample CSV file with Norwegian companies and revenue data"""

    sample_data = [
        {"company_name": "Equinor ASA", "revenue": "750000000000"},
        {"company_name": "DNB Bank", "revenue": "45000000000"},
        {"company_name": "Telenor Norge AS", "revenue": "12500000000"},
        {"company_name": "Rema 1000", "revenue": "95000000000"},
        {"company_name": "IKEA", "revenue": "4500000000"},
        {"company_name": "H&M", "revenue": "2300000000"},
        {"company_name": "Apotek 1", "revenue": "8900000000"},
        {"company_name": "Elkjøp", "revenue": "15600000000"},
        {"company_name": "Oslo Kommune", "revenue": "85000000000"},
        {"company_name": "Lego", "revenue": "1200000000"},
    ]

    fieldnames = ["company_name", "revenue"]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=CSV_DELIMITER)
        writer.writeheader()
        writer.writerows(sample_data)

    print(f"✅ Sample CSV file generated: {output_path}")
    print(f"   Using delimiter: '{CSV_DELIMITER}'")


if __name__ == "__main__":
    generate_sample_csv("../input/sample_companies.csv")

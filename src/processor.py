"""
CSV Processing Module for Norwegian Company Categorization

This module handles reading CSV files with company name and revenue data,
categorizing the companies, and outputting results with categories included.
"""

import csv
import os
import time
from datetime import datetime
from pathlib import Path
from .categorizer import categorize_company
from .config import PRODUCT_CATEGORIES, CSV_DELIMITER


def read_input_csv(file_path):
    """
    Read CSV file with company name and revenue columns

    Args:
        file_path (str): Path to input CSV file

    Returns:
        list: List of dictionaries with 'company_name' and 'revenue' keys

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file has insufficient columns
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    companies = []

    with open(file_path, "r", encoding="utf-8") as csvfile:
        # Use configured delimiter (can be changed in config.py)
        reader = csv.reader(csvfile, delimiter=CSV_DELIMITER)

        # Read first row to check if we have headers and determine column count
        try:
            first_row = next(reader)
        except StopIteration:
            raise ValueError("CSV file appears to be empty")

        # Check if we have at least 2 columns
        if len(first_row) < 2:
            raise ValueError(
                "CSV file must have at least 2 columns (company name and revenue)"
            )

        # Determine if first row is headers (contains non-numeric data in revenue column)
        has_headers = True
        try:
            # Try to parse the second column as a number (remove commas first)
            revenue_value = first_row[1].replace(",", "").replace('"', "").strip()
            if (
                revenue_value
                and revenue_value.replace(".", "").replace("-", "").isdigit()
            ):
                has_headers = False
        except (IndexError, AttributeError):
            pass

        print(f"✓ Detected {'headers' if has_headers else 'no headers'}")
        print(f"✓ Using column 1 as company name, column 2 as revenue")
        print(
            f"✓ Ignoring {len(first_row) - 2} additional columns"
            if len(first_row) > 2
            else "✓ Processing 2 columns"
        )

        # If first row is not headers, process it as data
        if not has_headers:
            company_name = first_row[0].strip()
            revenue = first_row[1].strip()

            if company_name:  # Only add if company name is not empty
                companies.append({"company_name": company_name, "revenue": revenue})

        # Process remaining rows
        for row_num, row in enumerate(reader, start=2 if has_headers else 3):
            # Skip rows with insufficient columns
            if len(row) < 2:
                print(f"⚠️  Warning: Row {row_num} has insufficient columns, skipping")
                continue

            company_name = row[0].strip()
            revenue = row[1].strip()

            if not company_name:
                print(f"⚠️  Warning: Empty company name in row {row_num}, skipping")
                continue

            companies.append({"company_name": company_name, "revenue": revenue})

    print(f"✓ Loaded {len(companies)} companies from {file_path}")
    return companies


def process_companies(companies, progress_callback=None):
    """
    Process companies and categorize them

    Args:
        companies (list): List of company dictionaries
        progress_callback (callable): Optional callback for progress updates

    Returns:
        list: List of processed company dictionaries with categories
    """
    results = []
    total = len(companies)

    print(f"\n🔄 Processing {total} companies...")
    print("=" * 60)

    for i, company in enumerate(companies, 1):
        # Categorize the company
        categorization_result = categorize_company(company["company_name"])

        # Create result record with granular metrics
        result = {
            "company_name": company["company_name"],
            "company_category": categorization_result["category"],
            "category_id": categorization_result.get("category_id", 0),
            "revenue": company["revenue"],
            # Core metadata
            "subsegment": categorization_result.get("subsegment", ""),
            "confidence": categorization_result.get("confidence", ""),
            "selected_company": categorization_result.get("selected_company", ""),
            "org_number": categorization_result.get("org_number", ""),
            # Granular confidence metrics
            "categorized_by_naringskode": categorization_result.get(
                "categorized_by_naringskode", 0
            ),
            "num_naringskoder": categorization_result.get("num_naringskoder", 0),
            "exact_code_match": categorization_result.get("exact_code_match", 0),
            "keyword_match": categorization_result.get("keyword_match", 0),
            "confidence_score": categorization_result.get("confidence_score", 0.0),
            "primary_naringskode": categorization_result.get("primary_naringskode", ""),
            "matching_keywords": categorization_result.get("matching_keywords", ""),
            "method": categorization_result.get("method", ""),
        }

        results.append(result)

        # Progress output
        print(
            f"[{i:3}/{total}] {company['company_name']} -> {result['company_category']}"
        )
        if result["selected_company"] != company["company_name"]:
            print(f"          [Selected: {result['selected_company']}]")

        # Call progress callback if provided
        if progress_callback:
            progress_callback(i, total, result)

        # API rate limiting
        if i % 10 == 0:
            print("          (Pausing for API rate limiting...)")
            time.sleep(1)

    return results


def write_output_csv(
    results, output_path, include_metadata=False, excel_compatible=True
):
    """
    Write results to CSV file

    Args:
        results (list): List of result dictionaries
        output_path (str): Path for output CSV file
        include_metadata (bool): Whether to include additional metadata columns
        excel_compatible (bool): Whether to optimize for Excel compatibility (adds BOM)
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if include_metadata:
        fieldnames = [
            "company_name",
            "company_category",
            "category_id",
            "revenue",
            "subsegment",
            "confidence",
            "selected_company",
            "org_number",
            # Granular confidence metrics
            "categorized_by_naringskode",
            "num_naringskoder",
            "exact_code_match",
            "keyword_match",
            "confidence_score",
            "primary_naringskode",
            "matching_keywords",
            "method",
        ]
    else:
        fieldnames = [
            "company_name",
            "company_category",
            "category_id",
            "revenue",
            # Always include the key granular flags even in basic mode
            "categorized_by_naringskode",
            "confidence_score",
        ]

    # Choose encoding based on Excel compatibility preference
    encoding = "utf-8-sig" if excel_compatible else "utf-8"

    with open(output_path, "w", newline="", encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=CSV_DELIMITER)
        writer.writeheader()

        for result in results:
            # Only write the specified fields
            filtered_result = {field: result.get(field, "") for field in fieldnames}
            writer.writerow(filtered_result)

    print(f"\n✅ Results saved to: {output_path}")
    print(f"   📊 Processed {len(results)} companies")
    if excel_compatible:
        print("   📋 Excel-compatible format (UTF-8 with BOM)")
    else:
        print("   🔤 Standard UTF-8 format")


def generate_summary_report(results):
    """Generate and print a detailed summary report with granular confidence metrics"""

    # Category distribution
    categories = {}
    confidence_levels = {}

    # Granular metrics
    naringskode_categorized = 0
    exact_code_matches = 0
    keyword_matches = 0
    avg_confidence_score = 0.0
    method_distribution = {}

    for result in results:
        cat = result["company_category"]
        categories[cat] = categories.get(cat, 0) + 1

        conf = result.get("confidence", "Unknown")
        confidence_levels[conf] = confidence_levels.get(conf, 0) + 1

        # Count granular metrics
        if result.get("categorized_by_naringskode", 0) == 1:
            naringskode_categorized += 1

        if result.get("exact_code_match", 0) == 1:
            exact_code_matches += 1

        if result.get("keyword_match", 0) == 1:
            keyword_matches += 1

        # Accumulate confidence scores
        conf_score = result.get("confidence_score", 0.0)
        avg_confidence_score += conf_score

        # Method distribution
        method = result.get("method", "unknown")
        method_distribution[method] = method_distribution.get(method, 0) + 1

    # Calculate averages
    total_companies = len(results)
    avg_confidence_score = (
        avg_confidence_score / total_companies if total_companies > 0 else 0.0
    )

    print(f"\n📈 Detailed Categorization Summary:")
    print("=" * 60)

    print("\n📋 Categories:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(results)) * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")

    print(f"\n🎯 Confidence Levels:")
    for conf, count in sorted(confidence_levels.items()):
        percentage = (count / len(results)) * 100
        print(f"   {conf}: {count} ({percentage:.1f}%)")

    print(f"\n📊 Granular Confidence Metrics:")
    print(
        f"   📍 Categorized by Næringskode: {naringskode_categorized}/{total_companies} ({naringskode_categorized/total_companies*100:.1f}%)"
    )
    print(
        f"   🎯 Exact Code Matches: {exact_code_matches}/{total_companies} ({exact_code_matches/total_companies*100:.1f}%)"
    )
    print(
        f"   🔍 Keyword Matches: {keyword_matches}/{total_companies} ({keyword_matches/total_companies*100:.1f}%)"
    )
    print(f"   📈 Average Confidence Score: {avg_confidence_score:.3f}")

    print(f"\n🔧 Categorization Methods:")
    for method, count in sorted(
        method_distribution.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / total_companies) * 100
        print(f"   {method}: {count} ({percentage:.1f}%)")

    # Quality assessment
    high_quality = sum(1 for r in results if r.get("confidence_score", 0) >= 0.8)
    medium_quality = sum(
        1 for r in results if 0.5 <= r.get("confidence_score", 0) < 0.8
    )
    low_quality = sum(1 for r in results if r.get("confidence_score", 0) < 0.5)

    print(f"\n🌟 Quality Assessment:")
    print(
        f"   🟢 High Quality (≥0.8): {high_quality} ({high_quality/total_companies*100:.1f}%)"
    )
    print(
        f"   🟡 Medium Quality (0.5-0.8): {medium_quality} ({medium_quality/total_companies*100:.1f}%)"
    )
    print(
        f"   🔴 Low Quality (<0.5): {low_quality} ({low_quality/total_companies*100:.1f}%)"
    )

    return {
        "categories": categories,
        "confidence_levels": confidence_levels,
        "total_companies": len(results),
        "naringskode_categorized": naringskode_categorized,
        "exact_code_matches": exact_code_matches,
        "keyword_matches": keyword_matches,
        "avg_confidence_score": avg_confidence_score,
        "method_distribution": method_distribution,
        "quality_distribution": {
            "high": high_quality,
            "medium": medium_quality,
            "low": low_quality,
        },
    }


def process_csv_file(
    input_path, output_path=None, include_metadata=False, excel_compatible=True
):
    """
    Main function to process a CSV file from input to output

    Args:
        input_path (str): Path to input CSV file
        output_path (str): Path for output CSV file (auto-generated if None)
        include_metadata (bool): Whether to include additional metadata columns
        excel_compatible (bool): Whether to optimize for Excel compatibility (adds BOM)

    Returns:
        dict: Summary statistics
    """
    try:
        # Read input CSV
        companies = read_input_csv(input_path)

        if not companies:
            print("❌ No companies found in input file")
            return None

        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_name = Path(input_path).stem
            output_path = f"output/{input_name}_categorized_{timestamp}.csv"

        # Process companies
        results = process_companies(companies)

        # Write output CSV
        write_output_csv(results, output_path, include_metadata, excel_compatible)

        # Generate summary
        summary = generate_summary_report(results)

        return summary

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise

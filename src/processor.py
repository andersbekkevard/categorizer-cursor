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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from .categorizer import categorize_company
from .config import PRODUCT_CATEGORIES, CSV_DELIMITER

# Global variables for progress tracking
_progress_lock = threading.Lock()
_processed_count = 0


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


def process_single_company(company_data, progress_callback=None):
    """Process a single company - used for concurrent processing"""
    global _processed_count

    # Categorize the company (quiet mode for performance)
    categorization_result = categorize_company(company_data["company_name"], quiet=True)

    # Create result record with granular metrics
    result = {
        "company_name": company_data["company_name"],
        "company_category": categorization_result["category"],
        "category_id": categorization_result.get("category_id", 0),
        "revenue": company_data["revenue"],
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

    # Thread-safe progress tracking
    with _progress_lock:
        _processed_count += 1
        current_count = _processed_count

    # Call progress callback if provided
    if progress_callback:
        progress_callback(current_count, result)

    return result


def process_companies_concurrent(companies, progress_callback=None, max_workers=5):
    """
    Process companies concurrently for better performance

    Args:
        companies (list): List of company dictionaries
        progress_callback (callable): Optional callback for progress updates
        max_workers (int): Maximum number of concurrent workers

    Returns:
        list: List of processed company dictionaries with categories
    """
    global _processed_count
    _processed_count = 0  # Reset counter

    results = []
    total = len(companies)

    print(
        f"\n🚀 Processing {total} companies concurrently (max {max_workers} workers)..."
    )
    print("=" * 60)

    # Progress tracking callback
    def progress_tracker(current_count, result):
        if current_count % 100 == 0 or current_count <= 10:
            print(
                f"[{current_count:5}/{total}] {result['company_name']} -> {result['company_category']}"
            )
            if result["selected_company"] != result["company_name"]:
                print(f"          [Selected: {result['selected_company']}]")

    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_company = {
            executor.submit(process_single_company, company, progress_tracker): company
            for company in companies
        }

        # Collect results as they complete
        for future in as_completed(future_to_company):
            try:
                result = future.result()
                results.append(result)

                # Custom progress callback
                if progress_callback:
                    progress_callback(_processed_count, total, result)

            except Exception as e:
                company = future_to_company[future]
                print(f"❌ Error processing {company['company_name']}: {e}")
                # Add a failed result to maintain count
                results.append(
                    {
                        "company_name": company["company_name"],
                        "company_category": "Error",
                        "category_id": 0,
                        "revenue": company["revenue"],
                        "confidence_score": 0.0,
                        "method": "error",
                    }
                )

    # Sort results by original order (if needed, maintain input order)
    company_names = [c["company_name"] for c in companies]
    results.sort(
        key=lambda x: (
            company_names.index(x["company_name"])
            if x["company_name"] in company_names
            else len(company_names)
        )
    )

    return results


def process_companies(
    companies, progress_callback=None, concurrent=True, max_workers=5
):
    """
    Process companies and categorize them - with optional concurrent processing

    Args:
        companies (list): List of company dictionaries
        progress_callback (callable): Optional callback for progress updates
        concurrent (bool): Whether to use concurrent processing
        max_workers (int): Maximum number of concurrent workers (if concurrent=True)

    Returns:
        list: List of processed company dictionaries with categories
    """
    if concurrent and len(companies) > 10:  # Use concurrent for larger datasets
        return process_companies_concurrent(companies, progress_callback, max_workers)

    # Original sequential processing (kept for small datasets or fallback)
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
            f"[{i:5}/{total}] {company['company_name']} -> {result['company_category']}"
        )
        if result["selected_company"] != company["company_name"]:
            print(f"          [Selected: {result['selected_company']}]")

        # Call progress callback if provided
        if progress_callback:
            progress_callback(i, total, result)

        # Optimized rate limiting - less frequent for large datasets
        if i % 50 == 0:  # Changed from 10 to 50 for better performance
            print("          (Brief pause for API rate limiting...)")
            time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds

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
    input_path,
    output_path=None,
    include_metadata=False,
    excel_compatible=True,
    concurrent=True,
    max_workers=5,
    batch_size=None,
):
    """
    Main function to process a CSV file from input to output

    Args:
        input_path (str): Path to input CSV file
        output_path (str): Path for output CSV file (auto-generated if None)
        include_metadata (bool): Whether to include additional metadata columns
        excel_compatible (bool): Whether to optimize for Excel compatibility (adds BOM)
        concurrent (bool): Whether to use concurrent processing for speed
        max_workers (int): Maximum number of concurrent workers
        batch_size (int): Batch size for very large datasets (auto-determined if None)

    Returns:
        dict: Summary statistics
    """
    try:
        # Read input CSV
        companies = read_input_csv(input_path)

        if not companies:
            print("❌ No companies found in input file")
            return None

        # Show performance estimate for large datasets
        if len(companies) >= 1000:
            print_performance_summary(len(companies), concurrent, max_workers)

            # Ask for confirmation for very large datasets
            if len(companies) >= 10000:
                response = input(
                    f"\n⚠️  Processing {len(companies):,} companies will take significant time. Continue? (y/n): "
                )
                if response.lower().strip() not in ["y", "yes"]:
                    print("❌ Processing cancelled by user")
                    return None

        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_name = Path(input_path).stem
            output_path = f"output/{input_name}_categorized_{timestamp}.csv"

        # Process companies - use batch processing for very large datasets
        if len(companies) >= 5000:  # Use batch processing for 5k+ companies
            if batch_size is None:
                batch_size = min(
                    1000, len(companies) // 10
                )  # Auto-determine batch size
            results = process_companies_in_batches(
                companies,
                batch_size=batch_size,
                concurrent=concurrent,
                max_workers=max_workers,
            )
        else:
            results = process_companies(
                companies, concurrent=concurrent, max_workers=max_workers
            )

        # Write output CSV
        write_output_csv(results, output_path, include_metadata, excel_compatible)

        # Generate summary
        summary = generate_summary_report(results)

        return summary

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise


def estimate_processing_time(num_companies, concurrent=True, max_workers=5):
    """Estimate processing time for large datasets"""
    if concurrent:
        # Assume average 0.3 seconds per company with concurrency and caching
        # With duplicates, effective time reduces significantly
        base_time_per_company = 0.3 / max_workers  # Parallel benefit
        total_time = num_companies * base_time_per_company

        # Factor in cache benefits for duplicates (assume 20% duplicates)
        duplicate_factor = 0.8  # 20% faster due to cache hits
        estimated_time = total_time * duplicate_factor
    else:
        # Sequential processing: ~0.7 seconds per company
        estimated_time = num_companies * 0.7

    return estimated_time


def print_performance_summary(num_companies, concurrent=True, max_workers=5):
    """Print performance summary and tips for large datasets"""
    estimated_time = estimate_processing_time(num_companies, concurrent, max_workers)

    hours = int(estimated_time // 3600)
    minutes = int((estimated_time % 3600) // 60)
    seconds = int(estimated_time % 60)

    print(f"\n📊 Performance Estimate for {num_companies:,} companies:")
    print("=" * 60)

    if hours > 0:
        print(f"⏱️  Estimated time: {hours}h {minutes}m {seconds}s")
    elif minutes > 0:
        print(f"⏱️  Estimated time: {minutes}m {seconds}s")
    else:
        print(f"⏱️  Estimated time: {seconds}s")

    if concurrent:
        print(f"🚀 Concurrent processing: {max_workers} workers")
        print("💾 Caching: Enabled (speeds up duplicate company names)")
        print("🔇 Quiet mode: Enabled (reduces output overhead)")
    else:
        print("🐌 Sequential processing")

    print(f"\n💡 Performance Tips:")
    if num_companies > 1000:
        print("   ✅ Use concurrent processing (already enabled)")
        print("   ✅ Increase workers (2-10) for better CPU utilization")
        print("   ✅ Run on machine with good internet connection")
        print("   ⚠️  Consider processing in smaller batches if memory limited")

    if num_companies > 10000:
        print("   �� For 10k+ companies, consider:")
        print("      - Processing overnight or during off-hours")
        print("      - Splitting into multiple smaller files")
        print("      - Using a dedicated server/VM")

    print(f"\n🔧 Current optimizations:")
    print(f"   • Company data caching (avoids duplicate API calls)")
    print(f"   • Reduced rate limiting (pause every 50 instead of 10)")
    print(f"   • Concurrent processing with {max_workers} workers")
    print(f"   • Quiet mode (minimal output during processing)")
    print(f"   • Optimized confidence scoring")

    return estimated_time


def process_companies_in_batches(
    companies, batch_size=1000, concurrent=True, max_workers=5, progress_callback=None
):
    """
    Process companies in batches to manage memory usage for very large datasets

    Args:
        companies (list): List of company dictionaries
        batch_size (int): Number of companies to process per batch
        concurrent (bool): Whether to use concurrent processing
        max_workers (int): Maximum number of concurrent workers
        progress_callback (callable): Optional callback for progress updates

    Returns:
        list: List of processed company dictionaries with categories
    """
    total = len(companies)
    all_results = []

    print(f"\n🔄 Processing {total:,} companies in batches of {batch_size:,}...")
    print("=" * 60)

    # Process in batches
    for i in range(0, total, batch_size):
        batch_end = min(i + batch_size, total)
        batch = companies[i:batch_end]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size

        print(
            f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} companies)..."
        )

        # Process this batch
        batch_results = process_companies(
            batch,
            concurrent=concurrent,
            max_workers=max_workers,
            progress_callback=None,  # We'll handle progress at batch level
        )

        all_results.extend(batch_results)

        print(
            f"✅ Completed batch {batch_num}/{total_batches} - {len(all_results):,}/{total:,} companies processed"
        )

        # Call progress callback if provided
        if progress_callback:
            for result in batch_results:
                progress_callback(len(all_results), total, result)

    print(f"\n🎉 All {total:,} companies processed successfully!")
    return all_results

# Granular Confidence Metrics

This document explains the detailed confidence metrics provided by the Norwegian Company Categorization System to help you assess the reliability of categorization results.

## 🎯 Core Confidence Flags

### `categorized_by_naringskode` (0 or 1)
**Primary confidence indicator** - Shows whether the categorization was based on official Norwegian industry codes (næringskoder).

- **1**: Company was categorized using næringskoder ✅ **HIGH CONFIDENCE**
- **0**: Company was categorized using keyword matching ⚠️ **LOWER CONFIDENCE**

This is the most important flag as næringskoder-based categorization is significantly more reliable than keyword-based categorization.

### `confidence_score` (0.0 - 1.0)
**Numerical confidence rating** - Quantitative measure of categorization confidence.

| Score Range | Quality Level | Description |
|-------------|---------------|-------------|
| **0.8 - 1.0** | 🟢 **High** | Very reliable categorization |
| **0.5 - 0.8** | 🟡 **Medium** | Moderately reliable categorization |
| **0.0 - 0.5** | 🔴 **Low** | Use with caution |

## 📊 Detailed Metrics (Available with `include_metadata=True`)

### Method Indicators

#### `exact_code_match` (0 or 1)
- **1**: Direct match between company's næringskode and category mapping
- **0**: No exact code match found

#### `keyword_match` (0 or 1)
- **1**: Categorization based on keyword analysis of company data
- **0**: No keyword matches found

#### `method` (string)
Categorization method used:
- **"naringskode"**: Used official industry codes (best)
- **"keywords"**: Used keyword analysis (fallback)
- **"api_error"**: Company not found in registry

### Data Quality Metrics

#### `num_naringskoder` (integer)
Number of næringskoder (industry codes) found for the company.
- **Higher values** = More comprehensive industry data
- **0** = No industry codes available (forces keyword categorization)

#### `primary_naringskode` (string)
The main næringskode used for categorization (e.g., "47.11")

#### `matching_keywords` (string)
Keywords that triggered the categorization (when keyword method is used)

## 🔍 How to Interpret Results

### Highest Confidence Results
```csv
categorized_by_naringskode=1, exact_code_match=1, confidence_score=0.95
```
- ✅ **Use with high confidence**
- Based on official industry codes
- Exact match between code and category

### Medium Confidence Results
```csv
categorized_by_naringskode=1, keyword_match=1, confidence_score=0.75
```
- ⚠️ **Use with moderate confidence**
- Has næringskoder but required keyword analysis within the code description
- Still better than pure keyword matching

### Lower Confidence Results
```csv
categorized_by_naringskode=0, keyword_match=1, confidence_score=0.5
```
- 🔴 **Use with caution**
- No næringskoder available
- Based purely on keyword analysis of company name/activities

### Unreliable Results
```csv
categorized_by_naringskode=0, keyword_match=0, confidence_score=0.1
```
- ❌ **Consider manual review**
- No næringskoder and no keyword matches
- Likely categorized as "Uncategorized"

## 📈 Confidence Score Calculation

The confidence score is calculated based on:

1. **Categorization Method** (Primary Factor):
   - Exact næringskode match: 0.95
   - Keyword within næringskode: 0.75
   - Pure keyword match: 0.5-0.6
   - No matches: 0.1-0.2

2. **Company Selection Quality** (Adjustment):
   - Different company selected: -10% penalty
   - Ensures confidence reflects both categorization and company matching quality

## 🎯 Recommended Usage

### For Business Analysis
- **High confidence (≥0.8)**: Use directly for analysis
- **Medium confidence (0.5-0.8)**: Good for trends, consider manual spot-checks
- **Low confidence (<0.5)**: Manual review recommended

### For Automated Processing
```python
# Filter for high-confidence results
reliable_results = [
    r for r in results 
    if r['categorized_by_naringskode'] == 1 and r['confidence_score'] >= 0.8
]

# Separate for manual review
review_needed = [
    r for r in results 
    if r['categorized_by_naringskode'] == 0 or r['confidence_score'] < 0.5
]
```

## 📋 Output Formats

### Basic Output (Always Included)
```csv
company_name,company_category,revenue,categorized_by_naringskode,confidence_score
Equinor ASA,Energy & Environment,750000000000,1,0.95
```

### Full Metadata Output
```csv
company_name,company_category,revenue,subsegment,confidence,selected_company,org_number,
categorized_by_naringskode,num_naringskoder,exact_code_match,keyword_match,
confidence_score,primary_naringskode,matching_keywords,method
```

## 🔧 Quality Monitoring

The system provides aggregate statistics:

- **Næringskode Coverage**: Percentage categorized using official codes
- **Average Confidence Score**: Overall quality measure
- **Quality Distribution**: High/Medium/Low confidence breakdowns

This helps you understand the overall reliability of your dataset categorization.

---

**💡 Pro Tip**: Always prioritize companies with `categorized_by_naringskode=1` for critical business decisions, as these are based on official Norwegian government industry classifications. 
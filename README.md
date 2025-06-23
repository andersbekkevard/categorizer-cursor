# Norwegian Company Categorization System

A modular Python system for automatically categorizing Norwegian companies based on data from Brønnøysundregistrene (BRREG) using industry codes (næringskoder) and keyword analysis.

## 🚀 Quick Start

### 1. **Put your CSV file in the `input/` directory**
   - Required columns: `company_name`, `revenue` (or similar)
   - See `input/sample_companies.csv` for example format

### 2. **Run the categorization tool**
   ```bash
   python categorize.py
   ```

### 3. **Find results in the `output/` directory**
   - Output format: `company_name`, `company_category`, `revenue`

## 📁 Project Structure

```
company-categorizer/
├── 📂 input/                    # 📥 PUT YOUR CSV FILES HERE
│   ├── sample_companies.csv     # Example format
│   └── README.txt              # Usage instructions
├── 📂 output/                   # 📤 RESULTS SAVED HERE
│   └── .gitkeep               
├── 📂 src/                      # Source code modules
│   ├── config.py               # Product categories & settings
│   ├── utils.py                # Utility functions
│   ├── api_client.py           # BRREG API interaction
│   ├── company_matcher.py      # Intelligent company selection
│   ├── categorizer.py          # Core categorization logic
│   └── processor.py            # CSV processing pipeline
├── 📂 docs/                     # Documentation
│   ├── grouping.md             # Category definitions
│   └── confidence_metrics.md  # Granular confidence guide
├── categorize.py               # 🎯 MAIN SCRIPT TO RUN
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## ✨ Features

- **🎯 Smart Company Selection**: Prioritizes companies with næringskoder for accurate categorization
- **📊 CSV Input/Output**: Simple CSV workflow with revenue data preservation
- **🔍 Intelligent Matching**: Uses name similarity, company status, and business data
- **🏷️ 9 Product Categories**: Comprehensive mapping from Fashion to Government
- **⚡ Batch Processing**: Efficient processing with API rate limiting
- **📈 Granular Confidence Metrics**: Detailed flags showing categorization method and confidence
- **🎯 Quality Assessment**: Numerical confidence scores and reliability indicators

## 📋 Input Format

Your CSV file must contain these columns (case-insensitive):

| **Column Name Options** | **Description** |
|------------------------|-----------------|
| `company_name`, `company name`, `name`, `company` | Company name to categorize |
| `revenue`, `revenues`, `turnover`, `sales` | Company revenue data |

### Example Input CSV:
```csv
company_name,revenue
Equinor ASA,750000000000
DNB Bank,45000000000
Rema 1000,95000000000
```

**Note**: CSV delimiter is configurable in `src/config.py` (change `CSV_DELIMITER` from "," to ";" for semicolon-separated files)

## 📤 Output Format

Results are saved with these columns:

| **Column** | **Description** |
|------------|-----------------|
| `company_name` | Original company name |
| `company_category` | Assigned product category |
| `revenue` | Original revenue data |
| `categorized_by_naringskode` | **Key confidence flag** (1=næringskode, 0=keyword) |
| `confidence_score` | **Numerical confidence** (0.0-1.0) |

**Full metadata** (if requested):
- `subsegment` - Specific business subsegment
- `confidence` - Categorization confidence level (High/Medium/Low)
- `selected_company` - Actual company matched from BRREG
- `org_number` - Norwegian organization number
- `num_naringskoder` - Number of industry codes found
- `exact_code_match` - Direct code match flag (1/0)
- `keyword_match` - Keyword matching flag (1/0)
- `primary_naringskode` - Main industry code used
- `matching_keywords` - Keywords that triggered categorization
- `method` - Categorization method (naringskode/keywords)

## 🏷️ Product Categories

1. **Fashion & Personal Accessories**
2. **Healthcare & Pharmaceuticals** 
3. **Food & Beverages**
4. **Technology & Electronics**
5. **Home & Garden**
6. **Automotive & Transportation**
7. **Financial Services**
8. **Energy & Environment**
9. **Government & Public Sector**

## 🛠️ Technical Details

### **Installation**
```bash
# Install dependencies
pip install -r requirements.txt
```

### **Configuration**
You can customize CSV delimiter in `src/config.py`:
```python
# CSV Configuration
CSV_DELIMITER = ","  # Change to ";" for semicolon-separated files
```

### **Architecture**
- **Modular Design**: Clean separation of concerns across 6 modules
- **BRREG API Integration**: Fetches real-time Norwegian company data
- **Intelligent Selection**: Prioritizes companies with industry codes
- **Fallback Categorization**: Keyword-based when industry codes unavailable

### **Company Selection Logic**
1. **Primary**: Companies with næringskoder (industry codes)
2. **Secondary**: Name similarity scoring (60% weight)
3. **Tertiary**: Company status (active vs inactive) (25% weight)
4. **Quaternary**: Business data availability (15% weight)

## 📖 Usage Examples

### **Basic Processing**
```bash
python categorize.py
# Select your CSV file from the input/ directory
# Results saved automatically to output/
```

### **Programmatic Usage**
```python
from src.processor import process_csv_file

summary = process_csv_file(
    "input/my_companies.csv",
    include_metadata=True
)
```

## 🔧 Development

### **Code Structure**
- `src/config.py` - Categories and API configuration
- `src/api_client.py` - BRREG API interactions  
- `src/company_matcher.py` - Smart company selection
- `src/categorizer.py` - Core categorization logic
- `src/processor.py` - CSV processing pipeline
- `src/utils.py` - Helper functions

### **Key Functions**
- `categorize_company()` - Main categorization function
- `select_best_company_match()` - Intelligent company selection
- `process_csv_file()` - End-to-end CSV processing

## 📊 Performance

- **API Rate Limiting**: Built-in delays for BRREG API compliance
- **Batch Processing**: Optimized for large company lists
- **Progress Tracking**: Real-time processing status
- **Error Handling**: Graceful handling of API issues

## 🚨 Troubleshooting

### **Common Issues**
- **"No CSV files found"** → Add your CSV to `input/` directory
- **"Column not found"** → Check column names match expected format
- **"API errors"** → Check internet connection and try again

### **Column Name Variations**
The system accepts various column name formats:
- Company: `company_name`, `company name`, `name`, `company`
- Revenue: `revenue`, `revenues`, `turnover`, `sales`

---

**🇳🇴 Built for Norwegian Business Data** | **⚡ Powered by BRREG API** | **🎯 Intelligent Categorization** 
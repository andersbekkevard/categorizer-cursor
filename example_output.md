# Example Enhanced Output

## Basic Output (Always Included)
```csv
company_name,company_category,revenue,categorized_by_naringskode,confidence_score
Equinor ASA,Energy & Environment,750000000000,1,0.95
DNB Bank,Financial Services,45000000000,1,0.95
H&M,Fashion & Personal Accessories,2300000000,0,0.6
Lego,Toys & Games,1200000000,1,0.75
```

## Full Metadata Output
```csv
company_name,company_category,revenue,subsegment,confidence,selected_company,org_number,categorized_by_naringskode,num_naringskoder,exact_code_match,keyword_match,confidence_score,primary_naringskode,matching_keywords,method
Equinor ASA,Energy & Environment,750000000000,Oil & Gas,High,EQUINOR ASA,923609016,1,3,1,0,0.95,06.100,"",naringskode
DNB Bank,Financial Services,45000000000,Finance & Insurance,High,DNB BANK ASA,984851006,1,2,1,0,0.95,64.191,"",naringskode
H&M,Fashion & Personal Accessories,2300000000,Apparel,Medium,H&M GIACHINO,815493472,0,0,0,1,0.6,"","klær,clothing",keywords
```

## Summary Report Example
```
📈 Detailed Categorization Summary:
============================================================

📋 Categories:
   Energy & Environment: 1 (25.0%)
   Financial Services: 1 (25.0%)
   Fashion & Personal Accessories: 1 (25.0%)
   Toys & Games: 1 (25.0%)

🎯 Confidence Levels:
   High: 3 (75.0%)
   Medium: 1 (25.0%)

📊 Granular Confidence Metrics:
   📍 Categorized by Næringskode: 3/4 (75.0%)
   🎯 Exact Code Matches: 3/4 (75.0%)
   🔍 Keyword Matches: 1/4 (25.0%)
   📈 Average Confidence Score: 0.788

🔧 Categorization Methods:
   naringskode: 3 (75.0%)
   keywords: 1 (25.0%)

🌟 Quality Assessment:
   🟢 High Quality (≥0.8): 3 (75.0%)
   🟡 Medium Quality (0.5-0.8): 1 (25.0%)
   🔴 Low Quality (<0.5): 0 (0.0%)
``` 
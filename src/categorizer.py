"""
Company Categorization Logic

This module contains the core business logic for categorizing Norwegian companies
based on their næringskoder (industry codes) and keywords from company data.
"""

from .config import PRODUCT_CATEGORIES
from .utils import extract_naringskoder, format_naringskoder
from .company_matcher import fetch_company_by_name


def categorize_by_naringskode(naringskoder):
    """Categorize company based on næringskoder with improved matching"""
    best_match = None
    best_score = 0

    for category, info in PRODUCT_CATEGORIES.items():
        for naringskode in naringskoder:
            code = naringskode.get("kode", "")
            description = naringskode.get("beskrivelse", "").lower()

            # Check exact code matches first
            for prefix in info["codes"]:
                if code.startswith(prefix):
                    # Prioritize more specific matches (longer prefixes)
                    score = len(prefix)
                    if score > best_score:
                        best_match = (
                            category,
                            code,
                            naringskode.get("beskrivelse", ""),
                        )
                        best_score = score

            # Also check description for keyword matches
            for keyword in info["keywords"]:
                if keyword.lower() in description:
                    score = len(keyword) * 0.5  # Lower priority than code matches
                    if score > best_score:
                        best_match = (
                            category,
                            f"{code} (keyword: {keyword})",
                            naringskode.get("beskrivelse", ""),
                        )
                        best_score = score

    return best_match if best_match else ("Uncategorized", "", "")


def categorize_by_keywords(company_data):
    """Enhanced fallback categorization using keywords from multiple fields"""
    text_fields = []

    # Collect all text to analyze
    text_fields.append(company_data.get("navn", "").lower())

    aktivitet = company_data.get("aktivitet", [])
    if aktivitet:
        text_fields.extend([act.lower() for act in aktivitet])

    vedtekt = company_data.get("vedtektsfestetFormaal", [])
    if vedtekt:
        text_fields.extend([ved.lower() for ved in vedtekt])

    # Also check VAT descriptions if available
    mva_beskrivelser = company_data.get("frivilligMvaRegistrertBeskrivelser", [])
    if mva_beskrivelser:
        text_fields.extend([mva.lower() for mva in mva_beskrivelser])

    combined_text = " ".join(text_fields)

    # Find best keyword match with scoring
    best_match = None
    best_score = 0

    for category, info in PRODUCT_CATEGORIES.items():
        category_score = 0
        matched_keywords = []

        for keyword in info["keywords"]:
            if keyword.lower() in combined_text:
                category_score += len(keyword)
                matched_keywords.append(keyword)

        if category_score > best_score:
            best_match = (
                category,
                "keyword_match",
                f"Keywords: {', '.join(matched_keywords)}",
            )
            best_score = category_score

    return best_match if best_match else ("Uncategorized", "no_match", "")


def get_subsegment_suggestion(category, company_data):
    """Suggest subsegment based on company data"""
    if category not in PRODUCT_CATEGORIES:
        return ""

    subsegments = PRODUCT_CATEGORIES[category].get("subsegments", [])
    if not subsegments:
        return ""

    # Simple heuristic to suggest subsegment based on keywords
    text = f"{company_data.get('navn', '')} {' '.join(company_data.get('aktivitet', []))}".lower()

    # Category-specific subsegment logic
    if category == "Fashion & Personal Accessories":
        if any(word in text for word in ["barn", "child", "kid"]):
            return "Childrenswear"
        elif any(word in text for word in ["sko", "shoe", "footwear"]):
            return "Footwear"
        elif any(word in text for word in ["sport"]):
            return "Sportswear"
        elif any(word in text for word in ["brille", "eyewear", "glasses"]):
            return "Eyewear"
        elif any(word in text for word in ["veske", "bag", "luggage"]):
            return "Bags and Luggage"
        elif any(word in text for word in ["smykke", "jewelry", "jewellery"]):
            return "Jewellery"
        elif any(word in text for word in ["klokke", "watch"]):
            return "Traditional and Connected Watches"
        else:
            return "Apparel"

    elif category == "Services, Trade & Institutions":
        if any(word in text for word in ["bank", "finans", "finance"]):
            return "Finance & Insurance"
        elif any(word in text for word in ["handel", "retail", "butikk"]):
            return "Retail & Wholesale"
        elif any(word in text for word in ["IT", "software", "data", "tech"]):
            return "Information & Communications"
        elif any(word in text for word in ["bygg", "construction", "eiendom"]):
            return "Construction & Real Estate"
        elif any(word in text for word in ["hotell", "restaurant"]):
            return "Hotels & Restaurants"
        elif any(word in text for word in ["skole", "utdanning", "education"]):
            return "Education"
        elif any(word in text for word in ["transport", "logistikk"]):
            return "Transport & Storage"
        else:
            return "Business Services"

    # Return first subsegment as default
    return subsegments[0] if subsegments else ""


def categorize_company(company_name):
    """Main function to categorize a single company with enhanced granular confidence metrics"""
    print(f"Processing: {company_name}")

    # Fetch company data with intelligent selection
    company_data = fetch_company_by_name(company_name)

    if not company_data:
        return {
            "company_name": company_name,
            "category": "Not Found",
            "subsegment": "",
            "method": "api_error",
            "code": "",
            "description": "Company not found in registry",
            "org_number": "",
            "activities": [],
            "statutory_purposes": [],
            "confidence": "Low",
            "selected_company": "",
            # Granular confidence flags
            "categorized_by_naringskode": 0,
            "num_naringskoder": 0,
            "exact_code_match": 0,
            "keyword_match": 0,
            "confidence_score": 0.0,
            "primary_naringskode": "",
            "matching_keywords": "",
        }

    selected_company_name = company_data.get("navn", "Unknown")
    org_number = company_data.get("organisasjonsnummer", "")

    # Extract næringskoder
    naringskoder = extract_naringskoder(company_data)
    num_naringskoder = len(naringskoder)

    # Initialize granular metrics
    categorized_by_naringskode = 0
    exact_code_match = 0
    keyword_match = 0
    confidence_score = 0.0
    primary_naringskode = ""
    matching_keywords = ""

    # Try categorization by næringskode first
    if naringskoder:
        naringskode_result = categorize_by_naringskode(naringskoder)

        if naringskode_result[0] != "Uncategorized":
            category, code, description = naringskode_result
            method = "naringskode"
            confidence = "High"

            # Set granular flags
            categorized_by_naringskode = 1
            confidence_score = 0.9
            primary_naringskode = (
                code.split(" ")[0] if code else ""
            )  # Extract just the code part

            # Check if it was exact code match or keyword match within næringskode
            if "(keyword:" in code:
                keyword_match = 1
                confidence_score = 0.75  # Slightly lower for keyword within næringskode
                matching_keywords = (
                    code.split("keyword: ")[1].rstrip(")") if "keyword:" in code else ""
                )
            else:
                exact_code_match = 1
                confidence_score = 0.95  # Highest confidence for exact code match
        else:
            # Fallback to keyword matching
            keyword_result = categorize_by_keywords(company_data)
            category, code, description = keyword_result
            method = "keywords"
            confidence = "Medium" if code != "no_match" else "Low"

            # Set granular flags for keyword fallback
            keyword_match = 1 if code != "no_match" else 0
            confidence_score = 0.6 if code != "no_match" else 0.2
            if "Keywords:" in description:
                matching_keywords = description.replace("Keywords: ", "")
    else:
        # No næringskoder available, use keyword matching
        keyword_result = categorize_by_keywords(company_data)
        category, code, description = keyword_result
        method = "keywords"
        confidence = "Medium" if code != "no_match" else "Low"

        # Set granular flags for pure keyword matching
        keyword_match = 1 if code != "no_match" else 0
        confidence_score = 0.5 if code != "no_match" else 0.1
        if "Keywords:" in description:
            matching_keywords = description.replace("Keywords: ", "")

    # Additional confidence adjustments based on company selection quality
    # (if different company was selected, reduce confidence slightly)
    if selected_company_name.lower() != company_name.lower():
        confidence_score *= 0.9  # Reduce by 10% for company name mismatch

    # Get subsegment suggestion
    subsegment = get_subsegment_suggestion(category, company_data)

    return {
        "company_name": company_name,
        "category": category,
        "subsegment": subsegment,
        "method": method,
        "code": code,
        "description": description,
        "org_number": org_number,
        "activities": company_data.get("aktivitet", []),
        "statutory_purposes": company_data.get("vedtektsfestetFormaal", []),
        "all_naringskoder": format_naringskoder(naringskoder),
        "confidence": confidence,
        "selected_company": selected_company_name,
        # Enhanced granular confidence metrics
        "categorized_by_naringskode": categorized_by_naringskode,
        "num_naringskoder": num_naringskoder,
        "exact_code_match": exact_code_match,
        "keyword_match": keyword_match,
        "confidence_score": round(confidence_score, 3),
        "primary_naringskode": primary_naringskode,
        "matching_keywords": matching_keywords,
    }

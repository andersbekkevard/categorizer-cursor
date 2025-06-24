"""
Configuration file for Norwegian Company Categorization System

This module contains product category mappings based on Norwegian industry codes
(næringskoder) and keywords for automated company categorization.
"""

import os
import platform

# BRREG API Configuration
BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


# SSL Configuration - automatically detect Windows and virtual environments
def _detect_ssl_issues():
    """Detect if we're in an environment that commonly has SSL issues"""
    # Check for Windows
    is_windows = platform.system().lower() == "windows"

    # Check for virtual desktop indicators
    virtual_indicators = [
        "SESSIONNAME" in os.environ,  # Windows Terminal Server
        "RDS" in os.environ.get("COMPUTERNAME", ""),  # Remote Desktop
        "CITRIX" in os.environ.get("COMPUTERNAME", ""),  # Citrix
        "VDI" in os.environ.get("COMPUTERNAME", ""),  # VDI
    ]

    is_virtual_desktop = any(virtual_indicators)

    # Default to False for SSL verification if on Windows virtual desktop
    if is_windows and is_virtual_desktop:
        print(
            "🖥️  Windows virtual desktop detected - SSL verification disabled by default"
        )
        return False

    return True


# SSL Configuration - set to False for virtual desktop environments with certificate issues
SSL_VERIFY = os.getenv("SSL_VERIFY", str(_detect_ssl_issues())).lower() == "true"

# Print SSL configuration on import (for debugging)
if not SSL_VERIFY:
    print(
        "⚠️  SSL verification is disabled - API calls will bypass certificate validation"
    )

# CSV Configuration
CSV_DELIMITER = ","  # Change to ";" for semicolon-separated files

# Category ID mapping (1-9)
CATEGORY_IDS = {
    "Fashion & Personal Accessories": 1,
    "Beauty, Health & Well-Being": 2,
    "Consumer Tech & Appliances": 3,
    "Food, Grocery & Pet": 4,
    "Home & Living": 5,
    "Toys, Games & Leisure Goods": 6,
    "Industrial & Manufacturing Supplies": 7,
    "Energy, Utilities & Recycling": 8,
    "Services, Trade & Institutions": 9,
    # Special categories
    "Uncategorized": 0,
    "Not Found": 0,
}

# Product category mapping based on grouping.md categories and næringskoder ranges
PRODUCT_CATEGORIES = {
    "Fashion & Personal Accessories": {
        "codes": [
            "14",
            "15.1",
            "32.1",
            "46.41",
            "46.42",
            "47.71",
            "47.72",
            "47.77",
            "95.25",
        ],
        "keywords": [
            "klær",
            "clothing",
            "apparel",
            "fashion",
            "mote",
            "sko",
            "shoes",
            "vesker",
            "bags",
            "smykker",
            "jewelry",
            "klokker",
            "watches",
            "briller",
            "eyewear",
            "accessories",
            "tilbehør",
        ],
        "subsegments": [
            "Apparel and Footwear",
            "Apparel",
            "Childrenswear",
            "Footwear",
            "Sportswear",
            "Eyewear",
            "Bags and Luggage",
            "Jewellery",
            "Traditional and Connected Watches",
            "Personal Accessories",
        ],
    },
    "Beauty, Health & Well-Being": {
        "codes": [
            "20.4",
            "21",
            "26.6",
            "32.5",
            "46.45",
            "46.46",
            "47.75",
            "86",
            "87",
            "88",
        ],
        "keywords": [
            "skjønnhet",
            "beauty",
            "kosmetikk",
            "cosmetics",
            "helse",
            "health",
            "medisin",
            "medical",
            "pharmaceutical",
            "farmasøytisk",
            "helsevesen",
            "healthcare",
            "wellness",
            "velvære",
        ],
        "subsegments": [
            "Beauty and Personal Care",
            "Consumer Health",
            "Pharmaceuticals and Medical Equipment",
        ],
    },
    "Consumer Tech & Appliances": {
        "codes": [
            "26.1",
            "26.2",
            "26.3",
            "26.4",
            "26.8",
            "27",
            "28.2",
            "46.43",
            "46.51",
            "47.5",
            "95.1",
            "95.2",
        ],
        "keywords": [
            "elektronikk",
            "electronics",
            "teknologi",
            "technology",
            "datamaskiner",
            "computers",
            "telefoner",
            "phones",
            "TV",
            "radio",
            "appliances",
            "hvitevarer",
            "kjøkken",
            "kitchen",
        ],
        "subsegments": ["Consumer Electronics", "Consumer Appliances"],
    },
    "Food, Grocery & Pet": {
        "codes": [
            "01",
            "02",
            "03",
            "10",
            "11",
            "12",
            "46.1",
            "46.2",
            "46.3",
            "47.1",
            "47.2",
            "47.9",
        ],
        "keywords": [
            "mat",
            "food",
            "matvarer",
            "grocery",
            "landbruk",
            "agriculture",
            "fiske",
            "fishing",
            "kjæledyr",
            "pet",
            "dyrefôr",
            "tobakk",
            "tobacco",
            "drikke",
            "beverage",
        ],
        "subsegments": ["Staple Foods", "Pet Care", "Tobacco Products", "Agriculture"],
    },
    "Home & Living": {
        "codes": [
            "16",
            "31",
            "32.9",
            "43.3",
            "46.47",
            "46.49",
            "47.52",
            "47.53",
            "47.54",
            "47.59",
        ],
        "keywords": [
            "møbler",
            "furniture",
            "hjem",
            "home",
            "bolig",
            "living",
            "interiør",
            "interior",
            "hage",
            "garden",
            "renovering",
            "renovation",
            "luksus",
            "luxury",
            "innredning",
            "furnishing",
        ],
        "subsegments": [
            "Home Improvement",
            "Gardening",
            "Homewares & Home Furnishings",
            "Household Goods",
            "Luxury Goods",
        ],
    },
    "Toys, Games & Leisure Goods": {
        "codes": ["32.4", "32.3", "46.49", "47.65", "93.1"],
        "keywords": [
            "leker",
            "toys",
            "spill",
            "games",
            "gaming",
            "sport",
            "sports",
            "fritid",
            "leisure",
            "hobby",
        ],
        "subsegments": ["Toys and Games", "Sports Goods"],
    },
    "Industrial & Manufacturing Supplies": {
        "codes": [
            "19",
            "20",
            "22",
            "23",
            "24",
            "25",
            "28",
            "29",
            "30",
            "33",
            "46.6",
            "46.7",
        ],
        "keywords": [
            "industri",
            "industrial",
            "produksjon",
            "manufacturing",
            "kjemisk",
            "chemical",
            "metall",
            "metal",
            "maskin",
            "machinery",
            "utstyr",
            "equipment",
            "råvarer",
            "materials",
        ],
        "subsegments": [
            "Chemical Products",
            "Metal Products",
            "Non-metallic Mineral Products",
            "Machinery and Equipment",
            "Transport Equipment",
            "Paper and Printing",
            "Building and Construction Materials",
            "Professional Equipment",
        ],
    },
    "Energy, Utilities & Recycling": {
        "codes": ["35", "36", "37", "38", "39", "05", "06", "07", "08", "09"],
        "keywords": [
            "energi",
            "energy",
            "elektrisitet",
            "electricity",
            "olje",
            "oil",
            "gass",
            "gas",
            "vann",
            "water",
            "avfall",
            "waste",
            "resirkulering",
            "recycling",
            "miljø",
            "environmental",
        ],
        "subsegments": ["Energy", "Utilities and Recycling"],
    },
    "Services, Trade & Institutions": {
        "codes": [
            "45",
            "46",
            "47",
            "49",
            "50",
            "51",
            "52",
            "53",
            "58",
            "59",
            "60",
            "61",
            "62",
            "63",
            "64",
            "65",
            "66",
            "68",
            "69",
            "70",
            "71",
            "72",
            "73",
            "74",
            "75",
            "77",
            "78",
            "79",
            "80",
            "81",
            "82",
            "84",
            "85",
            "90",
            "91",
            "92",
            "93",
            "94",
            "95",
            "96",
            "97",
            "98",
            "99",
        ],
        "keywords": [
            "handel",
            "trade",
            "service",
            "tjeneste",
            "bank",
            "finans",
            "finance",
            "forsikring",
            "insurance",
            "eiendom",
            "real estate",
            "rådgivning",
            "consulting",
            "IT",
            "software",
            "utdanning",
            "education",
            "helse",
            "health",
            "kultur",
            "culture",
            "transport",
            "logistics",
            "hotell",
            "restaurant",
        ],
        "subsegments": [
            "Retail & Wholesale",
            "Information & Communications",
            "Publishing & Printing",
            "Finance & Insurance",
            "Real Estate",
            "Consulting & Business Services",
            "Education",
            "Health & Social Services",
            "Arts & Culture",
            "Transportation & Storage",
            "Hotels & Restaurants",
            "Business Services",
            "Construction & Real Estate",
        ],
    },
}

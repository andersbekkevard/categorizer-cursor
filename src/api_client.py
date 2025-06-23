"""
BRREG API Client for Norwegian Company Data

This module handles all interactions with the Brønnøysundregistrene API
for fetching company data from the Norwegian business registry.
"""

import requests
from urllib.parse import urlencode
from .config import BASE_URL


def fetch_companies_by_name(company_name, size=10):
    """
    Fetch companies by name from BRREG API

    Args:
        company_name (str): Name of the company to search for
        size (int): Maximum number of results to return (default: 10)

    Returns:
        list: List of company data dictionaries, or empty list if error
    """
    params = {
        "navn": company_name,
        "size": size,  # Get up to 10 matches for better selection
    }

    url = f"{BASE_URL}?{urlencode(params)}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        companies = data.get("_embedded", {}).get("enheter", [])
        return companies

    except Exception as e:
        print(f"Error fetching {company_name}: {e}")
        return []

"""
BRREG API Client for Norwegian Company Data

This module handles all interactions with the Brønnøysundregistrene API
for fetching company data from the Norwegian business registry.
"""

import requests
import certifi
import ssl
from urllib.parse import urlencode
from .config import BASE_URL, SSL_VERIFY


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
        # Use SSL verification based on configuration
        if SSL_VERIFY:
            response = requests.get(
                url, timeout=10, verify=certifi.where()  # Use certifi bundle explicitly
            )
        else:
            # Disable SSL verification for environments with certificate issues
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, timeout=10, verify=False)

        response.raise_for_status()
        data = response.json()

        companies = data.get("_embedded", {}).get("enheter", [])
        return companies

    except requests.exceptions.SSLError as ssl_error:
        print(f"SSL Error for {company_name}: {ssl_error}")
        print("Trying without SSL verification...")

        # Retry without SSL verification as fallback
        try:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()
            companies = data.get("_embedded", {}).get("enheter", [])
            return companies
        except Exception as fallback_error:
            print(f"Fallback also failed for {company_name}: {fallback_error}")
            return []

    except Exception as e:
        print(f"Error fetching {company_name}: {e}")
        return []

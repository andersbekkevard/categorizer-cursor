"""
Utility functions for the Norwegian Company Categorization System

This module contains utility functions for string similarity, company validation,
and other helper functions used throughout the categorization system.
"""

from difflib import SequenceMatcher


def similarity_score(str1, str2):
    """Calculate similarity score between two strings"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def has_naringskoder(company_data):
    """Check if company has any næringskoder"""
    for i in range(1, 4):
        nk = company_data.get(f"naeringskode{i}")
        if nk and nk.get("kode"):
            return True
    return False


def is_company_active(company_data):
    """Check if company appears to be active"""
    # Check for inactive indicators
    if company_data.get("konkurs"):  # Bankruptcy
        return False
    if company_data.get("underAvvikling"):  # Under liquidation
        return False
    if company_data.get(
        "underTvangsavviklingEllerTvangsopplosning"
    ):  # Forced liquidation
        return False
    if company_data.get("nedleggelsesdato"):  # Closure date
        return False

    return True


def extract_naringskoder(company_data):
    """Extract all næringskoder from company data"""
    naringskoder = []
    for i in range(1, 4):
        nk = company_data.get(f"naeringskode{i}")
        if nk:
            naringskoder.append(nk)
    return naringskoder


def format_naringskoder(naringskoder):
    """Format næringskoder for display"""
    return [f"{nk.get('kode', '')}: {nk.get('beskrivelse', '')}" for nk in naringskoder]

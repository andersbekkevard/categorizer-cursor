"""
Company Matching and Selection Logic

This module contains the intelligent logic for selecting the best company match
from multiple BRREG API results, prioritizing companies with næringskoder for
better categorization outcomes.
"""

from .utils import similarity_score, has_naringskoder, is_company_active
from .api_client import fetch_companies_by_name


def get_company_relevance_score(company_data, search_name):
    """Calculate relevance score for a company match (næringskoder handled separately)"""
    score = 0.0
    company_name = company_data.get("navn", "")

    # 1. Name similarity (60% weight - increased since næringskoder removed)
    name_similarity = similarity_score(search_name, company_name)
    score += name_similarity * 0.6

    # 2. Company is active (25% weight - increased)
    if is_company_active(company_data):
        score += 0.25

    # 3. Has business activities or statutory purposes (10% weight)
    if company_data.get("aktivitet") or company_data.get("vedtektsfestetFormaal"):
        score += 0.10

    # 4. Company type bonus (5% weight)
    org_form = company_data.get("organisasjonsform", {})
    org_code = org_form.get("kode", "") if org_form else ""

    # Prefer main business entities over subsidiaries/branches
    if org_code in ["AS", "ASA", "ENK", "DA", "BA", "SA"]:
        score += 0.05
    elif org_code in ["NUF", "FIL"]:  # Foreign branches might be less relevant
        score -= 0.02

    return score


def select_best_company_match(companies, search_name):
    """Select the best company match from multiple alternatives, prioritizing categorizable companies"""
    if not companies:
        return None

    if len(companies) == 1:
        return companies[0]

    print(f"    Found {len(companies)} potential matches, evaluating...")

    # First, separate companies with and without næringskoder
    companies_with_nk = [c for c in companies if has_naringskoder(c)]
    companies_without_nk = [c for c in companies if not has_naringskoder(c)]

    print(f"    Companies with næringskoder: {len(companies_with_nk)}")
    print(f"    Companies without næringskoder: {len(companies_without_nk)}")

    # PRIORITY RULE: If exactly one company has næringskoder, always choose it
    if len(companies_with_nk) == 1:
        selected_company = companies_with_nk[0]
        print(
            f"    ✓ SELECTED (only company with næringskoder): {selected_company.get('navn', 'N/A')}"
        )
        return selected_company

    # If multiple companies have næringskoder, score only those
    if len(companies_with_nk) > 1:
        print(f"    Multiple companies with næringskoder found, scoring among them...")
        companies_to_score = companies_with_nk
    # If NO companies have næringskoder, fall back to scoring all
    elif len(companies_with_nk) == 0:
        print(
            f"    ⚠️  No companies have næringskoder, will result in uncategorizable match"
        )
        companies_to_score = companies
    else:
        companies_to_score = companies

    # Score the selected group of companies
    scored_companies = []
    for company in companies_to_score:
        score = get_company_relevance_score(company, search_name)
        scored_companies.append((score, company))

        # Debug info
        company_name = company.get("navn", "N/A")
        org_num = company.get("organisasjonsnummer", "N/A")
        has_nk = "✓" if has_naringskoder(company) else "✗"
        is_active = "✓" if is_company_active(company) else "✗"
        print(
            f"      {score:.3f}: {company_name} (Org: {org_num}) [NK: {has_nk}, Active: {is_active}]"
        )

    # Sort by score (highest first)
    scored_companies.sort(key=lambda x: x[0], reverse=True)
    best_score, best_company = scored_companies[0]

    # Check if there are very close scores (within 0.1) for additional tie-breaking
    close_matches = [sc for sc in scored_companies if abs(sc[0] - best_score) <= 0.1]

    if len(close_matches) > 1:
        print(f"    {len(close_matches)} companies have similar scores...")

        # If we're already within companies with næringskoder, use other criteria
        if len(companies_with_nk) > 1:
            # Among companies with næringskoder, prefer active ones, then by name similarity
            active_matches = [sc for sc in close_matches if is_company_active(sc[1])]
            if active_matches:
                best_company = active_matches[0][1]
                print(f"    Selected active company: {best_company.get('navn', 'N/A')}")
            else:
                print(f"    Selected highest scored: {best_company.get('navn', 'N/A')}")
        else:
            # We're in the fallback scenario - no companies have næringskoder
            print(
                f"    Selected highest scored (no næringskoder available): {best_company.get('navn', 'N/A')}"
            )
    else:
        selection_reason = (
            "with næringskoder"
            if has_naringskoder(best_company)
            else "without næringskoder (uncategorizable)"
        )
        print(
            f"    ✓ SELECTED ({selection_reason}): {best_company.get('navn', 'N/A')} (score: {best_score:.3f})"
        )

    return best_company


def fetch_company_by_name(company_name):
    """Fetch company data by name with intelligent selection"""
    companies = fetch_companies_by_name(company_name)

    if not companies:
        return None

    # Use intelligent selection to pick the best match
    selected_company = select_best_company_match(companies, company_name)

    # Return both the selected company and search metadata
    if selected_company:
        search_metadata = {
            "total_matches": len(companies),
            "companies_with_naringskoder": len(
                [c for c in companies if has_naringskoder(c)]
            ),
            "exact_name_match": any(
                c.get("navn", "").lower() == company_name.lower() for c in companies
            ),
            "selected_company_has_naringskoder": has_naringskoder(selected_company),
        }
        return selected_company, search_metadata

    return None

"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "fedex-office" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 24-scenario row).
MIX = {"easy": 5, "boundary_twin": 6, "multi_rule": 4, "hidden_clause": 2, "distractor": 2, "refusal": 2, "flag": 3}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. The handbook has no
# overnight-stop rule, so no overnight scenario is required.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "multi_traveller": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "first", "business", "coach", "economy", "premium", "vice", "president", "vp", "senior", "director", "managing",
    "md", "manager", "supervisor", "spouse", "husband", "wife", "family", "dependent", "guest", "supplier", "vendor",
    "consultant", "personal", "vacation", "weekend", "sister", "medical", "surgery", "physician", "size", "certified",
    "certification", "exception", "policy", "loyalty", "status", "miles", "airline", "connection", "connecting",
    "layover", "nonstop", "stop", "delay", "savings", "international", "domestic", "canada", "vancouver", "toronto",
    "hawaii", "honolulu", "refundable", "advance", "notice", "inflight", "meeting", "colleague", "event", "sponsored",
    "pays", "pay", "difference", "board", "united", "global", "agency",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Passenger, contract.Purpose, contract.SignOffSubject, contract.JobLevel, contract.Routing]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section).
MAX_PASS_ALWAYS_FLAG = 2
MAX_PASS_ALWAYS_LOWEST = 7

# Hand-built duration cases beyond the automatic both-sides tests: (rule, outbound scheduled minutes per
# flight, layovers, expected True / False / None for unclear).
DURATION_CASES = [
    ("international-business", [361], [], True),
    ("international-business", [360], [], False),
    ("international-business", [361, 60], [90], True),  # one flight alone over: over on every reading
    ("international-business", [90, 400], [200], True),
    ("international-business", [180, 180], [120], False),  # flights total 360, ground time never counts
    ("international-business", [150, 200], [300], False),
    ("international-business", [180, 181], [60], None),  # flights total 361, none alone over: unclear
    ("international-business", [235, 205], [75], None),
    ("international-business", [100, 150, 200], [60, 60], None),
    ("international-business", [100, 100, 160], [60, 60], False),
]

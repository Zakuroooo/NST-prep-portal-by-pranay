"""
bootstrap_companies.py

Queries the raw_scraped_data collection for distinct companySlugs.
Generates a JSON file with valid stub representations of each company to pass schema rules.
Supports manual override dicts for correct capitalizations and categories.
"""

import json
import logging
import sys
import argparse
from typing import List, Dict, Any
from pathlib import Path
from config.db import get_db
import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("bootstrapper")

SEED_FILE = Path(__file__).parent / "company_seed_review.json"

# Manual Overrides for Proper Nouns / Acronyms
NAME_OVERRIDES = {
    "ibm": "IBM",
    "vmware": "VMware",
    "paypal": "PayPal",
    "tcs": "TCS",
    "sap": "SAP",
    "jp-morgan": "JPMorgan Chase",
    "jpmorgan": "JPMorgan Chase",
    "jp-morgan-chase": "JPMorgan Chase",
    "morgan-stanley": "Morgan Stanley",
    "goldman-sachs": "Goldman Sachs",
    "bny-mellon": "BNY Mellon",
    "hsbc": "HSBC",
    "cisco": "Cisco",
    "linkedin": "LinkedIn",
    "youtube": "YouTube",
    "bookingcom": "Booking.com",
    "booking": "Booking.com",
    "github": "GitHub",
    "salesforce": "Salesforce",
    "walmart": "Walmart",
    "wipro": "Wipro",
    "infosys": "Infosys",
    "hcl": "HCL",
    "cognizant": "Cognizant",
    "zoho": "Zoho"
}

# Categorization rules
# Valid values: maang, product, service, startup, bfsi, other
CATEGORY_MAPPINGS = {
    # MAANG / Big Tech
    "maang": ["google", "amazon", "apple", "meta", "facebook", "netflix", "microsoft"],
    # BFSI (Banking, Financial Services, Insurance)
    "bfsi": [
        "goldman-sachs", "jpmorgan", "jp-morgan", "jp-morgan-chase", "morgan-stanley",
        "bny-mellon", "hsbc", "citi", "citibank", "barclays", "deutsche-bank", 
        "visa", "mastercard", "american-express", "amex", "capital-one", "bloomberg",
        "fidelity", "two-sigma", "citadel", "wells-fargo", "bank-of-america"
    ],
    # Service / Consulting
    "service": ["tcs", "infosys", "wipro", "cognizant", "hcl", "accenture", "capgemini", "deloitte", "ibm", "tech-mahindra"],
    # Major Product/SaaS
    "product": [
        "adobe", "atlassian", "salesforce", "cisco", "oracle", "sap", "vmware", 
        "linkedin", "twitter", "uber", "lyft", "airbnb", "doordash", "paypal", 
        "stripe", "square", "snowflake", "databricks", "palantir", "intuit", "zoom",
        "bookingcom", "booking", "expedia", "walmart", "target", "samsung", "nvidia", "intel", "amd"
    ]
}

def generate_stubs():
    db = get_db()
    slugs = db.raw_scraped_data.distinct("companySlug")
    logger.info(f"Found {len(slugs)} distinct company slugs in raw data.")
    
    # Reverse the category mapping for fast lookup O(1)
    slug_to_category = {}
    for cat, slug_list in CATEGORY_MAPPINGS.items():
        for s in slug_list:
            slug_to_category[s] = cat

    stubs = []
    
    for slug in sorted(slugs):
        # Determine name
        if slug in NAME_OVERRIDES:
            name = NAME_OVERRIDES[slug]
        else:
            # Title case by default, replacing hyphens with spaces
            name = slug.replace("-", " ").title()
            
        # Determine category
        category = slug_to_category.get(slug, "other")
        
        stub = {
            "slug": slug,
            "name": name,
            "category": category,
            "isSeeded": True,
            "createdAt": str(datetime.datetime.utcnow()),
            "updatedAt": str(datetime.datetime.utcnow())
        }
        stubs.append(stub)
        
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(stubs, f, indent=4)
        
    logger.info(f"Generated seed file with {len(stubs)} records at {SEED_FILE}")
    logger.info("Please review the JSON file, then run with --insert to populate the database.")

def insert_stubs():
    if not SEED_FILE.exists():
        logger.error(f"Seed file not found: {SEED_FILE}. Run with --generate first.")
        return
        
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        stubs = json.load(f)
        
    db = get_db()
    
    # Format strings back to proper datetime objects for MongoDB
    for stub in stubs:
        if "createdAt" in stub:
            stub["createdAt"] = datetime.datetime.fromisoformat(stub["createdAt"])
        if "updatedAt" in stub:
            stub["updatedAt"] = datetime.datetime.fromisoformat(stub["updatedAt"])
    
    from pymongo.errors import BulkWriteError
    
    try:
        # Ensure a unique index on slug prevents duplicates
        db.companies.create_index("slug", unique=True)
        
        result = db.companies.insert_many(stubs, ordered=False)
        logger.info(f"Successfully inserted {len(result.inserted_ids)} companies.")
    except BulkWriteError as bwe:
        inserted = bwe.details['nInserted']
        logger.info(f"Inserted {inserted} new companies. Ignored {len(bwe.details['writeErrors'])} duplicates.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--insert", action="store_true")
    args = parser.parse_args()
    
    if args.generate:
        generate_stubs()
    elif args.insert:
        insert_stubs()
    else:
        logger.warning("Specify either --generate or --insert")

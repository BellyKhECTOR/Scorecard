#!/usr/bin/env python3
"""Initialise topic seed data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from src.database import SessionLocal
from src.models import Topic

TOPICS = [
    ("governance", "Governance", "Corporate governance and board matters"),
    ("aum-fees", "AUM & Fees", "Assets under management and fee structures"),
    ("investment-process", "Investment Process", "Investment decision-making and portfolio management"),
    ("esg", "ESG", "Environmental, social and governance integration"),
    ("climate", "Climate", "Climate risk and net zero commitments"),
    ("proxy-voting", "Proxy Voting", "Shareholder voting and engagement"),
    ("operations", "Operations", "Operational infrastructure and processes"),
    ("valuation", "Valuation", "Valuation policies and practices"),
    ("risk", "Risk", "Risk management frameworks"),
    ("business-continuity", "Business Continuity", "BCP and disaster recovery"),
    ("privacy-cyber", "Privacy & Cyber", "Data privacy and cybersecurity"),
    ("regulatory", "Regulatory", "Regulatory compliance and licensing"),
    ("compliance", "Compliance", "Compliance policies and monitoring"),
    ("ownership", "Ownership", "Ownership structure and related parties"),
    ("people", "People", "Human resources and key personnel"),
    ("financial-sustainability", "Financial Sustainability", "Financial health and sustainability"),
    ("trading", "Trading", "Trading practices and best execution"),
    ("reporting", "Reporting", "Client reporting and transparency"),
    ("performance", "Performance", "Performance measurement and attribution"),
    ("other", "Other", "Topics not covered elsewhere"),
]


def main() -> int:
    print("Initialising topics...")
    db = SessionLocal()
    created = 0
    updated = 0
    try:
        for slug, display_name, description in TOPICS:
            existing = db.execute(select(Topic).where(Topic.slug == slug)).scalar_one_or_none()
            if existing:
                existing.display_name = display_name
                existing.description = description
                updated += 1
            else:
                db.add(Topic(slug=slug, display_name=display_name, description=description))
                created += 1
        db.commit()
        print(f"SUCCESS: {created} topics created, {updated} updated.")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"FAILURE: {exc}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

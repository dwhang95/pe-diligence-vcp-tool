"""
tier.py — Pricing tier logic for PE Ops Tool Suite.

Tiers:
  standard — Sonnet only, max 3 briefs/session, watermark on Word export
  premium  — Opus available, unlimited briefs, clean export, all data sources

Password is read from PREMIUM_PASSWORD env var.
Replace with Stripe later.
"""

import os
from typing import Literal

TierType = Literal["standard", "premium"]

STANDARD_BRIEF_LIMIT = 3

# Sources available per tier
STANDARD_SOURCES = {"sec_edgar", "yahoo_finance", "bls", "news"}
PREMIUM_ONLY_SOURCES = {"damodaran", "naver_finance"}
ALL_SOURCES = STANDARD_SOURCES | PREMIUM_ONLY_SOURCES

# Sections that run on Opus in Premium mode
PREMIUM_MODEL_SECTIONS = {"exec_summary", "risk_flags", "value_creation"}

STANDARD_MODEL = "claude-sonnet-4-6"
PREMIUM_MODEL  = "claude-opus-4-6"

WATERMARK_TEXT = "Generated with PE Ops Tool — Standard Tier"


def get_premium_password() -> str:
    return os.environ.get("PREMIUM_PASSWORD", "pe-ops-premium-2026")


def check_premium_password(password: str) -> bool:
    return bool(password.strip()) and password.strip() == get_premium_password()


def is_source_locked(source_key: str, tier: TierType) -> bool:
    return source_key in PREMIUM_ONLY_SOURCES and tier == "standard"


def get_model_for_section(section_key: str, model_mode: str) -> str:
    """Return the model ID to use for a given section and mode."""
    if model_mode == "premium" and section_key in PREMIUM_MODEL_SECTIONS:
        return PREMIUM_MODEL
    return STANDARD_MODEL


def get_research_model(model_mode: str) -> str:
    """Research agent also uses Opus in premium mode."""
    return PREMIUM_MODEL if model_mode == "premium" else STANDARD_MODEL

from typing import Dict, Optional
import difflib
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

from os import environ
from dotenv import load_dotenv
load_dotenv()
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# SPARE_PARTS_CSV_PATH=test/sku_register_full.csv
CSV_ENV = environ.get("SPARE_PARTS_CSV_PATH", "tests/data/sku_register_full.csv")

csv_path = Path(CSV_ENV)
if not csv_path.is_absolute():
    csv_path = PROJECT_ROOT / csv_path

CATALOG_CSV_PATH = csv_path

try:
    logger.debug("Loading spare parts catalog from %r", str(CATALOG_CSV_PATH))
    CATALOG_DF = pd.read_csv(CATALOG_CSV_PATH)
    logger.info(
        "Spare parts catalog loaded: path=%r, rows=%d, columns=%s",
        str(CATALOG_CSV_PATH),
        len(CATALOG_DF),
        list(CATALOG_DF.columns),
    )
except Exception as e:
    logger.exception(
        "Failed to load spare parts catalog from %r: %s",
        str(CATALOG_CSV_PATH),
        e,
    )
    CATALOG_DF = pd.DataFrame()

def _string_similarity(a: str, b: str) -> float:
    """
    Simple string similarity based on difflib.SequenceMatcher.
    Returns a number between 0 and 1.
    """
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_part_by_term(term: str) -> Optional[Dict[str, object]]:
    """
    Looking in CATALOG_DF for a row whose 'name' is most similar to the term.
    Returns a dict with sku, name, score or None if nothing suitable is found.
    """
    logger.debug("find_best_part_by_term: term=%r", term)

    if CATALOG_DF is None or CATALOG_DF.empty:
        logger.warning("find_best_part_by_term: CATALOG_DF is empty or not loaded")
        return None

    if "name" not in CATALOG_DF.columns:
        logger.warning(
            "find_best_part_by_term: 'name' column not found in CATALOG_DF. Columns: %s",
            list(CATALOG_DF.columns),
        )
        return None

    logger.debug(
        "find_best_part_by_term: catalog size=%d, first rows=%s",
        len(CATALOG_DF),
        CATALOG_DF.head().to_dict(orient="records"),
    )

    similarities = CATALOG_DF["name"].astype(str).apply(
        lambda x: _string_similarity(term, x)
    )

    best_idx = similarities.idxmax()
    best_score = float(similarities.loc[best_idx])
    row = CATALOG_DF.loc[best_idx]

    logger.debug(
        "find_best_part_by_term: best_idx=%s, best_name=%r, best_score=%.3f",
        best_idx,
        row.get("name"),
        best_score,
    )

    if best_score < 0.5:
        logger.info(
            "find_best_part_by_term: best_score %.3f below threshold for term=%r",
            best_score,
            term,
        )
        return None

    sku = row.get("sku") if "sku" in CATALOG_DF.columns else None
    name = row.get("name") if "name" in CATALOG_DF.columns else None

    result = {
        "sku": sku,
        "name": name,
        "score": best_score,
    }
    logger.debug("find_best_part_by_term: result=%s", result)
    return result

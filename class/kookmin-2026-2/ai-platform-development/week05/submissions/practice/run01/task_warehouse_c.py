"""DAG task: aggregate warehouse C.

Reads practice/data/warehouse-c.md via warehouse_lib and writes the
per-warehouse intermediate file warehouse_c.json in run01/.

This task is independent of warehouse A and B — it only depends on the
shared warehouse_lib module, so the DAG runner can execute A, B and C in
parallel.
"""
from __future__ import annotations

import json
from pathlib import Path

import warehouse_lib

# run01/ -> submissions/practice -> week05; data lives at week05/practice/data.
_RUN01_DIR = Path(__file__).resolve().parent
_WEEK05_DIR = _RUN01_DIR.parents[2]
DATA_FILE = _WEEK05_DIR / "practice" / "data" / "warehouse-c.md"
OUTPUT_FILE = _RUN01_DIR / "warehouse_c.json"

WAREHOUSE_ID = "C"


def run() -> dict:
    """Aggregate warehouse C and write warehouse_c.json; return the result dict."""
    result = warehouse_lib.aggregate_warehouse(DATA_FILE)
    result["warehouse"] = WAREHOUSE_ID
    OUTPUT_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    r = run()
    print(f"warehouse {WAREHOUSE_ID}: total={r['total']} -> {OUTPUT_FILE.name}")

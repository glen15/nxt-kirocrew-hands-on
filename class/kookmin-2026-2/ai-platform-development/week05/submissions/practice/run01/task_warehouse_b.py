#!/usr/bin/env python3
"""DAG task: aggregate warehouse B.

Reads practice/data/warehouse-b.md via warehouse_lib, computes
(1) total, (2) per-item quantities, (3) low-stock list (warehouse_row basis,
quantity < 5), and writes warehouse_b.json into this run01/ directory.

Independent of warehouses A and C — safe to run in parallel with them.
"""
from __future__ import annotations

import json
from pathlib import Path

import warehouse_lib

# run01/ (this file's directory) is where the intermediate file is written.
RUN_DIR = Path(__file__).resolve().parent
# practice/data/warehouse-b.md relative to run01/:
# run01 -> practice -> submissions -> week05, then week05/practice/data.
DATA_FILE = RUN_DIR.parents[2] / "practice" / "data" / "warehouse-b.md"
OUTPUT_FILE = RUN_DIR / "warehouse_b.json"

WAREHOUSE_NAME = "B"


def run() -> dict:
    """Aggregate warehouse B and write warehouse_b.json. Returns the result dict."""
    result = warehouse_lib.aggregate_warehouse(DATA_FILE)
    result["warehouse"] = WAREHOUSE_NAME
    OUTPUT_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    out = run()
    print(f"[warehouse {WAREHOUSE_NAME}] wrote {OUTPUT_FILE.name}: "
          f"total={out['total']}, items={out['item_quantities']}, "
          f"low_stock={out['low_stock']}")

"""Warehouse A aggregation task (DAG node, independent of B and C).

Reads practice/data/warehouse-a.md via warehouse_lib, computes the warehouse
total, per-item quantities and the low-stock list (warehouse_row basis,
quantity < 5), and writes the intermediate file warehouse_a.json into run01/.

Run standalone:  python3 task_warehouse_a.py
"""
from __future__ import annotations

import json
from pathlib import Path

import warehouse_lib

WAREHOUSE = "A"
# run01/ dir this file lives in; data dir is week05/practice/data.
RUN_DIR = Path(__file__).resolve().parent
DATA_FILE = RUN_DIR.parents[2] / "practice" / "data" / "warehouse-a.md"
OUTPUT_FILE = RUN_DIR / "warehouse_a.json"


def build() -> dict:
    """Aggregate warehouse A and return the intermediate-file payload."""
    agg = warehouse_lib.aggregate_warehouse(DATA_FILE)
    agg["warehouse"] = WAREHOUSE
    return agg


def main() -> None:
    payload = build()
    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUTPUT_FILE.name}: total={payload['total']}, "
          f"items={len(payload['item_quantities'])}, "
          f"low_stock={len(payload['low_stock'])}")


if __name__ == "__main__":
    main()

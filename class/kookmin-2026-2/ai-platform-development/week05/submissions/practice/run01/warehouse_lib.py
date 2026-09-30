"""Reusable warehouse parsing and aggregation helpers.

Parses a warehouse-*.md file whose body is a Markdown table of
| 품목 | 수량 | rows, and computes per-warehouse aggregates:
  (1) total sum, (2) per-item quantities, (3) low-stock list.

Low-stock rule: a warehouse row whose quantity is strictly less than the
threshold (default 5). Basis is the raw warehouse row quantity (warehouse_row).

Used by task_warehouse_a/b/c.py and task_integrate.py.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

LOW_STOCK_THRESHOLD = 5

# A Markdown table data row: | text | number |
_ROW_RE = re.compile(r"^\|\s*(.+?)\s*\|\s*([0-9]+)\s*\|$")
# Header / separator rows to ignore.
_HEADER_TOKENS = {"품목", "수량", "item", "quantity"}


def parse_rows(md_text: str) -> List[Tuple[str, int]]:
    """Parse a warehouse markdown table into a list of (item, quantity) tuples.

    Only pipe-delimited rows whose second cell is an integer are kept, so the
    heading line (# 창고 A 재고), the header row and the |---|---:| separator
    are all skipped.
    """
    rows: List[Tuple[str, int]] = []
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        m = _ROW_RE.match(line)
        if not m:
            continue
        item = m.group(1).strip()
        if item.lower() in _HEADER_TOKENS or set(item) <= {"-", ":", " "}:
            continue
        rows.append((item, int(m.group(2))))
    return rows


def read_warehouse_file(path: str | Path) -> List[Tuple[str, int]]:
    """Read a warehouse-*.md file and return its parsed (item, quantity) rows."""
    text = Path(path).read_text(encoding="utf-8")
    return parse_rows(text)


def total_sum(rows: List[Tuple[str, int]]) -> int:
    """Sum of all quantities in the rows."""
    return sum(qty for _item, qty in rows)


def per_item_quantities(rows: List[Tuple[str, int]]) -> Dict[str, int]:
    """Map each item name to the sum of its quantities (integers)."""
    out: Dict[str, int] = {}
    for item, qty in rows:
        out[item] = out.get(item, 0) + qty
    return out


def low_stock(rows: List[Tuple[str, int]], threshold: int = LOW_STOCK_THRESHOLD) -> List[Tuple[str, int]]:
    """Rows whose quantity is strictly below the threshold (warehouse_row basis)."""
    return [(item, qty) for item, qty in rows if qty < threshold]


def aggregate_warehouse(
    path: str | Path, threshold: int = LOW_STOCK_THRESHOLD
) -> Dict[str, object]:
    """Read one warehouse file and return its total, per-item map and low-stock list.

    Returns a dict shaped for a per-warehouse intermediate file:
      {
        "source_file": <basename>,
        "total": <int>,
        "item_quantities": {item: int, ...},
        "threshold": <int>,
        "low_stock": [{"item": str, "quantity": int}, ...],
      }
    """
    p = Path(path)
    rows = read_warehouse_file(p)
    return {
        "source_file": p.name,
        "total": total_sum(rows),
        "item_quantities": per_item_quantities(rows),
        "threshold": threshold,
        "low_stock": [{"item": item, "quantity": qty} for item, qty in low_stock(rows, threshold)],
    }

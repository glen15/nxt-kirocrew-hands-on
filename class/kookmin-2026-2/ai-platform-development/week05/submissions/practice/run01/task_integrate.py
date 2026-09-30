"""Integration task (DAG sink node; depends on warehouse A, B and C tasks).

Reads the three per-warehouse intermediate files (warehouse_a.json,
warehouse_b.json, warehouse_c.json) produced by the independent warehouse
tasks and merges them into:
  (1) per-warehouse totals,
  (2) per-item total quantities across all warehouses,
  (3) a combined low-stock list on the warehouse_row basis (each source row
      whose quantity < threshold, tagged with its warehouse).

Writes two deliverables into run01/:
  - result.json following practice/출력형식.md, with low_stock_basis="warehouse_row".
  - report.md, a human-readable summary whose numbers match result.json.

Run standalone (after A/B/C have written their JSON):
    python3 task_integrate.py
"""
from __future__ import annotations

import json
from pathlib import Path

import warehouse_lib

RUN_DIR = Path(__file__).resolve().parent
LOW_STOCK_BASIS = "warehouse_row"
THRESHOLD = warehouse_lib.LOW_STOCK_THRESHOLD

# Ordered warehouse label -> intermediate file.
WAREHOUSE_FILES = [
    ("A", RUN_DIR / "warehouse_a.json"),
    ("B", RUN_DIR / "warehouse_b.json"),
    ("C", RUN_DIR / "warehouse_c.json"),
]

RESULT_FILE = RUN_DIR / "result.json"
REPORT_FILE = RUN_DIR / "report.md"


def load_warehouses() -> list[dict]:
    """Load the three per-warehouse intermediate payloads, in A, B, C order."""
    loaded: list[dict] = []
    for label, path in WAREHOUSE_FILES:
        if not path.exists():
            raise FileNotFoundError(
                f"missing intermediate file {path.name}; run task_warehouse_{label.lower()}.py first"
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("warehouse", label)
        loaded.append(data)
    return loaded


def build_result(warehouses: list[dict]) -> dict:
    """Merge per-warehouse payloads into the result.json structure."""
    source_files: list[str] = []
    warehouse_totals: dict[str, int] = {}
    item_totals: dict[str, int] = {}
    low_stock: list[dict] = []

    for wh in warehouses:
        label = wh["warehouse"]
        source_files.append(wh["source_file"])
        warehouse_totals[label] = int(wh["total"])

        for item, qty in wh["item_quantities"].items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)

        # warehouse_row basis: each intermediate low_stock entry is a raw row.
        for entry in wh["low_stock"]:
            low_stock.append(
                {
                    "item": entry["item"],
                    "quantity": int(entry["quantity"]),
                    "warehouse": label,
                }
            )

    grand_total = sum(warehouse_totals.values())

    return {
        "source_files": source_files,
        "warehouse_totals": warehouse_totals,
        "item_totals": item_totals,
        "grand_total": grand_total,
        "low_stock_basis": LOW_STOCK_BASIS,
        "threshold": THRESHOLD,
        "low_stock": low_stock,
    }


def render_report(result: dict) -> str:
    """Render a human-readable report.md whose numbers match result.json."""
    lines: list[str] = []
    lines.append("# 창고 A·B·C 재고 통합 리포트")
    lines.append("")
    lines.append(f"- 입력 파일: {', '.join(result['source_files'])}")
    lines.append(f"- 저재고 기준(low_stock_basis): `{result['low_stock_basis']}` "
                 f"(창고별 행 수량이 {result['threshold']} 미만)")
    lines.append(f"- 전체 합계(grand_total): **{result['grand_total']}**")
    lines.append("")

    lines.append("## 창고별 합계")
    lines.append("")
    lines.append("| 창고 | 합계 |")
    lines.append("|---|---:|")
    for wh, total in result["warehouse_totals"].items():
        lines.append(f"| {wh} | {total} |")
    lines.append("")

    lines.append("## 품목별 총수량")
    lines.append("")
    lines.append("| 품목 | 총수량 |")
    lines.append("|---|---:|")
    for item, qty in result["item_totals"].items():
        lines.append(f"| {item} | {qty} |")
    lines.append("")

    lines.append("## 저재고 목록 (창고별 행 수량 < %d)" % result["threshold"])
    lines.append("")
    if result["low_stock"]:
        lines.append("| 창고 | 품목 | 수량 |")
        lines.append("|---|---|---:|")
        for entry in result["low_stock"]:
            lines.append(f"| {entry['warehouse']} | {entry['item']} | {entry['quantity']} |")
    else:
        lines.append("저재고 항목 없음.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    warehouses = load_warehouses()
    result = build_result(warehouses)

    RESULT_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    REPORT_FILE.write_text(render_report(result) + "\n", encoding="utf-8")

    print(f"wrote {RESULT_FILE.name}: warehouses={len(result['warehouse_totals'])}, "
          f"items={len(result['item_totals'])}, grand_total={result['grand_total']}, "
          f"low_stock={len(result['low_stock'])}")
    print(f"wrote {REPORT_FILE.name}")


if __name__ == "__main__":
    main()

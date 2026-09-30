# Task 1 — Input Data & Output Format Findings

Recorded from the actual source files; no values invented.

## Sources read
- `practice/data/warehouse-a.md`
- `practice/data/warehouse-b.md`
- `practice/data/warehouse-c.md`
- `practice/출력형식.md`

## Input data format
Each `warehouse-*.md` is a Markdown document with:
- A level-1 header line: `# 창고 X 재고`.
- A two-column table with header `| 품목 | 수량 |` and the alignment row `|---|---:|`.
- One data row per item: `| <품목> | <수량> |`.

Columns: **품목** = item name (string), **수량** = quantity (integer, right-aligned).

### Parse rule
Skip the `#` header line, the table header line (`| 품목 | 수량 |`), and the
separator line (`|---|---:|`). For each remaining non-empty line, split on `|`,
strip whitespace from cells, take cell 1 = item (str), cell 2 = quantity (int).

### Actual rows (verbatim from source)
| Warehouse | file | rows (품목: 수량) |
|---|---|---|
| A | warehouse-a.md | mug: 12, bottle: 3, sensor: 7 |
| B | warehouse-b.md | mug: 5, bottle: 9, hub: 2 |
| C | warehouse-c.md | sensor: 4, hub: 11, cable: 1 |

## Output format: result.json structure (from 출력형식.md)
```json
{
  "source_files": [],
  "warehouse_totals": {},
  "item_totals": {},
  "grand_total": 0,
  "low_stock_basis": "item_total",
  "threshold": 5,
  "low_stock": []
}
```

Key semantics (from the spec):
- `source_files`: list of input file names used.
- `warehouse_totals`: mapping of warehouse name -> integer sum. Base data is A, B, C.
- `item_totals`: mapping of each item name appearing in the sources -> integer sum across all warehouses.
- `grand_total`: total quantity (integer).
- `low_stock_basis`: `item_total` for whole-item-sum basis, or `warehouse_row` for per-warehouse-row basis.
- `threshold`: upper bound for low stock; a quantity is low-stock when it is **strictly less than** this value.
- `low_stock`: for `item_total` basis each entry is `{"item": "<name>", "quantity": <int>}`;
  for `warehouse_row` basis each entry additionally includes `"warehouse"`, i.e.
  `{"item": "<name>", "quantity": <int>, "warehouse": "<name>"}`.
- Numbers must be stored as integers, not strings.

## This task's binding requirements (override the spec's example default)
- `low_stock_basis` MUST be **`warehouse_row`** (per the task requirements; the
  `item_total` in the example JSON is only a structure placeholder).
- `threshold` = 5. Low-stock = per-warehouse **row** quantity `< 5`.

## Derived expected values (computed from the source rows above, for downstream verification)
- warehouse_totals: A = 12+3+7 = 22, B = 5+9+2 = 16, C = 4+11+1 = 16.
- item_totals: mug = 17, bottle = 12, sensor = 11, hub = 13, cable = 1.
- grand_total: 54.
- low_stock (warehouse_row, quantity < 5):
  - A: bottle (3)
  - B: hub (2)
  - C: sensor (4), cable (1)

## Notes
- The 출력형식.md verifier note ("제공 검사기는 2차 기준인 item_total, threshold=5를 검사") refers to
  the run02 checker; run01 uses the basis chosen for this task = `warehouse_row`.
- Report (report.md) must contain warehouse totals, item totals, low-stock list, and the applied basis,
  with numbers matching result.json.

"""통합 작업 (DAG 통합 노드).

세 창고 중간 파일(warehouse-a/b/c.result.json)을 읽어 품목별 총수량(item_total)을
합산하고, item_total < 5 인 품목을 저재고로 판정한다. practice/출력형식.md 형식에
맞춰 result.json(low_stock_basis=item_total, threshold=5)과 report.md 를 같은
run02 디렉터리에 작성한다.

이 노드는 창고 A·B·C 세 집계 작업 모두에 의존한다(각 창고의 중간 result.json 이
선행 생성되어 있어야 한다).
"""

import json
import os

# 이 스크립트가 위치한 run02 디렉터리.
HERE = os.path.dirname(os.path.abspath(__file__))

# 저재고 판정 상한. 품목별 총수량이 이 값보다 작으면 저재고.
THRESHOLD = 5

# 창고 이름 -> (중간 파일명, 원본 입력 파일명).
WAREHOUSES = [
    ("A", "warehouse-a.result.json", "warehouse-a.md"),
    ("B", "warehouse-b.result.json", "warehouse-b.md"),
    ("C", "warehouse-c.result.json", "warehouse-c.md"),
]

RESULT_PATH = os.path.join(HERE, "result.json")
REPORT_PATH = os.path.join(HERE, "report.md")


def load_warehouse_results():
    """세 창고 중간 파일을 읽어 (창고별 데이터 리스트, 사용한 원본 파일명 리스트)를 반환한다.

    선행 창고 집계 작업이 만든 중간 파일이 하나라도 없으면 FileNotFoundError 를
    그대로 올린다(통합은 세 작업 모두에 의존하므로).
    """
    results = []
    source_files = []
    for name, result_file, source_file in WAREHOUSES:
        path = os.path.join(HERE, result_file)
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"창고 {name} 중간 파일이 없습니다: {path} "
                f"(선행 집계 작업을 먼저 실행하세요)"
            )
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        results.append(data)
        source_files.append(source_file)
    return results, source_files


def integrate(results):
    """창고별 중간 결과 리스트를 통합한다.

    Returns:
        (warehouse_totals, item_totals, grand_total, low_stock) 튜플.
        - warehouse_totals: {창고명: 정수 합계}
        - item_totals: {품목명: 전체 창고 정수 합계}
        - grand_total: 전체 수량 합계(int)
        - low_stock: item_total < THRESHOLD 인 품목 목록
          [{"item": 품목명, "quantity": 정수}], 품목명 오름차순 정렬.
    """
    warehouse_totals = {}
    item_totals = {}
    for data in results:
        wh = data["warehouse"]
        warehouse_totals[wh] = int(data["total"])
        for item, qty in data["items"].items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)

    grand_total = sum(warehouse_totals.values())

    low_stock = [
        {"item": item, "quantity": total}
        for item, total in sorted(item_totals.items())
        if total < THRESHOLD
    ]
    return warehouse_totals, item_totals, grand_total, low_stock


def write_result_json(source_files, warehouse_totals, item_totals, grand_total, low_stock):
    """출력형식.md 구조에 맞춰 result.json 을 작성한다."""
    result = {
        "source_files": source_files,
        "warehouse_totals": warehouse_totals,
        "item_totals": item_totals,
        "grand_total": grand_total,
        "low_stock_basis": "item_total",
        "threshold": THRESHOLD,
        "low_stock": low_stock,
    }
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return result


def write_report_md(warehouse_totals, item_totals, grand_total, low_stock):
    """창고별 합계·품목별 합계·저재고 목록·적용 기준을 담은 짧은 보고서를 작성한다.

    수치는 result.json 과 동일한 값을 그대로 사용한다.
    """
    lines = []
    lines.append("# 창고 재고 집계 보고서 (run02)")
    lines.append("")
    lines.append("## 창고별 합계")
    lines.append("")
    lines.append("| 창고 | 합계 |")
    lines.append("|---|---:|")
    for wh in sorted(warehouse_totals):
        lines.append(f"| {wh} | {warehouse_totals[wh]} |")
    lines.append("")
    lines.append(f"전체 합계(grand_total): {grand_total}")
    lines.append("")
    lines.append("## 품목별 총수량 (item_total)")
    lines.append("")
    lines.append("| 품목 | 총수량 |")
    lines.append("|---|---:|")
    for item in sorted(item_totals):
        lines.append(f"| {item} | {item_totals[item]} |")
    lines.append("")
    lines.append("## 저재고 목록")
    lines.append("")
    lines.append(f"- 판정 기준(low_stock_basis): item_total")
    lines.append(f"- 임계값(threshold): {THRESHOLD} (총수량이 이 값 미만이면 저재고)")
    lines.append("")
    if low_stock:
        lines.append("| 품목 | 총수량 |")
        lines.append("|---|---:|")
        for entry in low_stock:
            lines.append(f"| {entry['item']} | {entry['quantity']} |")
    else:
        lines.append("저재고 품목 없음.")
    lines.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    results, source_files = load_warehouse_results()
    warehouse_totals, item_totals, grand_total, low_stock = integrate(results)
    write_result_json(source_files, warehouse_totals, item_totals, grand_total, low_stock)
    write_report_md(warehouse_totals, item_totals, grand_total, low_stock)
    print(
        f"통합 완료: 창고 {len(warehouse_totals)}곳, 품목 {len(item_totals)}종, "
        f"전체 {grand_total}, 저재고 {len(low_stock)}종 "
        f"-> {RESULT_PATH}, {REPORT_PATH}"
    )
    return {
        "source_files": source_files,
        "warehouse_totals": warehouse_totals,
        "item_totals": item_totals,
        "grand_total": grand_total,
        "low_stock_basis": "item_total",
        "threshold": THRESHOLD,
        "low_stock": low_stock,
    }


if __name__ == "__main__":
    main()

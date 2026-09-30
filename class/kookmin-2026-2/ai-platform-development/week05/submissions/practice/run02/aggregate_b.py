"""창고 B 독립 집계 작업 (DAG 노드).

warehouse_common 을 이용해 practice/data/warehouse-b.md 를 파싱하고,
창고 B 의 합계와 품목별 수량을 warehouse-b.result.json (같은 run02 디렉터리)에
저장한다. 창고 A·C 에 의존하지 않는 독립 작업이다.
"""

import os

from warehouse_common import parse_warehouse, write_warehouse_result

# 이 스크립트(run02) 기준 경로.
HERE = os.path.dirname(os.path.abspath(__file__))
# run02 -> practice/data/warehouse-b.md
DATA_PATH = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "practice", "data", "warehouse-b.md")
)
OUT_PATH = os.path.join(HERE, "warehouse-b.result.json")


def main():
    items, total = parse_warehouse(DATA_PATH)
    data = write_warehouse_result("B", items, total, OUT_PATH)
    print(f"[창고 B] 품목 {len(items)}종, 합계 {total} -> {OUT_PATH}")
    return data


if __name__ == "__main__":
    main()

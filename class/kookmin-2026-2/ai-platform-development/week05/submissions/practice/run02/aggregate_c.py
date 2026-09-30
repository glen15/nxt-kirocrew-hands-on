"""창고 C 독립 집계 작업.

practice/data/warehouse-c.md를 파싱해 창고 C의 합계와 품목별 수량을
warehouse-c.result.json에 저장한다. 창고 A·B 작업에 의존하지 않는
독립 작업이다(DAG 상 세 창고 집계는 상호 독립).
"""

import os

from warehouse_common import parse_warehouse, write_warehouse_result

# 이 스크립트가 위치한 run02 디렉터리.
_HERE = os.path.dirname(os.path.abspath(__file__))
# week05/ 루트 (run02 -> practice -> submissions -> week05).
_WEEK05 = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))

WAREHOUSE_PATH = os.path.join(_WEEK05, "practice", "data", "warehouse-c.md")
OUT_PATH = os.path.join(_HERE, "warehouse-c.result.json")


def main():
    items, total = parse_warehouse(WAREHOUSE_PATH)
    data = write_warehouse_result("C", items, total, OUT_PATH)
    print(f"창고 C 집계 완료: 품목 {len(data['items'])}종, 합계 {data['total']} -> {OUT_PATH}")
    return data


if __name__ == "__main__":
    main()

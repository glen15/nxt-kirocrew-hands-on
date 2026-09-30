"""창고 파서 공용 모듈.

warehouse-a/b/c.md 는 다음과 같은 마크다운 표 구조를 가진다:

    # 창고 A 재고

    | 품목 | 수량 |
    |---|---:|
    | mug | 12 |
    | bottle | 3 |
    | sensor | 7 |

이 모듈은 창고 파일 경로를 받아 {품목: 수량} 딕셔너리와 합계를 반환하는
parse_warehouse(path) 함수와, 창고별 중간 결과(JSON)를 저장하는
write_warehouse_result(name, items, total, out_path) 함수를 제공한다.
"""

import json
import os


def parse_warehouse(path):
    """창고 마크다운 파일을 파싱한다.

    Args:
        path: 창고 마크다운 파일 경로.

    Returns:
        (items, total) 튜플.
        items: {품목명(str): 수량(int)} 딕셔너리.
        total: 해당 창고의 수량 합계(int).

    마크다운 표에서 '| 품목 | 수량 |' 헤더 행과 '|---|---:|' 구분 행은
    건너뛰고, 데이터 행만 {품목: 수량}으로 수집한다.
    """
    items = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            # 표 행이 아니면 건너뛴다.
            if not line.startswith("|"):
                continue
            # '| a | b |' -> ['a', 'b'] (앞뒤 빈 셀 제거)
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            name, qty = cells[0], cells[1]
            # 헤더 행('품목'/'수량')과 구분 행('---', '---:') 을 건너뛴다.
            if name in ("품목", ""):
                continue
            if set(qty) <= set("-: "):
                continue
            try:
                quantity = int(qty)
            except ValueError:
                # 수량이 정수가 아닌 행은 데이터 행이 아니므로 건너뛴다.
                continue
            items[name] = items.get(name, 0) + quantity
    total = sum(items.values())
    return items, total


def write_warehouse_result(name, items, total, out_path):
    """창고별 중간 결과를 JSON 파일로 저장한다.

    Args:
        name: 창고 이름(예: "A").
        items: {품목명: 수량} 딕셔너리.
        total: 창고 수량 합계(int).
        out_path: 저장할 JSON 파일 경로.

    Returns:
        저장한 데이터 딕셔너리.

    숫자는 문자열이 아닌 정수로 저장한다.
    """
    data = {
        "warehouse": name,
        "items": {k: int(v) for k, v in items.items()},
        "total": int(total),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return data

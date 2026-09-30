#!/usr/bin/env python3
"""요약 JSON을 검사하고 HTML 리포트로 조립한다.

이 스크립트는 원본 md/csv를 읽거나 요약하지 않는다.
AI가 만든 요약 JSON의 스키마만 검사하고, 통과하면 HTML을 조립한다.
모든 텍스트 값은 HTML 이스케이프해 삽입한다.

사용법:
    python3 build_report.py 요약.json 리포트.html
    cat 요약.json | python3 build_report.py - 리포트.html

종료 코드: 0 저장 완료 / 1 검사 실패(저장 안 함) / 2 사용법·입출력 오류
"""
import html
import json
import os
import sys

# 최상위 스키마: 필드 이름 -> 자료형
TOP_FIELDS = {
    "title": str,
    "generated_on": str,
    "documents": list,
    "tables": list,
}
DOC_FIELDS = {"source": str, "summary": str, "key_points": list}
TABLE_FIELDS = {
    "source": str,
    "caption": str,
    "columns": list,
    "rows": list,
    "notes": str,
}


def _fail(msg):
    print(f"검사 실패: {msg}", file=sys.stderr)
    sys.exit(1)


def _check_fields(obj, spec, where):
    if not isinstance(obj, dict):
        _fail(f"{where}: 객체여야 하는데 {type(obj).__name__}")
    got = set(obj.keys())
    want = set(spec.keys())
    missing = want - got
    extra = got - want
    if missing:
        _fail(f"{where}: 누락된 필드 {sorted(missing)}")
    if extra:
        _fail(f"{where}: 허용되지 않은 필드 {sorted(extra)}")
    for name, typ in spec.items():
        if not isinstance(obj[name], typ):
            _fail(f"{where}.{name}: {typ.__name__} 여야 하는데 {type(obj[name]).__name__}")


def _check_str_list(items, where):
    for i, v in enumerate(items):
        if not isinstance(v, str):
            _fail(f"{where}[{i}]: 문자열이어야 하는데 {type(v).__name__}")


def validate(data):
    _check_fields(data, TOP_FIELDS, "root")

    for di, doc in enumerate(data["documents"]):
        _check_fields(doc, DOC_FIELDS, f"documents[{di}]")
        _check_str_list(doc["key_points"], f"documents[{di}].key_points")

    for ti, tbl in enumerate(data["tables"]):
        _check_fields(tbl, TABLE_FIELDS, f"tables[{ti}]")
        _check_str_list(tbl["columns"], f"tables[{ti}].columns")
        ncols = len(tbl["columns"])
        if ncols == 0:
            _fail(f"tables[{ti}].columns: 열이 최소 1개는 있어야 한다")
        for ri, row in enumerate(tbl["rows"]):
            if not isinstance(row, list):
                _fail(f"tables[{ti}].rows[{ri}]: 목록이어야 하는데 {type(row).__name__}")
            if len(row) != ncols:
                _fail(
                    f"tables[{ti}].rows[{ri}]: 길이 {len(row)} != 열 개수 {ncols}"
                )
            for ci, cell in enumerate(row):
                if not isinstance(cell, (str, int, float, bool)) and cell is not None:
                    _fail(
                        f"tables[{ti}].rows[{ri}][{ci}]: 문자열·숫자·불리언·null 만 허용"
                    )


def _cell(v):
    if v is None:
        return ""
    return html.escape(str(v))


def build_html(data):
    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="ko">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f"<title>{html.escape(data['title'])}</title>")
    # 다크모드에서도 글자가 보이도록 배경·글자색을 고정한다.
    parts.append(
        "<style>"
        "body{background:#ffffff;color:#1a1a1a;"
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
        "line-height:1.6;max-width:900px;margin:0 auto;padding:2rem;}"
        "h1{border-bottom:2px solid #333;padding-bottom:.3rem;}"
        "h2{margin-top:2rem;color:#111;}"
        ".sub{color:#666;font-size:.9rem;margin-top:-.5rem;}"
        ".doc{margin-bottom:1.5rem;}"
        ".src{color:#888;font-size:.85rem;}"
        "table{border-collapse:collapse;width:100%;margin:.5rem 0;}"
        "th,td{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;}"
        "th{background:#f2f2f2;color:#1a1a1a;}"
        "caption{text-align:left;font-weight:bold;margin-bottom:.3rem;}"
        ".notes{color:#666;font-size:.85rem;margin-top:.2rem;}"
        "</style>"
    )
    parts.append("</head>")
    parts.append("<body>")
    parts.append(f"<h1>{html.escape(data['title'])}</h1>")
    if data["generated_on"]:
        parts.append(f'<p class="sub">{html.escape(data["generated_on"])}</p>')

    if data["documents"]:
        parts.append("<h2>문서 요약</h2>")
        for doc in data["documents"]:
            parts.append('<div class="doc">')
            parts.append(f'<p class="src">출처: {html.escape(doc["source"])}</p>')
            parts.append(f"<p>{html.escape(doc['summary'])}</p>")
            if doc["key_points"]:
                parts.append("<ul>")
                for kp in doc["key_points"]:
                    parts.append(f"<li>{html.escape(kp)}</li>")
                parts.append("</ul>")
            parts.append("</div>")

    if data["tables"]:
        parts.append("<h2>핵심 표</h2>")
        for tbl in data["tables"]:
            parts.append("<table>")
            parts.append(f"<caption>{html.escape(tbl['caption'])}</caption>")
            parts.append(f'<tr class="src-row"><td colspan="{len(tbl["columns"])}"'
                         f' class="src">출처: {html.escape(tbl["source"])}</td></tr>')
            parts.append("<tr>")
            for col in tbl["columns"]:
                parts.append(f"<th>{html.escape(col)}</th>")
            parts.append("</tr>")
            for row in tbl["rows"]:
                parts.append("<tr>")
                for cell in row:
                    parts.append(f"<td>{_cell(cell)}</td>")
                parts.append("</tr>")
            parts.append("</table>")
            if tbl["notes"]:
                parts.append(f'<p class="notes">{html.escape(tbl["notes"])}</p>')

    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts)


def main():
    if len(sys.argv) != 3:
        print("사용법: python3 build_report.py <요약.json|-> <출력.html>", file=sys.stderr)
        sys.exit(2)

    in_path, out_path = sys.argv[1], sys.argv[2]
    try:
        if in_path == "-":
            raw = sys.stdin.read()
        else:
            with open(in_path, encoding="utf-8") as f:
                raw = f.read()
    except OSError as e:
        print(f"입력 읽기 오류: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}", file=sys.stderr)
        sys.exit(2)

    validate(data)  # 실패 시 내부에서 exit 1
    out = build_html(data)

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out)
    except OSError as e:
        print(f"출력 쓰기 오류: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"저장 완료: {out_path} ({len(out)} bytes)")
    sys.exit(0)


if __name__ == "__main__":
    main()

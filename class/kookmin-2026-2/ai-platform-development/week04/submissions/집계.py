#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빛담 가을사진전(E04) 집계 스크립트
- 원본 CSV는 읽기 전용으로만 사용(수정하지 않음)
- 적용 근거:
  * ACCOUNT-01 제1조: 기초잔액 학교지원금 0 / 동아리회비 800,000, 기간 2026-07-01~2026-09-22, E01~E04 혼재
  * ACCOUNT-01 제2조: 수입·환불입금 = +, 지출·환불지급 = - (금액은 양의 정수 원)
  * ACCOUNT-01 제3조: 현재잔액 = 기초 + 수입 + 환불입금 - 지출 - 환불지급
                       E04 순지출 = E04(지출 + 환불지급 - 환불입금), 수입 제외
  * ACCOUNT-01 제5조: 구매계획 수량 -> 참가자=확정인원×계수, 고정=계수, 예정비용=단가×수량
                       (구매계획은 회계 거래에 합산하지 않음)
  * CLUB-01 제1조: 물품 구매 기본 인원 = 확정 인원. 대기자 포함은 별도 시나리오.
  * RULE-02 제1·2조 + APPROVAL-SPACE-04: 승인 정원 160명(변경 승인서 없으면 유지)
    -> 정원은 하드코딩하지 않고 140/160/180 세 시나리오를 모두 계산해 보고서 문서 근거로 판단 이관
"""
import csv, json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "submissions", "집계결과.json")

EVENT = "E04"
# ACCOUNT-01 제1조 기초 잔액
BASE_BALANCE = {"학교지원금": 0, "동아리회비": 800_000}
# 구매 시나리오 정원 (하드코딩된 '승인 정원'이 아니라 계산용 시나리오)
SCENARIOS = [140, 160, 180]


def read_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def main():
    part = read_csv("참가신청.csv")
    acc = read_csv("회계내역.csv")
    plan = read_csv("구매계획.csv")

    rows_read = {"참가신청": len(part), "회계내역": len(acc), "구매계획": len(plan)}

    # --- 1. 참가 상태별 인원 (E04만) ---
    part_e04 = [r for r in part if r["행사_ID"] == EVENT]
    status_counts = {}
    for r in part_e04:
        status_counts[r["신청상태"]] = status_counts.get(r["신청상태"], 0) + 1

    confirmed = [r for r in part_e04 if r["신청상태"] == "확정"]
    n_confirmed = len(confirmed)

    # --- 2. 확정자의 선택 ---
    choice_photo = sum(1 for r in confirmed if r["인화체험"] == "신청")
    choice_food = sum(1 for r in confirmed if r["식음료"] == "신청")

    # --- 3. 재원별 현재 잔액 (동아리 전체, 전 행사) ACCOUNT-01 제2·3조 ---
    def signed(r):
        amt = int(r["금액"])
        t = r["유형"]
        if t in ("수입", "환불입금"):
            return amt
        if t in ("지출", "환불지급"):
            return -amt
        raise ValueError(f"미정의 유형: {t}")

    balances = dict(BASE_BALANCE)
    income = {"학교지원금": 0, "동아리회비": 0}
    for r in acc:
        fund = r["재원"]
        balances[fund] = balances.get(fund, 0) + signed(r)
        if r["유형"] == "수입":
            income[fund] = income.get(fund, 0) + int(r["금액"])

    # --- 4. E04 순지출 (수입 제외) ACCOUNT-01 제3조 ---
    e04_net = {"학교지원금": 0, "동아리회비": 0}
    for r in acc:
        if r["행사_ID"] != EVENT:
            continue
        fund = r["재원"]
        amt = int(r["금액"])
        t = r["유형"]
        if t == "지출" or t == "환불지급":
            e04_net[fund] = e04_net.get(fund, 0) + amt
        elif t == "환불입금":
            e04_net[fund] = e04_net.get(fund, 0) - amt
        # 수입은 순지출에서 제외

    # --- 5. 구매계획 예정비용 ACCOUNT-01 제5조 ---
    def plan_for(headcount):
        by_fund = {"학교지원금": 0, "동아리회비": 0}
        lines = []
        for r in plan:
            base = r["수량기준"]
            k = int(r["계수"])
            unit = int(r["단가"])
            if base == "참가자":
                qty = headcount * k
            elif base == "고정":
                qty = k
            else:
                raise ValueError(f"미정의 수량기준: {base}")
            cost = unit * qty
            fund = r["예정재원"]
            by_fund[fund] = by_fund.get(fund, 0) + cost
            lines.append({"항목_ID": r["항목_ID"], "물품": r["물품"],
                          "수량기준": base, "수량": qty, "단가": unit,
                          "예정비용": cost, "예정재원": fund})
        return by_fund, lines

    purchase = {}
    for hc in SCENARIOS:
        by_fund, lines = plan_for(hc)
        purchase[str(hc)] = {"재원별_예정비용": by_fund, "상세": lines}

    result = {
        "행사_ID": EVENT,
        "회계_기준일": "2026-09-22 (ACCOUNT-01)",
        "읽은_행수": rows_read,
        "참가_상태별_인원": status_counts,
        "확정_인원": n_confirmed,
        "확정자_선택": {"인화체험_신청": choice_photo, "식음료_신청": choice_food},
        "기초잔액": BASE_BALANCE,
        "재원별_수입": income,
        "재원별_현재잔액": balances,
        "E04_순지출": e04_net,
        "구매계획_시나리오": purchase,
        "적용근거": {
            "기초잔액_부호_잔액식": "ACCOUNT-01 제1·2·3조",
            "E04_순지출_수입제외": "ACCOUNT-01 제3조",
            "구매수량_예정비용_산식": "ACCOUNT-01 제5조",
            "확정인원_기본": "CLUB-01 제1조",
            "정원_근거": "RULE-02 제1·2조 + APPROVAL-SPACE-04 (승인 160명; 변경 승인서 미확인이면 유지)",
        },
        "확인_필요": [
            "정원 180명 적용: 유효한 변경 승인서(CHANGE-SPACE-04)가 등록 지식기반/data/updates에 없음. MEMO-04는 변경 승인 기록 없음 명시.",
            "잔여 지원금 500,000원(APPROVAL-FUND-04): 정산 승인 후 지급 예정이라 현재 가용 현금에 미포함(ACCOUNT-01 제5조/RULE-01 제5조).",
        ],
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n[저장]", OUT)


if __name__ == "__main__":
    main()

# 창고 재고 집계 보고서 (run02)

## 창고별 합계

| 창고 | 합계 |
|---|---:|
| A | 22 |
| B | 16 |
| C | 16 |

전체 합계(grand_total): 54

## 품목별 총수량 (item_total)

| 품목 | 총수량 |
|---|---:|
| bottle | 12 |
| cable | 1 |
| hub | 13 |
| mug | 17 |
| sensor | 11 |

## 저재고 목록

- 판정 기준(low_stock_basis): item_total
- 임계값(threshold): 5 (총수량이 이 값 미만이면 저재고)

| 품목 | 총수량 |
|---|---:|
| cable | 1 |

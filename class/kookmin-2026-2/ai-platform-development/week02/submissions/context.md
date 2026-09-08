# 다음 작업에 넘길 맥락

## 판단 기준
- 기준과 이유:
  - 항목별 나중 공지 우선(later-notice-wins): 같은 과제에 여러 공지가 있으면 최신 공지가 이전 것을 덮는다. 예) 과제1은 N02가 N01을 연장.
  - 없는 값은 만들지 않는다: 날짜만 있는 마감에 시각을 임의로 넣지 않고 '확인 불가'로 둔다. 본인 임의 입력값은 근거로 보지 않는다.
  - 준비완료 ≠ 실제 제출완료: 로컬 기록의 '완료'를 실제 LMS/GitHub 제출 근거로 삼지 않는다. 본인 확인이 있으면 '본인 확인' 근거로만 기록한다.
  - 제출/완료 상태는 원본 기록(notices·my-tasks)만으로 판단하고, 로컬 submissions 폴더의 존재를 제출 근거로 오해하지 않는다.
  - 저장 전 같은 이름 파일이 있으면 덮어쓰지 않고 알린다. 원본은 보존하고 결과물은 submissions/ 하위에 둔다.

## 현재 상태
- 반영한 자료·기준 시각:
  - 기준 시각 2026-09-09(수) 09:00 KST
  - 원본: data/course/notices.md, data/course/my-tasks.md
  - 산출물: submissions/course-check.md, submissions/notices-final.md, submissions/work.md
- 완료한 일:
  - 공지↔내 업무 대조 검증 → submissions/course-check.md 저장(원본 미수정)
  - 변경 공지 확인: N02가 유일. 과제1 마감 9/11 18:00 → 9/14 18:00 연장(방식 불변)
  - work.md '할 일'의 과제1을 '제출 완료 [x]'로 체크(근거: 본인 직접 확인, 2026-09-08). '내 일정·조건'과 원문 보존
  - 원본 notices.md 보존 + 최종 확정본 submissions/notices-final.md 별도 생성
- 미해결·확인 질문:
  - 데이터분석 과제2 CSV 원자료 준비 여부(미기재)
  - 진로탐색 설문 정확한 마감 '시각'(공지에 없음)
  - LMS/GitHub 실제 접수 기록(이 자료로 조회 불가) — 과제1은 본인 확인만 있고 접수 증빙은 미확보

## 다음 행동
- 할 일:
  - 과제2(마감 9/10 23:59): CSV 준비 확인 후 PDF+CSV 함께 LMS 제출
  - 진로 설문(9/11 금): 응답 완료, 마감 시각 확인
  - 팀 프로젝트 메모(9/16 12:00): 주제 후보 2개 중 확정 → README 작성
- 읽을 파일:
  - data/course/notices.md, data/course/my-tasks.md
  - submissions/course-check.md, submissions/notices-final.md, submissions/work.md
- 수정 가능한 범위:
  - submissions/ 하위 산출물(work.md 할 일 등)
  - 원본(notices.md, my-tasks.md) 및 work.md '내 일정·조건'은 수정 금지(보존)
- 보존할 내용:
  - 원본 공지·과제 기록 파일
  - work.md '내 일정·조건'(예: 매주 수요일 알바) 및 사용자 입력 원문

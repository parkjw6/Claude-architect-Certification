# 12.2 Few-Shot 프롬프팅 활용

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 — 적정 수(2-4개) 암기

---

## Few-Shot 프롬프팅이란?

예시를 제공하여 LLM이 원하는 패턴을 학습하게 하는 기법

```
Zero-shot: 예시 없이 지시만
Few-shot:  2-4개 예시 + 지시
```

---

## 최적 예시 수

```
1개:  패턴 학습 불충분
2-4개: ✅ 최적 (각각 다른 케이스)
5-8개: 토큰 오버헤드 증가, 개선 미미
10개+: 역효과 가능 (노이즈)
```

---

## 좋은 Few-Shot 예시의 특징

```
1. 각 예시가 다른 케이스를 다룸
   (비슷한 예시 중복 금지)

2. 엣지 케이스 포함

3. 원하는 출력 형식과 정확히 일치

4. 실제로 모호한 상황 처리
```

---

## 실전 예시: 에스컬레이션 판단

```python
FEW_SHOT_PROMPT = """
다음 예시를 참고하여 에스컬레이션 여부를 결정하세요:

예시 1:
고객: "환불 받고 싶어요. 주문 #12345가 손상되어 도착했어요"
판단: 에스컬레이션 불필요
이유: 표준 손상 교체 케이스, 정책 내 처리 가능

예시 2:
고객: "도저히 못 참겠어요. 매니저 연결해주세요"
판단: 에스컬레이션 필요
이유: 고객이 명시적으로 사람 연결 요청

예시 3:
고객: "VIP 고객에게만 주는 특별 할인이 있다고 들었는데요"
판단: 에스컬레이션 필요
이유: 정책에 없는 예외 사항

---
현재 상황:
{customer_message}

판단:"""
```

---

## Few-Shot 사용 시기

```
✅ Few-shot 효과적:
- 모호한 케이스 처리 방법
- 출력 형식 일관성
- 다양한 입력 구조 처리
- 엣지 케이스 동작

❌ Few-shot 불필요:
- 명확한 지시로 충분한 경우
- 출력 형식이 단순한 경우
- 일관성이 크게 중요하지 않은 경우
```

---

> 🔗 다음: [Chapter 13: 구조화된 출력 설계](13_structured_output.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Few-shot 예시를 Skill과 평가 자산으로 관리하기

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | Skill의 `references/`에 report/ignore/boundary 예시를 두는 것이 중심입니다. |
| **Codex app** | Skill 관리 UI로 같은 Skill과 reference 기반 workflow를 선택할 수 있습니다. 예시 설계 원리는 CLI와 같습니다. |
| **Codex SDK** | coding-focused thread에 동일 few-shot/reference 계약을 programmatically 적용합니다. |
| **OpenAI Agents SDK** | 범용 agent의 tool 선택·분류 경계에 few-shot을 적용합니다. |

### 1. Few-shot 자체는 제품 중립적이다

Claude와 Codex 모두 **설명만으로 경계가 모호한 분류**에서 few-shot이 유효합니다. 다만 Codex repository에서는 긴 예시를 모든 요청에 로드하기보다 Skill의 reference로 분리할 수 있습니다.

```text
.agents/
└── skills/
    └── security-review/
        ├── SKILL.md
        └── references/
            ├── report-examples.md
            └── ignore-examples.md
```

`SKILL.md`:

```markdown
---
name: security-review
description: >
  Review changed code for concrete security vulnerabilities.
---

# Security review

Apply the criteria in:

- `references/report-examples.md`
- `references/ignore-examples.md`

Do not report a finding without a reachable path and evidence.
```

### 2. 좋은 예시는 “판정 경계”를 가르친다

```markdown
## Report

Input:
`query = f"SELECT * FROM users WHERE id = {user_input}"`

Decision:
Critical — untrusted input is interpolated into SQL.

## Ignore

Input:
`logger.info("request started")`

Decision:
No finding — no secret, credential, PII, or sensitive payload is logged.

## Boundary case

Input:
`logger.info("request_id=%s", request_id)`

Decision:
No finding unless `request_id` itself embeds sensitive data according to
the repository's documented format.
```

같은 유형의 positive example만 여러 개 넣는 것보다 positive, negative, boundary case를 각각 포함하는 편이 낫습니다.

### 3. 예시를 prompt 자산이 아니라 eval 자산으로도 유지

Few-shot을 변경하면 동일한 fixture로 회귀를 확인합니다.

```json
{"id":"sql-001","expected":"report","category":"sql_injection"}
{"id":"log-001","expected":"ignore","category":"normal_log"}
{"id":"log-002","expected":"report","category":"credential_leak"}
```

권장 흐름:

```text
examples 수정
→ 고정 fixture 실행
→ 오탐·누락 비교
→ 기준 변경 승인
→ Skill reference 반영
```

### 4. 과도한 few-shot을 피하는 기준

- 명확한 schema 문제는 Structured Outputs로 해결합니다.
- command permission은 Rules/Sandbox로 해결합니다.
- critical invariant는 application code로 해결합니다.
- few-shot은 **모델이 해석해야 하는 경계**에만 사용합니다.

즉 예시를 늘리기 전에 “이 문제가 정말 prompt 문제인가?”를 먼저 확인해야 합니다.


### 공식 문서

- [Codex Skills](https://developers.openai.com/codex/build-skills)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

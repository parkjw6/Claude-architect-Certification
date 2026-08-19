# 15.3 Progressive Summarization 주의점

> 📅 2026년 04월 05일 기준

---

## Progressive Summarization이란?

긴 대화를 단계적으로 요약하여 컨텍스트를 관리하는 기법

```
원본 대화 (긴 컨텍스트)
    ↓ 요약
압축된 요약 (짧은 컨텍스트)
    ↓ + 새 대화 계속
새 대화 + 요약 (적절한 컨텍스트)
```

---

## 요약 시 반드시 보존해야 할 것

```
✅ 반드시 보존:
- 금액: "$150.00" (❌ "환불 금액")
- 날짜: "2024-03-15" (❌ "며칠 전")
- 주문 번호: "#45678" (❌ "주문")
- 고객 ID: "CUST-12345" (❌ "고객")
- 결정 사항: 구체적으로

❌ 일반화하면 안 됨:
"여러 주문에 대해 환불 요청" 
→ 어떤 주문? 얼마? 모름!

✅ 올바른 요약:
"주문 #45678 ($150.00), #89012 ($230.00)에 대해 환불 요청"
```

---

## 요약 지시문 템플릿

```python
SUMMARIZATION_PROMPT = """
다음 고객 지원 대화를 요약하세요.

반드시 포함할 항목:
- 고객 ID와 이름
- 각 주문 번호 (예: #12345, #67890)
- 각 주문의 금액 (예: $150.00)
- 날짜와 기한
- 취해진 행동 (승인/거부/보류)
- 미해결 사항

❌ 절대 일반화 금지:
- "여러 주문" → 각 주문 번호 명시
- "큰 금액" → 정확한 금액 명시
- "얼마 전" → 정확한 날짜 명시

대화:
{conversation}
"""
```

---

## 스크래치패드 패턴

```python
SCRATCHPAD = """
[현재 세션 스크래치패드]

## 확인된 정보
- 고객: 홍길동 (CUST-789)
- 확인된 주문: #34567 ($89.00)

## 완료된 작업
- get_customer: 완료
- lookup_order: 완료

## 다음 단계
- process_refund 실행 예정
"""
```

스크래치패드는 긴 세션에서 중간 상태를 기억하는 데 도움을 줍니다.

---

> 🔗 다음: [Chapter 16: 에스컬레이션과 신뢰성](16_escalation_reliability.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 요약과 authoritative state의 분리

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | `/compact`는 coding conversation 요약이며 결정·검증 결과는 file/artifact에 남깁니다. |
| **Codex app** | 긴 project/thread를 UI에서 관리할 수 있지만 authoritative state를 대신하지는 않습니다. |
| **Codex SDK** | thread를 resume하기 위한 context continuity를 제공하며, application은 중요한 state를 별도 저장합니다. |
| **OpenAI Agents SDK** | Session/RunState와 typed business state를 관리합니다. |

### 1. 요약 결과를 typed object로 만든다

```python
from typing import Literal
from pydantic import BaseModel


class OrderIssue(BaseModel):
    order_id: str
    amount: float
    currency: str
    reason: str


class CaseSummary(BaseModel):
    customer_id: str
    issues: list[OrderIssue]
    deadline: str | None
    completed_actions: list[str]
    unresolved_actions: list[str]
    decision: Literal["continue", "escalate", "closed"]
```

구조화된 요약은 다음 검증이 가능합니다.

```python
def validate_summary(
    summary: CaseSummary,
    state: dict,
) -> list[str]:
    errors: list[str] = []

    if summary.customer_id != state["customer_id"]:
        errors.append("customer_id mismatch")

    state_order_ids = set(state["order_ids"])
    summary_order_ids = {i.order_id for i in summary.issues}

    if summary_order_ids != state_order_ids:
        errors.append("order set mismatch")

    return errors
```

### 2. 요약에서 보존할 것과 버릴 것을 명시

```text
Preserve exactly:
- identifiers
- monetary values and currencies
- dates and deadlines
- approvals/rejections
- policy version
- unresolved blockers
- source references

Compress:
- repeated explanations
- exploratory branches that were rejected
- raw logs already stored elsewhere
```

### 3. Codex `/compact` 사용 시 주의

`/compact`는 현재 coding conversation을 계속하기 위한 기능입니다. 다음은 별도 파일에 남겨야 합니다.

```text
architecture decision
migration plan
accepted API contract
test command and result
known unresolved risk
```

예:

```text
docs/decisions/ADR-017-refund-idempotency.md
.codex/session_notes.md
artifacts/test-results.json
```

### 4. Scratchpad는 source of truth가 아니다

Scratchpad는 작업 메모입니다. 자동 삭제·오래된 내용·충돌 가능성을 고려해야 합니다. 실제 business 상태와 승인 이력은 database나 issue tracker에 둡니다.

### 5. Progressive summary의 회귀 검증

긴 대화 fixture를 준비하고 다음 필드가 여러 차례 요약 후에도 보존되는지 확인합니다.

```text
customer_id
order_id
amount/currency
deadline
decision
source
```

단일 요약 품질뿐 아니라 “요약을 다시 요약하는 과정”의 정보 손실을 평가해야 합니다.


### 공식 문서

- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Codex slash commands](https://developers.openai.com/codex/cli/slash-commands)
- [Responses API compaction](https://developers.openai.com/api/docs/guides/compaction)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

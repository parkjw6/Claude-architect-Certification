# 16.1 에스컬레이션 패턴 설계

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 — 에스컬레이션 기준 암기

---

## 에스컬레이션 기준 (암기 필수!)

### 즉시 에스컬레이션해야 하는 경우

```
✅ 에스컬레이션:
1. 고객이 명시적으로 요청:
   "사람과 통화하고 싶어요"
   "상담원 연결해 주세요"
   "매니저 바꿔주세요"

2. 정책 공백:
   시스템에 없는 예외 상황
   정책 문서가 다루지 않는 케이스

3. 진전 불가:
   동일 시도 3번 이상 실패
   기술적으로 처리 불가한 상황
```

### 에스컬레이션하면 안 되는 경우

```
❌ 에스컬레이션 금지:
- 고객이 화났을 때 (감정 기반)
- 에이전트 자신감이 낮을 때
- 단순히 복잡해 보일 때
- 처리에 시간이 걸릴 것 같을 때
```

---

## 잘못된 에스컬레이션 설계

```python
# ❌ 감정 기반 에스컬레이션
def should_escalate(message: str) -> bool:
    negative_words = ["화났", "불만", "실망", "짜증"]
    if any(word in message for word in negative_words):
        return True  # ← 이것이 잘못됨

# ❌ 자신감 기반
if confidence_score < 0.6:
    escalate()  # ← 이것도 잘못됨
```

---

## 올바른 에스컬레이션 설계

```python
# ✅ 명시적 기준 기반
ESCALATION_TRIGGERS = [
    "사람 연결",
    "상담원",
    "매니저",
    "직원",
    "human agent"
]

def should_escalate(message: str, context: dict) -> tuple[bool, str]:
    """명시적 기준으로 에스컬레이션 판단"""
    
    # 1. 고객 명시적 요청
    if any(trigger in message for trigger in ESCALATION_TRIGGERS):
        return True, "고객 명시적 요청"
    
    # 2. 정책 공백
    if context.get("policy_gap"):
        return True, "정책 공백"
    
    # 3. 진전 불가
    if context.get("retry_count", 0) >= 3:
        return True, "반복 시도 실패"
    
    return False, ""
```

---

## 구조화된 핸드오프

```python
# 에스컬레이션 시 항상 구조화된 요약 포함
def escalate(customer_id: str, reason: str, context: dict) -> dict:
    return {
        "customer_id": customer_id,
        "reason": reason,
        "summary": f"""
고객: {context['customer_name']}
주문: {context.get('order_id', '없음')}
문제: {context['issue_description']}
시도된 해결: {context.get('attempted_solutions', [])}
        """,
        "priority": determine_priority(context)
    }
```

---

> 🔗 다음: [16.2 에러 전파 전략](16_2_error_propagation.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 명시적 escalation engine과 구조화 handoff

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | remote write나 위험 command의 approval 정책에 적용합니다. |
| **Codex app** | 사람이 승인·diff를 시각적으로 검토하는 UI를 제공합니다. Business escalation engine은 app 기능이 아닙니다. |
| **Codex SDK** | coding action의 sandbox/turn policy를 programmatically 설정합니다. |
| **OpenAI Agents SDK** | 고객지원·운영 escalation signal과 structured handoff를 구현합니다. |

### 1. Model 판단과 policy engine을 분리

모델은 사용자의 표현에서 signal을 추출할 수 있지만 최종 routing 기준은 코드가 소유하는 편이 안정적입니다.

```python
from typing import Literal
from pydantic import BaseModel


class EscalationSignals(BaseModel):
    explicit_human_request: bool
    legal_or_regulatory_issue: bool
    policy_gap: bool
    attempts: int
    progress_made: bool
    refund_amount: float | None


class EscalationDecision(BaseModel):
    should_escalate: bool
    reason: Literal[
        "explicit_request",
        "legal_issue",
        "policy_gap",
        "no_progress",
        "approval_threshold",
        "none",
    ]


def decide_escalation(
    signals: EscalationSignals,
) -> EscalationDecision:
    if signals.explicit_human_request:
        return EscalationDecision(
            should_escalate=True,
            reason="explicit_request",
        )

    if signals.legal_or_regulatory_issue:
        return EscalationDecision(
            should_escalate=True,
            reason="legal_issue",
        )

    if signals.policy_gap:
        return EscalationDecision(
            should_escalate=True,
            reason="policy_gap",
        )

    if signals.attempts >= 3 and not signals.progress_made:
        return EscalationDecision(
            should_escalate=True,
            reason="no_progress",
        )

    if (
        signals.refund_amount is not None
        and signals.refund_amount > 500
    ):
        return EscalationDecision(
            should_escalate=True,
            reason="approval_threshold",
        )

    return EscalationDecision(
        should_escalate=False,
        reason="none",
    )
```

### 2. Handoff schema

```python
class Handoff(BaseModel):
    customer_id: str
    verified: bool
    order_ids: list[str]
    issue_summary: str
    exact_amounts: list[str]
    attempted_actions: list[str]
    completed_side_effects: list[str]
    pending_side_effects: list[str]
    escalation_reason: str
    policy_version: str
    source_refs: list[str]
```

Handoff를 prose 한 문단으로만 만들면 ID·금액·상태가 누락되기 쉽습니다.

### 3. Codex에서 “승인”이 필요한 coding action

예를 들어 `git push`는 Rules에서 prompt로 분류할 수 있습니다.

```python
prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
    justification = "Remote writes require approval.",
)
```

하지만 이 command rule은 고객지원 escalation engine의 대체물이 아닙니다. 서로 다른 runtime과 책임 영역입니다.


### 공식 문서

- [Agents SDK human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- [Codex Rules](https://developers.openai.com/codex/rules)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

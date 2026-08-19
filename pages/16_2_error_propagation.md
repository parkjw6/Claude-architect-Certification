# 16.2 에러 전파 전략

> 📅 2026년 04월 05일 기준

---

## 구조화된 에러 컨텍스트

단순히 오류 메시지만 전파하면 다음 에이전트/단계가 상황을 이해하기 어렵습니다.

```python
# ❌ 단순한 오류 전파
raise Exception("데이터베이스 오류")

# ✅ 구조화된 오류 컨텍스트
return {
    "errorType": "database_timeout",
    "attemptedQuery": "SELECT * FROM orders WHERE customer_id = 123",
    "partialResults": [{"order_id": "ORD-001"}, {"order_id": "ORD-002"}],
    "isRetryable": True,
    "retryAfterSeconds": 30,
    "suggestedAlternatives": [
        "캐시된 데이터 사용",
        "부분 결과로 계속 진행"
    ]
}
```

---

## 에러 전파 체인

```
서브에이전트 → 코디네이터 → 사용자

각 단계에서:
1. 오류 유형 분류
2. 부분 결과 보존
3. 재시도 가능 여부 판단
4. 대안 제안
```

---

## 멀티에이전트에서 에러 처리

```python
def handle_subagent_error(error: dict, partial_results: list) -> dict:
    """서브에이전트 오류를 코디네이터가 처리"""
    
    if error["isRetryable"]:
        # 재시도
        return retry_subagent(error["attemptedTask"])
    
    elif error.get("partialResults"):
        # 부분 결과로 계속
        return {
            "status": "partial",
            "data": error["partialResults"],
            "warning": f"일부 데이터 누락: {error['errorType']}"
        }
    
    else:
        # 대안 사용
        for alternative in error.get("suggestedAlternatives", []):
            result = try_alternative(alternative)
            if result:
                return result
        
        # 최후 수단: 에스컬레이션
        return escalate_to_human(error)
```

---

## 에러 컨텍스트 보존

```
에러 전파 시 반드시 포함:
✅ 오류 유형 (errorType)
✅ 시도된 작업 (attemptedQuery/Task)
✅ 부분 결과 (partialResults)
✅ 재시도 가능 여부 (isRetryable)
✅ 대안 방법 (suggestedAlternatives)

❌ 포함하면 안 되는 것:
- 스택 트레이스 전체 (민감한 내부 정보)
- 데이터베이스 연결 문자열
```

---

> 🔗 다음: [16.3 대규모 코드베이스 탐색](16_3_large_codebase.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Typed error envelope과 partial success

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | command/tool 실패를 숨기지 않고 실행하지 못한 검증과 부분 결과를 보고합니다. |
| **Codex app** | thread별 실패와 결과를 사람이 검토할 수 있지만 error contract 자체는 code에서 정의합니다. |
| **Codex SDK** | Codex result와 exception을 내부 error envelope으로 변환합니다. |
| **OpenAI Agents SDK** | tool error, partial success, retry/escalation routing을 coordinator가 처리합니다. |

### 1. 공통 error envelope

```python
from typing import Generic, Literal, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    category: Literal[
        "transient",
        "validation",
        "permission",
        "not_found",
        "business",
        "unknown",
    ]
    code: str
    message: str
    retryable: bool
    attempted_action: str
    retry_after_seconds: int | None = None
    suggested_actions: list[str] = []


class ResultEnvelope(BaseModel, Generic[T]):
    status: Literal["success", "partial", "failed"]
    data: T | None = None
    partial_data: T | None = None
    error: ErrorDetail | None = None
```

### 2. Retry router

```python
def next_action(result: ResultEnvelope) -> str:
    if result.status == "success":
        return "continue"

    if result.error is None:
        return "escalate"

    if result.error.category == "transient":
        return "retry_with_backoff"

    if result.error.category == "validation":
        return "repair_input"

    if result.error.category == "not_found":
        return "ask_for_more_information"

    if result.error.category in {"permission", "business"}:
        return "request_approval_or_escalate"

    return "escalate"
```

### 3. Partial success를 명시한다

멀티에이전트 연구나 여러 backend 조회에서는 하나가 실패해도 전체를 실패 처리할 필요가 없을 수 있습니다.

```json
{
  "status": "partial",
  "data": {
    "customer": {"id": "C-17"},
    "order": null
  },
  "error": {
    "category": "transient",
    "code": "ORDER_DB_TIMEOUT",
    "retryable": true,
    "attempted_action": "lookup_order:ORD-92",
    "message": "Order database timed out"
  }
}
```

Coordinator는 부분 결과를 숨기지 않고 최종 응답의 제한사항에 반영해야 합니다.

### 4. 민감 정보 제거

Agent에 전달할 오류에는 다음을 포함하지 않습니다.

- database connection string
- access token
- 전체 stack trace의 secret
- 내부 user PII
- production filesystem path가 불필요하게 노출되는 정보

운영 log에는 상세 trace를 보관하고 agent에는 correlation ID와 정제된 오류만 제공합니다.

### 5. 동일 요청 재실행의 idempotency

Side effect tool의 timeout은 “실행되지 않았다”는 뜻이 아닙니다. 결제·환불·ticket 생성에는 idempotency key와 조회 가능한 operation status가 필요합니다.

```text
timeout
→ operation status 조회
→ 미실행 확인
→ 같은 idempotency key로 retry
```


### 공식 문서

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

<!-- CODEX-ADDENDUM-END -->

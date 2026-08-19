# 13.2 스키마 설계 원칙

> 📅 2026년 04월 05일 기준

---

## 핵심 원칙: nullable 필드

```python
# ❌ 잘못된 설계 — 없는 값을 추측하게 만듦
{
    "properties": {
        "tax_rate": {"type": "number"}  # null 불가
    },
    "required": ["tax_rate"]
}
# 세율이 없으면 LLM이 임의로 값 생성 (환각!)

# ✅ 올바른 설계 — null 명시 허용
{
    "properties": {
        "tax_rate": {
            "type": ["number", "null"],
            "description": "세율 %. 문서에 명시되지 않은 경우 null"
        }
    },
    "required": ["tax_rate"]
}
```

---

## 스키마 설계 체크리스트

```
□ 문서에 항상 있는 필드만 required에 포함
□ 선택적 필드는 nullable (["type", "null"])
□ 설명에 "없으면 null" 명시
□ 날짜는 ISO 8601 형식 지정 (YYYY-MM-DD)
□ 금액은 숫자 타입 (통화 기호 제거 지시)
□ enum으로 허용 값 제한
```

---

## 완전한 스키마 예시

```python
INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        # 필수 — 항상 존재
        "invoice_number": {
            "type": "string",
            "description": "인보이스 번호 (예: INV-2024-001)"
        },
        "vendor_name": {
            "type": "string",
            "description": "발행 회사명"
        },
        "total_amount": {
            "type": "number",
            "description": "총 금액 (통화 기호 제외, 숫자만)"
        },
        # 선택적 — nullable
        "tax_rate": {
            "type": ["number", "null"],
            "description": "세율 %. 명시되지 않으면 null"
        },
        "payment_terms": {
            "type": ["string", "null"],
            "enum": ["net30", "net60", "immediate", None],
            "description": "지불 조건. 명시되지 않으면 null"
        },
        "due_date": {
            "type": ["string", "null"],
            "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
            "description": "지불 기한 YYYY-MM-DD. 없으면 null"
        }
    },
    "required": [
        "invoice_number", "vendor_name", "total_amount",
        "tax_rate", "payment_terms", "due_date"
    ]
}
```

---

> 🔗 다음: [13.3 검증과 재시도 루프](13_3_validation_retry.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Pydantic 중심의 nullable·enum·근거 schema

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | review/report schema를 JSON Schema file로 관리할 수 있습니다. |
| **Codex app** | CLI와 같은 Codex coding agent와 repository 설정을 데스크톱 UI에서 사용합니다. 이 장에는 별도 app-only 동작이 없으므로 CLI 설명을 자연어로 실행하면 됩니다. |
| **Codex SDK** | coding automation 결과 contract를 내부 type으로 다룰 수 있으나 business extraction schema 자체는 application 계층에서 설계합니다. |
| **OpenAI Agents SDK** | Agent final output과 tool argument의 typed contract를 설계합니다. |

> **별도 OpenAI API 계층:** Pydantic/JSON Schema 기반 Structured Outputs가 핵심입니다.

### 1. Optional은 “생략 가능”과 “null 가능”을 명확히 설계한다

문서 추출에서는 source에 없는 값을 강제로 채우게 하지 않습니다.

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    document_id: str
    page: Optional[int] = None
    excerpt: str


class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = Field(default=None, ge=0)
    currency: Optional[Literal["KRW", "USD", "EUR", "JPY", "other"]] = None
    currency_detail: Optional[str] = None
    due_date: Optional[str] = None
    evidence: list[Evidence] = []
```

`currency == "other"`일 때 `currency_detail`이 필요하다는 관계는 schema만으로 끝내지 말고 semantic validator에서 확인합니다.

```python
def validate_invoice(invoice: Invoice) -> list[str]:
    errors: list[str] = []

    if invoice.currency == "other" and not invoice.currency_detail:
        errors.append("currency_detail required for other currency")

    if invoice.total_amount is not None and not invoice.evidence:
        errors.append("amount requires source evidence")

    return errors
```

### 2. 추출 상태를 별도 필드로 둔다

모든 값이 `null`인 이유를 구분해야 합니다.

```python
class ExtractionEnvelope(BaseModel):
    status: Literal[
        "ok",
        "partial",
        "not_found",
        "access_error",
        "parse_error",
    ]
    data: Optional[Invoice]
    error_message: Optional[str] = None
```

```text
not_found
= 문서를 정상적으로 읽었으나 정보가 없음

access_error
= 문서에 접근하지 못함

parse_error
= 읽었지만 형식을 해석하지 못함
```

이 구분이 있어야 retry와 escalation을 정확히 결정할 수 있습니다.

### 3. Schema에서 권장할 세부 사항

- 가능한 경우 `additionalProperties: false`
- enum은 안정된 canonical value로 제한
- free-text detail은 별도 nullable field
- 날짜는 ISO 8601로 정규화하되 실제 날짜 유효성 검증
- 금액과 통화는 분리
- 중요한 claim에는 evidence/source를 함께 저장
- source에 없는 값을 계산한 경우 `derived: true`와 계산식을 기록

### 4. Schema 변경은 API contract 변경이다

Downstream system이 결과를 소비하면 schema version을 둡니다.

```python
class ExtractionEnvelopeV1(BaseModel):
    schema_version: Literal["1.0"]
    status: Literal["ok", "partial", "not_found"]
    data: Optional[Invoice]
```

Prompt만 바꾸는 것과 달리 필드 삭제·enum 변경은 consumer를 깨뜨릴 수 있으므로 migration과 compatibility test가 필요합니다.


### 공식 문서

- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

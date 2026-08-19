# 13.1 tool_use와 JSON 스키마

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 — tool_use가 보장하는 것 vs 않는 것

---

## tool_use로 구조화된 출력

```python
# tool_use 사용 시 JSON 구문 오류 API 수준에서 제거
response = client.messages.create(
    model="claude-sonnet-4-6",
    tools=[{
        "name": "extract_data",
        "description": "데이터 추출",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "amount": {"type": "number"},
                "date": {"type": ["string", "null"]}
            },
            "required": ["name", "amount", "date"]
        }
    }],
    tool_choice={"type": "tool", "name": "extract_data"},
    messages=[{"role": "user", "content": "..."}]
)

# 결과는 항상 올바른 JSON 구조
data = response.content[0].input
```

---

## tool_use가 보장하는 것

```
✅ JSON 구문 오류 없음
✅ 스키마에 정의된 필드 존재
✅ 필드 타입 (string, number, boolean, null 등)

❌ 보장 안 함:
- 값이 실제로 정확한가 (의미적 정확성)
- 숫자 합산이 맞는가
- 날짜가 실제로 유효한가
→ 이는 별도 검증 필요!
```

---

## 일반 텍스트 응답 vs tool_use

```python
# 일반 텍스트 응답 — JSON 추출 불안정
response_text = """
{
  "name": "홍길동",
  "amount": 150.00
  "date": null  ← 콤마 누락 — 파싱 오류!
}
"""

# tool_use — API 수준 보장
tool_result = {
    "name": "홍길동",
    "amount": 150.00,
    "date": None    ← 항상 올바른 형식
}
```

---

## 스키마 설계 팁

```python
# 선택적 필드는 nullable로
{
    "type": "object",
    "properties": {
        "required_field": {"type": "string"},
        "optional_field": {
            "type": ["number", "null"],   # ← nullable!
            "description": "없으면 null"
        }
    },
    "required": ["required_field", "optional_field"]
    # optional_field도 required에 포함하되 null 허용
}
```

---

> 🔗 다음: [13.2 스키마 설계 원칙](13_2_schema_design.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 구조 보장과 의미 보장의 분리

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | CI/script 결과에는 `--output-schema`를 사용합니다. |
| **Codex app** | interactive 결과 검토에는 적합하지만 downstream parser용 schema interface로 설명하지 않습니다. |
| **Codex SDK** | Codex thread result를 code에서 다룹니다. 실제 function execution과 final data schema를 혼동하지 않습니다. |
| **OpenAI Agents SDK** | tool execution에는 function tool, final typed result에는 agent output type을 사용합니다. |

> **별도 OpenAI API 계층:** Function Calling과 Structured Outputs를 목적에 따라 구분합니다.

### 1. OpenAI에서 선택 기준

```text
모델이 실제 function을 호출해야 함
→ Function Calling

모델의 최종 결과를 Pydantic/JSON Schema로 받아야 함
→ Structured Outputs

Codex CLI의 결과를 CI가 파싱해야 함
→ --output-schema
```

단순 추출 결과를 받기 위해 실행할 필요가 없는 “가상 tool”을 만들기보다 Structured Outputs를 사용하면 목적이 더 명확합니다.

### 2. 최종 출력 schema 예시

```python
from typing import Optional
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()


class ExtractedData(BaseModel):
    name: Optional[str]
    amount: Optional[float]
    date: Optional[str]


response = client.responses.parse(
    model="gpt-5.6",
    input=(
        "Extract the fields. "
        "Use null for values not explicitly present.\n\n"
        + source_text
    ),
    text_format=ExtractedData,
)

data = response.output_parsed
```

### 3. “올바른 JSON”의 두 단계

```text
Syntactic/schema correctness
- JSON 파싱 가능
- field와 type이 schema와 일치

Semantic correctness
- 값이 source와 일치
- 숫자·날짜·ID가 실제 근거를 가짐
- business relation이 유효
```

구조화 기능은 첫 번째를 강하게 보장하지만 두 번째는 별도 검증 대상입니다.

```python
def validate_against_source(data: ExtractedData, source: str) -> list[str]:
    errors: list[str] = []

    if data.name is not None and data.name not in source:
        errors.append("name has no direct source evidence")

    if data.amount is not None and data.amount < 0:
        errors.append("amount cannot be negative")

    return errors
```

### 4. Function Calling을 써야 하는 경우

```python
def save_invoice(invoice_id: str, amount: float) -> dict:
    """Persist a validated invoice."""
    ...
```

이처럼 실제 side effect가 있는 기능은 function tool로 노출합니다. 하지만 저장 전에 authoritative application code가 validation과 authorization을 다시 수행해야 합니다.


### 공식 문서

- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

# 13.3 검증과 재시도 루프

> 📅 2026년 04월 05일 기준

---

## 검증-재시도 패턴

```python
def extract_with_retry(document: str, max_retries: int = 3) -> dict:
    """추출 + 검증 + 재시도"""
    
    for attempt in range(max_retries):
        # 1. 추출 시도
        result = extract_with_tool_use(document)
        
        # 2. 검증
        errors = validate(result)
        
        if not errors:
            return result  # 성공!
        
        # 3. 오류 피드백으로 재시도
        print(f"시도 {attempt+1} 실패: {errors}")
        
        # 오류를 문서와 함께 다시 시도
        document = f"""
이전 추출 오류:
{errors}

위 오류를 수정하여 다시 추출하세요:
{document}
"""
    
    # 최대 재시도 후 부분 결과
    return {"data": result, "validation_errors": errors}
```

---

## 검증 레이어 설계

```python
def validate(data: dict) -> list[str]:
    """구조적 + 의미적 검증"""
    
    errors = []
    
    # 구조적 검증 (tool_use가 대부분 처리하지만 추가 확인)
    if not data.get("invoice_number"):
        errors.append("invoice_number 필수")
    
    # 의미적 검증 (tool_use가 보장하지 않음)
    amount = data.get("total_amount")
    if amount is not None and amount < 0:
        errors.append(f"total_amount 음수 불가: {amount}")
    
    due_date = data.get("due_date")
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"due_date 형식 오류: {due_date}")
    
    # 비즈니스 규칙 검증
    tax = data.get("tax_rate")
    if tax is not None and (tax < 0 or tax > 100):
        errors.append(f"tax_rate 범위 오류: {tax}% (0-100)")
    
    return errors
```

---

## 재시도 전략

```
재시도 가능:
- 날짜 형식 오류 (피드백으로 수정 가능)
- 금액 형식 오류 (다시 시도하면 수정 가능)

재시도 불필요:
- 필수 정보가 문서에 없음 (찾을 수 없음)
- 문서 자체가 손상됨

최대 재시도: 3회 (기본값)
```

---

> 🔗 다음: [Chapter 14: 배치 처리와 리뷰 아키텍처](14_batch_review.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 검증 오류와 재시도 가능성의 분리

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | command 실패와 final schema 결과를 분리하고 재실행 여부를 결정합니다. |
| **Codex app** | 사람이 실패와 diff를 보고 재지시할 수 있습니다. 자동 retry policy는 CLI/SDK/application code에서 명시합니다. |
| **Codex SDK** | thread 결과를 검사하고 같은 thread 또는 새 thread에서 제한적으로 재시도합니다. |
| **OpenAI Agents SDK** | tool error, RunState, retry/escalation routing을 application code로 구현합니다. |

> **별도 OpenAI API 계층:** transient API error와 semantic validation failure를 구분합니다.

### 1. 재시도는 오류 유형에 따라 결정한다

```text
transient API/network error
→ exponential backoff로 재시도

schema 또는 형식 오류
→ validation feedback과 함께 제한적 재시도

source에 정보가 없음
→ 재시도하지 않고 null/not_found

permission error
→ 권한 변경 또는 human intervention

business rule violation
→ 동일 입력 재시도 금지
```

### 2. Typed validation loop

```python
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ValidationFailure:
    category: Literal[
        "format",
        "semantic",
        "missing_source",
        "permission",
        "business",
    ]
    message: str
    retryable: bool


def classify_failures(errors: list[str]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []

    for error in errors:
        if "no source evidence" in error:
            failures.append(
                ValidationFailure(
                    category="missing_source",
                    message=error,
                    retryable=False,
                )
            )
        elif "invalid date format" in error:
            failures.append(
                ValidationFailure(
                    category="format",
                    message=error,
                    retryable=True,
                )
            )
        else:
            failures.append(
                ValidationFailure(
                    category="semantic",
                    message=error,
                    retryable=True,
                )
            )

    return failures
```

### 3. 원본 입력을 변형하지 말고 시도 이력을 별도로 유지

원문의 앞에 오류 메시지를 계속 붙이면 source와 instruction이 뒤섞입니다.

```python
def build_retry_input(
    *,
    original_document: str,
    previous_result: str,
    errors: list[str],
) -> list[dict]:
    return [
        {
            "role": "system",
            "content": (
                "Re-extract the document. "
                "Never invent missing values."
            ),
        },
        {
            "role": "user",
            "content": original_document,
        },
        {
            "role": "user",
            "content": (
                "Previous result:\n"
                f"{previous_result}\n\n"
                "Validation errors:\n- "
                + "\n- ".join(errors)
            ),
        },
    ]
```

### 4. 최대 재시도 뒤에는 상태를 숨기지 않는다

```json
{
  "status": "partial",
  "data": {
    "invoice_number": "INV-17",
    "total_amount": null
  },
  "validation_errors": [
    "total amount has no source evidence"
  ],
  "attempt_count": 3
}
```

“최선의 결과”만 반환하면서 실패 정보를 버리면 downstream이 정상 결과로 오해할 수 있습니다.


### 공식 문서

- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Responses API](https://developers.openai.com/api/docs/guides/responses)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

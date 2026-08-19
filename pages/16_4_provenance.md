# 16.4 정보 출처 보존

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 — 상충 정보 처리

---

## 정보 출처 보존이 중요한 이유

```
두 소스에서 다른 정보가 올 때:
소스 A: "가격 $99.99"
소스 B: "가격 $89.99"

❌ 임의 선택: 둘 중 하나를 선택하여 보고
✅ 출처 보존: 두 값을 모두 출처와 함께 보고
```

---

## 상충 정보 처리 패턴

```python
def handle_conflicting_info(sources: list[dict]) -> dict:
    """상충 정보를 출처와 함께 보고"""
    
    consolidated = {}
    conflicts = []
    
    for field in get_all_fields(sources):
        values = [(s["source"], s["data"].get(field)) for s in sources]
        
        # 모든 소스가 동의하는 경우
        unique_values = set(v for _, v in values if v is not None)
        
        if len(unique_values) == 1:
            consolidated[field] = list(unique_values)[0]
        
        elif len(unique_values) > 1:
            # 상충 — 모두 보고
            conflicts.append({
                "field": field,
                "values": [
                    {"source": src, "value": val}
                    for src, val in values
                ],
                "requires_human_review": True
            })
    
    return {
        "consolidated": consolidated,
        "conflicts": conflicts,
        "confidence": "low" if conflicts else "high"
    }
```

---

## 출처 추적 패턴

```python
# 모든 데이터에 출처 메타데이터 포함
def fetch_with_provenance(source_name: str, query: str) -> dict:
    data = fetch_data(query)
    
    return {
        "data": data,
        "provenance": {
            "source": source_name,
            "fetched_at": datetime.now().isoformat(),
            "query": query,
            "confidence": "high"
        }
    }
```

---

## 시험 핵심 정리

```
Q: 두 소스에서 다른 가격 정보가 오면?
A: 두 가격을 모두 출처와 함께 보고하고 인간 검토 요청

Q: 상충 정보를 임의로 선택하는 것의 문제는?
A: 어떤 정보가 맞는지 알 수 없고, 오류 원인 추적이 불가능

✅ 원칙: 불확실한 상황에서 임의 선택 금지
→ 두 값을 출처와 함께 투명하게 제공
```

---

> 🔗 다음: [Part 7: 실전 시나리오](17_scenario1_customer_support.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 근거 중심 schema와 충돌 보존

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | review finding에 file/line/evidence를 요구합니다. |
| **Codex app** | diff와 source를 시각적으로 확인하기 편하지만 provenance schema는 동일합니다. |
| **Codex SDK** | Codex 결과를 claim/source object로 변환해 내부 system에 저장합니다. |
| **OpenAI Agents SDK** | 여러 specialist 결과의 source mapping과 conflict를 synthesis 단계에서 보존합니다. |

### 1. Claim과 source를 같은 object에 둔다

```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class Source(BaseModel):
    source_id: str
    title: str
    uri_or_path: str
    retrieved_at: datetime
    published_at: datetime | None = None
    page_or_line: str | None = None
    excerpt: str


class Finding(BaseModel):
    claim: str
    evidence: str
    source: Source
    confidence_label: Literal["high", "medium", "low"]
    temporal_note: str | None = None
```

`confidence_label`은 source 품질과 직접성에 대한 설명적 label이지 통계적으로 교정된 확률로 취급하지 않습니다.

### 2. 상충 정보는 별도 conflict object로 유지

```python
class ConflictingValue(BaseModel):
    value: str
    source: Source


class Conflict(BaseModel):
    field: str
    values: list[ConflictingValue]
    reason_for_difference: str | None = None
    resolution_status: Literal[
        "unresolved",
        "resolved_by_policy",
        "resolved_by_human",
    ]
```

다음은 금지합니다.

```text
첫 번째 값 자동 선택
최신 값 무조건 선택
평균 계산
source를 제거한 단일 숫자만 보고
```

정책상 source priority가 정해져 있다면 그 정책을 code로 적용하고 어떤 규칙으로 해결했는지 기록합니다.

### 3. 코드 리뷰에서도 provenance가 필요하다

```json
{
  "claim": "authorization can be bypassed",
  "source": {
    "path": "backend/api/admin.py",
    "lines": "81-96"
  },
  "evidence": "role check occurs only in the UI path",
  "reachable_path": "POST /admin/export -> export_data",
  "impact": "non-admin user can export records"
}
```

“보안 문제가 있을 수 있다”처럼 파일·line·path가 없는 finding은 review gate에 사용하지 않습니다.

### 4. Temporal metadata

가격, 규정, API spec처럼 바뀌는 정보는 다음을 보존합니다.

```text
published_at
retrieved_at
effective_date
policy_version
model/docs version
```

상충이 날짜 차이에서 생겼는지, 정의 차이에서 생겼는지 판단할 수 있어야 합니다.

### 5. 최종 synthesis에서 source를 잃지 않는다

Subagent 결과를 coordinator가 요약할 때 `claim_id → source_id` 관계를 유지합니다. 최종 문장만 생성하고 source mapping을 버리면 후속 검증이 불가능합니다.


### 공식 문서

- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Codex subagents](https://developers.openai.com/codex/subagents)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

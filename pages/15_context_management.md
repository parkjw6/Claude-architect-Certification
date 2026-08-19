# Chapter 15: 컨텍스트 관리 전략

> 📅 2026년 04월 05일 기준  
> 🎯 Domain 5: 15% — Lost-in-the-Middle, 구조화된 사실 추출


[← Chapter 14](14_batch_review.md) | [목차](../TOC.md) | [Chapter 16: 에스컬레이션 →](16_escalation_reliability.md)

---

## 15.1 컨텍스트 창의 한계와 대응

### 컨텍스트 누적 문제

```
초기 상태:
[시스템 프롬프트] [사용자 메시지]

여러 툴 호출 후:
[시스템 프롬프트] [사용자 메시지] 
[툴1 응답 - 40개 필드] [툴2 응답 - 40개 필드]
[툴3 응답 - 40개 필드] [툴4 응답 - 40개 필드]
...
→ 컨텍스트가 순식간에 가득 참!
```

### 툴 결과 트리밍 (Trimming)

```python
def trim_order_result(raw_order: dict) -> dict:
    """주문 조회 결과에서 필요한 필드만 추출"""
    
    # 원본: 40개 이상의 필드
    # 환불 처리에 필요한 5개만 유지
    return {
        "order_id": raw_order["order_id"],
        "status": raw_order["status"],
        "items": raw_order["items"],
        "total_amount": raw_order["total_amount"],
        "customer_id": raw_order["customer_id"]
        # 나머지 35개 필드는 제거
    }
```

---

## 15.2 Lost-in-the-Middle 효과

> 🎯 시험 최빈출 개념

### 현상 설명

```
긴 컨텍스트 처리 시 주의도 분포:

높음 ▲
     |█                              █
     |██                            ██
     |███                          ███
     |████                        ████
낮음 |─────████████████████████─────
     시작                         끝
     ← 잘 처리됨  중간 (누락 위험)  잘 처리됨 →
```

### 대응 전략

```python
def structure_for_attention(data: dict) -> str:
    """중요 정보를 앞뒤에 배치하여 주의도 최적화"""
    
    return f"""
## ⚠️ 핵심 사실 (반드시 참조)
고객 ID: {data['customer_id']}
주문 ID: {data['order_id']}
환불 금액: {data['refund_amount']}
기한: {data['deadline']}

## 상세 분석 결과
{data['detailed_analysis']}

## ✅ 요약 및 권장 조치
{data['summary']}
중요: 위의 핵심 사실과 일치하는지 확인하세요.
"""
```

---

## 15.3 Progressive Summarization 주의점

### 위험한 요약

```python
# ❌ 잘못된 요약 (수치 정보 손실)
wrong_summary = """
고객이 여러 주문에 대해 문제를 제기했습니다.
환불 처리가 필요한 상황입니다.
"""
# → "여러 주문", "어느 정도의 환불" → 실제 처리 불가!

# ✅ 올바른 요약 (수치 정보 보존)
correct_summary = """
고객 (ID: CUST-2024-789):
- 주문 #ORD-001: $45.99 환불 요청 (손상 제품)
- 주문 #ORD-002: $120.00 부분 환불 (배송 지연 보상)
- 총 환불 예정: $165.99
- 고객 요구: 영업일 기준 3일 이내 처리
"""
```

### 구조화된 사실 블록 패턴

```python
CASE_FACTS_TEMPLATE = """
## CASE FACTS (항상 참조)
고객 ID: {customer_id}
이름: {customer_name}
연락처: {contact}

주문 이슈:
{issues}

금액 정보:
{amounts}

기한 및 약속:
{deadlines}

현재 상태: {current_status}
"""

def create_case_facts(customer_data: dict) -> str:
    """각 프롬프트에 포함할 불변 사실 블록"""
    return CASE_FACTS_TEMPLATE.format(**customer_data)

# 매 API 호출마다 포함
def process_customer_request(customer_data: dict, user_message: str):
    case_facts = create_case_facts(customer_data)
    
    return client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=f"""
당신은 고객 지원 에이전트입니다.

{case_facts}

위의 CASE FACTS를 항상 참조하여 정확한 정보를 제공하세요.
""",
        messages=[{"role": "user", "content": user_message}]
    )
```

---

## 📝 챕터 요약

- 툴 결과 트리밍: 불필요한 필드 제거로 컨텍스트 절약
- Lost-in-the-Middle: 중간 정보가 누락될 수 있음 → 중요 정보는 앞뒤에 배치
- 요약 시 수치(금액, 날짜, 주문번호) 반드시 보존
- 구조화된 사실 블록: 매 프롬프트에 핵심 사실 포함

---

> 🔗 다음 챕터: [에스컬레이션과 신뢰성](16_escalation_reliability.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Codex context 관리 도구와 상태 분리

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | `/compact`, `/side`, subagent로 main coding context를 관리합니다. |
| **Codex app** | 여러 project/thread를 화면에서 유지하고 장시간 작업 사이를 전환하는 것이 app-only UI 장점입니다. |
| **Codex SDK** | thread ID로 coding session을 계속하거나 resume하고, 여러 thread의 상태를 application이 관리합니다. |
| **OpenAI Agents SDK** | Session, RunState, 결과 요약, tool state를 production agent application에서 관리합니다. |

> **별도 OpenAI API 계층:** Responses API compaction은 lower-level context 기능입니다.

### 1. Codex의 세 가지 context 관리 층

```text
현재 대화를 압축
→ /compact

잠깐 별도 방향을 탐색
→ /side

대량 탐색·리뷰를 별도 agent thread로 격리
→ subagent
```

`/compact`는 대화를 계속하기 위한 요약입니다. 중요한 business state를 저장하는 database가 아닙니다.

### 2. 대규모 탐색을 main thread에서 하지 않는다

```text
Main Codex
  └─ explorer subagent
       ├─ 파일 구조 탐색
       ├─ symbol/search
       ├─ call path 추적
       └─ 정제된 evidence summary 반환
```

Main에는 다음 정도만 남깁니다.

```json
{
  "entry_point": "api/routes/refunds.py:create_refund",
  "call_path": [
    "RefundService.create",
    "RefundPolicy.validate",
    "PaymentGateway.refund"
  ],
  "invariants": [
    "customer verification precedes refund",
    "amount > 500 requires approval"
  ],
  "open_questions": [
    "retry idempotency key ownership is unclear"
  ]
}
```

### 3. Tool output 자체를 줄인다

외부 API/MCP tool이 50개 field를 반환하더라도 모델에 전부 보내지 않습니다.

```python
def trim_order(raw: dict) -> dict:
    return {
        "order_id": raw["order_id"],
        "customer_id": raw["customer_id"],
        "status": raw["status"],
        "total": raw["total"],
        "refundable": raw["refundable"],
    }
```

Tool boundary에서 데이터를 줄이면 token 비용뿐 아니라 잘못된 field를 근거로 사용하는 위험도 줄어듭니다.

### 4. 대화 context와 authoritative state를 분리

```python
from pydantic import BaseModel


class CaseState(BaseModel):
    customer_id: str
    verified: bool
    order_ids: list[str]
    approved_refund_limit: float
    policy_version: str
```

이 상태는 database/session store에 보관하고, 모델에는 현재 action에 필요한 snapshot만 전달합니다.

### 5. Responses API compaction

API 애플리케이션에서는 server-side compaction을 구성할 수 있습니다.

```python
response = client.responses.create(
    model="gpt-5.6",
    input=messages,
    context_management=[
        {
            "type": "compaction",
            "compact_threshold": 200_000,
        }
    ],
)
```

Compaction 결과는 conversation continuity를 위한 것이며 금액·승인·identity의 authoritative record를 대체하지 않습니다.



### Codex SDK의 thread continuity

Codex SDK에서는 conversation을 단순 message 배열로 직접 이어 붙이기보다 Codex thread를 시작하고 같은 thread에서 turn을 이어가거나 thread ID로 resume할 수 있습니다.

#### TypeScript

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();

const exploration = await thread.run(
  "Trace the authentication flow and summarize the relevant files"
);

console.log(exploration.finalResponse);

const implementation = await thread.run(
  "Using the established context, fix the token refresh bug"
);

console.log(implementation.finalResponse);

// Application이 저장해 둔 thread ID로 재개
const resumed = codex.resumeThread("<thread-id>");
const review = await resumed.run(
  "Review the current diff and list remaining risks"
);
```

#### Python

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(
        sandbox=Sandbox.read_only,
    )

    exploration = thread.run(
        "Trace the authentication flow"
    )
    print(exploration.final_response)

    implementation = thread.run(
        "Implement the approved fix",
        sandbox=Sandbox.workspace_write,
    )
    print(implementation.final_response)
```

중요한 구분:

```text
Codex SDK thread state
= coding agent가 작업을 이어가기 위한 context

Application database/session state
= 승인, 금액, identity, 정책 버전의 source of truth
```

### 공식 문서

- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex slash commands](https://developers.openai.com/codex/cli/slash-commands)
- [Responses API compaction](https://developers.openai.com/api/docs/guides/compaction)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

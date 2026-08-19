# Chapter 17: 시나리오 1 — 고객 지원 에이전트

> 📅 2026년 04월 05일 기준  
> 🎯 실제 시험 시나리오 1 해설


[← Chapter 16](16_escalation_reliability.md) | [목차](../TOC.md) | [Chapter 18: 시나리오 2 →](18_scenario2_code_generation.md)

---

## 시나리오 개요

> 당신은 Claude Agent SDK를 사용하여 고객 지원 에이전트를 구축하고 있습니다.
> 에이전트는 반품, 청구 분쟁, 계정 이슈 등 모호한 요청을 처리합니다.
> 백엔드에는 MCP 툴 4개가 있습니다: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`
> 목표: 80%+ 첫 접촉 해결율 (first-contact resolution)

---

## 핵심 아키텍처 결정

### 툴 구성

```python
customer_support_tools = [
    {
        "name": "get_customer",
        "description": """고객 계정 정보를 이메일 또는 전화번호로 검색합니다.
        
        사용 시점: 고객 신원 확인, 계정 상태 조회
        입력: email (str) 또는 phone (str)
        반환: customer_id, name, tier, account_status
        
        주의: 반드시 lookup_order나 process_refund 전에 호출해야 합니다.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "phone": {"type": "string"}
            }
        }
    },
    {
        "name": "lookup_order",
        "description": """주문 정보를 조회합니다.
        
        사용 시점: 특정 주문 확인, 환불 전 주문 검증
        필요 조건: get_customer 먼저 호출하여 customer_id 획득
        입력: order_id (str), customer_id (str, get_customer 결과)
        반환: order_id, status, items, total, shipping_info""",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "customer_id": {"type": "string"}
            },
            "required": ["order_id", "customer_id"]
        }
    },
    {
        "name": "process_refund",
        "description": """환불을 처리합니다.
        
        전제 조건: get_customer로 고객 확인, lookup_order로 주문 확인 후 사용
        $500 초과 환불은 자동 처리 불가 → escalate_to_human 사용
        입력: customer_id, order_id, amount, reason""",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
                "reason": {"type": "string"}
            },
            "required": ["customer_id", "order_id", "amount", "reason"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": """케이스를 인간 상담원에게 에스컬레이션합니다.
        
        사용 시점:
        - 고객이 명시적으로 사람 연결 요청
        - $500 초과 환불
        - 정책이 다루지 않는 예외
        
        반드시 structured handoff 요약 포함 필수.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "reason": {"type": "string"},
                "summary": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]}
            },
            "required": ["customer_id", "reason", "summary"]
        }
    }
]
```

### 프로그래밍적 게이트 구현

```python
class CustomerSupportWorkflow:
    """고객 지원 워크플로우 — 프로그래밍적 강제 적용"""
    
    def __init__(self):
        self.verified_customer_id = None
        self.verified_order_id = None
        self.client = anthropic.Anthropic()
    
    def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """툴 실행 with 프로그래밍적 전제조건 검사"""
        
        # 게이트 1: 환불은 고객 확인 후에만
        if tool_name == "process_refund":
            if not self.verified_customer_id:
                return {
                    "isError": True,
                    "message": "고객 확인 없이 환불 불가. get_customer 먼저 호출하세요.",
                    "required_action": "call_get_customer_first"
                }
            
            # 게이트 2: $500 초과 환불은 자동 처리 불가
            if tool_input.get("amount", 0) > 500:
                return {
                    "isError": True,
                    "errorCategory": "business",
                    "message": f"자동 환불 한도($500) 초과. 에스컬레이션 필요.",
                    "isRetryable": False,
                    "required_action": "escalate_to_human"
                }
        
        # 실제 툴 실행
        if tool_name == "get_customer":
            result = self._call_get_customer(tool_input)
            if result.get("customer_id"):
                self.verified_customer_id = result["customer_id"]
            return result
        
        elif tool_name == "lookup_order":
            result = self._call_lookup_order(tool_input)
            if result.get("order_id"):
                self.verified_order_id = result["order_id"]
            return result
        
        elif tool_name == "process_refund":
            return self._call_process_refund(tool_input)
        
        elif tool_name == "escalate_to_human":
            return self._call_escalate(tool_input)
    
    def handle_request(self, customer_message: str) -> str:
        """고객 요청 처리"""
        
        messages = [{
            "role": "user",
            "content": customer_message
        }]
        
        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=SUPPORT_AGENT_PROMPT,
                tools=customer_support_tools,
                messages=messages
            )
            
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text
                break
            
            elif response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self.execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        })
                
                messages.append({"role": "user", "content": tool_results})
```

---

## 시나리오 기반 예상 문제

### Q1: 고객 확인 건너뜀 문제
상황: 12%의 케이스에서 에이전트가 `get_customer`를 건너뛰고 `lookup_order`를 직접 호출합니다.

최선의 해결책은?

A) 프롬프트에 "반드시 get_customer를 먼저 호출하라"고 강조  
B) 프로그래밍적 게이트: lookup_order와 process_refund를 get_customer 성공 전에 차단  
C) few-shot 예시로 올바른 순서 보여주기  
D) 요청 유형에 따라 적절한 툴만 활성화하는 라우터 구현  

정답: B — 금융 거래에서 LLM 확률적 준수는 불충분. 프로그래밍적 강제만이 보장 가능.

---

## 📝 챕터 요약

- 고객 지원 에이전트: get_customer → lookup_order → process_refund 순서
- 순서 강제는 프롬프트가 아닌 프로그래밍적 게이트로
- $500 초과 환불은 자동 처리 불가 → hooks로 차단
- 에스컬레이션 시 구조화된 핸드오프 요약 필수
- 다중 고객 매칭 시 추가 식별자 요청

---

> 🔗 다음 챕터: [시나리오 2 — Claude Code로 코드 생성](18_scenario2_code_generation.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 고객 지원 시스템은 Codex CLI가 아니라 Agents SDK 영역

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | 고객지원 backend를 개발·테스트·리뷰하는 도구입니다. Production 고객 요청 runtime이 아닙니다. |
| **Codex app** | CLI와 같은 개발 작업을 UI에서 수행합니다. 고객지원 agent orchestration 기능으로 설명하지 않습니다. |
| **Codex SDK** | 고객지원 repository의 coding automation에는 쓸 수 있지만 고객 대화·환불 workflow의 primary runtime은 아닙니다. |
| **OpenAI Agents SDK** | 고객지원 agent, business tools, handoff, guardrail, HITL을 구현하는 primary runtime입니다. |

### 1. 제품 선택부터 바로잡기

이 시나리오의 주 실행 환경은 repository를 수정하는 Codex CLI가 아닙니다.

```text
고객 메시지를 받고
CRM·주문·환불 tool을 호출하고
conversation state를 유지
→ OpenAI Agents SDK

tool loop와 state를 직접 구현
→ Responses API

고객지원 backend 코드를 개발·수정
→ Codex
```

Codex는 이 서비스를 **만드는 개발 도구**일 수 있지만 production 고객 요청을 처리하는 runtime으로 직접 사용하지는 않습니다.

### 2. 권장 아키텍처

```text
Client
  ↓
Support API
  ↓
Support Agent
  ├─ get_customer
  ├─ lookup_order
  ├─ request_refund
  └─ create_handoff
  ↓
Application service
  ├─ identity gate
  ├─ authorization
  ├─ refund limit
  ├─ idempotency
  └─ audit log
  ↓
CRM / Order DB / Payment gateway
```

Agent는 다음 action을 고르지만 authoritative service가 허용 여부를 결정합니다.

### 3. Agents SDK 예시

```python
from dataclasses import dataclass
from typing import Literal

from agents import Agent, Runner
from agents.decorators import tool


@dataclass
class SupportState:
    verified_customer_id: str | None = None
    verified_order_id: str | None = None


class RefundService:
    def request_refund(
        self,
        *,
        verified_customer_id: str | None,
        order_customer_id: str,
        order_id: str,
        amount: float,
        idempotency_key: str,
    ) -> dict:
        if verified_customer_id is None:
            return {
                "status": "rejected",
                "reason": "customer_verification_required",
            }

        if verified_customer_id != order_customer_id:
            return {
                "status": "rejected",
                "reason": "customer_order_mismatch",
            }

        if amount > 500:
            return {
                "status": "approval_required",
                "reason": "refund_limit_exceeded",
            }

        return {
            "status": "accepted",
            "operation_id": execute_refund(
                order_id=order_id,
                amount=amount,
                idempotency_key=idempotency_key,
            ),
        }


refund_service = RefundService()


@tool
def lookup_customer(email: str) -> dict:
    """Find an exact customer by email. Never guess between multiple matches."""
    return crm_lookup_customer(email=email)


@tool
def lookup_order(
    customer_id: str,
    order_id: str,
) -> dict:
    """Return an order only when it belongs to the supplied customer."""
    return order_service_lookup(
        customer_id=customer_id,
        order_id=order_id,
    )


@tool
def request_refund(
    verified_customer_id: str,
    order_customer_id: str,
    order_id: str,
    amount: float,
    idempotency_key: str,
) -> dict:
    """Request a refund. The service enforces identity and monetary limits."""
    return refund_service.request_refund(
        verified_customer_id=verified_customer_id,
        order_customer_id=order_customer_id,
        order_id=order_id,
        amount=amount,
        idempotency_key=idempotency_key,
    )


support_agent = Agent(
    name="support_agent",
    instructions="""
Resolve customer requests using the provided tools.

Never invent identifiers.
When multiple customers match, ask for another identifier.
Explain approval-required and rejected states accurately.
Do not claim a refund completed unless the tool returns accepted.
""",
    tools=[
        lookup_customer,
        lookup_order,
        request_refund,
    ],
)

result = await Runner.run(
    support_agent,
    "I need a refund for order ORD-123.",
)
```

예시는 agent orchestration을 보여주기 위한 것입니다. 실제로는 인증 context에서 verified customer ID를 주입하고, 모델이 임의로 `verified_customer_id`를 만들어 tool argument로 보내지 못하도록 service/session 계층에서 재검증해야 합니다.

### 4. 민감 action의 human approval

```python
@tool(needs_approval=True)
async def approve_large_refund(
    order_id: str,
    amount: float,
) -> str:
    return approve_refund(order_id, amount)
```

Runner가 interruption을 반환하면 승인 UI나 workflow service에서 결정을 받은 뒤 `RunState`를 resume합니다. 모델에게 “승인되었다고 가정하라”고 요청해서는 안 됩니다.

### 5. Tool description의 경계

좋은 description은 다음을 포함합니다.

```text
무엇을 하는가
언제 쓰는가
어떤 exact identifier가 필요한가
빈 결과와 multiple match는 어떻게 반환하는가
비슷한 tool과 무엇이 다른가
side effect가 있는가
```

하지만 tool description은 보안 경계가 아닙니다. Identity, amount, ownership, idempotency는 코드에서 다시 검사합니다.

### 6. 에러와 부분 성공

```json
{
  "status": "partial",
  "customer": {"customer_id": "C-17"},
  "order": null,
  "error": {
    "category": "transient",
    "code": "ORDER_DB_TIMEOUT",
    "retryable": true
  }
}
```

Agent는 부분 성공을 정상 완료로 포장하지 않고, 재시도·대체·handoff를 선택해야 합니다.


### 공식 문서

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Agents SDK human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- [Agents SDK tools and agents-as-tools](https://openai.github.io/openai-agents-python/tools/)

<!-- CODEX-ADDENDUM-END -->

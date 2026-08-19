# 15.2 Lost-in-the-Middle 효과

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 개념

---

## 개념

LLM은 긴 컨텍스트에서 중간에 있는 정보를 놓치는 경향이 있습니다.

```
컨텍스트 위치와 정보 처리 품질:

처음 (높음)  ████████████
중간 (낮음)  ████
끝   (높음)  ████████████
```

---

## 실제 예시

```
컨텍스트:
[주요 규칙]                     ← 처음 (잘 기억)
...
[중간에 묻힌 예외 사항]           ← 중간 (놓칠 수 있음)
...
...많은 내용...
[또 다른 규칙]                   ← 끝 (잘 기억)

결과: 중간의 예외 사항이 무시됨
```

---

## 대응 전략

### 1. 중요 정보를 앞뒤에 배치

```python
SYSTEM_PROMPT = """
[핵심 제약 사항 — 항상 적용]
- $500 초과 환불은 수동 승인 필요
- 고객 확인 없이 주문 처리 금지

{배경 정보, 예시, 상세 가이드라인}

[핵심 제약 사항 요약 — 다시 확인]
- 금액 한도: $500
- 순서: get_customer → lookup_order → process_refund
"""
```

### 2. 섹션 헤더 사용

```
# 고객 확인 필수 (섹션 헤더)
...상세 내용...

# 환불 처리 (섹션 헤더)
...상세 내용...

# 에스컬레이션 기준 (섹션 헤더)
...상세 내용...
```

### 3. 구조화된 사실 블록

```
매 턴마다 핵심 사실 반복:

[현재 케이스 정보]
고객: 김철수 (ID: CUST-123)
주문: #45678 ($230.00)
요청: 파손 상품 환불
```

---

## 시험 포인트

```
Q: Lost-in-the-Middle 효과를 완화하려면?
A: 중요 정보를 컨텍스트의 처음과 끝에 배치

Q: 요약 시 특히 주의해야 할 것은?
A: 수치(금액, 날짜, ID 번호) 반드시 보존
```

---

> 🔗 다음: [15.3 Progressive Summarization 주의점](15_3_summarization.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 긴 입력의 구조화와 bounded subagent

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | 짧은 `AGENTS.md`, nested instruction, bounded Skill/subagent로 긴 context를 줄입니다. |
| **Codex app** | CLI와 같은 Codex coding agent와 repository 설정을 데스크톱 UI에서 사용합니다. 이 장에는 별도 app-only 동작이 없으므로 CLI 설명을 자연어로 실행하면 됩니다. |
| **Codex SDK** | 각 Codex thread의 task scope를 좁히고 summary object만 coordinator code에 전달합니다. |
| **OpenAI Agents SDK** | agent별 context contract와 structured state를 사용합니다. |

### 1. Lost-in-the-Middle 대응은 Codex에서도 동일하다

중요한 규칙을 긴 `AGENTS.md` 중간에 한 번만 넣는 것보다, 문서를 짧고 계층적으로 나누는 편이 낫습니다.

```text
root AGENTS.md
→ repo 공통 invariant

backend/AGENTS.md
→ backend 전용 규칙

payments/AGENTS.md
→ 결제 전용 규칙

Skill references
→ 특정 workflow의 긴 세부 기준
```

### 2. 중요 정보의 재배치

```markdown
# Critical constraints

- Never change the public API response schema.
- Do not perform production deployment.
- Preserve transaction atomicity.

# Background

... 상세 아키텍처 ...

# Completion check

Before finishing, verify again:

- public API unchanged
- no production action
- transaction remains atomic
```

중요한 내용을 무작정 여러 번 복제하기보다, 시작에 constraint를 두고 끝에 검증 checklist를 두는 방식이 좋습니다.

### 3. 거대한 입력을 agent별 bounded task로 나눈다

```text
❌ "저장소 전체를 다 읽고 모든 문제를 찾아라"

✅ explorer:
   "refund request의 entry point부터 gateway까지 call path만 추적"

✅ test reviewer:
   "변경된 refund behavior의 누락 test만 확인"

✅ migration reviewer:
   "schema backward compatibility만 확인"
```

Subagent마다 task boundary와 출력 schema를 명확히 해야 분해 후 범위가 다시 무한히 커지는 것을 막을 수 있습니다.

### 4. 중요 사실은 position보다 structure로 보호

```json
{
  "critical_facts": {
    "customer_id": "CUST-123",
    "order_id": "ORD-456",
    "refund_amount": 150.0,
    "currency": "USD",
    "deadline": "2026-08-22"
  },
  "analysis": "...",
  "required_action": "manager_approval"
}
```

JSON/Pydantic state는 prose 중간에 숫자를 묻어두는 것보다 검증하기 쉽습니다.

### 5. `AGENTS.md`를 무한정 키우지 않는다

Always-on instruction은 concise하게 유지하고, 긴 checklist·예시·workflow는 Skill로 이동합니다. 이는 context 절약뿐 아니라 소유권과 변경 이력을 명확하게 합니다.


### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)

- [Codex SDK](https://developers.openai.com/codex/sdk)
<!-- CODEX-ADDENDUM-END -->

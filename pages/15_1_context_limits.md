# 15.1 컨텍스트 창의 한계와 대응

> 📅 2026년 04월 05일 기준

---

## 컨텍스트 한계

```
Claude Opus/Sonnet: 1,000,000 토큰 ≈ 750만 단어
Claude Haiku:       200,000 토큰  ≈ 150만 단어

현실적 제한:
- 너무 긴 컨텍스트 = 비용 증가
- Lost-in-the-Middle 효과
- 응답 속도 저하
```

---

## 컨텍스트 관리 전략

### 1. 트리밍 (Trimming)

```python
def trim_old_messages(messages: list, max_tokens: int = 800_000) -> list:
    """오래된 메시지 제거"""
    
    while calculate_tokens(messages) > max_tokens:
        if len(messages) <= 2:  # 최소 유지
            break
        # 두 번째 메시지 제거 (첫 번째는 시스템/사용자 유지)
        messages.pop(1)
    
    return messages
```

### 2. 요약 (Summarization)

```python
def summarize_history(messages: list) -> str:
    """이전 대화를 요약으로 압축"""
    
    history_text = "\n".join([
        f"{m['role']}: {m['content']}" for m in messages[:-5]
    ])
    
    summary = claude.create(
        messages=[{
            "role": "user",
            "content": f"""다음 대화를 요약하세요.
수치(금액, 날짜, ID)를 반드시 포함하세요:
{history_text}"""
        }]
    )
    
    return summary.content[0].text
```

### 3. 핵심 사실 블록

```python
# 매 턴마다 핵심 사실 포함
FACTS_BLOCK = """
[핵심 사실 — 항상 참조]
고객 ID: CUST-12345
주문 번호: ORD-67890
환불 금액: $150.00
케이스 시작: 2024-03-10
"""
```

---

## 컨텍스트 효율화 팁

```
1. 필요한 정보만 포함 (불필요한 대화 제거)
2. 핵심 사실은 구조화된 블록으로
3. 오래된 세부 사항은 요약으로 압축
4. 중요 정보는 앞뒤에 배치
```

---

> 🔗 다음: [15.2 Lost-in-the-Middle 효과](15_2_lost_middle.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 고정 token 수 암기보다 모델·작업별 예산 관리

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | tool output trimming, phase 분리, subagent 격리가 중심입니다. |
| **Codex app** | 여러 thread를 별도 화면으로 유지하지만 각 thread의 context budget 문제 자체는 CLI와 같습니다. |
| **Codex SDK** | thread별 context와 resume를 code로 관리하고 output/log를 별도 artifact로 저장합니다. |
| **OpenAI Agents SDK** | Session/state store와 agent별 bounded context를 설계합니다. |

### 1. Claude의 token 수치를 Codex에 복사하지 않는다

Codex가 사용하는 model과 실행 환경에 따라 context window, output limit, compaction 동작이 달라질 수 있습니다. 따라서 특정 Claude model의 수치를 Codex의 고정 한계처럼 기록하면 안 됩니다.

권장 원칙:

```text
현재 model/documentation 확인
→ 작업별 input budget 설정
→ tool output 제한
→ subagent로 noisy work 격리
→ 필요 시 /compact
```

### 2. Context budget을 내용 유형별로 관리

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBudget:
    instructions: int
    source_evidence: int
    tool_results: int
    conversation: int
    output_reserve: int
```

정확한 token 계산이 아니더라도 category별 budget을 두면 대용량 로그가 중요한 지침을 밀어내는 문제를 줄일 수 있습니다.

### 3. 오래된 메시지를 무작정 제거하지 않는다

```text
절대 보존
- user goal
- accepted constraints
- IDs, amounts, dates
- decisions and approvals
- unresolved blockers

요약 가능
- 반복 설명
- 완료된 탐색 과정
- raw command logs
- 중복 tool output

외부 저장
- 전체 logs
- large source documents
- full test output
```

### 4. 실패 로그는 head/tail + 파일 경로로

```python
def summarize_command_output(
    output: str,
    *,
    head_lines: int = 80,
    tail_lines: int = 80,
) -> dict:
    lines = output.splitlines()

    if len(lines) <= head_lines + tail_lines:
        return {"truncated": False, "preview": output}

    return {
        "truncated": True,
        "preview": "\n".join(
            lines[:head_lines]
            + ["... output omitted ..."]
            + lines[-tail_lines:]
        ),
        "line_count": len(lines),
    }
```

전체 로그는 artifact/file에 보관하고 모델에는 핵심 preview와 경로를 전달합니다.

### 5. 긴 작업은 phase를 분리

```text
Phase 1: explore
Phase 2: decision/plan
Phase 3: implementation
Phase 4: validation
Phase 5: independent review
```

각 phase 종료 시 산출물을 파일로 남기면 conversation 하나에 모든 intermediate detail을 유지할 필요가 줄어듭니다.


### 공식 문서

- [Responses API compaction](https://developers.openai.com/api/docs/guides/compaction)
- [Codex subagents](https://developers.openai.com/codex/subagents)

- [Codex SDK](https://developers.openai.com/codex/sdk)
<!-- CODEX-ADDENDUM-END -->

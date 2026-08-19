# 14.2 멀티패스 리뷰 설계

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 — 자기 리뷰 vs 독립 인스턴스

---

## 자기 리뷰의 한계

```
❌ 자기 리뷰:
Claude A: "이 코드를 작성했습니다"
Claude A: "이제 내 코드를 리뷰하겠습니다"
→ 같은 모델 인스턴스, 같은 편향
→ 자신의 실수를 놓침

✅ 독립 인스턴스 리뷰:
Claude A: 코드 작성
Claude B: (새 세션, 다른 관점) 리뷰
→ 다른 관점으로 실수 발견
```

---

## 멀티패스 리뷰 구조

```python
def multipass_review(files: list[str]) -> dict:
    """
    1패스: 개별 파일 분석 (로컬 이슈)
    2패스: 크로스파일 통합 분석 (전역 이슈)
    """
    
    # 패스 1: 각 파일 개별 분석
    local_results = {}
    for file_path in files:
        content = read_file(file_path)
        local_results[file_path] = analyze_single_file(content)
    
    # 패스 2: 크로스파일 통합 (독립 인스턴스!)
    cross_file_issues = analyze_cross_dependencies(
        files=files,
        local_results=local_results
    )
    
    return {
        "local_issues": local_results,
        "cross_file_issues": cross_file_issues
    }
```

---

## 독립 인스턴스 구현

```python
def independent_review(code: str) -> str:
    """완전히 새로운 Claude 인스턴스로 리뷰"""
    
    # 새 클라이언트 = 새 인스턴스 (이전 컨텍스트 없음)
    reviewer = anthropic.Anthropic()
    
    response = reviewer.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""다음 코드를 독립적으로 리뷰하세요.
이 코드가 어떻게 작성되었는지 모르는 상태로 분석하세요:

{code}"""
        }]
    )
    
    return response.content[0].text
```

---

## 시험 핵심 정리

```
자기 리뷰 < 독립 인스턴스 리뷰

멀티패스 순서:
1. 파일별 로컬 분석
2. 크로스파일 통합 분석

독립 인스턴스 = 새 세션, 새 컨텍스트
```

---

> 🔗 다음: [Chapter 15: 컨텍스트 관리 전략](15_context_management.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 독립 context 리뷰와 Codex reviewer

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | `codex review` 또는 read-only subagent로 독립 review pass를 실행합니다. |
| **Codex app** | 구현 thread와 review thread를 분리하고 worktree/diff를 시각적으로 비교하는 데 유리합니다. |
| **Codex SDK** | 별도 Codex thread를 programmatically 생성해 local/cross-file review를 실행합니다. |
| **OpenAI Agents SDK** | 독립 reviewer agents와 synthesis agent를 구성합니다. |

### 1. 중요한 정정: 새 SDK client 객체만으로 독립 리뷰가 되지는 않는다

다음 코드는 transport client를 하나 더 만들 뿐입니다.

```python
reviewer = OpenAI()
```

독립성은 client 객체 수가 아니라 **이전 conversation/history를 전달하지 않는 별도 run**, 별도 subagent thread, 또는 별도 process에서 나옵니다.

```text
같은 client + 새 input/history 없음
→ 독립 context 가능

새 client + 이전 history 그대로 전달
→ 독립 context 아님
```

### 2. Codex에서의 독립 리뷰

```bash
# 현재 작업과 별도의 review workflow
codex review --uncommitted

# main과 비교
codex review --base main
```

대규모 PR에서는 custom reviewer를 사용합니다.

```toml
# .codex/agents/integration-reviewer.toml

name = "integration_reviewer"
description = "Read-only cross-file integration reviewer."
sandbox_mode = "read-only"

developer_instructions = """
Focus only on cross-file behavior:
- API/schema compatibility
- transaction boundaries
- state transitions
- cache invalidation
- migration compatibility

Do not repeat local style findings.
"""
```

### 3. 파일별 병렬 분석 + 통합 pass

```python
import asyncio
from agents import Agent, Runner

file_reviewer = Agent(
    name="file_reviewer",
    instructions=(
        "Review one file in the supplied diff. "
        "Return only evidence-backed local findings."
    ),
)

integration_reviewer = Agent(
    name="integration_reviewer",
    instructions=(
        "Review cross-file contracts using the local summaries."
    ),
)


async def multipass_review(file_inputs: list[str]) -> str:
    local_runs = [
        Runner.run(file_reviewer, file_input)
        for file_input in file_inputs
    ]
    local_results = await asyncio.gather(*local_runs)

    summaries = "\n\n".join(
        result.final_output for result in local_results
    )

    integration = await Runner.run(
        integration_reviewer,
        "Local review summaries:\n\n" + summaries,
    )
    return integration.final_output
```

### 4. 통합 입력은 raw 파일 전체가 아니라 evidence summary

```json
{
  "file": "backend/orders/service.py",
  "finding": "transaction commits before audit write",
  "lines": [88, 104],
  "impact": "audit and business state can diverge",
  "evidence": "commit() precedes write_audit_event()",
  "severity": "warning"
}
```

이런 구조로 전달하면 통합 reviewer가 중복 제거와 cross-file 추론에 집중할 수 있습니다.

### 5. 독립 리뷰의 한계

독립 context가 자동으로 더 정확한 것은 아닙니다. 다음도 필요합니다.

- 같은 불완전한 diff를 주지 않기
- test/contract 문서 제공
- finding criterion 통일
- false-positive fixture 유지
- 최종 human ownership 유지


### 공식 문서

- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex slash commands](https://developers.openai.com/codex/cli/slash-commands)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
<!-- CODEX-ADDENDUM-END -->

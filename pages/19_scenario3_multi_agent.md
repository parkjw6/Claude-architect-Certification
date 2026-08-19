# Chapter 19: 시나리오 3 — 멀티에이전트 연구 시스템

> 📅 2026년 04월 05일 기준  
> 🎯 실제 시험 시나리오 3 해설


[← Chapter 18](18_scenario2_code_generation.md) | [목차](../TOC.md) | [Chapter 20: 시나리오 4 →](20_scenario4_developer_productivity.md)

---

## 시나리오 개요

> 당신은 Claude Agent SDK를 사용하여 멀티에이전트 연구 시스템을 구축하고 있습니다.
> 시스템은 복잡한 비즈니스 주제를 분석하고 심층 보고서를 생성합니다.
> 여러 서브에이전트가 병렬로 연구를 수행하고, 코디네이터가 통합합니다.

---

## 아키텍처 설계

### Hub-and-Spoke 구조

```
                    ┌─────────────────┐
                    │  코디네이터 에이전트  │
                    │  (연구 주제 분해)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ 서브에이전트 A  │ │ 서브에이전트 B  │ │ 서브에이전트 C  │
    │  시장 분석    │ │  경쟁사 분석   │ │  규제 환경    │
    └──────────────┘ └──────────────┘ └──────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │  코디네이터 에이전트  │
                    │  (결과 통합 + 보고서) │
                    └─────────────────┘
```

### 코디네이터 구현

```python
import anthropic
import json
from concurrent.futures import ThreadPoolExecutor

client = anthropic.Anthropic()

COORDINATOR_PROMPT = """당신은 연구 코디네이터입니다.
복잡한 비즈니스 주제를 받아 여러 서브에이전트에게 분배하고,
결과를 통합하여 종합 보고서를 생성합니다.

Task 도구를 사용하여 서브에이전트를 스폰하세요.
각 서브에이전트는 독립적인 연구 영역을 담당합니다.
"""

def run_coordinator(research_topic: str) -> str:
    """코디네이터 에이전트 실행"""
    
    messages = [{
        "role": "user",
        "content": f"다음 주제를 완전히 연구하세요: {research_topic}"
    }]
    
    # 코디네이터는 Task 도구를 포함해야 서브에이전트 스폰 가능
    tools = [
        {
            "type": "computer_use_20250124",
            "name": "Task",
            "description": "서브에이전트를 스폰하여 독립적인 연구 수행"
        }
    ]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8096,
            system=COORDINATOR_PROMPT,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            # 병렬 서브에이전트 실행
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            results = run_subagents_parallel(tool_calls)
            
            messages.append({"role": "user", "content": results})
```

### 병렬 서브에이전트 실행

```python
def run_subagent(task_description: str, context: dict) -> str:
    """개별 서브에이전트 실행
    
    중요: 서브에이전트는 코디네이터 컨텍스트를 자동으로 받지 않습니다!
    필요한 컨텍스트는 명시적으로 전달해야 합니다.
    """
    
    SUBAGENT_PROMPT = f"""당신은 전문 연구 에이전트입니다.
    
연구 주제: {context['main_topic']}
담당 영역: {context['assigned_domain']}
특별 지시사항: {context.get('special_instructions', '없음')}

위 영역에 대해 심층 분석을 수행하세요."""
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SUBAGENT_PROMPT,
        messages=[{"role": "user", "content": task_description}]
    )
    
    return response.content[0].text


def run_subagents_parallel(tool_calls: list) -> list:
    """모든 서브에이전트를 병렬로 실행"""
    
    results = []
    
    # ThreadPoolExecutor로 병렬 실행
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        
        for tool_call in tool_calls:
            if tool_call.name == "Task":
                task_input = tool_call.input
                future = executor.submit(
                    run_subagent,
                    task_input["description"],
                    task_input.get("context", {})
                )
                futures[future] = tool_call.id
        
        for future, tool_id in futures.items():
            result = future.result()
            results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result
            })
    
    return results
```

---

## 태스크 분해 전략

### 범위 설정의 중요성

```
❌ 너무 좁은 분해 (범위 누락):
연구 주제: "전기차 시장"
서브에이전트 A: 테슬라만 분석
서브에이전트 B: 미국 시장만 분석
결과: 중국, 유럽, 신흥 플레이어 완전 누락

✅ 적절한 분해:
코디네이터 태스크: "전기차 시장 전체"를 어떻게 나눌지 먼저 판단
서브에이전트 A: 주요 제조사 (테슬라, BYD, 폭스바겐)
서브에이전트 B: 지역별 시장 (미국, 유럽, 아시아)
서브에이전트 C: 기술 트렌드 (배터리, 충전 인프라)
서브에이전트 D: 규제/정책 환경
```

### 동적 분해 vs 프롬프트 체이닝

```python
# 프롬프트 체이닝: 순차적, 고정 워크플로우
# 언제: 단계가 명확하고 각 단계가 이전 결과에 의존할 때

def prompt_chaining_approach(topic: str):
    # 1단계: 아웃라인 생성
    outline = generate_outline(topic)
    
    # 2단계: 각 섹션 작성 (아웃라인 필요)
    sections = [write_section(s, outline) for s in outline]
    
    # 3단계: 통합 및 편집 (모든 섹션 필요)
    report = integrate_and_edit(sections)
    return report


# 동적 분해: LLM이 판단, 적응적
# 언제: 주제 복잡도나 범위가 미리 알 수 없을 때

DYNAMIC_DECOMPOSITION_PROMPT = """
연구 주제: {topic}

1. 먼저 이 주제의 핵심 영역을 파악하세요
2. 각 영역에 대해 Task를 사용하여 전문 에이전트를 스폰하세요
3. 결과를 통합하여 종합 보고서를 작성하세요

판단: 이 주제에 필요한 분석 영역은 무엇인가요?
"""
```

---

## 컨텍스트 전달 패턴

### 명시적 컨텍스트 전달

```python
def spawn_subagent_with_context(coordinator_context: dict, task: str) -> str:
    """서브에이전트에게 필요한 컨텍스트를 명시적으로 전달"""
    
    # ❌ 틀린 가정: 서브에이전트가 코디네이터 컨텍스트를 알 것이다
    # ✅ 올바른 방법: 필요한 모든 정보를 명시적으로 전달
    
    context_summary = f"""
연구 프로젝트 배경:
- 주제: {coordinator_context['main_topic']}
- 클라이언트: {coordinator_context['client']}
- 마감: {coordinator_context['deadline']}
- 이미 완료된 분석: {coordinator_context['completed_analyses']}
- 당신의 담당 영역: {coordinator_context['your_domain']}
"""
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=context_summary,
        messages=[{"role": "user", "content": task}]
    )
    
    return response.content[0].text
```

---

## 결과 통합 패턴

### 구조화된 결과 수집

```python
def integrate_research_results(subagent_results: list[dict]) -> str:
    """서브에이전트 결과를 통합하여 최종 보고서 생성"""
    
    results_formatted = "\n\n".join([
        f"## {r['domain']}\n{r['content']}"
        for r in subagent_results
    ])
    
    integration_prompt = f"""
다음은 각 전문 에이전트의 연구 결과입니다:

{results_formatted}

이 결과들을 통합하여:
1. 일관성 있는 최종 보고서 작성
2. 각 영역 간 연관성 분석
3. 종합 결론 및 추천사항 도출
"""
    
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8096,
        messages=[{"role": "user", "content": integration_prompt}]
    )
    
    return response.content[0].text
```

---

## 시나리오 기반 예상 문제

### Q: 서브에이전트 컨텍스트 문제

상황: 코디네이터가 연구 주제와 클라이언트 정보를 가지고 있습니다. 서브에이전트를 스폰했을 때, 서브에이전트가 클라이언트 요구사항을 모르고 분석을 수행했습니다.

원인과 해결책은?

A) 코디네이터 모델을 더 강력한 것으로 교체  
B) 서브에이전트는 코디네이터 컨텍스트를 자동 상속하지 않으므로, Task 호출 시 필요한 컨텍스트를 명시적으로 전달  
C) 서브에이전트가 코디네이터 API를 직접 호출하도록 설정  
D) 공유 데이터베이스에 컨텍스트 저장  

정답: B — 서브에이전트 컨텍스트 자동 상속 없음, 명시적 전달 필수

---

### Q: 태스크 분해 범위 문제

상황: "글로벌 반도체 공급망 분석"을 요청받았습니다. 코디네이터가 3개 서브에이전트를 스폰했지만, 최종 보고서에서 동남아시아 공급망이 완전히 누락되었습니다.

가장 가능한 원인은?

A) 서브에이전트 수가 너무 적음  
B) 코디네이터의 태스크 분해 단계에서 전체 범위를 고려하지 않고 좁게 분해  
C) 모델 컨텍스트 윈도우 부족  
D) 병렬 실행 중 레이스 컨디션  

정답: B — 코디네이터 태스크 분해가 좁으면 범위 누락. 분해 단계에서 전체 범위 검토 필수

---

## 📝 챕터 요약

| 개념 | 핵심 내용 |
|------|---------|
| 서브에이전트 컨텍스트 | 자동 상속 없음, 명시적 전달 필수 |
| allowedTools | "Task" 포함해야 서브에이전트 스폰 가능 |
| 병렬 실행 | 한 응답에서 여러 Task 동시 호출 |
| 태스크 분해 | 전체 범위 고려 (좁으면 누락 발생) |
| 프롬프트 체이닝 | 순차, 고정 워크플로우 |
| 동적 분해 | LLM이 판단, 미지의 범위 |

---

> 🔗 다음 챕터: [시나리오 4 — 개발자 생산성 도구](20_scenario4_developer_productivity.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: CLI·app·Codex SDK·Agents SDK의 병렬 작업 비교

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | repository 작업은 native subagent/custom agent로 분해합니다. |
| **Codex app** | 여러 agent thread와 worktree를 command-center UI에서 병렬 감독하는 것이 가장 큰 app 전용 장점입니다. |
| **Codex SDK** | 여러 Codex coding thread를 `Promise.all`/`asyncio.gather`로 programmatically 병렬 실행합니다. |
| **OpenAI Agents SDK** | 범용 multi-agent research/business system의 manager, handoff, tools, synthesis를 구현합니다. |

> **별도 OpenAI API 계층:** Responses Multi-agent beta는 별도 model-directed API 경로입니다.

### 1. 먼저 실행 주체를 구분한다

| 실행 주체와 목적 | 권장 방식 |
|---|---|
| 개발자가 terminal에서 repository 작업을 분해 | **Codex CLI native subagents** |
| 개발자가 여러 coding task를 화면에서 감독 | **Codex app의 project/thread/worktree UI** |
| 프로그램이 여러 coding-focused Codex 작업을 실행 | **Codex SDK의 여러 thread** |
| 범용 연구·고객지원·업무 specialist를 조율 | **OpenAI Agents SDK** |
| 한 Responses API 요청에서 모델 주도 subagent 분해 | **Responses Multi-agent beta** |
| 정해진 N개 작업을 반드시 실행 | SDK/application code의 `Promise.all()`·`asyncio.gather()` |

Claude의 `allowedTools=["Task"]`를 어느 OpenAI 계층에도 그대로 복사하지 않습니다.

```text
Codex CLI
→ native subagent/custom agent

Codex app
→ CLI와 같은 Codex agent를 별도 thread/worktree에서 시각적으로 관리

Codex SDK
→ 여러 Codex thread를 code로 start/run/resume

OpenAI Agents SDK
→ 서로 다른 역할, tool, handoff, guardrail을 가진 범용 agent orchestration
```

### 2. Codex CLI — native subagents

사용자 요청 예시:

```text
현재 변경사항을 세 관점에서 병렬 검토해.

- security reviewer: exploit 가능한 취약점
- correctness reviewer: 동작 오류와 regression
- test reviewer: 누락된 test

각 작업을 별도 subagent에 위임하고,
모두 완료된 뒤 중복을 제거해 severity 순으로 정리해.
```

Project config:

```toml
[agents]
max_concurrent_threads_per_session = 6
```

Custom agent:

```toml
# .codex/agents/security-reviewer.toml

name = "security_reviewer"
description = "Read-only reviewer for exploitable security risks."
sandbox_mode = "read-only"

developer_instructions = """
Report only reachable, evidence-backed vulnerabilities.
Do not edit files.
Include file, line, attack path, impact, and fix.
"""
```

Subagent는 별도 context를 사용합니다. Main agent의 전체 conversation을 자동으로 안다고 가정하지 말고 task에 필요한 목표·범위·제약·출력 형식을 전달합니다.

### 3. Codex app — parallel threads와 worktrees

Codex app은 CLI와 같은 coding agent를 사용하지만, **사람이 여러 작업을 동시에 감독하는 UI**에 강점이 있습니다.

```text
Project
├─ Thread A / worktree A: security review
├─ Thread B / worktree B: correctness review
└─ Thread C / worktree C: missing-test review
```

App에서 별도로 가능한 일:

- agent를 project별 별도 thread로 유지
- built-in worktree로 같은 repository의 변경 충돌 격리
- 각 thread의 진행 상태를 전환하며 감독
- diff에 comment
- 결과를 editor로 열기
- 여러 장기 작업을 review queue에서 확인

이는 다음과 다릅니다.

```text
App parallel UI
= 사람이 여러 Codex thread를 시각적으로 감독

Codex SDK parallel threads
= program이 여러 Codex thread를 실행

Agents SDK multi-agent
= 범용 agent 역할과 tool/handoff를 orchestration
```

### 4. 별도 API 경로 — Responses Multi-agent beta

API 요청 하나 안에서 root model이 subagent를 만들도록 할 수 있습니다.

```python
from openai import OpenAI

client = OpenAI()

response = client.beta.responses.create(
    model="gpt-5.6-sol",
    input="""
Analyze the supplied material using three independent subagents:

1. market structure
2. competitors
3. regulation

Each subagent must return claims with sources.
Reconcile conflicts and preserve unresolved differences.
""",
    multi_agent={
        "enabled": True,
        "max_concurrent_subagents": 3,
    },
    betas=["responses_multi_agent=v1"],
)

print(response.output_text)
```

이 기능은 beta이므로 API shape와 지원 model을 공식 문서에서 재확인해야 합니다.

적합:

```text
bounded independent research
parallel document comparison
independent codebase exploration
```

부적합:

```text
여러 agent가 같은 mutable file을 동시 수정
고정된 deterministic graph가 반드시 필요
정확히 N개 단계의 실행 보장이 필요
```

### 5. OpenAI Agents SDK — manager가 agent를 tool처럼 사용

```python
from agents import Agent, Runner

market_agent = Agent(
    name="market_agent",
    instructions="Analyze market size, segments, and trends.",
)

competitor_agent = Agent(
    name="competitor_agent",
    instructions="Analyze competitors and differentiation.",
)

regulation_agent = Agent(
    name="regulation_agent",
    instructions="Analyze current and pending regulation.",
)

coordinator = Agent(
    name="research_coordinator",
    instructions="""
Decompose the request.
Call only relevant specialist tools.
When tasks are independent, call them in the same turn.
Preserve source attribution and unresolved conflicts.
""",
    tools=[
        market_agent.as_tool(
            tool_name="market_research",
            tool_description="Research market structure and trends.",
        ),
        competitor_agent.as_tool(
            tool_name="competitor_research",
            tool_description="Research competitors.",
        ),
        regulation_agent.as_tool(
            tool_name="regulation_research",
            tool_description="Research regulation.",
        ),
    ],
)

result = await Runner.run(
    coordinator,
    "Research the electric vehicle supply chain.",
)
```

`Agent.as_tool()`의 nested run은 parent conversation state를 자동 상속한다고 가정하지 않습니다. 필요한 context를 tool input이나 shared session/context로 명시적으로 설계합니다.

### 6. Agents SDK에서 모든 specialist를 반드시 실행할 때

```python
import asyncio
from agents import Runner


async def run_fixed_research(topic: str):
    market, competitors, regulation = await asyncio.gather(
        Runner.run(
            market_agent,
            f"Topic: {topic}\nAnalyze the market.",
        ),
        Runner.run(
            competitor_agent,
            f"Topic: {topic}\nAnalyze competitors.",
        ),
        Runner.run(
            regulation_agent,
            f"Topic: {topic}\nAnalyze regulation.",
        ),
    )

    return {
        "market": market.final_output,
        "competitors": competitors.final_output,
        "regulation": regulation.final_output,
    }
```

```text
parallel_tool_calls를 허용
= 모델이 여러 call을 낼 수 있음

asyncio.gather로 N개 run 생성
= code가 N개 실행을 보장
```

### 7. Context contract

각 subagent task에는 최소한 다음을 포함합니다.

```json
{
  "project_goal": "global semiconductor supply-chain analysis",
  "assigned_scope": "Southeast Asia manufacturing",
  "excluded_scope": ["US fab policy", "EU subsidies"],
  "time_cutoff": "2026-08-19",
  "required_output": {
    "claims": "with source and date",
    "conflicts": "preserve all values",
    "unknowns": "explicit list"
  }
}
```

### 8. Synthesis는 단순 연결이 아니다

Coordinator는 다음을 수행합니다.

- 중복 claim 병합
- 동일 용어의 정의 차이 확인
- 상충 수치 보존
- source quality와 날짜 비교
- 누락된 scope 확인
- final recommendation과 evidence 분리

분해 전에 coverage matrix를 만들면 특정 지역이나 관점을 통째로 빠뜨리는 문제를 줄일 수 있습니다.



### Codex SDK로 여러 coding thread를 병렬 실행

Codex SDK는 범용 agent role framework가 아니라 **동일한 Codex coding agent의 여러 thread를 programmatically 관리**하는 데 적합합니다.

#### TypeScript

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();

const securityThread = codex.startThread();
const correctnessThread = codex.startThread();
const testThread = codex.startThread();

const [security, correctness, tests] = await Promise.all([
  securityThread.run(
    "Review the current branch for exploitable security issues. Do not edit."
  ),
  correctnessThread.run(
    "Review the current branch for correctness regressions. Do not edit."
  ),
  testThread.run(
    "Review the current branch for missing tests. Do not edit."
  ),
]);

const results = {
  security: security.finalResponse,
  correctness: correctness.finalResponse,
  tests: tests.finalResponse,
};

console.log(results);
```

#### Python

```python
import asyncio

from openai_codex import AsyncCodex, Sandbox


async def main() -> None:
    async with AsyncCodex() as codex:
        security_thread = await codex.thread_start(
            sandbox=Sandbox.read_only,
        )
        test_thread = await codex.thread_start(
            sandbox=Sandbox.read_only,
        )

        security, tests = await asyncio.gather(
            security_thread.run(
                "Review security risks in the current branch"
            ),
            test_thread.run(
                "Review missing tests in the current branch"
            ),
        )

        print(security.final_response)
        print(tests.final_response)


asyncio.run(main())
```

### Codex SDK와 Agents SDK의 병렬화 차이

```text
Codex SDK
→ 여러 coding-focused Codex thread
→ 모두 repository 작업자
→ start/run/resume와 sandbox 중심

OpenAI Agents SDK
→ 서로 다른 역할의 범용 agent
→ market, regulation, customer support, coding specialist 등
→ tools, handoffs, guardrails, HITL, tracing 중심
```

예:

```text
PR security/correctness/test review
→ Codex SDK 여러 thread가 자연스러울 수 있음

시장·경쟁사·규제 연구
→ OpenAI Agents SDK가 더 자연스러움

연구 coordinator가 patch까지 필요
→ Agents SDK manager + Codex coding specialist
```

### Codex app에서의 병렬화

App은 위의 여러 coding thread를 사람이 시각적으로 감독할 때 가장 편리합니다.

- 각 thread를 project 안에서 유지
- worktree로 file 충돌 격리
- 진행 상태 전환
- diff 비교
- 더 나은 결과를 선택해 local state로 가져오기

App의 병렬 UI는 SDK의 programmatic `Promise.all()`이나 Agents SDK orchestration과 같은 개념이 아닙니다.

### 공식 문서

- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Responses Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent)
- [Agents SDK tools and agents-as-tools](https://openai.github.io/openai-agents-python/tools/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
<!-- CODEX-ADDENDUM-END -->

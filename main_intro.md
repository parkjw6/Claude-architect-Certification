# Claude Code 학습서를 Codex 관점에서 읽는 방법

> 기준일: **2026-08-19**  
> 적용 범위: `pages/12_*.md`부터 `pages/31_final_checklist.md`까지  
> 기본 설명 환경: **Codex CLI**  
> 목적: 기존 Claude 학습 내용을 보존하면서, 같은 설계 원리를 **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**에서 어떻게 구현하는지 구분한다.

---

## 1. 이 문서에서 반드시 구분하는 네 계층

OpenAI 쪽 설명은 다음 네 계층을 섞지 않습니다.

| 계층 | 사용하는 사람/프로그램 | 핵심 목적 | 대표 인터페이스 |
|---|---|---|---|
| **Codex CLI** | 개발자 | 터미널에서 repository를 탐색·수정·테스트·리뷰 | `codex`, `codex exec`, `codex review` |
| **Codex app** | 개발자·리뷰어 | Codex 작업을 데스크톱 UI에서 병렬 관리·감독 | 프로젝트/스레드 UI, diff review, worktree, Automations |
| **Codex SDK** | 애플리케이션 코드 | CLI를 구동하는 동일한 Codex coding agent를 프로그램에서 호출 | `@openai/codex-sdk`, `openai-codex` |
| **OpenAI Agents SDK** | 애플리케이션 코드 | 고객지원·연구·업무 자동화 같은 일반 agent application 구성 | `Agent`, `Runner`, tools, handoffs, guardrails, HITL |

### 문서의 기본 규칙

1. **사용법은 Codex CLI를 기본으로 작성합니다.**
2. Codex app에서 자연어로 같은 작업을 수행할 수 있으면 CLI 설명을 반복하지 않습니다.
3. app에서만 의미가 큰 UI 기능이 있을 때만 `Codex app 전용`으로 별도 설명합니다.
4. 자동화 코드에서 Codex 자체를 호출할 때는 **Codex SDK**로 표시합니다.
5. 일반적인 multi-agent business application은 **OpenAI Agents SDK**로 표시합니다.
6. Structured Outputs, Batch API, Responses API는 네 제품 중 하나가 아니라 필요한 기능을 제공하는 **OpenAI API 계층**으로 별도 표기합니다.

---

## 2. Codex app이라는 이름에 대한 현재 기준

2026년 2월에는 별도 **Codex app**으로 발표되었고, 2026년 3월 Windows 지원이 추가되었습니다. 현재 공식 `/codex/app` 문서는 ChatGPT desktop app 문서로 연결되며, 데스크톱 앱 안에서 Codex를 선택해 사용할 수 있습니다.

이 문서에서는 편의상 다음을 모두 **Codex app**이라고 부릅니다.

```text
데스크톱 앱에서 Codex를 선택하고
repository/project/thread를 열어
coding agent를 자연어로 지시·검토하는 경험
```

Codex app은 CLI와 별개의 coding agent를 쓰는 것이 아니라 같은 Codex agent stack과 설정을 공유하는 UI입니다. 따라서 `AGENTS.md`, Skills, MCP, Rules, Sandbox 같은 핵심 개념은 CLI 설명을 그대로 따릅니다.

---

## 3. 네 계층의 가장 중요한 차이

### 3.1 Codex CLI

사람이 terminal에서 Codex를 직접 사용합니다.

```bash
# 대화형
codex

# 비대화형 자동화
codex exec \
  "Review the current repository for release blockers"

# 코드 리뷰
codex review --uncommitted
codex review --base main
```

주요 책임:

- repository 구조 탐색
- source 수정
- test·lint·type check 실행
- diff review
- `AGENTS.md`와 Skill 적용
- MCP tool 사용
- sandbox·approval·Rules 적용
- `codex exec` 기반 CI/script

**이 저장소의 Codex 사용법은 원칙적으로 CLI 기준으로 설명합니다.**

---

### 3.2 Codex app

Codex CLI와 같은 종류의 coding task를 사람이 데스크톱 UI에서 수행합니다.

CLI와 공통:

- 같은 repository instruction
- 같은 Skills
- 같은 MCP와 설정 계층
- 같은 sandbox와 Rules 개념
- 같은 자연어 task
- CLI/IDE의 session history와 configuration 연계

App에서 별도로 의미가 큰 기능:

1. **여러 project와 agent thread를 시각적으로 병렬 관리**
2. **내장 worktree 지원으로 agent별 격리된 repository copy 관리**
3. **thread 안에서 diff를 검토하고 comment한 뒤 editor로 열기**
4. **Skill을 생성·관리하는 전용 UI**
5. **Automations로 일정 기반 반복 작업 실행**
6. **Automation 결과를 review queue에서 확인**
7. 장시간 작업을 여러 thread 사이에서 전환하며 감독

예:

```text
CLI:
codex에서 "backend와 frontend를 각각 별도 agent로 분석해"

App:
프로젝트 안에서 두 thread/worktree를 만들고
각 agent의 진행 상태와 diff를 나란히 감독
```

App에 특별한 차이가 없는 장에서는 다음처럼 표기합니다.

```text
Codex app:
별도 app-only 동작 없음. CLI 설명을 자연어로 실행하면 됨.
```

---

### 3.3 Codex SDK

**Codex CLI를 구동하는 coding agent를 애플리케이션 코드에서 직접 제어**합니다.

적합한 경우:

- 내부 developer tool에 Codex 내장
- coding-focused CI/CD workflow
- 자동 code cleanup
- repository migration bot
- thread를 시작·계속·resume해야 하는 coding automation
- Codex 결과를 application에서 구조적으로 처리

Codex SDK는 “일반적인 모든 종류의 agent framework”가 아닙니다. 중심 abstraction은 **coding-focused Codex thread**입니다.

#### TypeScript

```bash
npm install @openai/codex-sdk
```

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();

const plan = await thread.run(
  "Make a plan to diagnose and fix the CI failures"
);
console.log(plan.finalResponse);

const implementation = await thread.run(
  "Implement the plan and run the relevant tests"
);
console.log(implementation.finalResponse);

// 이전 thread resume
const resumed = codex.resumeThread("<thread-id>");
const followUp = await resumed.run("Review the remaining risks");
console.log(followUp.finalResponse);
```

Codex SDK는 coding thread의 turn마다 JSON Schema를 적용할 수도 있습니다.

```typescript
import { Codex } from "@openai/codex-sdk";

const schema = {
  type: "object",
  properties: {
    summary: { type: "string" },
    status: {
      type: "string",
      enum: ["ok", "action_required"],
    },
  },
  required: ["summary", "status"],
  additionalProperties: false,
} as const;

const codexForSchema = new Codex();
const schemaThread = codexForSchema.startThread();

const structured = await schemaThread.run(
  "Summarize repository status",
  { outputSchema: schema },
);

const parsed = JSON.parse(structured.finalResponse);
```

#### Python

```bash
pip install openai-codex
```

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(
        model="gpt-5.6-terra",
        sandbox=Sandbox.workspace_write,
    )

    result = thread.run(
        "Diagnose and fix the CI failures"
    )
    print(result.final_response)

    review = thread.run(
        "Review the diff only",
        sandbox=Sandbox.read_only,
    )
    print(review.final_response)
```

Python SDK는 local Codex app-server를 JSON-RPC로 제어하고, published build에는 pinned Codex CLI runtime dependency가 포함됩니다. 2026-08-19 기준 Python package는 beta 상태이므로 설치 방식과 API는 공식 문서를 다시 확인해야 합니다.

Codex SDK가 제공하는 핵심:

```text
Codex thread start
same-thread continuation
past thread resume
streaming events
coding agent result object
per-turn JSON Schema (`outputSchema`)
working directory control
sandbox per thread/turn
programmatic integration
```

---

### 3.4 OpenAI Agents SDK

일반적인 agent application을 구성합니다.

적합한 경우:

- 고객지원 agent
- 연구 coordinator
- 문서 처리 agent
- 사내 업무 agent
- 여러 specialist agent orchestration
- handoff
- input/output guardrail
- session과 state
- tracing
- human-in-the-loop approval

```python
from agents import Agent, Runner, function_tool


@function_tool
def lookup_order(order_id: str) -> dict:
    """Look up an order by exact order ID."""
    return order_service.get(order_id)


support_agent = Agent(
    name="support_agent",
    instructions=(
        "Resolve support requests using policy. "
        "Never invent order identifiers."
    ),
    tools=[lookup_order],
)

result = await Runner.run(
    support_agent,
    "Check order ORD-123",
)

print(result.final_output)
```

Agents SDK의 중심 abstraction:

```text
Agent
Runner
Tool
Agent.as_tool()
Handoff
Guardrail
Session / RunState
Tracing
Human-in-the-loop
```

---

## 4. Codex SDK와 OpenAI Agents SDK의 차이

이 둘은 가장 명확히 구분해야 합니다.

| 항목 | Codex SDK | OpenAI Agents SDK |
|---|---|---|
| 중심 목적 | Codex coding agent를 code로 호출 | 범용 agent application 구성 |
| 대표 작업 | repo 수정, test, review, migration | 고객지원, 연구, 업무 자동화 |
| 핵심 abstraction | Codex thread | Agent + Runner |
| Codex CLI와 관계 | 동일한 Codex agent/harness를 programmatic control | 별도의 범용 orchestration framework |
| repository awareness | Codex의 기본 강점 | tool/context를 직접 설계 |
| thread resume | 기본 핵심 기능 | Session/RunState로 상태 설계 |
| sandbox | Codex sandbox preset | sandbox agent/tool 또는 application 환경 설계 |
| multi-agent | 여러 Codex thread를 code로 병렬화 가능 | agents-as-tools, handoffs, manager, code orchestration |
| guardrails/HITL | Codex policy·sandbox 중심 | input/output guardrails와 HITL workflow |
| 최적 사용 | coding-focused internal tool/CI | broader production agent system |

### 선택 기준

```text
"우리 내부 도구에서 Codex가 repository를 고치게 하겠다"
→ Codex SDK

"우리 고객지원 서비스에 여러 agent와 tool을 구성하겠다"
→ OpenAI Agents SDK

"고객지원 agent가 필요할 때 coding specialist에게 repo 수정도 맡긴다"
→ Agents SDK가 상위 coordinator
   + Codex를 specialist로 연결
```

공식 Codex SDK 문서도 **Codex가 broader orchestrated workflow 안의 specialist라면 Codex CLI를 MCP server로 실행하고 Agents SDK에서 orchestration**하는 패턴을 권장합니다.

---

## 5. Codex CLI와 Codex SDK의 차이

| 항목 | Codex CLI | Codex SDK |
|---|---|---|
| 호출자 | 사람 또는 shell script | TypeScript/Python application |
| 입력 | terminal prompt와 flag | method call |
| 상태 | interactive session | thread object와 thread ID |
| 자동화 | `codex exec` | application logic 안에서 start/run/resume |
| 결과 처리 | stdout, JSONL, output file | result object |
| 사용 난이도 | 가장 단순 | 더 세밀한 제어 |
| 권장 상황 | 개발자 사용, 단순 CI | 제품/내부 도구에 Codex embedding |

### CLI를 먼저 선택할 상황

```text
shell에서 한 번 실행
CI step 하나
사람이 terminal에서 상호작용
결과 file 하나만 필요
```

### SDK를 선택할 상황

```text
여러 turn을 programmatically 이어감
thread ID를 저장하고 나중에 resume
여러 Codex thread를 code에서 병렬 관리
결과를 내부 system object로 처리
자체 UI·서비스에 Codex를 내장
```

---

## 6. Codex app과 CLI의 관계

이 문서는 CLI를 기본으로 설명하지만 app 사용자는 대부분 그대로 자연어로 실행할 수 있습니다.

```text
CLI 설명:
codex review --base main

App 사용:
"main과 비교해서 현재 변경사항을 리뷰해"
```

```text
CLI 설명:
$team-review

App 사용:
team-review Skill을 선택하거나
"team-review skill로 현재 diff를 검토해"
```

App-only section이 따로 필요한 대표 상황:

- 여러 agent를 동시에 시각적으로 관리
- worktree별 diff 비교
- Automations scheduling
- review queue
- Skill 관리 UI
- editor handoff

그 외 설정 파일과 repository 설계는 CLI 기준을 그대로 사용합니다.

---

## 7. 네 계층과 OpenAI API의 관계

Structured Outputs, Responses API, Batch API는 네 계층 중 하나가 아니라 API 기능입니다.

```text
Codex CLI / app
→ Codex runtime이 API와 agent loop를 관리

Codex SDK
→ 같은 Codex runtime을 code에서 관리

Agents SDK
→ agent application runtime을 구성

Responses API
→ model call과 tool interaction의 lower-level API

Batch API
→ 대량 비동기 API request transport
```

예:

```text
invoice JSON extraction만 필요
→ Responses API Structured Outputs

coding agent가 repository에서 extraction pipeline을 구현
→ Codex CLI/app

내부 tool이 repository migration을 자동 수행
→ Codex SDK

production document-processing agent와 approvals 필요
→ Agents SDK
```

---

## 8. Claude 개념의 네 계층 대응표

| Claude 개념 | Codex CLI | Codex app | Codex SDK | OpenAI Agents SDK |
|---|---|---|---|---|
| `CLAUDE.md` | `AGENTS.md` | 동일 | thread가 repository에서 동일 지침 사용 | agent instructions는 별도 |
| `.claude/commands/` | Skills | Skill UI/자연어 실행 | coding thread가 Skill 사용 | application tool/workflow로 구현 |
| `context: fork` | subagent | 별도 thread/worktree UI | 별도 Codex thread | 별도 Agent run / agent-as-tool |
| `Task` | native subagent | 병렬 agent UI | 여러 thread programmatic 실행 | Agent.as_tool / handoff / gather |
| `.mcp.json` | `.codex/config.toml` | 동일 | Codex runtime 설정 사용 | Agents SDK MCP/tool integration |
| `claude -p` | `codex exec` | 해당 없음 | SDK method call | `Runner.run()` |
| Plan Mode | `/plan` | 자연어/Plan UI | thread에 plan 요청 | workflow step으로 구현 |
| 독립 review | `/review`, `codex review` | diff review UI | read-only review turn/thread | reviewer agent |
| `allowed-tools` | sandbox/MCP filter/Rules | 동일 | sandbox per thread/turn | Agent tools/guardrails |
| `tool_use` JSON | `--output-schema` 가능 | UI 결과 | result object; strict data schema는 API 검토 | `output_type`/Structured Outputs |

---

## 9. 권장 repository 구조

```text
my-project/
├── AGENTS.md
├── backend/
│   └── AGENTS.md
├── frontend/
│   └── AGENTS.md
│
├── .agents/
│   └── skills/
│       ├── team-review/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── review-checklist.md
│       └── release-check/
│           └── SKILL.md
│
├── .codex/
│   ├── config.toml
│   ├── agents/
│   │   ├── explorer.toml
│   │   └── reviewer.toml
│   ├── hooks.json
│   ├── hooks/
│   │   └── block_dangerous_command.py
│   └── rules/
│       └── default.rules
│
└── .github/
    └── workflows/
        └── codex-review.yml
```

이 repository 구조는 CLI, app, Codex SDK의 Codex thread에 공통으로 적용됩니다. Agents SDK의 agent definition은 보통 application source code 안에 별도로 둡니다.

---

## 10. AGENTS.md, Skill, Subagent, MCP, Hook의 책임

```text
AGENTS.md
= Codex coding agent가 항상 따를 repository 규칙

Skill
= Codex coding agent가 필요할 때 수행할 workflow

Subagent
= Codex 안에서 별도 context로 수행할 coding specialist

MCP
= Codex 또는 Agents SDK가 외부 tool/data에 연결되는 방식

Hook
= Codex lifecycle event에서 custom code 실행

Rules
= Codex command permission policy

Sandbox
= Codex가 실제로 할 수 있는 filesystem/command 범위

Agents SDK Agent
= production application의 역할과 tool orchestration
```

---

## 11. Codex SDK 병렬 coding thread 예시

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();

const securityThread = codex.startThread();
const testThread = codex.startThread();

const [security, tests] = await Promise.all([
  securityThread.run(
    "Review the current branch for exploitable security issues. Do not edit."
  ),
  testThread.run(
    "Review the current branch for missing tests. Do not edit."
  ),
]);

console.log(security.finalResponse);
console.log(tests.finalResponse);
```

이 방식은 여러 **coding-focused Codex thread**를 code에서 병렬 실행하는 것입니다.

범용 agent 역할, handoff, business tool, guardrail이 필요하면 Agents SDK가 더 적합합니다.

---

## 12. Agents SDK가 Codex를 specialist로 사용하는 구조

```text
Research/Support/Operations Manager
        OpenAI Agents SDK
                 │
       ┌─────────┴─────────┐
       │                   │
 business specialist   coding specialist
 Agents SDK Agent      Codex MCP/SDK
```

예:

```text
상위 agent:
"CI 장애가 product release에 미치는 영향을 판단"

Codex specialist:
"repository에서 CI 실패 원인을 분석하고 patch 제안"

상위 agent:
"승인 정책과 release workflow에 따라 다음 행동 결정"
```

Coding specialist가 broader workflow의 일부라면 Codex의 강점을 유지하면서 Agents SDK가 전체 orchestration을 소유하게 할 수 있습니다.

현재 공식 문서에서 확인할 수 있는 연결 방식은 두 가지입니다.

```text
권장된 안정적 구성:
Agents SDK manager
→ Codex CLI를 MCP server로 연결
→ bounded repository task 위임

Agents SDK의 실험적 구성:
experimental codex_tool
→ Agents SDK run 안에서 workspace-scoped Codex task 호출
```

`codex_tool`은 실험적 surface이므로 production 설계에서는 version 고정, sandbox, working directory, approval policy를 명시하고 변경 가능성을 전제로 해야 합니다.

---

## 13. Critical invariant의 위치

다음은 네 계층 어느 prompt에도 단독으로 맡기지 않습니다.

```text
고객 인증 전 환불 금지
500달러 초과 자동 환불 금지
production 직접 배포 금지
개인정보 외부 전송 금지
```

```python
def process_refund(
    *,
    verified_customer_id: str | None,
    order_customer_id: str,
    amount: float,
) -> dict:
    if verified_customer_id is None:
        raise PermissionError("Customer verification required")

    if verified_customer_id != order_customer_id:
        raise PermissionError("Customer/order mismatch")

    if amount > 500:
        return {
            "status": "approval_required",
            "reason": "refund_limit_exceeded",
        }

    return execute_refund(amount=amount)
```

```text
Codex CLI/app/SDK
= 해당 code를 작성·검토

Agents SDK
= tool 선택·handoff·approval workflow

Application service/RBAC
= 실제 invariant 강제
```

---

## 14. Chapter 12~31을 읽는 방식

각 페이지는 다음 순서로 읽습니다.

1. 기존 Claude 본문과 시험 정답
2. `Codex/OpenAI 대응` 절
3. 절 시작의 네 계층 표
4. 해당 장의 primary layer 코드
5. 다른 세 계층과의 차이

시험 문제에서는 Claude syntax를 답하고, 실무 전환에서는 원리를 네 계층에 다시 배치합니다.

```text
Claude-specific syntax
        ↓
underlying engineering principle
        ↓
CLI / app / Codex SDK / Agents SDK
중 적합한 계층
```

---

## 15. 공식 문서

### Codex CLI와 공통 configuration

- [Codex CLI](https://learn.chatgpt.com/docs/codex-cli)
- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex Sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)

### Codex app

- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [현재 desktop app 문서](https://developers.openai.com/codex/app)

### Codex SDK

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex App Server](https://developers.openai.com/codex/app-server)
- [TypeScript SDK README](https://github.com/openai/codex/blob/main/sdk/typescript/README.md)
- [Python SDK README](https://github.com/openai/codex/blob/main/sdk/python/README.md)
- [Python SDK API reference](https://github.com/openai/codex/blob/main/sdk/python/docs/api-reference.md)

### OpenAI Agents SDK

- [Agents SDK overview](https://openai.github.io/openai-agents-python/)
- [Agents](https://openai.github.io/openai-agents-python/agents/)
- [Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [Tools and agents-as-tools](https://openai.github.io/openai-agents-python/tools/)
- [Handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [Human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)

### OpenAI API

- [Responses API](https://developers.openai.com/api/docs/guides/responses)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Batch API](https://developers.openai.com/api/docs/guides/batch)
- [Responses Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent)

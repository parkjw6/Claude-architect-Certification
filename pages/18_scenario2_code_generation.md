# Chapter 18: 시나리오 2 — Claude Code로 코드 생성

> 📅 2026년 04월 05일 기준  
> 🎯 실제 시험 시나리오 2 해설


[← Chapter 17](17_scenario1_customer_support.md) | [목차](../TOC.md) | [Chapter 19: 시나리오 3 →](19_scenario3_multi_agent.md)

---

## 시나리오 개요

> 당신은 소프트웨어 개발 팀을 위해 Claude Code를 구성하고 있습니다.
> 팀은 React/TypeScript 프론트엔드와 Python 백엔드를 가진 대규모 모노레포를 관리합니다.
> 목표: Claude Code를 생산성 도구로 효과적으로 통합하고, 코드 품질을 유지하면서 개발 속도를 높이는 것

---

## 핵심 아키텍처 결정

### CLAUDE.md 계층 구조 설계

```
모노레포 구조:
/
├── .claude/
│   ├── CLAUDE.md          ← 프로젝트 전체 규칙 (팀 공유)
│   ├── commands/          ← 팀 공유 슬래시 커맨드
│   │   ├── review.md      ← /review 커맨드
│   │   ├── test.md        ← /test 커맨드
│   │   └── deploy.md      ← /deploy 커맨드
│   └── rules/
│       ├── frontend.yaml  ← React/TS 규칙
│       └── backend.yaml   ← Python 규칙
├── frontend/
│   ├── CLAUDE.md          ← 프론트엔드 전용 규칙
│   └── src/
│       └── components/
│           └── CLAUDE.md  ← 컴포넌트 레벨 규칙
├── backend/
│   └── CLAUDE.md          ← 백엔드 전용 규칙
└── ~/ (사용자 홈)
    └── .claude/
        ├── CLAUDE.md      ← 개인 설정 (팀 공유 ❌)
        └── commands/      ← 개인 커맨드
```

### 프로젝트 CLAUDE.md 설계

```markdown
# 프로젝트 가이드라인

## 기술 스택
- 프론트엔드: React 18, TypeScript 5.4, Vite
- 백엔드: Python 3.12, FastAPI, PostgreSQL
- 테스트: pytest (백엔드), Vitest + RTL (프론트엔드)

## 코드 규칙
- 모든 공개 API는 타입 힌트 포함
- 커밋 전 반드시 테스트 통과 확인
- PR 크기: 200줄 이하 권장

## 금지 사항
- console.log() 프로덕션 코드에 포함 금지
- TODO 주석 없이 미완성 코드 커밋 금지
- 하드코딩된 자격증명 금지

@backend/CLAUDE.md
@frontend/CLAUDE.md
```

### .claude/rules/ 설정

```yaml
# frontend.yaml
---
paths:
  - "frontend/**/*.tsx"
  - "frontend/**/*.ts"
  - "**/*.test.tsx"
---
React 컴포넌트 작성 규칙:
- Props 인터페이스 반드시 정의
- memo(), useCallback()은 실제 성능 이슈 있을 때만 사용
- 컴포넌트당 하나의 책임
```

```yaml
# backend.yaml
---
paths:
  - "backend/**/*.py"
  - "tests/**/*.py"
---
Python 코드 규칙:
- type hints 필수
- docstring: Google 스타일
- 예외 처리: 구체적인 예외 클래스 사용
```

### 팀 공유 커맨드 설계

```markdown
<!-- .claude/commands/review.md -->
---
description: "코드 리뷰 체크리스트 실행"
argument-hint: "PR 번호 또는 파일 경로 (선택)"
allowed-tools: Read, Grep, Glob
---

다음 체크리스트로 코드를 리뷰하세요:

## 보안 검토
- [ ] SQL 인젝션 취약점
- [ ] XSS 가능성
- [ ] 인증/인가 검사

## 코드 품질
- [ ] 함수 복잡도 (10 이하)
- [ ] 중복 코드
- [ ] 타입 안전성

## 테스트
- [ ] 새 코드에 대한 테스트 존재
- [ ] 엣지 케이스 처리

$ARGUMENTS
```

```markdown
<!-- .claude/commands/test.md -->
---
description: "테스트 실행 및 커버리지 확인"
context: fork
allowed-tools: Bash
---

1. 프론트엔드 테스트: `npm run test --coverage`
2. 백엔드 테스트: `pytest --cov=app tests/`
3. 커버리지 80% 미만 파일 식별
4. 실패 테스트 원인 분석

$ARGUMENTS
```

---

## Plan Mode vs Direct Execution 판단

### Plan Mode 사용 시나리오

```
✅ Plan Mode 필요:
- 마이크로서비스 분리 (45개+ 파일 영향)
- 인증 시스템 전면 교체
- 데이터베이스 스키마 마이그레이션
- API 버전 업그레이드 (v1 → v2)

❌ Plan Mode 불필요:
- 단일 파일 버그 수정
- 명확한 스택 트레이스가 있는 오류
- 새 유틸리티 함수 추가
- 로컬라이제이션 문자열 업데이트
```

### Plan Mode 결정 트리

```
변경이 필요한가?
    ↓
여러 파일에 걸쳐 있는가?
    ├─ 아니오 → Direct Execution
    └─ 예 → 아키텍처적 결정이 필요한가?
                ├─ 아니오 → Direct Execution
                └─ 예 → Plan Mode
```

---

## CI/CD 통합

### GitHub Actions 파이프라인

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    branches: [main, develop]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Claude Code Review
        run: |
          claude -p "
          PR의 변경된 파일을 검토하세요.
          보안 취약점, 코드 품질 문제, 성능 이슈를 식별하세요.
          각 문제를 파일:라인 형식으로 명확히 표시하세요.
          
          변경된 파일:
          $(git diff --name-only origin/main...HEAD)
          " \
          --output-format json \
          --max-tokens 4096
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 비대화형 모드 활용

```bash
# CI/CD에서 Claude Code 사용
# -p (--print): 비대화형 모드, 한 번 실행 후 종료
# --output-format json: 기계 처리 가능한 JSON 출력

claude -p "코드 분석 작업" --output-format json | jq '.result'

# JSON 스키마 강제
claude -p "분석 수행" \
  --output-format json \
  --json-schema '{"type": "object", "properties": {"issues": {"type": "array"}}}'
```

---

## 세션 관리 전략

### 장기 세션 관리

```bash
# 이름 있는 세션 시작
claude --session-name "feature-auth-redesign"

# 다음 날 세션 재개
claude --resume "feature-auth-redesign"

# fork_session: 공통 기준점에서 독립 탐색
# 예: 동일한 버그에 대해 두 가지 해결책 탐색
```

### context: fork 사용

```markdown
<!-- .claude/commands/explore.md -->
---
description: "독립적인 코드 탐색"
context: fork    ← 격리된 서브에이전트로 실행
---

이 커맨드는 현재 세션에 영향 없이
독립적으로 코드를 분석합니다.
```

---

## 시나리오 기반 예상 문제

### Q: 디렉토리별 규칙 적용

상황: React 컴포넌트 디렉토리에만 적용되는 규칙을 설정하고 싶습니다.

최선의 방법은?

A) 프로젝트 CLAUDE.md에 모든 규칙 한꺼번에 작성  
B) `.claude/rules/` 디렉토리에 glob 패턴이 있는 YAML 파일 생성  
C) 각 개발자의 `~/.claude/CLAUDE.md`에 규칙 추가  
D) `config.json`의 rules 배열에 규칙 정의  

정답: B — `.claude/rules/`의 YAML 파일에 `paths` frontmatter로 glob 패턴 지정

---

### Q: Plan Mode 판단

상황: 모노리식 앱을 6개의 마이크로서비스로 분리하는 작업을 시작합니다.

올바른 접근은?

A) 바로 코드 변경 시작 (직접 실행)  
B) Plan Mode로 전체 마이그레이션 계획 수립 후 진행  
C) 각 서비스를 별도 세션에서 구현  
D) CI/CD 파이프라인을 먼저 설정  

정답: B — 45개+ 파일, 아키텍처 결정, 마이크로서비스 분리 → Plan Mode 사용 기준 충족

---

## 📝 챕터 요약

| 개념 | 핵심 내용 |
|------|---------|
| CLAUDE.md | 계층: 사용자 → 프로젝트 → 디렉토리 |
| .claude/rules/ | glob 패턴으로 특정 파일에만 규칙 적용 |
| 팀 커맨드 | .claude/commands/ (버전 관리, 공유) |
| Plan Mode | 대규모 아키텍처 변경에 사용 |
| -p 플래그 | CI/CD 비대화형 모드 필수 |
| context: fork | 격리된 독립 탐색 |

---

> 🔗 다음 챕터: [시나리오 3 — 멀티에이전트 연구 시스템](19_scenario3_multi_agent.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Claude Code 저장소 구성을 Codex 구조로 변환하기

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | 이 장의 기본이자 primary 계층입니다. repository를 직접 탐색·수정·검증합니다. |
| **Codex app** | CLI 기능을 UI로 사용하며, 병렬 thread, built-in worktree, visual diff, editor handoff, Skill UI가 app 전용 장점입니다. |
| **Codex SDK** | 동일한 Codex coding agent를 내부 도구·CI·서비스에서 programmatically 호출합니다. |
| **OpenAI Agents SDK** | Codex가 broader agent workflow의 coding specialist일 때 상위 orchestration을 담당합니다. |

### 1. 전체 대응 구조

```text
Claude Code                         Codex
────────────────────────────────────────────────────────
CLAUDE.md                           AGENTS.md
nested CLAUDE.md                    nested AGENTS.md
.claude/rules paths glob            정확한 1:1 없음
.claude/commands/*.md               .agents/skills/*/SKILL.md
Skill context: fork                 subagent/custom agent
Skill allowed-tools                 sandbox/MCP filter/hooks/rules
.mcp.json                           .codex/config.toml
PreToolUse/PostToolUse              Codex native Hooks
command permission                  .codex/rules/*.rules
claude -p                           codex exec
--json-schema                       --output-schema
Plan Mode                           /plan
독립 review                         /review, codex review
```

### 2. 권장 repository layout

```text
repo/
├── AGENTS.md
├── frontend/
│   └── AGENTS.md
├── backend/
│   └── AGENTS.md
│
├── .agents/
│   └── skills/
│       ├── team-review/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── checklist.md
│       └── test-analysis/
│           └── SKILL.md
│
├── .codex/
│   ├── config.toml
│   ├── agents/
│   │   ├── explorer.toml
│   │   └── reviewer.toml
│   ├── hooks.json
│   ├── hooks/
│   │   └── pre_tool_policy.py
│   └── rules/
│       └── default.rules
│
└── .github/
    └── workflows/
        └── codex-review.yml
```

### 3. `AGENTS.md`

```markdown
# Repository instructions

## Stack

- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI, PostgreSQL
- Tests: Vitest/Testing Library and pytest

## Change policy

- Keep public API contracts backward compatible.
- Do not perform unrelated refactors.
- Never commit credentials.
- Read affected tests before changing behavior.
- Add or update tests for behavior changes.

## Completion criteria

- Run the smallest relevant test suite.
- Run type checks for touched packages.
- Report commands that could not run.
- Summarize modified files and remaining risks.
```

`frontend/AGENTS.md`:

```markdown
# Frontend instructions

- Define explicit prop types.
- Test user-visible behavior.
- Do not assert private component state.
- Use memoization only for demonstrated need.
```

`backend/AGENTS.md`:

```markdown
# Backend instructions

- Public functions require type hints.
- Keep database writes transaction-scoped.
- Map domain exceptions to API responses at the boundary.
- Do not use blocking I/O inside async handlers.
```

### 4. Claude `.claude/rules/paths`의 대체

Codex `.codex/rules/`는 glob-based coding guidance가 아닙니다. 다음 중 하나를 사용합니다.

```text
특정 directory 전체
→ nested AGENTS.md

여러 directory에 흩어진 *.test.tsx
→ root AGENTS.md에 조건부 문장

복잡한 test workflow
→ testing Skill
```

Root 예시:

```markdown
## Test files

When creating or modifying `*.test.ts` or `*.test.tsx`:

- Use Vitest and Testing Library.
- Test observable behavior.
- Avoid implementation-detail assertions.
- Mock external boundaries, not internal functions.
```

Claude의 path matcher처럼 runtime이 glob을 평가해 지침을 조건부 로드하는 정확한 동일 기능은 아닙니다. Codex가 instruction 조건을 해석해 적용합니다.

### 5. 팀 공유 command는 Skill로

```markdown
<!-- .agents/skills/team-review/SKILL.md -->

---
name: team-review
description: >
  Review current changes using the team's correctness,
  security, performance, and test criteria.
---

# Team review

Review the current diff. Do not modify files.

For every finding provide:

1. severity
2. file and line
3. concrete evidence
4. impact
5. recommended correction

Apply:
- `references/checklist.md`
```

사용:

```text
$team-review
```

일반 review는 별도 Skill 없이 다음을 사용할 수 있습니다.

```text
/review
```

```bash
codex review --uncommitted
codex review --base main
```

### 6. 격리 작업은 subagent

```toml
# .codex/agents/test-analyzer.toml

name = "test_analyzer"
description = "Read-only test failure and coverage analyst."
sandbox_mode = "read-only"

developer_instructions = """
Analyze test failures and missing coverage.
Do not edit code.
Return root cause, evidence, and recommended tests.
"""
```

Claude의:

```yaml
context: fork
allowed-tools: Read, Grep, Bash
```

를 Codex Skill에 복사하지 않습니다. 격리는 subagent가, capability는 sandbox와 정책이 담당합니다.

### 7. MCP 설정

```toml
# .codex/config.toml

[mcp_servers.internal_docs]
url = "https://docs.example.com/mcp"
bearer_token_env_var = "DOCS_MCP_TOKEN"
required = true
enabled_tools = ["search_documents", "get_document"]
default_tools_approval_mode = "prompt"
```

개인 token은 환경 변수로 둡니다.

### 8. Hook

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .codex/hooks/pre_tool_policy.py",
            "timeout": 30,
            "statusMessage": "Checking command policy"
          }
        ]
      }
    ]
  }
}
```

Hook은 tool lifecycle의 custom logic입니다. Project hook은 trusted project에서 로드되며 변경된 hook definition은 review/trust가 필요합니다.

### 9. Rules

```python
# .codex/rules/default.rules

prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
    justification = "Remote writes require approval.",
)

prefix_rule(
    pattern = ["rm", "-rf"],
    decision = "forbidden",
    justification = "Recursive deletion is prohibited.",
)
```

### 10. Plan Mode 판단

```text
여러 subsystem에 영향
migration 또는 public API 변경
architecture trade-off 필요
unknown root cause와 여러 대안
→ /plan

명확한 단일 파일 버그
작은 문서 수정
well-scoped test 추가
→ 바로 구현 가능
```

Plan은 최종 목적이 아닙니다. 좋은 흐름은:

```text
explore
→ plan
→ implement
→ validate
→ independent review
```

### 11. 비대화형 실행

```bash
# 분석
codex exec \
  "Review the current checkout for release blockers"

# 파일 수정 허용
codex exec \
  --sandbox workspace-write \
  "Fix the failing unit tests"

# 최종 schema
codex exec \
  "Extract release risk metadata" \
  --output-schema ./risk-schema.json \
  -o ./risk.json

# 전체 event stream
codex exec --json \
  "Analyze the current branch" \
  > ./codex-events.jsonl
```

`--json`은 최종 business object가 아니라 JSONL event stream입니다.

### 12. 안전성 계층

```text
AGENTS.md
→ 행동 지침

Skill
→ workflow 지침

Hook
→ lifecycle 검사

Rules / approval
→ command 정책

Sandbox
→ 실제 workspace capability

GitHub/DB/cloud RBAC
→ 외부 시스템 권한
```

Production deployment, secret access, destructive data operation은 저장소 prompt만으로 보호하지 않습니다.



### 13. Codex app에서만 별도로 설명할 기능

Codex app은 이 장의 CLI 기능을 자연어 UI로 실행합니다. 다음은 app에서 별도로 의미가 큰 기능입니다.

```text
여러 project와 thread를 동시에 화면에서 관리
agent별 built-in worktree
thread 안에서 diff review와 comment
변경사항을 editor로 열기
Skill 생성·관리 UI
장시간 task의 진행 상태 전환·감독
Automations와 review queue
```

예를 들어 CLI에서는 같은 repository에서 parallel agent를 직접 관리해야 하지만, app에서는 각 agent를 별도 thread/worktree에 두고 diff를 시각적으로 비교할 수 있습니다.

Repository 파일 자체는 그대로 공유됩니다.

```text
AGENTS.md
.agents/skills/
.codex/config.toml
.codex/agents/
.codex/hooks.json
.codex/rules/
```

따라서 app을 사용한다고 별도의 `APP_AGENTS.md`나 app 전용 Skill 형식을 만들지 않습니다.

### 14. Codex SDK로 같은 coding workflow를 프로그램에서 호출

#### TypeScript

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();

const plan = await thread.run(
  "Inspect this repository and plan the authentication migration"
);

if (!plan.finalResponse) {
  throw new Error("Codex did not return a plan");
}

const implementation = await thread.run(
  "Implement the approved plan and run the relevant tests"
);

console.log(implementation.finalResponse);
```

#### Python

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(
        model="gpt-5.6-terra",
        sandbox=Sandbox.workspace_write,
    )

    plan = thread.run(
        "Plan the authentication migration"
    )
    print(plan.final_response)

    implementation = thread.run(
        "Implement the plan and run relevant tests"
    )
    print(implementation.final_response)

    review = thread.run(
        "Review the diff only",
        sandbox=Sandbox.read_only,
    )
    print(review.final_response)
```

SDK를 선택하는 기준:

```text
사람이 terminal에서 작업
→ Codex CLI

사람이 desktop UI에서 여러 작업 감독
→ Codex app

내부 service나 developer portal이 Codex를 호출
→ Codex SDK
```

### 15. OpenAI Agents SDK는 언제 추가하는가

다음처럼 coding task보다 더 큰 workflow가 있을 때 Agents SDK를 상위 계층으로 사용합니다.

```text
release manager agent
├─ Jira 상태 조회
├─ Slack 승인 요청
├─ deployment policy 판단
└─ Codex coding specialist에게 patch 요청
```

이때 Codex는 coding specialist이고, Agents SDK는 business workflow와 handoff를 소유합니다.

```text
Agents SDK manager
        ↓
Codex CLI as MCP server 또는 Codex integration
        ↓
repository 수정·test·review
```

단순 repository 변경에 Agents SDK부터 도입하면 불필요한 orchestration complexity가 생길 수 있습니다.

### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [Codex slash commands](https://developers.openai.com/codex/cli/slash-commands)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

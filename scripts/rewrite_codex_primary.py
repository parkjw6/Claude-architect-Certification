#!/usr/bin/env python3
"""Make every handbook page Codex-first while preserving Claude content.

The script:
1. adds a Codex/OpenAI primary section to every pages/*.md file;
2. moves any existing CODEX addendum into that primary section;
3. preserves the previous Claude-centered body under a later appendix;
4. rewrites README.md, TOC.md, and main_intro.md as Codex-first entry points.
"""

from __future__ import annotations

from pathlib import Path
import re

AS_OF = "2026-08-19"
PRIMARY_MARKER = "<!-- CODEX-PRIMARY-REWRITE -->"
ADDENDUM_START = "<!-- CODEX-ADDENDUM-START -->"
ADDENDUM_END = "<!-- CODEX-ADDENDUM-END -->"

GUIDES = {
    "00": """
## Codex/OpenAI 기준

이 저장소는 **Codex CLI·Codex App·Codex SDK·OpenAI Agents SDK**를 본문 기준으로 학습합니다.

```text
Codex CLI/App  → 사람이 repository를 작업
Codex SDK      → coding thread를 프로그램에서 제어
Agents SDK     → 범용 agent workflow를 orchestration
Responses API  → lower-level model·structured data
```

- 항상 적용되는 규칙은 `AGENTS.md`에 둡니다.
- 반복 workflow는 Skill, 격리된 탐색은 subagent/thread에 둡니다.
- Critical invariant는 prompt가 아니라 code·sandbox·RBAC에서 강제합니다.
""",
    "01": """
## Codex/OpenAI 기준

LLM은 database나 policy engine이 아니라 확률적 생성 모델입니다. 실제 agent 품질은 다음 결합으로 결정됩니다.

```text
Model + Instructions + Context + Tools + Runtime
+ State + Permissions + Validators + Human approval
```

Codex는 이 구조를 repository 작업에 적용하고, Agents SDK는 범용 workflow에 적용합니다.
""",
    "02": """
## Codex/OpenAI 기준

모델 이름을 고정 암기하기보다 실제 task의 품질·지연·비용·tool reliability를 평가합니다.

- coding, routing, validation task를 분리합니다.
- model ID는 configuration으로 둡니다.
- 동일 golden fixture로 회귀를 측정합니다.
- Claude tier와의 비교도 이름이 아니라 동일 task 결과로 수행합니다.
""",
    "03": """
## Codex/OpenAI 기준

```text
Codex CLI/App → 사람이 사용하는 coding interface
Codex SDK     → repository-aware coding thread의 programmatic control
Agents SDK    → Agent·Runner·tools·handoffs·HITL
Responses API → model call·function calling·structured output
```

이 네 계층을 하나의 SDK처럼 설명하지 않습니다.
""",
    "04": """
## Codex/OpenAI 기준

Agent loop는 관찰→판단→tool 실행→검증→종료의 반복입니다.

- Codex runtime은 coding loop를 관리합니다.
- Agents SDK `Runner`는 범용 agent loop를 관리합니다.
- max turns와 timeout은 정상 완료가 아니라 안전망입니다.
- business completion은 application code가 별도로 검사합니다.
""",
    "05": """
## Codex/OpenAI 기준

멀티에이전트는 agent 수를 늘리는 기법이 아니라 **context·tool·책임 분리**입니다.

- Manager가 전체 목표와 synthesis를 소유합니다.
- Specialist에는 goal·scope·exclusions·output contract를 명시합니다.
- 한 artifact에는 writer를 한 명만 둡니다.
- 필수 병렬 task는 `asyncio.gather()` 같은 code-level orchestration으로 강제합니다.
""",
    "06": """
## Codex/OpenAI 기준

Workflow는 model judgment와 deterministic enforcement의 경계를 설계하는 일입니다.

```text
Prompt/Skill → 행동 지침
Hook/Rules   → tool·command 정책
Sandbox/RBAC→ 실제 capability
Service code→ business invariant
```

결제·배포·삭제·identity 규칙은 prompt만으로 강제하지 않습니다.
""",
    "07": """
## Codex/OpenAI 기준

좋은 tool은 이름·description·schema·권한·오류·side effect가 명확합니다.

- Read와 write tool을 분리합니다.
- 정확한 identifier와 ambiguous match를 정의합니다.
- 결과는 `success | partial | failed` envelope로 반환합니다.
- write에는 approval과 idempotency를 둡니다.
""",
    "08": """
## Codex/OpenAI 기준

Codex project MCP는 `.codex/config.toml`, 개인 MCP는 `~/.codex/config.toml`에 둡니다.

```toml
[mcp_servers.internal_docs]
url = "https://docs.example.com/mcp"
bearer_token_env_var = "DOCS_MCP_TOKEN"
enabled_tools = ["search_documents", "get_document"]
default_tools_approval_mode = "prompt"
```

Server 설정은 공유하되 실제 token은 environment/secret store에 둡니다.
""",
    "09": """
## Codex/OpenAI 기준

Codex repository 운영의 기본 구조입니다.

```text
repo/
├── AGENTS.md
├── .agents/skills/
├── .codex/config.toml
├── .codex/agents/
├── .codex/hooks.json
└── .codex/rules/
```

CLI는 terminal·CI에, App은 parallel threads·worktrees·visual diff에 강점이 있습니다.
""",
    "10": """
## Codex/OpenAI 기준

팀 reusable workflow의 중심은 `.agents/skills/<name>/SKILL.md`입니다.

- Skill은 instructions·references·scripts·assets로 구성합니다.
- Skill 자체가 자동으로 별도 context를 만드는 것은 아닙니다.
- 격리는 Codex subagent, App thread/worktree, Codex SDK thread로 구현합니다.
- Built-in `/review`와 team `$team-review` Skill을 구분합니다.
""",
    "11": """
## Codex/OpenAI 기준

큰 작업의 기본 흐름입니다.

```text
Explore → Plan → Approval → Bounded implementation
→ Tests/build → Independent review → Handoff
```

CI의 단순 실행은 `codex exec`, 상태 있는 coding automation은 Codex SDK를 사용합니다.
""",
    "12": """
## Codex/OpenAI 기준

Prompt는 다음 계약을 명시합니다.

```text
Goal:
Context:
Constraints:
Done when:
```

모호한 지시보다 report/ignore 기준을 쓰고, few-shot은 positive·negative·boundary case를 포함합니다.
""",
    "13": """
## Codex/OpenAI 기준

```text
Codex CLI   → --output-schema
Codex SDK   → thread.run(..., { outputSchema })
Agents SDK  → output_type
Responses   → Structured Outputs
```

Schema 준수는 사실 정확성을 보장하지 않으므로 semantic validation을 별도로 실행합니다.
""",
    "14": """
## Codex/OpenAI 기준

```text
Offline 대량 처리 → OpenAI Batch API
현재 checkout review → codex review / codex exec
독립 관점 → 별도 Codex thread / reviewer agent
Merge gate → deterministic policy
```

Self-review보다 independent context review를 사용합니다.
""",
    "15": """
## Codex/OpenAI 기준

```text
Conversation summary
≠ Codex coding thread
≠ Agents SDK RunState
≠ Business source of truth
≠ Artifact archive
```

`/compact`는 conversation 요약이며 ID·금액·승인·정책 버전은 typed state에 보존합니다.
""",
    "16": """
## Codex/OpenAI 기준

신뢰성은 objective trigger·typed error·idempotency·provenance·human approval의 결합입니다.

- model confidence나 감정만으로 escalation하지 않습니다.
- timeout 후 operation status를 조회합니다.
- 상충 정보는 source와 함께 모두 보존합니다.
- Codex command approval과 business HITL을 구분합니다.
""",
    "17": """
## Codex/OpenAI 기준

고객지원의 main runtime은 **OpenAI Agents SDK**입니다. Codex는 backend를 개발하거나 bounded repository task를 수행하는 specialist입니다.

Identity·order ownership·refund limit은 service code가 강제하고, large refund와 policy gap은 HITL로 보냅니다.
""",
    "18": """
## Codex/OpenAI 기준

코드 생성의 기본은 Codex CLI/App이며, 반복 internal automation은 Codex SDK를 사용합니다.

```typescript
const codex = new Codex();
const thread = codex.startThread();
await thread.run("Plan the minimal safe fix. Do not edit.");
await thread.run("Implement the approved plan and run tests.");
```

Agents SDK는 release·Jira·approval까지 포함한 broader workflow의 manager로 사용합니다.
""",
    "19": """
## Codex/OpenAI 기준

범용 연구는 Agents SDK manager가 specialist를 조율하고 repository 작업에만 Codex specialist를 호출합니다.

- 시장·경쟁사·규제 → 범용 agents
- codebase·test·patch → Codex specialist
- 필수 specialist → code-level parallel execution
- synthesis → source conflict와 coverage 보존
""",
    "20": """
## Codex/OpenAI 기준

개발자 생산성 도구는 다음처럼 책임을 나눕니다.

```text
Developer Assistant (Agents SDK)
├── Docs/Jira/Slack specialists
└── Codex coding specialist
      └── repository·test·diff
```

MCP tool surface, Hooks, Rules, Sandbox, external RBAC를 계층적으로 적용합니다.
""",
    "21": """
## Codex/OpenAI 기준

단순 CI는 `codex exec`, 상태 있는 coding worker는 Codex SDK, release workflow 전체는 Agents SDK를 사용합니다.

- read-only review가 기본입니다.
- `--json` event stream과 `--output-schema` final result를 구분합니다.
- App Automation은 required CI check와 다릅니다.
- API key를 untrusted build step 전체에 노출하지 않습니다.
""",
    "22": """
## Codex/OpenAI 기준

문서 추출의 primary는 Responses Structured Outputs입니다.

- nullable·status·evidence를 schema에 포함합니다.
- schema validation과 semantic validation을 분리합니다.
- source에 정보가 없으면 retry로 발명하지 않습니다.
- Codex는 extraction pipeline의 code·schema·tests를 개발합니다.
""",
    "23": """
## Codex/OpenAI 기준

이 문제군은 programmatic gate, tool description, escalation criteria, team Skill을 다룹니다. 항상 제품 계층을 먼저 식별하고 가장 직접적이며 결정론적인 해결책을 선택합니다.
""",
    "24": """
## Codex/OpenAI 기준

이 문제군은 typed state, runtime loop owner, Codex MCP scope, conflicting source 보존을 다룹니다. Conversation summary와 authoritative state를 구분합니다.
""",
    "25": """
## Codex/OpenAI 기준

이 문제군은 false positive criteria, subagent/thread 격리, mandatory parallel execution, Structured Outputs를 다룹니다. Claude syntax를 Codex에 그대로 복사하지 않습니다.
""",
    "26": """
## Codex/OpenAI 기준

연습문제는 다음 순서로 풉니다.

```text
1. Product layer
2. Root cause
3. Deterministic boundary
4. Minimal solution
5. Claude equivalent
```
""",
    "27": """
## Codex/OpenAI 기준

학습 범위를 다섯 트랙으로 나눕니다.

1. Codex CLI
2. Codex App
3. Codex SDK
4. OpenAI Agents SDK
5. Responses·Batch·MCP·Security·Evaluation
""",
    "28": """
## Codex/OpenAI 기준

시험에서 비출제라는 말과 production에서 불필요하다는 말은 다릅니다. OAuth·token scope·CI security·sandbox·RBAC·idempotency·audit는 실무에서 핵심일 수 있습니다.
""",
    "29": """
## Codex/OpenAI 기준

```text
Week 1 CLI + AGENTS
Week 2 Skills + subagents
Week 3 MCP + permissions
Week 4 Hooks + Rules + Sandbox
Week 5 Codex SDK
Week 6 Agents SDK
Week 7 Structured Outputs + Batch
Week 8 Capstone + eval + HITL
```
""",
    "30": """
## Codex/OpenAI 기준

문제를 다음 순서로 판단합니다.

1. 어떤 제품 계층인가?
2. 근본 원인은 무엇인가?
3. 무엇을 code가 강제해야 하는가?
4. 가장 단순한 해결책은 무엇인가?
5. 어떻게 검증하는가?
""",
    "31": """
## Codex/OpenAI 기준

```text
AGENTS.md  = always-on guidance
Skill      = on-demand workflow
Subagent   = isolated specialist
MCP        = external capability
Rules      = command policy
Sandbox    = actual capability
Codex SDK  = coding thread embedding
Agents SDK = general orchestration
```
""",
    "32": """
## Codex/OpenAI 기준

좋은 agent system은 “모델이 알아서 한다”가 아니라 책임이 분리되고, 근거가 보존되고, 권한이 제한되고, 검증 가능하며, 사람이 최종 통제할 수 있는 system입니다.
""",
    "A": """
## Codex/OpenAI 기준

이 부록은 Codex/OpenAI 용어·명령·공식 자료·최소 코드 예제를 먼저 제공하고 Claude 대응은 뒤에서 비교합니다.
""",
}

CLAUDE_MAP = """
| Codex/OpenAI 중심 | Claude/Anthropic 대응 |
|---|---|
| `AGENTS.md` | `CLAUDE.md` |
| Codex Skills | Claude Commands / Skills |
| Codex subagent/thread | Claude subagent / `context: fork` |
| `.codex/config.toml` | `.mcp.json` / `~/.claude.json` |
| `codex exec` | `claude -p` |
| Structured Outputs | `tool_use` + schema |
| OpenAI Agents SDK | Claude Agent SDK |
"""


def chapter_of(path: Path) -> str:
    if path.name.startswith("A"):
        return "A"
    return path.name[:2]


def extract_title(text: str, fallback: str) -> tuple[str, str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            return line[2:].strip(), "\n".join(lines[:index] + lines[index + 1 :]).lstrip()
    return fallback, text


def codex_title(title: str) -> str:
    replacements = [
        ("Claude Certified Architect", "Codex 중심 Agent Engineering"),
        ("Claude Code", "Codex"),
        ("Claude API", "OpenAI API"),
        ("Claude 모델", "OpenAI/Codex 모델"),
        ("Claude와 AI", "Codex/OpenAI와 AI"),
        ("Claude", "Codex/OpenAI"),
    ]
    for old, new in replacements:
        title = title.replace(old, new)
    return title


def extract_addendum(text: str) -> tuple[str, str]:
    if ADDENDUM_START not in text or ADDENDUM_END not in text:
        return "", text
    start = text.index(ADDENDUM_START)
    end = text.index(ADDENDUM_END, start) + len(ADDENDUM_END)
    block = text[start:end]
    inner = block.replace(ADDENDUM_START, "", 1).replace(ADDENDUM_END, "", 1).strip()
    cleaned = (text[:start] + text[end:]).rstrip()
    return inner, cleaned


def rewrite_page(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    if PRIMARY_MARKER in original:
        return

    old_title, body = extract_title(original, path.stem)
    addendum, claude_body = extract_addendum(body)
    new_title = codex_title(old_title)
    chapter = chapter_of(path)
    guide = GUIDES.get(chapter, GUIDES["A"]).strip()

    detailed = ""
    if addendum:
        detailed = (
            "\n\n## 기존 Codex 보완 내용을 본문으로 승격\n\n"
            + addendum
        )

    rewritten = f"""{PRIMARY_MARKER}
# {new_title}

> 📅 기준일: **{AS_OF}**  
> 🧭 기본 관점: **Codex가 main, Claude/Anthropic은 비교·이식 참고**  
> 📁 원본 파일명: `{path.name}` — 기존 WikiDocs·GitHub 링크 호환성을 위해 유지합니다.

[목차](../TOC.md)

---

{guide}
{detailed}

## 이 파일에 적용할 Codex-first 질문

1. 이 주제는 Codex CLI/App, Codex SDK, Agents SDK, Responses API 중 어디에 속하는가?
2. Model judgment와 deterministic enforcement의 경계는 어디인가?
3. 필요한 context, tools, permissions, artifact, validator는 무엇인가?
4. 실패·retry·approval·handoff를 어떻게 명시할 것인가?
5. 실제 repository fixture로 어떻게 검증할 것인가?

## 공통 운영 체크리스트

- [ ] Codex/OpenAI 설명이 Claude 설명보다 먼저 배치되었다.
- [ ] 항상 적용되는 지침과 on-demand workflow를 분리했다.
- [ ] read-only 조사와 write side effect를 분리했다.
- [ ] 중요 claim과 artifact에 provenance를 남겼다.
- [ ] Claude 고유 syntax를 Codex 설정에 그대로 복사하지 않았다.

---

## Claude Code / Anthropic 보충 설명

> 아래 내용은 이 파일의 기존 Claude 중심 원문을 보존한 것입니다.  
> 이 저장소에서는 **제품 비교·Claude 시험 대비·기존 자산 이식 참고**로 읽습니다.

{CLAUDE_MAP}

{claude_body.strip()}

---

## 공식 문서

- [Codex](https://developers.openai.com/codex/)
- [Codex SDK](https://developers.openai.com/codex/sdk)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Responses API](https://developers.openai.com/api/docs/guides/responses)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
"""
    path.write_text(rewritten.strip() + "\n", encoding="utf-8", newline="\n")


def rewrite_toc(repo: Path) -> None:
    path = repo / "TOC.md"
    original = path.read_text(encoding="utf-8") if path.exists() else "# 목차\n"
    transformed = codex_title(original)
    if transformed.startswith("# "):
        transformed = re.sub(
            r"^# .+$",
            "# Codex 중심 Agent Engineering 목차",
            transformed,
            count=1,
            flags=re.MULTILINE,
        )
    header = (
        "<!-- CODEX-PRIMARY-REWRITE -->\n"
        "> **Codex/OpenAI가 본문**, Claude/Anthropic은 각 페이지 후반의 비교 절입니다.\n\n"
    )
    path.write_text(header + transformed.lstrip(), encoding="utf-8", newline="\n")


def rewrite_entry_points(repo: Path) -> None:
    (repo / "README.md").write_text(
        """# Codex 중심 Agent Engineering Handbook

> **Codex가 main, Claude/Anthropic은 비교·이식 참고**

이 저장소는 **Codex CLI·Codex App·Codex SDK·OpenAI Agents SDK**를 기준으로 전면 재구성되었습니다. `pages/`의 기존 Claude 중심 내용은 삭제하지 않고 각 파일 후반의 보충 설명으로 이동했습니다.

```text
사람 + terminal repository 작업 → Codex CLI
사람 + desktop 병렬 감독        → Codex App
프로그램 + coding thread         → Codex SDK
범용 business/research agent     → OpenAI Agents SDK
strict JSON model call           → Structured Outputs
대량 비차단 요청                 → Batch API
```

- [메인 소개](main_intro.md)
- [전체 목차](TOC.md)
- [이 책을 읽는 방법](pages/00_how_to_read.md)
""",
        encoding="utf-8",
        newline="\n",
    )

    (repo / "main_intro.md").write_text(
        """# Codex 중심으로 읽는 Agent Engineering

> 기준일: **2026-08-19**  
> **Codex가 본문**, Claude/Anthropic은 제품 비교와 migration 참고입니다.

| 계층 | 책임 |
|---|---|
| **Codex CLI** | terminal에서 repository 탐색·수정·테스트·review |
| **Codex App** | parallel threads·worktrees·visual diff·Automations |
| **Codex SDK** | coding thread의 programmatic start/run/resume |
| **OpenAI Agents SDK** | 범용 Agent·Runner·tools·handoffs·guardrails·HITL |
| **OpenAI API** | Responses·Structured Outputs·Batch |

```text
AGENTS.md  = always-on repository guidance
Skill      = on-demand workflow
Subagent   = isolated coding specialist
MCP        = external capability
Rules      = command permission
Sandbox    = actual capability
Code/RBAC  = critical invariant
```

- [전체 목차](TOC.md)
- [Codex CLI·App 실전 활용](pages/09_claude_code.md)
- [Codex 기반 코드 생성](pages/18_scenario2_code_generation.md)
- [최종 체크리스트](pages/31_final_checklist.md)
""",
        encoding="utf-8",
        newline="\n",
    )


def validate(repo: Path) -> None:
    files = sorted((repo / "pages").glob("*.md"))
    problems: list[str] = []
    if len(files) != 88:
        problems.append(f"expected 88 Markdown pages, got {len(files)}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        if PRIMARY_MARKER not in text:
            problems.append(f"{path}: missing primary marker")
        if "Codex가 main" not in text:
            problems.append(f"{path}: missing Codex-first statement")
        if "## Claude Code / Anthropic 보충 설명" not in text:
            problems.append(f"{path}: missing Claude appendix")
        if text.index("Codex가 main") > text.index("Claude Code / Anthropic 보충 설명"):
            problems.append(f"{path}: Claude appears before Codex")
        if text.count("```") % 2:
            problems.append(f"{path}: unbalanced code fences")

    if problems:
        raise RuntimeError("\n".join(problems))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    pages = sorted((repo / "pages").glob("*.md"))
    if len(pages) != 88:
        raise RuntimeError(f"Expected 88 pages/*.md files, got {len(pages)}")

    for path in pages:
        rewrite_page(path)

    rewrite_toc(repo)
    rewrite_entry_points(repo)
    validate(repo)

    print("Rewrote all 88 pages as Codex-first and preserved Claude content as appendices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

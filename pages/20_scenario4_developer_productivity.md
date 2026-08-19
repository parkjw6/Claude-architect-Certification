# Chapter 20: 시나리오 4 — 개발자 생산성 도구

> 📅 2026년 04월 05일 기준  
> 🎯 실제 시험 시나리오 4 해설


[← Chapter 19](19_scenario3_multi_agent.md) | [목차](../TOC.md) | [Chapter 21: 시나리오 5 →](21_scenario5_cicd.md)

---

## 시나리오 개요

> 당신은 내부 개발자 도구 팀에 있습니다.
> Claude를 사용하여 개발자의 일상적인 작업(코드 리뷰, 버그 분석, 문서화)을 자동화합니다.
> 여러 개발자 도구와 통합된 MCP 서버 기반 시스템을 설계합니다.

---

## 핵심 아키텍처: 툴 배분 전략

### 문제: 너무 많은 툴

```
❌ 잘못된 설계: 모든 기능을 하나의 에이전트에
tools = [
    "search_code", "read_file", "write_file", "run_tests",
    "check_ci", "post_comment", "assign_reviewer", "create_pr",
    "update_jira", "send_slack", "check_coverage", "lint_code",
    "analyze_performance", "check_security", "update_docs",
    "create_ticket", "search_docs", "run_migration"
]
# 18개 툴 → 선택 신뢰도 저하!
```

```
✅ 올바른 설계: 전문화된 에이전트로 분리
코드 리뷰 에이전트: 4-5개 툴
  - read_file, search_code, lint_code, post_comment, check_coverage

CI/CD 에이전트: 4-5개 툴
  - check_ci, run_tests, get_build_logs, trigger_deploy, notify_team

문서화 에이전트: 3-4개 툴
  - read_file, update_docs, search_docs, create_ticket
```

### 툴 수와 선택 신뢰도

```
툴 수    선택 신뢰도
 4개    ██████████ 매우 높음
 8개    ████████   높음  
12개    ██████     보통
18개    ████       낮음 ← 18개가 기준점
20개+   ██         매우 낮음
```

---

## MCP 서버 설계

### 코드 리뷰 MCP 서버

```python
# code_review_mcp_server.py
from mcp import MCPServer, tool

server = MCPServer("code-review-tools")

@tool(
    name="analyze_code_quality",
    description="""코드 품질을 분석합니다.
    
    사용 시점:
    - PR 리뷰 시 코드 품질 자동 검사
    - 특정 파일의 복잡도, 중복, 코딩 컨벤션 확인
    
    입력:
    - file_path: 분석할 파일 경로
    - checks: 수행할 검사 목록 (complexity, duplication, style)
    
    반환:
    - issues: 발견된 문제 목록 (심각도 포함)
    - score: 품질 점수 (0-100)
    
    주의: security 검사는 scan_security_vulnerabilities 사용"""
)
async def analyze_code_quality(file_path: str, checks: list[str]):
    """코드 품질 분석 구현"""
    pass


@tool(
    name="scan_security_vulnerabilities",
    description="""보안 취약점을 스캔합니다.
    
    사용 시점: analyze_code_quality와 구별하여 보안 전용 검사
    
    입력:
    - file_path: 분석할 파일 경로
    - scan_depth: 'quick' | 'thorough'
    
    반환:
    - vulnerabilities: OWASP 기반 취약점 목록
    - severity: critical/high/medium/low
    - fix_suggestions: 수정 제안"""
)
async def scan_security_vulnerabilities(file_path: str, scan_depth: str = "quick"):
    """보안 취약점 스캔 구현"""
    pass
```

### .mcp.json 설정

```json
{
  "mcpServers": {
    "code-review": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "code_review_mcp_server"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "JIRA_API_KEY": "${JIRA_API_KEY}",
        "LOG_LEVEL": "info"
      }
    },
    "cicd-tools": {
      "type": "stdio",
      "command": "node",
      "args": ["cicd_mcp_server.js"],
      "env": {
        "JENKINS_URL": "${JENKINS_URL}",
        "JENKINS_TOKEN": "${JENKINS_TOKEN}"
      }
    }
  }
}
```

---

## 내장 툴 최적 활용

### 툴 선택 기준

```
시나리오                          최적 툴
───────────────────────────────────────────
특정 함수 정의 찾기              → Grep
모든 테스트 파일 목록            → Glob (*.test.tsx)
파일 전체 내용 읽기              → Read
특정 텍스트 교체 (유일한 텍스트) → Edit
파일 전체 재작성                 → Write (Read 먼저!)
```

### 올바른 툴 사용 예시

```python
# 코드 리뷰 에이전트의 작업 흐름

# 1. 변경된 파일 목록 찾기
# Glob: "**/*.py" 패턴으로 Python 파일 검색

# 2. 특정 패턴 검색 (예: TODO 주석)
# Grep: "TODO|FIXME|HACK" 패턴으로 내용 검색

# 3. 특정 파일 내용 읽기
# Read: 전체 파일 내용 확인

# 4. 코드 수정 (특정 함수 교체)
# Edit: 고유한 함수명으로 정확한 위치 교체

# 5. 새 파일 생성 (테스트 파일)
# Write: 새 파일 작성
```

---

## Hooks를 활용한 자동화

### PostToolUse 훅 설계

```python
# .claude/hooks/post_tool_use.py
import json
import sys

def normalize_code_output(tool_name: str, tool_result: dict) -> dict:
    """툴 결과를 정규화하는 PostToolUse 훅"""
    
    if tool_name == "run_tests":
        # 테스트 결과 표준화
        return {
            "passed": tool_result.get("exit_code") == 0,
            "total": tool_result.get("test_count", 0),
            "failed": tool_result.get("failures", []),
            "coverage": tool_result.get("coverage_percent", None)
        }
    
    elif tool_name == "check_ci":
        # CI 상태 정규화
        raw_status = tool_result.get("status", "unknown")
        status_map = {
            "SUCCESS": "passed",
            "FAILURE": "failed",
            "RUNNING": "in_progress",
            "PENDING": "queued"
        }
        return {
            "status": status_map.get(raw_status, raw_status),
            "duration_minutes": tool_result.get("duration", 0) / 60,
            "url": tool_result.get("build_url")
        }
    
    return tool_result


# stdin으로 툴 결과 받기
tool_event = json.loads(sys.stdin.read())
normalized = normalize_code_output(
    tool_event["tool_name"],
    tool_event["result"]
)
print(json.dumps(normalized))
```

### PreToolUse 훅 — 정책 강제

```python
# .claude/hooks/pre_tool_use.py
def enforce_policy(tool_name: str, tool_input: dict) -> bool:
    """툴 사용 전 정책 검사"""
    
    # 프로덕션 환경에 직접 배포 차단
    if tool_name == "deploy":
        if tool_input.get("environment") == "production":
            if not tool_input.get("approval_ticket"):
                print(json.dumps({
                    "blocked": True,
                    "reason": "프로덕션 배포는 승인 티켓이 필요합니다"
                }))
                return False
    
    # 메인 브랜치 직접 커밋 차단
    if tool_name == "git_commit":
        if tool_input.get("branch") in ["main", "master"]:
            print(json.dumps({
                "blocked": True,
                "reason": "메인 브랜치에 직접 커밋할 수 없습니다"
            }))
            return False
    
    return True
```

---

## 에러 처리 전략

### 구조화된 에러 응답

```python
# 내부 도구 에러 응답 설계
def get_error_response(error_type: str, context: dict) -> dict:
    
    if error_type == "test_failure":
        return {
            "isError": True,
            "errorCategory": "business",    # 비즈니스 규칙 위반 (재시도 불가)
            "isRetryable": False,
            "message": "테스트 실패: 코드를 수정 후 다시 실행하세요",
            "details": context.get("failed_tests", [])
        }
    
    elif error_type == "timeout":
        return {
            "isError": True,
            "errorCategory": "transient",   # 일시적 오류 (재시도 가능)
            "isRetryable": True,
            "message": "CI 서버 응답 시간 초과",
            "retry_after_seconds": 30
        }
    
    elif error_type == "permission":
        return {
            "isError": True,
            "errorCategory": "permission",  # 권한 오류 (재시도 불가)
            "isRetryable": False,
            "message": "해당 저장소에 접근 권한이 없습니다"
        }
```

---

## 시나리오 기반 예상 문제

### Q: 툴 배분 결정

상황: 코드 리뷰 에이전트에 18개의 툴을 제공했더니 에이전트가 자주 잘못된 툴을 선택합니다.

가장 효과적인 해결책은?

A) 각 툴의 설명을 더 자세하게 작성  
B) Few-shot 예시를 추가하여 올바른 툴 선택 패턴 교육  
C) 에이전트를 기능별로 분리하여 각 에이전트가 4-5개 툴만 사용하도록 설계  
D) 더 강력한 모델(Opus)으로 교체  

정답: C — 너무 많은 툴(18개)은 선택 신뢰도 저하. 전문화된 에이전트로 분리하여 툴 수 줄이기

---

### Q: Grep vs Glob 선택

상황: 특정 import 문(`import anthropic`)을 사용하는 모든 Python 파일을 찾고 싶습니다.

올바른 툴은?

A) Glob ("*.py")  
B) Grep ("import anthropic", glob: "*.py")  
C) Read (모든 파일 읽기)  
D) Bash (find + grep)  

정답: B — 파일 내용에서 패턴 검색 = Grep. Glob은 파일 경로 패턴으로 찾을 때 사용

---

## 📝 챕터 요약

| 개념 | 핵심 내용 |
|------|---------|
| 툴 수 제한 | 18개 이하 (4-5개가 이상적) |
| 에이전트 전문화 | 기능별 분리로 선택 신뢰도 향상 |
| MCP 서버 | .mcp.json으로 팀 공유 |
| Hooks | PostToolUse (정규화), PreToolUse (차단) |
| 내장 툴 | Grep(내용), Glob(경로), Read, Edit, Write |
| 에러 분류 | transient(재시도 가능) vs others(불가) |

---

> 🔗 다음 챕터: [시나리오 5 — CI/CD 통합](21_scenario5_cicd.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Codex MCP, Hooks, Rules, Sandbox의 역할 분리

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | MCP, Hooks, Rules, Sandbox, Skills를 사용하는 기본 developer-tool 계층입니다. |
| **Codex app** | Skill 생성·관리 UI와 여러 coding task의 visual supervision이 app 전용 장점입니다. |
| **Codex SDK** | 내부 developer portal이나 bot에 Codex coding thread를 내장합니다. |
| **OpenAI Agents SDK** | 여러 business/developer specialist를 조율하고 Codex를 coding specialist로 호출할 때 사용합니다. |

### 1. “18개 tool”은 Codex의 공식 hard limit가 아니다

원문의 수치는 tool surface가 너무 커질 때 selection 품질과 schema token 비용이 악화될 수 있다는 **설계 휴리스틱**으로 읽어야 합니다. Codex/OpenAI에 “18개를 넘으면 안 된다”는 고정 제한으로 적용하면 안 됩니다.

Tool surface가 커지면 다음을 검토합니다.

```text
agent 역할 분리
MCP enabled_tools / disabled_tools
tool description 개선
관련 tool만 조건부 노출
Agents SDK tool search/deferred loading
read-only와 write tool 분리
```

### 2. Codex MCP project config

```toml
# .codex/config.toml

[mcp_servers.github_read]
command = "github-mcp-server"
args = ["stdio"]
env_vars = ["GITHUB_TOKEN"]
required = true

enabled_tools = [
  "search_code",
  "get_file_contents",
  "get_pull_request",
]

disabled_tools = [
  "delete_repository",
  "merge_pull_request",
]

default_tools_approval_mode = "prompt"
```

Remote HTTP:

```toml
[mcp_servers.internal_docs]
url = "https://docs.example.com/mcp"
bearer_token_env_var = "DOCS_MCP_TOKEN"
startup_timeout_sec = 15
tool_timeout_sec = 60
required = true
enabled_tools = ["search_documents", "get_document"]
```

프로젝트 config는 trusted project에서만 로드합니다. 개인 실험 MCP는 `~/.codex/config.toml`에 둡니다.

### 3. Tool description checklist

```text
동사와 대상이 명확한 이름
정확한 사용 시점
필수 identifier와 format
빈 결과의 의미
multiple match의 처리
side effect 여부
비슷한 tool과의 구분
error envelope
```

예:

```text
get_customer_by_erp_id
- exact ERP ID로 한 명을 조회
- free-text 이름 검색에는 사용하지 않음
- 없으면 not_found
- 중복은 data_error
- read-only
```

### 4. Native Hooks

`.codex/hooks.json`:

```json
{
  "description": "Repository lifecycle policy",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .codex/hooks/pre_tool_policy.py",
            "timeout": 30,
            "statusMessage": "Checking Bash command"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "^Bash$",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .codex/hooks/post_tool_review.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

`PreToolUse`는 Bash, `apply_patch`, MCP와 다수의 local function tool을 검사할 수 있습니다. Hosted tool은 같은 hook 경로에 포함되지 않을 수 있으므로 Hook을 완전한 보안 경계로 보지 않습니다.

차단 반환:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Production command blocked."
  }
}
```

입력 rewrite:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {
      "command": "pytest tests/unit"
    }
  }
}
```

### 5. Rules

```python
# .codex/rules/default.rules

prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
    justification = "Remote writes require approval.",
    match = [
        "git push",
        "git push origin feature/a",
    ],
    not_match = [
        "git status",
    ],
)
```

Rules는 sandbox 밖에서 command를 어떻게 처리할지 결정합니다. `.claude/rules/`의 파일별 coding convention과 전혀 다른 기능입니다.

### 6. Sandbox

```text
reviewer / explorer
→ read-only

일반 coding
→ workspace-write

fully isolated disposable environment에서만
→ danger-full-access 고려
```

`workspace-write`는 Claude의 `allowed-tools: Write`보다 넓습니다. 파일 쓰기 외 routine command도 가능하므로 “Write tool만” 같은 세밀한 allowlist와 1:1이 아닙니다.

### 7. Policy strength

```text
instruction
< Skill
< Hook / Rules / approval
< Sandbox
< external system RBAC
```

예를 들어 GitHub write operation은 MCP tool을 숨기는 것뿐 아니라 GitHub token 자체를 read-only permission으로 발급하는 것이 더 강한 통제입니다.

### 8. Error response

```json
{
  "status": "failed",
  "error": {
    "category": "permission",
    "code": "GITHUB_WRITE_FORBIDDEN",
    "retryable": false,
    "attempted_action": "merge_pull_request",
    "message": "The connected token has read-only repository permission."
  }
}
```

Agent가 오류를 우회하기 위해 다른 write tool을 찾지 않도록 required action과 retryability를 명시합니다.



### Codex SDK로 내부 developer tool 만들기

CLI command 하나로 충분하지 않고 자체 service/UI가 Codex thread를 소유해야 한다면 SDK를 사용합니다.

```typescript
import { Codex } from "@openai/codex-sdk";

export async function analyzePullRequest(
  repositoryPath: string,
  prompt: string,
) {
  const codex = new Codex({
    // 실제 configuration은 배포 환경과 SDK reference를 따릅니다.
  });

  const thread = codex.startThread({
    workingDirectory: repositoryPath,
  });

  const result = await thread.run(prompt);
  const threadId = thread.id;

  if (!threadId) {
    throw new Error("Codex thread ID was not initialized");
  }

  return {
    threadId,
    finalResponse: result.finalResponse,
  };
}
```

> SDK option 이름과 thread metadata surface는 version에 따라 바뀔 수 있으므로 실제 구현 시 현재 package reference를 확인합니다. 핵심은 application이 Codex thread lifecycle을 소유한다는 점입니다.

### Agents SDK가 Codex를 specialist로 호출하는 경우

Developer productivity system이 coding 외 업무까지 포함하면 Agents SDK가 상위 coordinator가 될 수 있습니다.

```text
Developer assistant
├─ Jira agent
├─ Slack agent
├─ docs agent
└─ Codex coding specialist
```

공식 Codex SDK 문서는 broader orchestrated workflow에서 Codex가 specialist라면 Codex CLI를 MCP server로 실행하고 Agents SDK에서 조율하는 패턴을 제시합니다.

```text
OpenAI Agents SDK
        ↓ MCP
Codex CLI / Codex coding agent
        ↓
repository
```

구분:

```text
Codex SDK
= 동일한 Codex coding agent를 자체 tool에 직접 embed

Agents SDK + Codex MCP
= 범용 manager가 Codex를 여러 specialist 중 하나로 사용
```

Agents SDK에는 workspace-scoped Codex 작업을 호출하는 실험적 `codex_tool`도 있습니다.

```python
from agents import Agent
from agents.extensions.experimental.codex import (
    ThreadOptions,
    TurnOptions,
    codex_tool,
)

agent = Agent(
    name="release_manager",
    instructions=(
        "Use Codex only for bounded repository tasks. "
        "Keep release policy decisions in this manager."
    ),
    tools=[
        codex_tool(
            working_directory="/path/to/repo",
            sandbox_mode="workspace-write",
            default_thread_options=ThreadOptions(
                approval_policy="never",
                web_search_mode="disabled",
            ),
            default_turn_options=TurnOptions(
                idle_timeout_seconds=60,
            ),
            persist_session=True,
        )
    ],
)
```

이 기능은 **실험적**입니다. 일반적인 선택 순서는 다음과 같습니다.

```text
Codex만 자체 product/tool에 embedding
→ Codex SDK

Agents SDK의 여러 specialist 중 Codex가 하나
→ Codex MCP 또는 experimental codex_tool
```

### 공식 문서

- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [Agents SDK tools and agents-as-tools](https://openai.github.io/openai-agents-python/tools/)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

# Chapter 27: 시험 범위 포함 주제

> 📅 2026년 04월 05일 기준  
> 🎯 시험 출제 범위 요약


[← Chapter 26](26_practice_questions.md) | [목차](../TOC.md) | [Chapter 28: 비출제 범위 →](28_out_of_scope.md)

---

## 시험 범위 개요

Claude Certified Architect – Foundations 시험은 다음 5개 도메인을 평가합니다.
각 도메인에서 확실히 알아야 할 핵심 주제를 정리했습니다.

---

## Domain 1: Agentic Architecture (27%)

### ✅ 반드시 알아야 할 주제

#### 에이전틱 루프
- `stop_reason` 기반 루프 제어
  - `"tool_use"` → 툴 실행 후 계속
  - `"end_turn"` → 루프 종료
  - `"max_tokens"` → 토큰 한계 도달
- 안티패턴: 텍스트 키워드, 고정 횟수만으로 종료

#### 멀티에이전트 시스템
- Hub-and-Spoke 아키텍처
- 서브에이전트 컨텍스트 자동 상속 없음
- `allowedTools`에 `"Task"` 포함 필요
- 병렬 실행: 단일 응답에서 여러 Task 동시 호출

#### 프로그래밍적 강제
- Critical 비즈니스 로직 = 코드로 강제
- 프롬프트 기반 = 확률적 (불충분)
- 게이트 패턴: `verified_customer_id` 확인 후 `process_refund` 허용

#### Hooks
- `PostToolUse`: 툴 결과 변환/정규화
- `PreToolUse`: 툴 호출 차단, 정책 강제

#### 세션 관리
- `--resume <session-name>`: 이름 있는 세션 재개
- `fork_session`: 공통 기준점에서 독립 탐색

#### 태스크 분해
- 프롬프트 체이닝: 순차, 각 단계가 이전 결과 의존
- 동적 분해: LLM이 판단, 미지의 범위 처리
- 좁은 분해의 위험: 범위 누락

---

## Domain 2: Tool Design & MCP (18%)

### ✅ 반드시 알아야 할 주제

#### 툴 설명 설계
- 설명 = LLM 툴 선택의 1차적 메커니즘
- 포함 내용: 사용 시점, 입력 형식, 예제, 엣지 케이스, 비슷한 툴과 구분
- 비슷한 툴은 설명에서 명확히 구분

#### 에러 응답 구조
| 필드 | 역할 |
|------|------|
| `isError` | 오류 여부 |
| `errorCategory` | transient/validation/business/permission |
| `isRetryable` | 재시도 가능 여부 |
| `message` | 사람이 읽을 수 있는 설명 |

- transient: 재시도 가능 (타임아웃, 서버 오류)
- validation/business/permission: 재시도 불가

#### tool_choice 옵션
- `"auto"`: 자율 선택 (기본값)
- `"any"`: 반드시 어떤 툴이든 사용
- `{"type": "tool", "name": "..."}`: 특정 툴 강제

#### MCP (Model Context Protocol)
- 표준 프로토콜: Claude와 외부 시스템 연결
- `.mcp.json` (프로젝트): 팀 공유, 버전 관리
- `~/.claude.json` (사용자): 개인 전용
- `${변수명}`: 환경 변수 참조

#### 내장 툴 선택 기준
| 툴 | 사용 시점 |
|----|----------|
| Grep | 파일 내용에서 패턴 검색 |
| Glob | 파일 경로 패턴으로 파일 찾기 |
| Read | 파일 전체 내용 읽기 |
| Edit | 유일한 텍스트 교체 |
| Write | 파일 전체 재작성 (Read 먼저!) |

---

## Domain 3: Claude Code (20%)

### ✅ 반드시 알아야 할 주제

#### CLAUDE.md 계층
```
우선순위 높음
~/.claude/CLAUDE.md          ← 사용자 (팀 공유 ❌)
.claude/CLAUDE.md            ← 프로젝트 (팀 공유 ✅)
src/payment/CLAUDE.md        ← 서브디렉토리 (더 높은 우선순위)
우선순위 낮음
```
- `@파일경로`: 다른 CLAUDE.md 파일 임포트

#### .claude/rules/
- YAML 파일 + glob 패턴 frontmatter
- 특정 파일 유형에만 조건부 적용
```yaml
---
paths:
  - "**/*.test.tsx"
  - "terraform/**/*"
---
```

#### 커맨드 vs Skills
| 위치 | 공유 범위 |
|------|---------|
| `.claude/commands/` | 팀 공유 (버전 관리) |
| `~/.claude/commands/` | 개인 전용 |

Skills frontmatter:
- `context: fork`: 격리 실행
- `allowed-tools`: 사용 가능 툴 목록
- `argument-hint`: 인자 없을 때 안내

#### Plan Mode 기준
- 사용: 45개+ 파일, 아키텍처 결정, 마이그레이션
- 불필요: 단일 파일 수정, 간단한 버그 수정

#### CI/CD
- `-p` / `--print`: 비대화형 모드 (필수!)
- `--output-format json`: 기계 처리 가능 출력
- `--json-schema`: 스키마 강제

---

## Domain 4: Prompt Engineering (20%)

### ✅ 반드시 알아야 할 주제

#### 명시적 기준 설계
- 모호한 지시 피하기: "보수적으로", "확신할 때만"
- 구체적 기준: "다음 조건을 모두 충족할 때만 X를 하라"
- False Positive: 일시 비활성화 → 기준 개발 → 재활성화

#### Few-Shot 패턴
- 2-4개 예시 (각각 다른 케이스)
- 모호한 케이스, 출력 형식, 다양한 구조 처리에 활용

#### 구조화된 출력
- `tool_use`: JSON 구문 오류 제거 (API 보장)
- 의미적 오류는 별도 검증 필요
- `nullable` 필드: 없는 정보 → null (환각 방지)

#### Batch API
- 50% 비용 절감
- 최대 24시간 처리
- SLA 없음 (지연 허용 시 사용)
- 적합: 야간 보고서, 대량 분류
- 부적합: pre-merge 체크, 실시간 응답

#### 리뷰 패턴
- 자기 리뷰 < 독립 인스턴스 리뷰
- 멀티패스: 파일별 분석 → 크로스파일 통합

---

## Domain 5: Context Management (15%)

### ✅ 반드시 알아야 할 주제

#### Lost-in-the-Middle
- 중간 정보 누락 위험
- 해결: 중요 정보를 처음과 끝에 배치
- 섹션 헤더로 구분

#### 요약 전략
- 수치(금액, 날짜, 번호) 반드시 보존
- "여러 주문" → "주문 #001 $45, #002 $120"
- 명시적 보존 지시 필요

#### 에스컬레이션 기준
즉시 에스컬레이션:
- 고객이 명시적으로 인간 요청
- 정책 공백/예외 상황
- 진전 불가한 상황

에스컬레이션 금지:
- 자신감 점수 낮음 ❌
- 고객이 화남 ❌
- 단순히 복잡해 보임 ❌

#### 에러 전파
구조화된 에러 컨텍스트:
- 에러 유형
- 시도된 작업
- 부분 결과
- 재시도 가능 여부
- 대안

#### 스크래치패드
- 긴 세션의 중간 상태 기록
- 컨텍스트 저하 방지

#### 상충 정보
- 임의 선택 금지
- 두 수치 모두 출처와 함께 보고

---

## 6개 시나리오 핵심 포인트

| 시나리오 | 핵심 개념 | 주요 함정 |
|---------|---------|---------|
| 1. 고객 지원 | 프로그래밍적 게이트 | 프롬프트로 순서 강제 불가 |
| 2. Claude Code | Plan Mode 판단 | 항상/절대 Plan Mode ❌ |
| 3. 멀티에이전트 연구 | 코디네이터 분해 | 좁은 분해 → 범위 누락 |
| 4. 개발자 생산성 | 툴 수 제한 | 더 많은 툴 = 더 나은 결과 ❌ |
| 5. CI/CD | -p 플래그 필수 | 대화형 모드로 파이프라인 ❌ |
| 6. 데이터 추출 | nullable + 재시도 | 없는 값 추측 ❌ |

---

> 🔗 다음 챕터: [시험 범위 외 주제](28_out_of_scope.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Codex 실무 학습 범위 재구성

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | Codex 실무 학습의 Level 1 기본입니다. |
| **Codex app** | CLI 학습 후 parallel thread/worktree/Automations UI를 추가 학습합니다. |
| **Codex SDK** | Codex를 자체 tool·CI에 embed하는 고급 개발 범위입니다. |
| **OpenAI Agents SDK** | production agent application 개발 범위입니다. |

Claude 시험 범위와 Codex 실무 범위는 겹치지만 동일하지 않습니다. Codex를 실제로 사용하려면 **네 개의 학습 트랙**과 별도 OpenAI API 기능을 구분합니다.

### Track 1. Codex CLI — repository 사용의 기본

```text
AGENTS.md
Skills
subagents
MCP
Hooks
Rules
Sandbox
/plan
/review
codex exec
codex review
```

완료 기준:

- root/nested `AGENTS.md`를 설명할 수 있음
- 팀 Skill을 만들 수 있음
- read-only와 workspace-write를 구분함
- project/user MCP config를 구분함
- `--json`과 `--output-schema`를 구분함

### Track 2. Codex app — 사람 중심의 병렬 감독

```text
projects and threads
parallel agents
built-in worktrees
visual diff and comments
open in editor
Skill management UI
Automations
review queue
```

완료 기준:

- CLI와 같은 configuration/session을 공유한다는 점을 설명
- app-only UI 기능과 CLI 기능을 구분
- 여러 worktree 결과를 사람이 비교·선택
- Automation과 deterministic CI gate를 구분

### Track 3. Codex SDK — Codex coding agent를 programmatically embedding

```text
@openai/codex-sdk
openai-codex
thread start/run/resume
runStreamed / event processing
outputSchema
sandbox per thread/turn
parallel coding threads
```

완료 기준:

- CLI shell 실행과 SDK embedding을 구분
- 같은 thread에서 여러 turn을 계속
- thread ID를 저장해 resume
- application에서 result object와 event를 처리
- coding-focused SDK임을 설명

### Track 4. OpenAI Agents SDK — 범용 agent application

```text
Agent
Runner
function tools
Agent.as_tool
handoffs
guardrails
sessions / RunState
tracing
human-in-the-loop
```

완료 기준:

- customer support/research/business agent를 설계
- Codex SDK와 Agents SDK의 책임을 구분
- critical invariant를 application code에 둠
- manager, handoff, code orchestration을 구분
- partial success와 typed errors를 처리
- Codex를 coding specialist로 연결할 시점을 판단

### 별도 OpenAI API 기능

```text
Responses API
Function Calling
Structured Outputs
Batch API
Responses Multi-agent
Compaction
```

이 API 기능은 CLI/app/SDK/Agents SDK 중 하나의 제품 이름으로 뭉뚱그리지 않습니다.

### Claude 시험 Domain별 네 계층 대응

| Claude Domain | 주요 대응 |
|---|---|
| Agentic Architecture | CLI subagents, app threads, Codex SDK threads, Agents SDK orchestration |
| Tool Design & MCP | Codex MCP와 Agents SDK tool/MCP integration |
| Claude Code | CLI/app 공통 AGENTS·Skills·Hooks·Rules·Sandbox |
| Prompt Engineering | Codex prompt/Skill, SDK output schema, Responses Structured Outputs |
| Context Management | CLI compact/subagent, app threads, SDK thread resume, Agents SDK session/state |

### 시험 범위에는 없지만 Codex 실무에서 필수에 가까운 것

```text
repository trust
sandbox boundary
secret scope
external RBAC
idempotency
audit trail
CI permissions
prompt injection from repository content
MCP OAuth/token scope
```

Claude 시험 준비와 production engineering의 범위를 혼동하지 않습니다.



### 네 계층별 최소 학습 목표

#### Codex CLI

```text
AGENTS.md
Skills
subagents
MCP
Hooks
Rules
Sandbox
/plan
/review
codex exec
codex review
```

#### Codex app

```text
project/thread 관리
parallel agents
built-in worktrees
visual diff/comment
Skill management UI
Automations
review queue
```

App은 CLI 개념을 대체하는 별도 설정 체계가 아니라 UI layer로 학습합니다.

#### Codex SDK

```text
TypeScript: @openai/codex-sdk
Python: openai-codex
thread start/run/resume
result object
sync/async use
sandbox per thread/turn
parallel coding threads
```

#### OpenAI Agents SDK

```text
Agent / Runner
function tools
Agent.as_tool()
handoffs
guardrails
sessions and RunState
tracing
HITL
Codex specialist orchestration
```

### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
<!-- CODEX-ADDENDUM-END -->

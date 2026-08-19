# Chapter 26: 추가 연습 문제 50선

> 📅 2026년 04월 05일 기준  
> 🎯 도메인별 실전 연습 문제


[← Chapter 25](25_sample_q9_12.md) | [목차](../TOC.md) | [Chapter 27: 출제 범위 →](27_in_scope.md)

---

## 사용 방법

- 각 문제를 읽고 정답을 결정한 후 해설을 확인하세요
- 각 도메인의 취약 부분을 파악하세요
- 틀린 문제는 해당 챕터로 돌아가 복습하세요

---

## Domain 1: Agentic Architecture (문제 1-14)

### 1. 에이전틱 루프 기본

에이전트가 `stop_reason == "tool_use"`를 받았을 때 올바른 동작은?

A) 루프 종료  
B) 툴 실행 후 결과를 messages에 추가하고 다음 API 호출  
C) 오류로 처리  
D) 새 세션 시작  

정답: B

---

### 2. 서브에이전트 컨텍스트

서브에이전트가 코디네이터의 정보에 접근하려면?

A) 자동으로 접근 가능  
B) 공유 메모리 사용  
C) 코디네이터가 Task 호출 시 컨텍스트를 명시적으로 전달  
D) 환경 변수로 공유  

정답: C — 자동 상속 없음, 명시적 전달 필수

---

### 3. allowedTools 설정

서브에이전트를 스폰하기 위해 코디네이터의 allowedTools에 반드시 포함해야 하는 것은?

A) "SubAgent"  
B) "Task"  
C) "Spawn"  
D) "Agent"  

정답: B

---

### 4. 병렬 실행

3개의 서브에이전트를 병렬로 실행하려면?

A) 3번의 별도 API 호출  
B) 코디네이터의 한 응답에서 3개의 Task를 동시에 호출  
C) async/await로 비동기 실행  
D) 3개의 코디네이터 인스턴스 사용  

정답: B

---

### 5. 프로그래밍적 강제 vs 프롬프트

어떤 경우에 프롬프트 지시 대신 프로그래밍적 강제가 필요한가?

A) 스타일 가이드 준수  
B) 응답 형식 설정  
C) 금전적 결과가 있는 비즈니스 로직 (예: 결제 승인)  
D) 언어 설정  

정답: C — Critical 비즈니스 로직 = 프로그래밍적 강제

---

### 6. PostToolUse 훅 용도

PostToolUse 훅의 주요 사용 목적은?

A) 툴 호출 차단  
B) 툴 결과 변환/정규화  
C) 새 툴 추가  
D) 세션 관리  

정답: B

---

### 7. PreToolUse 훅

PreToolUse 훅에서 가능한 것은?

A) 툴 결과 수정  
B) 툴 호출 차단 및 정책 강제  
C) 새 툴 생성  
D) 다른 에이전트 스폰  

정답: B

---

### 8. fork_session

fork_session의 주요 사용 목적은?

A) 현재 세션 삭제  
B) 공통 기준점에서 독립적인 여러 탐색 경로 시작  
C) 세션 병합  
D) 세션 백업  

정답: B

---

### 9. 태스크 분해 — 프롬프트 체이닝

프롬프트 체이닝이 가장 적합한 상황은?

A) 탐색 범위를 미리 알 수 없을 때  
B) 각 단계가 이전 결과에 의존하는 고정 워크플로우  
C) 여러 독립적인 분석이 필요할 때  
D) 빠른 병렬 처리가 필요할 때  

정답: B

---

### 10. 에이전트 루프 안전장치

에이전트 루프에서 최대 반복 횟수(예: 50)의 역할은?

A) 주요 종료 조건  
B) 성능 최적화  
C) 무한 루프 방지용 안전망 (보조적 역할)  
D) API 비용 제어  

정답: C

---

### 11. Hub-and-Spoke 장점

Hub-and-Spoke 아키텍처의 주요 장점은?

A) 모든 에이전트가 서로 직접 통신  
B) 코디네이터가 정보 흐름을 중앙에서 관리, 서브에이전트 간 직접 통신 없음  
C) 분산 처리로 인한 속도 향상  
D) 각 에이전트의 완전한 자율성  

정답: B

---

### 12. 세션 재개

이름 있는 세션을 재개하는 올바른 방법은?

A) `claude --session "session-name"`  
B) `claude --resume "session-name"`  
C) `claude --continue "session-name"`  
D) `claude --load "session-name"`  

정답: B

---

### 13. 동적 분해 vs 정적

동적 분해가 정적 분해보다 적합한 상황은?

A) 항상 5단계를 거치는 문서 처리  
B) 주제마다 필요한 분석 영역이 다른 연구 시스템  
C) 고정된 ETL 파이프라인  
D) 표준화된 보고서 생성  

정답: B

---

### 14. 컨텍스트 전달 실수

서브에이전트가 예상치 못한 결과를 반환하는 가장 흔한 원인은?

A) 모델 버전 불일치  
B) API 키 오류  
C) 코디네이터 컨텍스트를 전달하지 않아 서브에이전트가 배경 정보 부족  
D) 네트워크 지연  

정답: C

---

## Domain 2: Tool Design & MCP (문제 15-22)

### 15. 툴 설명의 역할

툴 설명(description)의 주요 역할은?

A) API 문서 생성  
B) LLM이 어떤 툴을 사용할지 결정하는 1차적 메커니즘  
C) 타입 검증  
D) 에러 메시지 생성  

정답: B

---

### 16. 에러 분류 — 재시도 가능

다음 중 `isRetryable: true`인 에러는?

A) 권한 없음 (permission)  
B) 서버 타임아웃 (transient)  
C) 정책 위반 (business)  
D) 잘못된 입력 형식 (validation)  

정답: B

---

### 17. tool_choice: any

`tool_choice: "any"`의 의미는?

A) 모든 툴 동시 사용  
B) 툴 선택 비활성화  
C) 모델이 반드시 어떤 툴이든 하나를 호출해야 함  
D) 가장 적합한 툴 자동 선택  

정답: C

---

### 18. 툴 수 최적화

에이전트에 제공할 최적 툴 수는?

A) 최대한 많이 (더 많은 기능)  
B) 18개 이하 (선택 신뢰도 유지)  
C) 정확히 5개  
D) 도메인에 따라 제한 없음  

정답: B

---

### 19. MCP 범위 — 팀 공유

팀이 공유해야 하는 MCP 서버 설정 위치는?

A) `~/.claude.json`  
B) `~/.claude/mcp.json`  
C) `.mcp.json` (프로젝트 루트)  
D) `CLAUDE.md`  

정답: C

---

### 20. 환경 변수 확장

.mcp.json에서 환경 변수를 참조하는 올바른 형식은?

A) `$GITHUB_TOKEN`  
B) `${GITHUB_TOKEN}`  
C) `ENV:GITHUB_TOKEN`  
D) `%GITHUB_TOKEN%`  

정답: B

---

### 21. Grep vs Glob

파일 내용에서 특정 함수 호출을 찾을 때 사용해야 하는 툴은?

A) Glob  
B) Read  
C) Grep  
D) Bash  

정답: C — 파일 내용 검색 = Grep

---

### 22. 빈 결과 vs 접근 실패

데이터베이스 쿼리에서 레코드가 없는 경우와 DB 연결 실패를 어떻게 구분해야 하는가?

A) 두 경우 모두 동일한 null 반환  
B) 빈 배열(레코드 없음) vs 에러 객체(접근 실패)로 명확히 구분  
C) 두 경우 모두 예외 발생  
D) 항상 재시도 후 구분  

정답: B

---

## Domain 3: Claude Code (문제 23-31)

### 23. CLAUDE.md 우선순위

CLAUDE.md 계층에서 가장 높은 우선순위는?

A) 프로젝트 루트 `.claude/CLAUDE.md`  
B) 사용자 `~/.claude/CLAUDE.md`  
C) 서브디렉토리 `CLAUDE.md`  
D) 모두 동일  

정답: C — 더 구체적인 (가까운) 파일이 우선 적용

---

### 24. 팀 공유 커맨드 위치

팀 전체가 사용할 `/deploy` 커맨드 파일 위치는?

A) `~/.claude/commands/deploy.md`  
B) `.claude/commands/deploy.md`  
C) `CLAUDE.md` 내 정의  
D) `.mcp.json`  

정답: B

---

### 25. CLAUDE.md vs .claude/rules/

`.claude/rules/`의 YAML 파일을 사용하는 주된 이유는?

A) CLAUDE.md보다 우선순위가 높음  
B) 특정 파일 패턴(glob)에만 조건부로 규칙 적용  
C) 더 많은 규칙 포함 가능  
D) 성능 최적화  

정답: B

---

### 26. Plan Mode 트리거

Plan Mode가 필요한 상황은?

A) 단일 파일 함수 추가  
B) 명확한 스택 트레이스가 있는 버그 수정  
C) 30개 이상 파일에 영향을 미치는 마이크로서비스 분리  
D) 변수명 변경  

정답: C

---

### 27. -p 플래그

Claude Code에서 `-p` 플래그의 역할은?

A) 프로필 설정  
B) 비대화형(headless) 단일 실행 모드  
C) 프롬프트 파일 지정  
D) 프리미엄 모드 활성화  

정답: B

---

### 28. context: fork

Skills/커맨드에서 `context: fork`의 효과는?

A) 현재 세션 복제  
B) 격리된 서브에이전트에서 실행 (현재 세션 컨텍스트 보호)  
C) 포크 프로세스 생성  
D) 병렬 세션 시작  

정답: B

---

### 29. @import 문법

CLAUDE.md에서 다른 파일을 포함하는 방법은?

A) `#include backend/CLAUDE.md`  
B) `{{import backend/CLAUDE.md}}`  
C) `@backend/CLAUDE.md`  
D) `!include backend/CLAUDE.md`  

정답: C

---

### 30. --output-format json

CI/CD에서 `--output-format json`의 주요 목적은?

A) 더 빠른 응답  
B) 기계가 파싱할 수 있는 구조화된 출력  
C) 저장 공간 절약  
D) 인코딩 문제 해결  

정답: B

---

### 31. 사용자 CLAUDE.md

`~/.claude/CLAUDE.md`의 특징은?

A) 팀과 자동으로 공유됨  
B) 버전 관리됨  
C) 개인 전용, 팀 공유 안 됨  
D) 모든 프로젝트에서 무시됨  

정답: C

---

## Domain 4: Prompt Engineering (문제 32-40)

### 32. 명시적 기준의 중요성

"보수적으로 평가하라"는 지시의 문제점은?

A) 너무 길다  
B) 모호하다 — 에이전트마다 "보수적"의 기준이 다르다  
C) 문법 오류  
D) 성능 저하  

정답: B

---

### 33. Few-Shot 최적 수

Few-shot 예시의 최적 수는?

A) 1개  
B) 2-4개 (각각 다른 케이스)  
C) 10개 이상  
D) 케이스마다 1개  

정답: B

---

### 34. tool_use의 보장

`tool_use`가 보장하는 것은?

A) 의미적으로 올바른 값  
B) JSON 구문 오류 없음  
C) 완전한 데이터 추출  
D) 실시간 처리  

정답: B — 구문 오류 제거. 의미적 검증은 별도 필요

---

### 35. nullable 필드

없을 수 있는 선택적 필드를 어떻게 정의해야 하는가?

A) required 목록에서 제외  
B) `{"type": ["string", "null"]}`로 정의하고 null 사용 지시  
C) 기본값 설정  
D) 필드 자체를 삭제  

정답: B

---

### 36. Batch API 적합 사용 사례

Batch API가 부적합한 사용 사례는?

A) 야간 보고서 생성  
B) 주간 코드베이스 분석  
C) PR 머지 전 자동 코드 리뷰 (즉각 응답 필요)  
D) 대량 문서 분류  

정답: C

---

### 37. 자기 리뷰 한계

에이전트가 자신의 출력을 검토하는 것의 한계는?

A) 속도가 느림  
B) 비용이 많이 듦  
C) 같은 편향을 공유하여 자신의 실수를 발견하지 못함  
D) API 제한  

정답: C

---

### 38. 독립 인스턴스 리뷰

코드 리뷰 품질을 높이는 가장 효과적인 방법은?

A) 더 강력한 모델 사용  
B) 리뷰 시간 증가  
C) 원본 분석과 다른 독립 Claude 인스턴스로 리뷰  
D) 여러 번 자기 리뷰  

정답: C

---

### 39. 멀티패스 리뷰

멀티패스 리뷰의 올바른 순서는?

A) 크로스파일 통합 → 개별 파일 분석  
B) 개별 파일 분석 → 크로스파일 통합 분석  
C) 동시에 모든 파일 분석  
D) 랜덤 순서  

정답: B

---

### 40. Batch API 특성

Batch API의 올바른 특성은?

A) 실시간 처리, 100% 비용 절감  
B) 최대 1시간 처리, 25% 비용 절감  
C) 최대 24시간 처리, 50% 비용 절감, SLA 없음  
D) 즉각 처리, 비용 동일  

정답: C

---

## Domain 5: Context Management (문제 41-50)

### 41. Lost-in-the-Middle

Lost-in-the-Middle 효과를 완화하는 방법은?

A) 컨텍스트 최소화  
B) 중요 정보를 컨텍스트의 처음과 끝에 배치  
C) 요약 사용 금지  
D) 짧은 메시지 사용  

정답: B

---

### 42. 요약 보존 필수 항목

요약 시 반드시 보존해야 하는 항목은?

A) 문체와 어조  
B) 배경 설명  
C) 금액, 날짜, 주문 번호, 고객 ID 등 구체적 수치  
D) 인사말  

정답: C

---

### 43. 에스컬레이션 기준

즉시 에스컬레이션해야 하는 상황은?

A) 고객이 화남  
B) 응답 자신감이 낮음  
C) 고객이 명시적으로 사람 연결을 요청  
D) 처리에 시간이 걸림  

정답: C

---

### 44. 에스컬레이션 하지 말아야 할 상황

에스컬레이션하지 않아야 하는 상황은?

A) 정책 공백 발생  
B) 고객이 인간 상담원 요청  
C) 에이전트의 자신감 점수가 4/10  
D) 시스템에서 처리 불가한 예외  

정답: C — 감정/자신감 기반 에스컬레이션 금지

---

### 45. 구조화된 에러 컨텍스트

에러 전파 시 포함해야 하는 정보는?

A) 스택 트레이스만  
B) 에러 유형, 시도된 작업, 부분 결과, 재시도 가능 여부, 대안  
C) 에러 코드만  
D) 타임스탬프만  

정답: B

---

### 46. 스크래치패드 패턴

스크래치패드를 사용하는 주된 이유는?

A) 최종 응답 품질 향상  
B) 긴 세션에서 중간 상태와 결정을 기록하여 컨텍스트 저하 방지  
C) API 비용 절감  
D) 응답 속도 향상  

정답: B

---

### 47. 상충 정보 처리

두 소스에서 다른 날짜를 받았을 때 올바른 처리는?

A) 최신 날짜 선택  
B) 첫 번째 소스 우선  
C) 두 날짜 모두 출처와 함께 보고  
D) 중간값 사용  

정답: C

---

### 48. 구조화된 사실 블록

긴 세션에서 중요한 사실을 유지하는 방법은?

A) 처음에만 언급  
B) 매 프롬프트에 핵심 사실을 구조화된 블록으로 반복 포함  
C) 별도 파일에 저장  
D) 요약으로 대체  

정답: B

---

### 49. 컨텍스트 트리밍

컨텍스트가 한계에 가까워질 때 올바른 트리밍 전략은?

A) 오래된 메시지를 무작위로 삭제  
B) 전체 컨텍스트 초기화  
C) 가장 오래된 turn부터 제거하되 핵심 시스템 프롬프트와 최근 컨텍스트 유지  
D) 응답 길이 제한  

정답: C

---

### 50. 에스컬레이션 정책 공백

정책이 명확하지 않은 예외 상황에서 에이전트는?

A) 가장 일반적인 정책 적용  
B) 처리 거부  
C) 에스컬레이션 (정책 공백은 에스컬레이션 조건)  
D) 고객에게 다시 물어봄  

정답: C — 정책 공백 = 즉시 에스컬레이션

---

## 점수 채점

| 맞은 수 | 평가 |
|---------|------|
| 45-50개 | 우수 — 합격 준비 완료 |
| 38-44개 | 양호 — 약점 도메인 추가 학습 |
| 30-37개 | 보통 — 전체 복습 필요 |
| 30개 미만 | 부족 — 기초 챕터부터 재학습 |

---

> 🔗 다음 챕터: [시험 범위 포함 주제](27_in_scope.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 50문제를 Codex 관점으로 변환하는 해답 키

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | Claude Code 문제를 `AGENTS.md`, Skill, subagent, MCP, exec로 변환하는 기본 답입니다. |
| **Codex app** | CLI와 공통인 답은 반복하지 않고, worktree·Automations·visual supervision만 별도 app 답으로 봅니다. |
| **Codex SDK** | coding agent를 programmatic thread로 호출해야 하는 문제에 사용합니다. |
| **OpenAI Agents SDK** | 고객지원·연구·업무 agent application 문제에 사용합니다. |

기존 50문제는 Claude 시험용이므로 정답을 바꾸지 않습니다. 대신 문제를 푼 뒤 **제품 syntax와 underlying principle을 분리**해 두 번째 답을 작성합니다.

### 1. Domain 1: Agentic Architecture 변환

| Claude 문제 키워드 | Codex/OpenAI 해석 |
|---|---|
| `stop_reason` | Claude API 전용. CLI/app/SDK는 Codex runtime, Agents SDK는 `Runner`가 loop 관리 |
| Task context | Codex subagent도 bounded task context를 명시적으로 받아야 함 |
| `allowedTools: Task` | Codex에는 복사하지 않음. Native subagents 사용 |
| 한 응답에서 여러 Task | CLI subagent / app parallel thread / Codex SDK 여러 thread / Agents SDK agent-as-tool |
| 반드시 N개 병렬 | Codex SDK 또는 Agents SDK/application code의 `Promise.all()`·`asyncio.gather()` |
| critical business rule | application code에서 강제 |
| PostToolUse | Codex native `PostToolUse` Hook |
| PreToolUse | Codex native `PreToolUse` Hook |
| `fork_session` | Codex subagent, `/side`, 별도 run의 목적과 비교 |
| prompt chaining | 단계 의존성이 있는 code-driven workflow |
| max iteration | 주 종료 조건이 아니라 안전망 |
| Hub-and-Spoke | Agents SDK manager pattern |
| session resume | 사용하는 Codex/Agents SDK session 기능을 공식 문서에서 확인 |
| dynamic decomposition | model-directed orchestration |
| context 전달 | task contract로 목표·범위·제약·output 전달 |

### 2. Domain 2: Tool Design & MCP 변환

| Claude 문제 키워드 | Codex/OpenAI 해석 |
|---|---|
| tool description | MCP/function tool 모두 동일하게 중요 |
| transient error | backoff retry |
| `tool_choice: any` | OpenAI에서는 `required` 등 제품별 값 확인 |
| tool 수 18개 | hard limit 아님. 역할 분리·filter·tool search 고려 |
| `.mcp.json` | `.codex/config.toml` |
| `${ENV_VAR}` | token value는 env/secret store |
| Grep vs Glob | 목적은 동일: content search vs path discovery |
| empty vs access failure | typed status/envelope로 분리 |

OpenAI Agents SDK의 tool choice는 `auto`, `required`, `none`, 특정 tool 이름처럼 표현될 수 있습니다. Anthropic의 문자열 값을 그대로 복사하지 않습니다.

### 3. Domain 3: Claude Code 변환

| Claude 정답 | Codex 대응 |
|---|---|
| `CLAUDE.md` | `AGENTS.md` |
| 팀 command | repo `.agents/skills/` |
| `.claude/rules/paths` | 정확한 1:1 없음 |
| Plan Mode | `/plan` |
| `claude -p` | `codex exec` |
| `context: fork` | subagent |
| `@import` | Codex에서는 계층적 AGENTS discovery를 우선 |
| JSON output | `--json` event stream 또는 `--output-schema` final schema |
| 사용자 CLAUDE | `~/.codex/AGENTS.md` |

### 4. Domain 4: Prompt/Output 변환

```text
명시적 기준
→ 동일

Few-shot
→ 동일, Skill references와 eval fixture로 관리

tool_use JSON
→ Structured Outputs 또는 Function Calling

nullable
→ Pydantic Optional/null

Batch
→ OpenAI Batch API

독립 review
→ /review, codex review, reviewer subagent
```

### 5. Domain 5: Context/Reliability 변환

```text
Lost-in-the-Middle
→ concise AGENTS + bounded Skill/subagent

요약 사실 보존
→ typed state + summary validation

escalation
→ objective code trigger + Agents SDK HITL

구조화 error
→ ResultEnvelope

scratchpad
→ 작업 메모일 뿐 source of truth 아님

상충 정보
→ source별 후보 보존
```

### 제품 계층을 묻는 문제의 빠른 답

| 문제 표현 | 선택 |
|---|---|
| 개발자가 terminal에서 repository를 직접 작업 | Codex CLI |
| 사람이 여러 agent/worktree/diff를 UI로 감독 | Codex app |
| 내부 프로그램이 Codex thread를 start/run/resume | Codex SDK |
| 고객지원·연구·업무 agent와 handoff/HITL | OpenAI Agents SDK |
| 일반 data schema를 model API에서 추출 | Responses Structured Outputs |
| 대량 비차단 request | Batch API |

### 6. 모든 문제에 적용할 10개 bucket

문제를 읽고 먼저 아래 중 하나로 분류합니다.

| 질문 | Codex/OpenAI 선택 |
|---|---|
| 항상 적용되는 repository 지침인가? | `AGENTS.md` |
| 반복 workflow인가? | Skill |
| noisy/독립 전문 작업인가? | Subagent |
| 외부 시스템 연결인가? | MCP |
| lifecycle event custom logic인가? | Hook |
| shell command 정책인가? | Rules/approval |
| 실제 파일·network capability인가? | Sandbox |
| critical business invariant인가? | Application code |
| machine-readable final output인가? | Structured Outputs |
| CI automation인가? | `codex exec` / GitHub Action |

### 7. 연습 방법

각 문제마다 답안을 두 줄로 기록합니다.

```text
Claude 시험 정답:
A — .claude/commands/

Underlying principle:
팀이 version control로 공유하는 reusable workflow

Codex 대응:
.agents/skills/<name>/SKILL.md
```

이 방식은 Claude syntax를 잊지 않으면서 다른 agent platform에도 원리를 적용하게 해줍니다.

### 8. 혼동 방지 규칙

- `.codex/rules/`를 Claude `.claude/rules/`의 대응으로 쓰지 않습니다.
- Codex Skill이 자동으로 별도 context를 만든다고 가정하지 않습니다.
- `codex exec --json`을 final schema output으로 오해하지 않습니다.
- Codex CLI, Codex app, Codex SDK, OpenAI Agents SDK를 하나의 runtime처럼 설명하지 않습니다.
- 모델 confidence를 objective approval probability로 사용하지 않습니다.


### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

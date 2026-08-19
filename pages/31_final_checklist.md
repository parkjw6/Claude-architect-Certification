# Chapter 31: 최종 체크리스트

> 📅 2026년 04월 05일 기준  
> ✅ 시험 전날과 당일 확인 목록


[← Chapter 30](30_exam_strategy.md) | [목차](../TOC.md) | [마치며 →](32_conclusion.md)

---

## 시험 전날 체크리스트

### 지식 확인

#### Domain 1: Agentic Architecture (27%)
- [ ] 에이전틱 루프: `stop_reason == "end_turn"` 시 종료
- [ ] 서브에이전트는 코디네이터 컨텍스트 자동 상속 안 함
- [ ] `allowedTools`에 `"Task"` 포함해야 서브에이전트 스폰 가능
- [ ] 병렬 서브에이전트 = 한 응답에서 여러 Task 동시 호출
- [ ] 프로그래밍적 강제 vs 프롬프트 지시 차이 명확히 이해
- [ ] `PostToolUse` 훅: 데이터 정규화
- [ ] 프롬프트 체이닝 vs 동적 분해 차이 이해
- [ ] `fork_session`: 공통 기준점에서 독립 탐색

#### Domain 2: Tool Design & MCP (18%)
- [ ] 툴 설명 = LLM 툴 선택의 1차적 메커니즘
- [ ] `isError`, `errorCategory`, `isRetryable` 필드
- [ ] transient(재시도 가능) vs validation/business/permission(불가)
- [ ] 빈 결과 vs 액세스 실패 구분
- [ ] `tool_choice`: auto / any / 강제 지정
- [ ] 너무 많은 툴(18개)은 선택 신뢰도 저하
- [ ] `.mcp.json` (프로젝트) vs `~/.claude.json` (사용자)
- [ ] `${변수명}` 환경 변수 확장
- [ ] Grep vs Glob vs Read vs Edit vs Write 선택 기준

#### Domain 3: Claude Code (20%)
- [ ] CLAUDE.md 3단계 계층: 사용자 → 프로젝트 → 디렉토리
- [ ] 사용자 수준 CLAUDE.md는 팀 공유 안 됨
- [ ] `.claude/rules/`의 YAML frontmatter glob 패턴
- [ ] 팀 커맨드: `.claude/commands/` / 개인: `~/.claude/commands/`
- [ ] `context: fork`: 격리 서브에이전트 실행
- [ ] `allowed-tools`: 스킬 툴 제한
- [ ] `argument-hint`: 인자 없을 때 안내
- [ ] Plan Mode vs Direct Execution 선택 기준
- [ ] `-p` 플래그: CI/CD 비대화형 모드
- [ ] `--output-format json`: 기계 처리 가능 출력

#### Domain 4: Prompt Engineering (20%)
- [ ] 명시적 기준 > "보수적으로", "확신할 때만" 같은 모호한 지시
- [ ] FP 높은 카테고리 → 일시 비활성화 후 기준 개선
- [ ] Few-shot: 2-4개, 각각 다른 케이스
- [ ] tool_use = JSON 구문 오류 제거 (의미 오류는 별도 검증)
- [ ] nullable 필드: 없는 정보 환각 방지
- [ ] Batch API: 50% 비용 절감, 최대 24시간, 비차단 작업만
- [ ] 자기 리뷰 < 독립 인스턴스 리뷰
- [ ] 멀티패스: 파일별 분석 + 크로스파일 통합

#### Domain 5: Context Management (15%)
- [ ] Lost-in-the-Middle: 중간 정보 누락 → 중요 내용 앞뒤 배치
- [ ] 요약 시 수치(금액, 날짜, 번호) 반드시 보존
- [ ] 구조화된 사실 블록: 매 프롬프트에 핵심 사실 포함
- [ ] 에스컬레이션 = 명시적 요청, 정책 공백, 진전 불가
- [ ] 감정/자신감 점수로 에스컬레이션 결정 금지
- [ ] 구조화된 에러 컨텍스트: 실패 유형 + 부분 결과 + 대안
- [ ] 스크래치패드: 긴 세션 컨텍스트 저하 방지
- [ ] 상충 정보: 임의 선택 대신 두 수치 모두 출처와 함께

---

## 6개 시나리오 핵심 포인트 확인

| 시나리오 | 가장 중요한 포인트 |
|---------|-----------------|
| 1. 고객 지원 | get_customer → 프로그래밍적 게이트 |
| 2. Claude Code | Plan Mode 판단 기준 |
| 3. 멀티에이전트 연구 | 코디네이터 태스크 분해 (좁으면 범위 누락) |
| 4. 개발자 생산성 | 툴 배분 (전문화, 적은 수) |
| 5. CI/CD | `-p` 플래그, JSON 출력 |
| 6. 데이터 추출 | nullable 필드, 재시도 유효성 |

---

## 시험 당일 체크리스트

### 응시 전 준비 (2시간 전)
- [ ] 치트시트 마지막으로 훑어보기
- [ ] 등록 확인: https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request
- [ ] 응시 환경 확인 (인터넷, 조용한 공간)

### 문제 풀이 전략

시간 관리:
- 총 시험 시간 확인 후 문제당 평균 시간 계산
- 모르는 문제는 표시하고 패스 → 나중에 재검토
- 오답 감점 없음 → 모든 문제 반드시 선택

문제 분석 순서:
1. 시나리오 파악 (어떤 시나리오인가?)
2. 핵심 제약 조건 파악 ("critical", "first step", "most effective" 등)
3. 각 선택지의 근본 원인 분석
4. 가장 "결정론적"이고 "직접적인" 해결책 선택

함정 피하기:
- "프롬프트에 강조하면 된다" → 보통 ❌ (프로그래밍적 강제가 필요한 경우)
- "감정/자신감으로 에스컬레이션" → 항상 ❌
- "더 많은 툴 제공" → 보통 ❌ (적은 도구, 명확한 역할)
- "같은 세션에서 리뷰" → ❌ (독립 인스턴스)

---

## 최종 마음가짐

### 합격자의 사고방식

이 시험은 "왜 이 선택이 더 나은가?" 를 판단하는 시험입니다.

모든 선택지가 그럴듯해 보일 수 있습니다. 
하지만 항상 근본 원인 직접 해결 + 가장 낮은 복잡도 + 결정론적 보장을 기준으로 판단하세요.

```
정답의 패턴:
- 단순하고 직접적인 해결책
- 근본 원인을 직접 해결
- 결정론적 보장 (확률적 준수 < 프로그래밍적 강제)
- 적절한 복잡도 (과도한 엔지니어링 ❌)
```

---

> 🏆 당신은 이 책을 통해 충분히 준비했습니다. 시험에서 실력을 발휘하세요!

---

> 🔗 마지막으로: [마치며](32_conclusion.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Codex/OpenAI 최종 체크리스트

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | repository 사용, configuration, exec/review의 최종 점검 대상입니다. |
| **Codex app** | parallel threads, worktrees, visual diff, Skill UI, Automations를 별도 점검합니다. |
| **Codex SDK** | TS/Python installation, thread start/run/resume, sandbox, result handling을 점검합니다. |
| **OpenAI Agents SDK** | Agent/Runner, tools, orchestration, guardrails, sessions, HITL을 점검합니다. |

## A. 제품 계층

- [ ] Codex CLI와 OpenAI Agents SDK를 구분할 수 있다.
- [ ] Responses API와 Agents SDK 중 loop 소유자가 누구인지 설명할 수 있다.
- [ ] Batch API를 interactive workflow에 사용하지 않는다.
- [ ] Codex는 production 고객지원 runtime이 아니라 coding agent라는 점을 구분한다.

## B. AGENTS.md

- [ ] root `AGENTS.md`에는 repo 공통 규칙만 둔다.
- [ ] directory-specific 규칙은 nested `AGENTS.md`에 둔다.
- [ ] `AGENTS.override.md`의 용도를 알고 있다.
- [ ] always-on 문서를 과도하게 키우지 않는다.
- [ ] critical invariant를 `AGENTS.md`만으로 강제하지 않는다.

## C. Skills

- [ ] 팀 Skill은 `.agents/skills/<name>/SKILL.md`에 둔다.
- [ ] `name`과 `description`이 실제 trigger를 명확히 설명한다.
- [ ] 긴 예시와 기준은 `references/`로 분리한다.
- [ ] 반복 script는 `scripts/`로 분리한다.
- [ ] Codex Skill에 Claude의 `context: fork`를 그대로 넣지 않는다.
- [ ] `argument-hint` 대신 Required input 계약을 작성한다.

## D. Subagents

- [ ] noisy exploration은 subagent에 위임한다.
- [ ] project custom agent는 `.codex/agents/*.toml`에 둔다.
- [ ] reviewer/explorer는 기본적으로 `read-only`를 사용한다.
- [ ] task에 goal, scope, exclusions, output을 명시한다.
- [ ] 병렬 agent가 같은 mutable file을 수정하지 않게 한다.
- [ ] 반드시 N개 run이 필요하면 code-level orchestration을 사용한다.

## E. MCP

- [ ] project MCP는 `.codex/config.toml`에 둔다.
- [ ] 개인 MCP는 `~/.codex/config.toml`에 둔다.
- [ ] token 값은 repository에 저장하지 않는다.
- [ ] `enabled_tools`와 `disabled_tools`로 tool surface를 줄인다.
- [ ] write tool은 approval과 external RBAC까지 확인한다.
- [ ] project config는 trusted project에서 로드된다는 점을 이해한다.

## F. Hooks, Rules, Sandbox

- [ ] Hook은 lifecycle custom code라는 점을 안다.
- [ ] `PreToolUse`와 `PostToolUse`의 차이를 안다.
- [ ] Hook이 모든 hosted tool을 포괄하는 security boundary가 아님을 안다.
- [ ] Rules는 shell command 정책이며 coding glob rule이 아님을 안다.
- [ ] `read-only`, `workspace-write`, `danger-full-access`를 구분한다.
- [ ] 실제 production permission은 외부 시스템에서 다시 강제한다.

## G. Review와 Plan

- [ ] 대규모 변경 전 `/plan`을 사용한다.
- [ ] 작은 명확한 수정에는 불필요한 plan을 강제하지 않는다.
- [ ] 일반 review는 `/review` 또는 `codex review`를 사용할 수 있다.
- [ ] 팀 review criteria는 Skill로 관리한다.
- [ ] 구현 thread의 self-review만 믿지 않는다.
- [ ] finding은 file, line, evidence, impact를 포함한다.

## H. CI/CD

- [ ] Claude `-p`의 Codex 대응이 `codex exec`임을 안다.
- [ ] `--json`은 JSONL event stream임을 안다.
- [ ] final schema에는 `--output-schema`를 쓴다.
- [ ] 분석은 read-only로 시작한다.
- [ ] write가 필요할 때만 workspace-write로 확장한다.
- [ ] API key를 untrusted build step과 job-wide로 공유하지 않는다.
- [ ] 공식 `openai/codex-action@v1`을 검토한다.

## I. Structured Outputs

- [ ] final output과 function call 목적을 구분한다.
- [ ] Pydantic Optional/null을 올바르게 설계한다.
- [ ] `not_found`, `access_error`, `parse_error`를 구분한다.
- [ ] schema validation 뒤 semantic validation을 수행한다.
- [ ] source에 없는 값은 retry로 발명하지 않는다.
- [ ] 중요한 claim에 evidence/source를 붙인다.

## J. Agents SDK

- [ ] `Agent`와 `Runner`의 역할을 설명할 수 있다.
- [ ] manager pattern과 handoff를 구분한다.
- [ ] `Agent.as_tool()`의 용도를 안다.
- [ ] fixed parallel workflow에는 `asyncio.gather()`를 고려한다.
- [ ] sensitive tool에는 HITL approval을 설계한다.
- [ ] interruption state를 저장·resume하는 책임을 이해한다.
- [ ] critical business rule은 tool 내부 service에서 재검증한다.

## K. Context와 Reliability

- [ ] `/compact`와 authoritative state를 구분한다.
- [ ] IDs, 금액, 통화, 날짜, approval을 typed state로 보존한다.
- [ ] raw logs는 artifact에 두고 model에는 요약을 전달한다.
- [ ] partial success를 정상 완료로 숨기지 않는다.
- [ ] transient/validation/permission/business 오류를 구분한다.
- [ ] side-effect retry에는 idempotency key를 사용한다.
- [ ] 상충 정보는 두 값을 source와 함께 보존한다.

## L. 최종 암기 문장

```text
AGENTS.md
= 항상 지킬 기준

Skill
= 온디맨드 workflow

Subagent
= 별도 context의 전문 작업

MCP
= 외부 tool/data 연결

Hook
= lifecycle intervention

Rules
= command policy

Sandbox
= actual capability

Structured Outputs
= final schema

Agents SDK
= application orchestration

Application code
= critical invariant
```



## M. Codex app 전용 점검

- [ ] App은 CLI와 같은 Codex coding agent/configuration을 쓰는 UI layer임을 안다.
- [ ] CLI 설명을 app에서는 자연어로 실행할 수 있음을 안다.
- [ ] 여러 project/thread를 병렬 관리할 수 있다.
- [ ] built-in worktree로 agent별 변경을 격리할 수 있다.
- [ ] thread 안에서 diff를 review하고 editor로 열 수 있다.
- [ ] Skill 관리 UI의 역할을 안다.
- [ ] Automations와 review queue를 사용할 수 있다.
- [ ] App Automation을 deterministic CI required check와 혼동하지 않는다.

## N. Codex SDK 전용 점검

- [ ] Codex SDK가 CLI를 구동하는 동일 coding agent를 programmatically 제어함을 안다.
- [ ] Codex SDK와 OpenAI Agents SDK를 구분한다.
- [ ] TypeScript package가 `@openai/codex-sdk`임을 안다.
- [ ] Python package가 `openai-codex`이며 2026-08-19 기준 beta임을 안다.
- [ ] thread start, repeated run, resume의 차이를 안다.
- [ ] SDK result object와 `finalResponse`/`final_response`를 처리할 수 있다.
- [ ] sync `Codex`와 async `AsyncCodex`의 용도를 안다.
- [ ] `Sandbox.read_only`, `workspace_write`, `full_access`를 구분한다.
- [ ] 여러 coding thread를 `Promise.all()` 또는 `asyncio.gather()`로 병렬 실행할 수 있다.
- [ ] strict business data extraction은 Codex SDK보다 Responses Structured Outputs가 적합할 수 있음을 안다.
- [ ] broader multi-agent workflow에서는 Agents SDK가 상위 coordinator가 될 수 있음을 안다.

## O. 네 계층 최종 선택 문제

```text
개발자가 terminal에서 repository를 수정
→ Codex CLI

개발자가 desktop에서 여러 agent/worktree를 감독
→ Codex app

내부 service가 Codex coding thread를 시작·resume
→ Codex SDK

고객지원·연구·업무 agent와 tools/handoff/HITL
→ OpenAI Agents SDK
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
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Agents SDK human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
<!-- CODEX-ADDENDUM-END -->

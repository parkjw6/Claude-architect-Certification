# Chapter 30: 시험 당일 전략

> 📅 2026년 04월 05일 기준  
> 🎯 합격을 위한 전략적 문제 풀이 접근법


[← Chapter 29](29_study_plan.md) | [목차](../TOC.md) | [Chapter 31: 최종 체크리스트 →](31_final_checklist.md)

---

## 시험 기본 정보

| 항목 | 내용 |
|------|------|
| 문제 유형 | 객관식 (4지 선다) |
| 합격 점수 | 1000점 만점 중 720점 |
| 시나리오 | 6개 중 4개 무작위 선택 |
| 오답 감점 | 없음 |
| 응시 플랫폼 | https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request |

---

## 문제 분석 프레임워크

### 4단계 분석법

```
1단계: 시나리오 파악
   "어떤 시나리오인가?"
   고객 지원? Claude Code? 멀티에이전트? 개발자 도구? CI/CD? 데이터 추출?

2단계: 핵심 제약 조건 파악
   문제의 핵심 키워드 찾기:
   - "first step" → 첫 번째 단계, 이후 단계 무시
   - "most effective" → 비용 대비 효과 고려
   - "critical" → 결정론적 보장 필요
   - "immediately" → 즉각 응답 필요
   - "team-wide" → 팀 공유 필요

3단계: 각 선택지의 근본 원인 분석
   "이 선택지는 어떤 원인을 해결하는가?"
   "더 단순한 방법이 있는가?"
   "이것이 확률적인가, 결정론적인가?"

4단계: 정답 선택 기준 적용
   단순 + 직접적 + 결정론적 + 낮은 복잡도
```

---

## 도메인별 정답 패턴

### Domain 1 패턴

```
문제 유형                     정답 경향
─────────────────────────────────────────
순서 강제 문제               → 프로그래밍적 게이트
서브에이전트 정보 누락        → 컨텍스트 명시적 전달
루프 종료 문제               → stop_reason == "end_turn"
병렬 실행 구현               → 한 응답에서 여러 Task
분해 범위 누락               → 코디네이터 분해 단계 수정
```

### Domain 2 패턴

```
문제 유형                     정답 경향
─────────────────────────────────────────
툴 선택 오류                 → 툴 설명 개선 (first step)
비슷한 툴 혼동               → 각 툴 설명에 구분 포함
에러 처리                   → errorCategory + isRetryable
MCP 팀 공유                 → .mcp.json (프로젝트)
MCP 개인 설정               → ~/.claude.json
내용 검색                   → Grep
경로 패턴 검색               → Glob
```

### Domain 3 패턴

```
문제 유형                     정답 경향
─────────────────────────────────────────
팀 커맨드 위치               → .claude/commands/
개인 커맨드 위치             → ~/.claude/commands/
CI/CD 실행                  → -p 플래그 필수
대규모 아키텍처 변경         → Plan Mode
세션 격리 실행               → context: fork
디렉토리별 규칙              → .claude/rules/ YAML
```

### Domain 4 패턴

```
문제 유형                     정답 경향
─────────────────────────────────────────
모호한 지시                  → 명시적 기준으로 교체
FP 높음                     → 일시 비활성화 + 기준 개발
JSON 구문 오류               → tool_use 사용
없는 정보 환각               → nullable 필드 + null
실시간 불필요 대량 처리       → Batch API
리뷰 품질 향상               → 독립 인스턴스 사용
```

### Domain 5 패턴

```
문제 유형                     정답 경향
─────────────────────────────────────────
중간 정보 누락               → 앞뒤 배치 + 섹션 헤더
요약 수치 손실               → 명시적 보존 지시
에스컬레이션 조정            → 명시적 기준 + few-shot
상충 정보                   → 두 수치 모두 출처와 함께
긴 세션 저하                 → 스크래치패드 패턴
정책 공백                   → 즉시 에스컬레이션
```

---

## 오답 함정 식별

### 항상 틀린 선택지 패턴

```
❌ 함정 1: "프롬프트에 강조하면 된다"
   → Critical 비즈니스 로직은 프로그래밍적 강제 필요
   → 예외: 스타일/형식은 프롬프트 지시 가능

❌ 함정 2: "감정/자신감으로 에스컬레이션"
   → 항상 틀림 (고객이 화남, 자신감 낮음 등)
   → 명시적 요청, 정책 공백, 진전 불가만 에스컬레이션

❌ 함정 3: "더 많은 툴 제공"
   → 툴 수 증가 = 선택 신뢰도 감소
   → 전문화된 에이전트로 분리

❌ 함정 4: "같은 세션에서 리뷰"
   → 자기 리뷰 = 편향 공유
   → 독립 인스턴스 사용

❌ 함정 5: "복잡한 분류기/라우터 추가"
   → 근본 원인 (설명 부족)을 해결하지 않음
   → 과도한 엔지니어링

❌ 함정 6: "Batch API를 실시간 작업에"
   → Batch API = 지연 허용 + 비차단 작업
   → pre-merge 체크는 실시간 필요
```

---

## 시간 관리 전략

### 문제당 시간 배분

```
전체 시험 시간 확인 후 계산:
문제당 평균 시간 = 총 시간 / 문제 수

예: 60분, 40문제 → 문제당 1.5분

전략:
- 빠른 문제 (확실한 것): 30-60초
- 중간 문제: 1-2분
- 어려운 문제: 표시 후 패스 → 나중에 재검토
- 마지막 5분: 미답 문제 처리 (감점 없음!)
```

### 막힐 때 전략

```
1. "가장 단순한 해결책"부터 확인
2. "근본 원인을 직접 해결하는가?" 확인
3. "결정론적인가 확률적인가?" 판단
4. 하나씩 제거법 적용:
   - 감정/자신감 언급 → 즉시 제거
   - 과도한 엔지니어링 → 제거
   - "프롬프트만으로" → 제거 (Critical 로직은)
```

---

## 시나리오별 핵심 판단 포인트

### 시나리오 1: 고객 지원 에이전트

문제를 읽을 때 확인:
- "순서 강제" 문제? → 프로그래밍적 게이트
- "에스컬레이션 조정"? → 명시적 기준 + few-shot
- "툴 선택 오류"? → 툴 설명 개선

### 시나리오 2: Claude Code

문제를 읽을 때 확인:
- "팀 공유" 필요? → `.claude/commands/` or `.mcp.json`
- "개인 설정"? → `~/.claude/`
- "대규모 변경"? → Plan Mode

### 시나리오 3: 멀티에이전트

문제를 읽을 때 확인:
- "정보 누락"? → 컨텍스트 명시적 전달
- "범위 누락"? → 분해 단계 수정
- "병렬화"? → 단일 응답에서 여러 Task

### 시나리오 4: 개발자 생산성

문제를 읽을 때 확인:
- "툴 선택 오류"? → 전문화된 에이전트 / 툴 설명
- "훅"? → PostToolUse(정규화) / PreToolUse(차단)

### 시나리오 5: CI/CD

문제를 읽을 때 확인:
- "파이프라인 실행"? → -p 플래그 필수
- "기계 처리"? → --output-format json
- "비용 절감"? → Batch API (실시간 아닌 경우만)

### 시나리오 6: 데이터 추출

문제를 읽을 때 확인:
- "환각 방지"? → nullable 필드
- "형식 보장"? → tool_use
- "없는 정보 채움"? → null 사용

---

## 시험 당일 루틴

### 응시 전 (2시간 전)
1. 치트시트 마지막으로 훑어보기
2. 등록 확인: https://anthropic.skilljar.com/claude-certified-architect-foundations-access-request
3. 조용한 환경 확보
4. 물 한 잔 준비

### 시험 시작 시
1. 전체 문제 수 확인 → 시간 배분 계산
2. 쉬운 문제부터 빠르게 처리
3. 어려운 문제는 표시 후 패스
4. 전체 완료 후 표시된 문제 재검토

### 마지막 확인
- 모든 문제에 답을 선택했는가? (감점 없음!)
- 시간이 남으면 불확실한 답 재검토

---

> 🔗 다음 챕터: [최종 체크리스트](31_final_checklist.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Claude 시험과 Codex 실무를 동시에 판단하는 2단계 전략

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | Claude Code syntax를 Codex repository usage로 번역할 때 기본 답입니다. |
| **Codex app** | CLI와 다른 app-only UI 기능이 선택지의 핵심일 때만 별도로 구분합니다. |
| **Codex SDK** | 문제에서 'programmatically embed/control Codex'가 나오면 선택합니다. |
| **OpenAI Agents SDK** | 문제에서 범용 multi-agent app, business tool, handoff, guardrail이 나오면 선택합니다. |

시험에서는 Claude product syntax가 정답입니다. Codex를 사용한다고 해서 시험 선택지를 Codex 파일명으로 바꾸어 답하면 안 됩니다.

### 1. 두 단계로 답한다

```text
Step 1
이 문제의 제품은 Claude인가?
→ 공식 Claude syntax로 정답 선택

Step 2
Underlying principle은 무엇인가?
→ Codex 대응을 별도로 기록
```

예:

```text
문제: 팀 공유 slash command 위치

Claude 시험 답:
.claude/commands/

원리:
version-controlled reusable team workflow

Codex 대응:
.agents/skills/<name>/SKILL.md
```

### 2. 네 제품을 먼저 선택하는 결정 트리

```text
사람이 terminal에서 repository를 직접 수정·검토?
→ Codex CLI

사람이 desktop UI에서 여러 thread/worktree를 감독?
→ Codex app

프로그램이 Codex coding thread를 시작·계속·resume?
→ Codex SDK

고객지원·연구·업무 specialist와 tools/handoff/HITL?
→ OpenAI Agents SDK

일반 model API의 strict data schema나 batch transport?
→ Responses API / Structured Outputs / Batch API
```

그다음 선택한 계층 안에서 `AGENTS.md`, Skill, subagent, MCP, Hook, Rules, Sandbox 같은 세부 기능을 고릅니다.

### 3. Codex CLI 내부 기능 결정 트리

```text
항상 적용되는 지침인가?
→ AGENTS.md

특정 workflow인가?
→ Skill

별도 context가 필요한가?
→ Subagent

외부 tool/data인가?
→ MCP

lifecycle event인가?
→ Hook

shell command 정책인가?
→ Rules/approval

실제 capability인가?
→ Sandbox

critical business rule인가?
→ Application code

정형 최종 출력인가?
→ Structured Outputs

CI인가?
→ codex exec / GitHub Action
```

### 4. 시험에서 특히 혼동할 항목

| Claude 시험 | Codex 실무 |
|---|---|
| `.claude/rules/` | Codex `.codex/rules/`와 역할이 다름 |
| `context: fork` | subagent |
| `allowed-tools` | sandbox/MCP filter/hooks/rules |
| `.mcp.json` | `.codex/config.toml` |
| `Task` | CLI subagent / app thread·worktree / Codex SDK thread / Agents SDK agent-as-tool·handoff |
| `claude -p` | `codex exec` |
| `tool_use` JSON | Structured Outputs 또는 Function Calling |
| terminal에서 직접 coding | Codex CLI |
| desktop에서 여러 coding task 감독 | Codex app |
| program에서 Codex coding thread 호출 | Codex SDK |
| 범용 agent app과 handoff/HITL | OpenAI Agents SDK |

### 5. “가장 직접적인 해결책” 원칙

제품이 바뀌어도 다음은 유지됩니다.

```text
순서·금액·권한 invariant
→ code

tool 선택 오류
→ description과 tool surface

판정 경계 불명확
→ explicit criteria + examples

context pollution
→ isolation + summary

schema 오류
→ API-level structured output

source conflict
→ provenance 보존
```

### 6. Codex 실무에서는 security layer까지 확인

시험 정답이 prompt나 Hook이어도 production에서는 다음 질문을 추가합니다.

```text
Sandbox가 실제로 막는가?
External token이 read-only인가?
DB/API가 authorization을 재검증하는가?
Operation은 idempotent한가?
Audit trail이 남는가?
```

### 7. 최신 문서 확인 대상

Codex는 빠르게 변하므로 다음은 시험 암기보다 공식 문서 재확인이 중요합니다.

- slash command 이름
- custom agent fields
- Hooks event/schema
- Rules maturity
- supported model
- Responses Multi-agent beta
- MCP approval options
- GitHub Action inputs

이 저장소의 Codex 절에는 기준일을 넣은 이유가 여기에 있습니다.


### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex Rules](https://developers.openai.com/codex/rules)
- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

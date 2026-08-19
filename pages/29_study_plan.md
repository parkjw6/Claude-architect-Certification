# Chapter 29: 12주 학습 계획표

> 📅 2026년 04월 05일 기준  
> 🎯 체계적인 합격 로드맵


[← Chapter 28](28_out_of_scope.md) | [목차](../TOC.md) | [Chapter 30: 시험 당일 전략 →](30_exam_strategy.md)

---

## 12주 전체 개요

```
주차  1  2  3  4  5  6  7  8  9  10  11  12
────────────────────────────────────────────
기초  ████
D1       ████
D2           ████
D3               ████
D4                   ████
D5                       ██
시나리오                   ████
문제풀이                        ████
최종정리                             ████
```

---

## Week 1-2: 기초 다지기

### Week 1 목표
- [ ] Claude API 계정 생성 및 첫 API 호출
- [ ] Chapter 01-3 완독
- [ ] 다중 턴 대화 구현 실습

### Week 1 일일 계획

| 요일 | 학습 내용 | 실습 |
|------|----------|------|
| 월 | Chapter 01: AI/LLM 기초 | - |
| 화 | Chapter 02: Claude 모델 | 모델별 API 호출 비교 |
| 수 | Chapter 03: API 기초 | 다중 턴 대화 구현 |
| 목 | 복습 + 실습 | ARIA 기본 챗봇 만들기 |
| 금 | 자유 실습 | API 응답 구조 탐색 |
| 토 | Week 1 요약 정리 | - |
| 일 | 휴식 / 선택적 복습 | - |

### Week 2 목표
- [ ] 시스템 프롬프트 설계 실습
- [ ] Temperature 실험
- [ ] 기본 툴 설계 이해

---

## Week 3-4: Domain 1 (Agentic Architecture)

### 핵심 학습 목표
- [ ] 에이전틱 루프 이해
- [ ] stop_reason 기반 루프 제어 구현
- [ ] 멀티에이전트 Hub-and-Spoke 구현

### Week 3 일일 계획

| 요일 | 학습 내용 | 실습 |
|------|----------|------|
| 월 | Chapter 04: 에이전트 기초 | 기본 에이전틱 루프 구현 |
| 화 | 04.3 stop_reason 이해 | stop_reason 테스트 코드 작성 |
| 수 | Chapter 05: 멀티에이전트 | 2에이전트 파이프라인 구현 |
| 목 | 05.4 병렬 실행 | 병렬 Task 호출 실습 |
| 금 | Chapter 06: 워크플로우 | 프로그래밍적 게이트 구현 |
| 토 | 06.2 Hooks | PostToolUse 훅 구현 |
| 일 | Week 3 요약 | - |

### Week 4: Domain 1 심화
- [ ] 태스크 분해 전략 (프롬프트 체이닝 vs 동적 분해)
- [ ] 세션 관리 및 fork_session
- [ ] Domain 1 모의 문제 10개 풀기

### Domain 1 자가 점검

다음 질문에 즉시 답할 수 있으면 합격 준비 완료:
1. 에이전틱 루프에서 언제 루프를 종료하나?
2. 서브에이전트가 코디네이터 컨텍스트를 자동으로 받는가?
3. allowedTools에 무엇이 반드시 포함되어야 서브에이전트를 스폰할 수 있나?
4. 프롬프트 체이닝과 동적 분해는 각각 언제 적합한가?

---

## Week 5-6: Domain 2 & 3

### Week 5: Domain 2 (Tool Design & MCP)
- [ ] 툴 설명 작성 실습 (좋은 예 vs 나쁜 예)
- [ ] MCP 서버 설정 실습
- [ ] 구조화된 에러 응답 구현
- [ ] tool_choice 각 옵션 테스트

| 요일 | 학습 내용 |
|------|----------|
| 월-화 | Chapter 07: 툴 설계 + 실습 |
| 수-목 | Chapter 08: MCP + .mcp.json 설정 |
| 금 | 내장 툴 선택 기준 정리 |
| 토 | Domain 2 모의 문제 8개 |

### Week 6: Domain 3 (Claude Code)
- [ ] CLAUDE.md 계층 구조 실습
- [ ] `.claude/rules/` 설정 실습
- [ ] 커스텀 슬래시 커맨드 만들기
- [ ] Skills 시스템 실습
- [ ] CI/CD 통합 구현

---

## Week 7-8: Domain 4 & 5

### Week 7: Domain 4 (Prompt Engineering)
- [ ] 명시적 기준 작성 실습
- [ ] Few-shot 예시 2-4개 작성 연습
- [ ] JSON 스키마 설계 실습
- [ ] 검증-재시도 루프 구현
- [ ] Batch API 실습

### Week 8: Domain 5 (Context Management)
- [ ] 컨텍스트 트리밍 구현
- [ ] 구조화된 사실 블록 패턴
- [ ] 에스컬레이션 기준 프롬프트 작성
- [ ] 정보 출처 보존 패턴

---

## Week 9-10: 시나리오 집중 훈련

### 6개 시나리오 순환 학습

| 시나리오 | 핵심 도메인 | 집중 포인트 |
|---------|------------|------------|
| 1. 고객 지원 에이전트 | D1, D2, D5 | 프로그래밍적 게이트 |
| 2. Claude Code 활용 | D3, D5 | CLAUDE.md, Plan Mode |
| 3. 멀티에이전트 연구 | D1, D2, D5 | 코디네이터 설계 |
| 4. 개발자 생산성 | D2, D3, D1 | 툴 배분 전략 |
| 5. CI/CD 통합 | D3, D4 | -p 플래그, JSON 출력 |
| 6. 데이터 추출 | D4, D5 | 스키마 설계, 재시도 |

### 시나리오 학습법

```
1단계: 시나리오 읽고 핵심 아키텍처 결정 요소 파악
2단계: 관련 챕터 다시 읽기
3단계: 해당 시나리오의 실제 코드 구현
4단계: 가능한 문제 유형 스스로 작성
5단계: 공식 샘플 문제 풀기
```

---

## Week 11: 문제 풀이 집중

### 일일 문제 풀이 루틴

```
오전: 20개 문제 풀기 (시간 측정)
오후: 틀린 문제 재검토 (관련 챕터 다시 읽기)
저녁: 1줄 요약으로 핵심 정리
```

### 취약점 보완 전략

| 내 약점 도메인 | 보완 방법 |
|--------------|----------|
| Domain 1 약함 | Chapter 04-6 재학습 + 코드 구현 |
| Domain 2 약함 | 툴 설명 작성 10개 연습 |
| Domain 3 약함 | CLAUDE.md 실제 프로젝트에 적용 |
| Domain 4 약함 | Few-shot 예시 50개 작성 |
| Domain 5 약함 | 컨텍스트 관리 패턴 코드 구현 |

---

## Week 12: 최종 정리

### 월-화: 취약 도메인 집중
### 수: 부록 B 치트시트 암기
### 목: 모의 전체 시험 (60분 제한)
### 금: 최종 체크리스트 확인
### 토: 가벼운 복습 + 충분한 휴식
### 일: 시험 응시!

---

## 효과적인 학습 팁

### ✅ Do
- 코드를 직접 실행해보기
- 틀린 문제의 '왜'를 이해하기
- 실제 프로젝트에 개념 적용하기
- 핵심 개념을 자신의 말로 설명해보기

### ❌ Don't
- 답만 외우기 (시험은 판단력을 평가함)
- 개념 이해 없이 암기
- 한 번에 너무 많은 내용 학습
- 실습 없이 이론만

---

> 🔗 다음 챕터: [시험 당일 전략](30_exam_strategy.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Claude 학습과 병행하는 Codex 실습 로드맵

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | 학습 계획의 기본 트랙입니다. |
| **Codex app** | CLI 원리를 익힌 뒤 parallel project/thread, worktree, Skill UI, Automations를 실습합니다. |
| **Codex SDK** | TypeScript/Python으로 start/run/resume와 sandbox를 실습합니다. |
| **OpenAI Agents SDK** | Agent/Runner/tools/handoff/HITL capstone을 구현합니다. |

기존 12주 Claude 시험 계획을 유지하면서, Codex 사용자에게 필요한 실습을 병행할 수 있습니다.

### 1. 8주 Codex 병행 트랙 — CLI를 기본으로, app·SDK·Agents SDK를 단계적으로 추가

#### Week 1 — 제품 계층과 AGENTS

목표:

- Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK 구분
- Responses API·Batch API는 별도 API 기능으로 구분
- root와 nested `AGENTS.md`
- 변경 범위와 완료 조건 작성

실습:

```text
repo root AGENTS.md 작성
backend/AGENTS.md 작성
동일 작업을 root와 backend에서 실행해 적용 지침 비교
```

산출물:

```text
AGENTS.md
backend/AGENTS.md
docs/codex-instruction-map.md
```

#### Week 2 — Skills

목표:

- team review Skill
- Skill reference와 script 분리
- explicit/implicit invocation 이해

실습 구조:

```text
.agents/skills/team-review/
├── SKILL.md
├── references/checklist.md
└── scripts/changed_files.py
```

검증:

```text
$team-review 명시 호출
일반 "변경사항 리뷰"에서 자동 선택 여부
출력 format 일관성
```

#### Week 3 — Subagents와 context isolation

목표:

- explorer와 reviewer custom agent
- read-only sandbox
- 병렬 bounded task

실습:

```toml
[agents]
max_concurrent_threads_per_session = 4
```

한 기능을 explorer, test reviewer, security reviewer가 각각 분석하게 하고 main 결과의 중복과 context 양을 비교합니다.

#### Week 4 — MCP와 권한

목표:

- project/user config
- environment secret
- enabled/disabled tool
- approval mode

실습:

```text
read-only docs MCP
read-only GitHub MCP
개인 token은 환경 변수
write tool은 disabled
```

#### Week 5 — Hooks, Rules, Sandbox

목표:

- PreToolUse
- command policy
- read-only/workspace-write
- guardrail과 security boundary 차이

실습:

```text
rm -rf 차단 Hook
git push prompt Rule
reviewer read-only
coding workspace-write
```

#### Week 6 — Automation

목표:

- `codex exec`
- JSONL events
- final schema
- GitHub Action

실습:

```bash
codex exec --json ...
codex exec --output-schema ...
codex review --base main
```

CI에서 API key가 job 전체에 노출되지 않도록 설계합니다.

#### Week 7 — Responses API

목표:

- Structured Outputs
- Function Calling 구분
- semantic validation
- Batch API

실습:

```text
invoice extraction
nullable fields
source evidence
validation feedback retry
100건 Batch
```

#### Week 8 — Agents SDK

목표:

- Agent/Runner
- Agent.as_tool
- fixed parallel orchestration
- HITL

실습:

```text
support agent
programmatic refund gate
approval interruption
structured handoff
```

### 2. 매주 공통 검증

```text
1. 공식 문서와 syntax 재확인
2. minimal working example 실행
3. 실패 사례 한 개 만들기
4. guardrail이 실제로 막는지 검증
5. artifact와 decision 기록
6. 다음 주 회귀 fixture로 보존
```

### 3. 최종 capstone

```text
Repository:
- AGENTS.md
- two Skills
- explorer/reviewer agents
- read-only MCP
- Hook and Rules
- CI codex review

Application:
- Structured extraction endpoint
- semantic validator
- Batch job
- Agents SDK coordinator
- HITL approval
```

최종 문서에는 “Claude 시험 정답”과 “Codex 구현”을 별도 열로 정리합니다.



### Codex app 별도 실습

CLI 기본기를 익힌 뒤 하루 정도 app-only 기능을 검증합니다.

```text
1. 같은 repository를 app에서 열기
2. CLI configuration과 session history 연계 확인
3. 두 agent를 별도 thread로 실행
4. built-in worktree에서 서로 다른 해결책 생성
5. 각 diff를 review하고 하나를 editor로 열기
6. team Skill을 UI에서 선택·관리
7. 반복 issue triage Automation 생성
8. 결과가 review queue에 들어오는지 확인
```

### Codex SDK 별도 실습

#### TypeScript

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();

const first = await thread.run("Explore this repository");
const second = await thread.run("Propose the smallest safe change");

console.log(first.finalResponse);
console.log(second.finalResponse);
```

#### Python

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(
        sandbox=Sandbox.read_only,
    )
    result = thread.run("Review the current branch")
    print(result.final_response)
```

학습 완료 기준:

- CLI shell automation과 SDK embedding을 구분
- thread ID를 저장하고 resume 가능
- read-only와 workspace-write를 turn별로 구분
- 여러 coding thread를 application code에서 병렬 실행
- Agents SDK가 필요한 broader workflow를 판별

### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex Hooks](https://developers.openai.com/codex/hooks)
- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
<!-- CODEX-ADDENDUM-END -->

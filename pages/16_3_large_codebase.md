# 16.3 대규모 코드베이스 탐색

> 📅 2026년 04월 05일 기준

---

## 대규모 코드베이스 탐색 전략

```
목표: 모든 파일을 읽지 않고 필요한 정보를 효율적으로 찾기

전략:
1. 구조 파악 (Glob)
2. 관련 파일 탐색 (Grep)
3. 핵심 파일 읽기 (Read)
4. 수정 (Edit/Write)
```

---

## 단계별 접근

### 1단계: 전체 구조 파악

```python
# Glob으로 파일 구조 파악
python_files = Glob("**/*.py")
test_files = Glob("**/*.test.ts")
config_files = Glob("**/*.config.{js,ts,json}")

# 디렉토리 구조 이해
main_dirs = ["src/", "tests/", "docs/", "scripts/"]
```

### 2단계: 관련 코드 찾기

```python
# Grep으로 관련 코드 검색
auth_usage = Grep("authenticate|login|jwt", type="py")
api_endpoints = Grep("@app.route|@router.get|@router.post", type="py")
TODO_items = Grep("TODO|FIXME|HACK")
```

### 3단계: 핵심 파일 읽기

```python
# 구조 파악 후 핵심 파일만 Read
key_files = [
    "src/auth/authentication.py",
    "src/models/user.py",
    "tests/test_auth.py"
]
```

---

## 멀티에이전트로 대규모 코드베이스 분석

```python
# 코드베이스를 영역으로 분할하여 병렬 분석
coordinator_prompt = """
이 코드베이스를 다음 영역으로 분할하여 분석하세요:

Task 1: src/auth/ 디렉토리 보안 분석
Task 2: src/api/ 디렉토리 API 설계 분석
Task 3: tests/ 디렉토리 테스트 커버리지 분석

세 Task를 동시에 실행하세요.
"""
```

---

## 효율적 탐색 팁

```
✅ 좋은 습관:
- 먼저 Glob/Grep으로 범위 파악
- 필요한 파일만 Read
- 변경 전 반드시 Read 먼저

❌ 나쁜 습관:
- 모든 파일을 순서대로 Read
- Write 전에 Read 안 함
- 관련 없는 파일까지 분석
```

---

> 🔗 다음: [16.4 정보 출처 보존](16_4_provenance.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: Codex explorer subagent와 단계적 탐색

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | search → 핵심 file 읽기 → subagent 탐색 → 수정의 기본 계층입니다. |
| **Codex app** | 여러 explorer thread를 worktree/project 단위로 시각적으로 병렬 관리할 수 있습니다. |
| **Codex SDK** | 여러 coding-focused exploration thread를 code에서 생성·resume합니다. |
| **OpenAI Agents SDK** | Codex를 broader workflow의 coding specialist로 연결할 때 사용합니다. |

### 1. Claude의 Glob/Grep/Read 사고방식은 Codex에서도 유효하다

도구 이름은 runtime에 따라 달라도 탐색 순서는 같습니다.

```text
1. repository structure와 entry point 확인
2. symbol/text 검색으로 범위 축소
3. 핵심 파일과 인접 test 읽기
4. call path와 invariant 정리
5. 필요한 범위만 수정
6. 관련 test 실행
```

모든 파일을 순서대로 읽는 방식은 피합니다.

### 2. Read-only explorer custom agent

```toml
# .codex/agents/explorer.toml

name = "explorer"
description = "Read-only codebase exploration and call-path tracing."
sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
Start from entry points and search outward.

Return:
1. relevant files
2. call path
3. state transitions
4. invariants
5. tests covering the path
6. unresolved questions

Do not edit files.
Do not dump raw search results.
"""
```

### 3. Skill이 explorer를 호출하도록 routing

```markdown
---
name: architecture-analysis
description: >
  Trace a feature across a large repository and produce
  a concise architecture map.
---

# Architecture analysis

Delegate broad exploration to the `explorer` subagent.

The main thread must receive only:

- relevant file map
- call path
- invariants
- evidence
- unresolved questions

Do not copy raw command output into the main thread.
```

Codex에서는 Claude Skill의 `context: fork`를 쓰지 않고 Skill instruction이 subagent delegation을 요구하도록 설계합니다.

### 4. 병렬 분해 시 shared mutable state를 피한다

```text
안전한 병렬 작업
- auth path 읽기
- API contract 읽기
- tests 읽기

위험한 병렬 작업
- 같은 파일 동시 수정
- 같은 migration number 생성
- 같은 generated artifact 덮어쓰기
```

탐색은 병렬화하기 쉽지만 구현은 ownership boundary를 분명히 해야 합니다.

### 5. 탐색 결과 형식

```json
{
  "scope": "refund creation",
  "entry_points": ["backend/api/refunds.py:42"],
  "call_path": [
    "RefundService.create",
    "RefundPolicy.validate",
    "Gateway.refund"
  ],
  "invariants": [
    "verified customer required",
    "idempotency key required"
  ],
  "tests": [
    "tests/refunds/test_create.py"
  ],
  "unknowns": [
    "retry ownership between service and gateway"
  ]
}
```


### 공식 문서

- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex Skills](https://developers.openai.com/codex/build-skills)
- [Codex sandboxing](https://developers.openai.com/codex/concepts/sandboxing)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
<!-- CODEX-ADDENDUM-END -->

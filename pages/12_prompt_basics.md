# Chapter 12: 프롬프트 엔지니어링 기초

> 📅 2026년 04월 05일 기준  
> 🎯 Domain 4: 20% — 명시적 기준과 Few-Shot이 핵심


[← Chapter 11](11_plan_mode.md) | [목차](../TOC.md) | [Chapter 13: 구조화된 출력 →](13_structured_output.md)

---

## 12.1 명시적 기준 설계

> 🎯 시험 출제: "명시적 기준 > 모호한 지시"

### 문제: 모호한 지시의 결과

```python
# ❌ 모호한 프롬프트
"""
코드 리뷰를 해줘. 정확한 이슈만 보고하고, 
확신이 없으면 보고하지 마.
"""
# → "정확한", "확신"의 기준이 없어 일관성 없음
# → 개발자 신뢰도 하락
```

### 해결: 명시적이고 구체적인 기준

```python
# ✅ 명시적 기준 프롬프트
"""
다음 코드를 리뷰해주세요. 정확한 기준으로 보고하세요:

## 보고해야 할 이슈
- 버그: 코드가 설명된 동작과 다르게 작동하는 경우
- 보안: 인젝션, XSS, 인증 우회 등 취약점
- 데이터 무결성: 트랜잭션 경계, 레이스 컨디션

## 보고하지 말아야 할 이슈
- 스타일 선호도: 탭 vs 스페이스, 따옴표 선택
- 팀 로컬 패턴: 코드베이스에 이미 사용되는 패턴
- 단순 최적화 제안 (성능 측정 없이)

## 심각도 기준
- Critical: 프로덕션 데이터 손실 또는 보안 침해 가능
- Warning: 특정 조건에서 버그 발생 가능
- Info: 코드 품질 개선 (선택적)

각 이슈에는 다음을 포함하세요:
1. 파일명과 줄 번호
2. 이슈 설명
3. 구체적인 수정 방법 또는 코드 예시
"""
```

### False Positive 문제 해결

```python
# 문제: 특정 카테고리에서 False Positive 높음
# → 개발자들이 모든 리뷰를 무시하기 시작

# 해결 방법:
# 1. 높은 FP 카테고리를 일시적으로 비활성화
# 2. 해당 카테고리 기준을 개선하는 동안

"""
현재 비활성화된 검사:
- 주석 정확성 체크 (기준 개선 중)

활성화된 검사:
- 버그, 보안, 데이터 무결성 (기준 명확)
"""
```

---

## 12.2 Few-Shot 프롬프팅 활용

> 🎯 시험 최빈출: "few-shot이 일관성과 품질 향상에 가장 효과적"

### Few-Shot이 특히 효과적인 경우

1. 모호한 케이스 처리: 어떤 툴을 선택해야 할지 불분명할 때
2. 형식 일관성: 일관된 출력 형식이 필요할 때
3. False Positive 감소: 허용 패턴과 실제 이슈를 구분할 때
4. 추출 정확도: 다양한 문서 구조에서 데이터를 추출할 때

### Few-Shot 예시 작성법

```python
few_shot_prompt = """
코드 리뷰 이슈를 다음 형식으로 보고해주세요:

## 예시 1: 버그 보고 (올바른 형식)
입력 코드:
```python
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")
```

출력:
{
  "file": "users/service.py",
  "line": 2,
  "severity": "critical",
  "category": "security",
  "issue": "SQL 인젝션 취약점: 사용자 입력이 직접 쿼리에 삽입됨",
  "fix": "파라미터화된 쿼리 사용: db.query('SELECT * FROM users WHERE id = ?', [user_id])"
}

## 예시 2: 스타일 이슈 무시 (보고하지 않음)
입력 코드:
```python
x=get_user( user_id )  # 스페이싱 일관성 없음
```

출력: (보고 없음 — 스타일 이슈는 보고 범위 외)

이유: 스타일 선호도는 기능적 이슈가 아니므로 보고하지 않음

## 예시 3: 팀 로컬 패턴 허용
입력 코드:
```python
result = process() or {}  # None 처리를 or로
```

출력: (보고 없음 — 팀 코드베이스에서 자주 사용하는 패턴)
"""
```

### Few-Shot으로 추출 품질 향상

```python
extraction_prompt = """
다음 형식으로 송장에서 정보를 추출해주세요.

## 예시 1: 표준 송장
입력:
Invoice #INV-2024-001
Date: January 15, 2024
Due: February 15, 2024
Total: $1,500.00

출력:
{
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "total_amount": 1500.00,
  "currency": "USD"
}

## 예시 2: 비공식 단위가 포함된 송장
입력:
"약 1천5백만원 정도"

출력:
{
  "total_amount": 15000000,
  "currency": "KRW",
  "is_approximate": true
}

## 예시 3: 정보가 없는 경우
입력:
"금액 추후 통보"

출력:
{
  "total_amount": null,  # 예외 발생 금지, null 반환
  "note": "금액 미확정"
}

이제 다음 송장을 처리해주세요:
{invoice_text}
"""
```

### Few-Shot 개수 가이드

```
- 2-4개: 모호한 시나리오용 (일반적으로 충분)
- 4-8개: 다양한 형식 처리 (문서 추출 등)
- 8개 이상: 매우 복잡한 패턴 (희귀한 경우)

많다고 좋은 것이 아님!
각 예시가 특정 케이스를 다루는지 확인하세요.
```

---

## 📝 챕터 요약

- 명시적 기준: "정확하게", "확신" 같은 모호한 표현 대신 구체적인 조건 명시
- FP 높은 카테고리는 일시 비활성화 후 기준 개선 → 개발자 신뢰 회복
- Few-Shot: 모호한 케이스, 형식 일관성, FP 감소, 추출 정확도에 탁월
- 예시는 2-4개면 충분, 각각 다른 케이스를 다뤄야 효과적

---

> 🔗 다음 챕터: [구조화된 출력 설계](13_structured_output.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 프롬프트 엔지니어링 원칙과 Codex 지침 계층

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | `AGENTS.md`, Skill, 현재 prompt에 목표·제약·완료 조건을 배치하는 기본 사용 계층입니다. |
| **Codex app** | CLI와 같은 Codex coding agent와 repository 설정을 데스크톱 UI에서 사용합니다. 이 장에는 별도 app-only 동작이 없으므로 CLI 설명을 자연어로 실행하면 됩니다. |
| **Codex SDK** | 반복되는 coding prompt를 `thread.run()`으로 호출하고 같은 thread를 이어갈 때 사용합니다. |
| **OpenAI Agents SDK** | 일반 agent application의 `instructions`, tool description, guardrail 기준을 설계할 때 사용합니다. |

> **별도 OpenAI API 계층:** 직접 model call의 prompt를 제어할 때 Responses API가 보조 계층입니다.

### 1. 원리는 동일하지만 저장 위치가 달라진다

명시적 기준, negative examples, few-shot 같은 프롬프트 원칙은 Claude와 Codex에 동일하게 적용됩니다. 차이는 **지침을 어디에 두는가**입니다.

| 지속 범위 | Codex 위치 | 예 |
|---|---|---|
| 이번 요청에만 적용 | 현재 사용자 prompt | 특정 버그의 acceptance criteria |
| 저장소 전체에 항상 적용 | `AGENTS.md` | 테스트·보안·변경 범위 원칙 |
| 특정 하위 시스템에 적용 | nested `AGENTS.md` | backend transaction 규칙 |
| 특정 작업에서만 적용 | `.agents/skills/<name>/SKILL.md` | PR review, 배포 점검 |
| 실제로 위반하면 안 되는 규칙 | application code / sandbox / RBAC | 환불 한도, production 권한 |

모든 내용을 root `AGENTS.md`에 넣으면 항상 context를 차지합니다. 반복 가능하지만 특정 작업에서만 필요한 세부 절차는 Skill로 분리하는 편이 낫습니다.

### 2. Codex용 작업 요청 템플릿

```text
Goal:
JWT refresh token 만료 처리 버그를 수정한다.

Context:
- 구현: backend/auth/
- token state: Redis
- API contract는 공개되어 있다.

Constraints:
- public response schema 변경 금지
- dependency 추가 금지
- unrelated refactor 금지

Done when:
- expired refresh token은 401
- valid refresh token은 access token 재발급
- 관련 unit/integration test 통과
- 실행하지 못한 검증은 이유와 함께 보고
```

이 형식은 모델에게 “무엇을 할지”뿐 아니라 **변경 경계와 완료 판정 기준**을 제공합니다.

### 3. 모호한 평가를 명시적 판정으로 전환

```text
❌ 정확한 문제만 보고하라.

✅ 다음 조건을 모두 만족할 때만 finding으로 보고하라.
1. 변경된 코드로 도달 가능한 실행 경로가 있다.
2. 재현 가능한 입력 또는 상태가 있다.
3. 관찰 가능한 잘못된 결과가 있다.
4. 파일과 줄, 근거를 제시할 수 있다.

다음은 보고하지 않는다.
- 근거 없는 가능성
- 코드베이스에 이미 확립된 스타일
- 측정 없는 미세 성능 제안
```

### 4. 중요한 구분

`AGENTS.md`에 “production에 배포하지 마라”라고 쓰는 것은 행동 지침입니다. 실제 차단이 필요하면 Codex Hook, Rules, Sandbox, 배포 API 권한까지 내려가야 합니다.

```text
prompt / AGENTS.md
→ 행동 유도

Hook / Rules
→ tool·command 검사

Sandbox / external RBAC
→ 실제 capability 제한
```


### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

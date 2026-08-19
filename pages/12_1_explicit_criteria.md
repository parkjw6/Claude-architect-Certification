# 12.1 명시적 기준 설계

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 개념

---

## 왜 명시적 기준이 필요한가?

```
모호한 지시: "보수적으로 에스컬레이션하세요"
→ '보수적'이 무엇인지 LLM마다 다르게 해석
→ 예측 불가능한 동작

명시적 기준: "다음 조건 중 하나라도 해당하면 에스컬레이션하세요:
  1. 고객이 명시적으로 사람 연결 요청
  2. 환불 금액 $500 초과
  3. 정책 문서에 없는 예외 상황"
→ 일관되고 예측 가능한 동작
```

---

## 모호한 지시 vs 명시적 기준

### 모호한 표현들

```
❌ "확신할 때만 행동하세요"
❌ "보수적으로 접근하세요"
❌ "복잡한 경우 에스컬레이션하세요"
❌ "적절히 판단하세요"
```

### 명시적 기준으로 변환

```
✅ "다음 조건이 모두 충족될 때만 환불 처리:
    - customer_id가 verified_customer_id와 일치
    - order_status가 'delivered'
    - 환불 요청일이 배송일로부터 30일 이내
    - 환불 금액이 $500 이하"

✅ "에스컬레이션 기준:
    - 고객이 '사람 연결', '상담원', '매니저' 요청
    - 동일 문제로 3번 이상 재시도
    - 정책 문서에 없는 예외 사례
    감정(화남, 불만)은 에스컬레이션 기준 아님"
```

---

## False Positive 해결 프로세스

```
1. FP가 높은 카테고리 식별
   (예: 로그 문에 대한 과도한 보안 경고)

2. 해당 카테고리 일시 비활성화

3. 실제 사례에서 기준 개발:
   - 실제 위험한 것: 어떤 특징?
   - FP: 어떤 특징?

4. 명시적 기준 작성 (few-shot 포함)

5. 카테고리 재활성화 + 모니터링
```

---

## 명시적 기준 템플릿

```
[행동 기준]
다음 조건이 모두 충족될 때: [행동]
- 조건 1: [구체적인 설명]
- 조건 2: [구체적인 설명]

다음 경우에는 절대 [행동]하지 마세요:
- 상황 1: [구체적인 예시]
- 상황 2: [구체적인 예시]

불확실한 경우: [대안 행동]
```

---

> 🔗 다음: [12.2 Few-Shot 프롬프팅 마스터](12_2_few_shot.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: 명시적 기준을 Codex workflow와 코드에 배치하기

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | repository coding/review 기준을 `AGENTS.md`와 Skill에 명시합니다. |
| **Codex app** | CLI와 같은 Codex coding agent와 repository 설정을 데스크톱 UI에서 사용합니다. 이 장에는 별도 app-only 동작이 없으므로 CLI 설명을 자연어로 실행하면 됩니다. |
| **Codex SDK** | 내부 coding tool이 동일 기준으로 Codex thread를 반복 실행하게 만들 때 사용합니다. |
| **OpenAI Agents SDK** | 고객지원·업무 agent의 escalation과 tool-use 기준을 정의합니다. Critical gate는 application code에 둡니다. |

### 1. Codex에서도 “명시적 기준”이 첫 번째 해결책이다

리뷰 오탐, 불필요한 escalation, 잘못된 tool 선택처럼 **판단 경계가 불분명한 문제**는 먼저 기준을 구체화합니다. 모델·reasoning effort를 높이는 것은 기준 자체가 없는 문제를 해결하지 못합니다.

```markdown
<!-- .agents/skills/team-review/SKILL.md -->

## Report a finding only when

- the changed code introduces or exposes the behavior;
- a concrete execution path can be identified;
- impact is observable;
- file and line evidence are available.

## Do not report

- purely stylistic preferences;
- hypothetical issues without a reachable path;
- pre-existing issues outside the diff;
- optimizations without evidence.
```

### 2. 결정론적이어야 하는 기준은 코드로 이동

다음은 좋은 prompt만으로 충분하지 않습니다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RefundRequest:
    verified_customer_id: str | None
    order_customer_id: str
    amount: float


def authorize_refund(request: RefundRequest) -> str:
    if request.verified_customer_id is None:
        return "customer_verification_required"

    if request.verified_customer_id != request.order_customer_id:
        return "customer_mismatch"

    if request.amount > 500:
        return "manager_approval_required"

    return "approved"
```

Agent에게는 `authorize_refund()`의 결과를 설명하고 다음 행동을 선택하게 할 수 있지만, 승인 규칙 자체를 다시 판단하게 해서는 안 됩니다.

### 3. Codex에서 기준을 배치하는 판단표

| 기준 | 위치 |
|---|---|
| 모든 변경에서 public API 보존 | root `AGENTS.md` |
| `backend/payments/`에서만 transaction 필수 | `backend/payments/AGENTS.md` |
| 보안 리뷰 finding 기준 | `security-review` Skill |
| `git push` 전 승인 | `.codex/rules/*.rules` |
| 위험 command 검사 | `PreToolUse` Hook |
| 환불·배포·권한 한도 | application/service code |

### 4. False Positive 개선 절차

```text
1. 오탐을 category별로 수집한다.
2. 재현 가능한 true positive와 false positive를 분리한다.
3. report / ignore의 판정 기준을 작성한다.
4. 경계 사례 2~4개를 few-shot으로 추가한다.
5. 고정 eval set으로 이전 대비 precision/recall을 확인한다.
6. 기준이 안정화되기 전에는 해당 category를 blocking gate로 쓰지 않는다.
```

Codex Skill의 `references/`에 실제 사례를 넣으면 `SKILL.md`를 짧게 유지하면서 반복 검증 기준을 공유할 수 있습니다.


### 공식 문서

- [AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [Codex Skills](https://developers.openai.com/codex/build-skills)

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

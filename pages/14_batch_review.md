# Chapter 14: 배치 처리와 리뷰 아키텍처

> 📅 2026년 04월 05일 기준  
> 🎯 Domain 4 — Batch API 50% 비용 절감, 차단/비차단 구분


[← Chapter 13](13_structured_output.md) | [목차](../TOC.md) | [Chapter 15: 컨텍스트 관리 →](15_context_management.md)

---

## 14.1 Message Batches API

> 🎯 시험 핵심: Batch API는 비차단 워크플로우에만 적합

### Batch API 특성

| 특성 | 값 |
|------|-----|
| 비용 절감 | 50% |
| 처리 시간 | 최대 24시간 |
| 지연 SLA | 없음 (보장 안 됨) |
| 멀티턴 툴 호출 | 지원 안 됨 |

### 언제 Batch API를 쓰나?

```
비차단 워크플로우 (Batch API 적합):
✅ 야간 기술 부채 보고서
✅ 주간 코드 품질 분석
✅ 대량 문서 분류 (하룻밤)
✅ 레거시 코드 분석

차단 워크플로우 (실시간 API 필수):
❌ 머지 전 코드 리뷰 (개발자가 대기 중)
❌ 고객 응답 (실시간 필요)
❌ CI/CD 게이트 (파이프라인 차단)
```

### Batch API 구현

```python
import anthropic
import json
import time

client = anthropic.Anthropic()

def batch_process_invoices(invoices: list[dict]) -> dict:
    """대량 송장 처리 (비용 최적화)"""
    
    # 배치 요청 생성
    requests = []
    for invoice in invoices:
        requests.append({
            "custom_id": invoice["id"],  # 나중에 결과 매핑용
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "tools": [extraction_tool],
                "tool_choice": {"type": "tool", "name": "extract_invoice_data"},
                "messages": [{
                    "role": "user",
                    "content": f"다음 송장을 처리해주세요:\n{invoice['text']}"
                }]
            }
        })
    
    # 배치 제출
    batch = client.beta.messages.batches.create(requests=requests)
    print(f"배치 제출 완료: {batch.id}")
    
    # 완료 대기 (폴링)
    while True:
        batch = client.beta.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        time.sleep(60)  # 1분마다 확인
    
    # 결과 처리
    results = {}
    failed_ids = []
    
    for result in client.beta.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            results[result.custom_id] = result.result.message
        else:
            failed_ids.append(result.custom_id)
            print(f"실패: {result.custom_id} - {result.result.error}")
    
    # 실패한 항목 재처리 (예: 컨텍스트 초과 → 청킹)
    if failed_ids:
        print(f"{len(failed_ids)}개 실패. 재처리 중...")
        for fail_id in failed_ids:
            invoice = next(i for i in invoices if i["id"] == fail_id)
            # 청킹 처리
            results[fail_id] = process_chunked(invoice)
    
    return results


def calculate_batch_schedule(sla_hours: int, batch_max_hours: int = 24) -> int:
    """SLA를 맞추기 위한 배치 제출 주기 계산"""
    # 예: SLA 30시간, 배치 최대 24시간
    # → 6시간마다 배치 제출해야 안전
    submission_interval = sla_hours - batch_max_hours
    return max(1, submission_interval)  # 최소 1시간

# 30시간 SLA의 경우
interval = calculate_batch_schedule(sla_hours=30)
print(f"배치 제출 주기: {interval}시간")  # → 6시간
```

---

## 14.2 멀티패스 리뷰 설계

> 🎯 시험 출제: 자기 리뷰의 한계, 독립 인스턴스가 더 효과적

### 자기 리뷰의 한계

```python
# ❌ 잘못된 방법: 생성한 세션에서 바로 리뷰
generated_code = generate_code(requirements)  # 세션 A
review = review_code(generated_code)  # 같은 세션 A → 편향!

# 문제: Claude가 생성 당시의 추론 컨텍스트를 기억
# → 자신의 결정에 의문을 갖지 않음
# → 미묘한 버그를 놓칠 가능성 높음

# ✅ 올바른 방법: 독립 인스턴스로 리뷰
generated_code = generate_code(requirements)  # 세션 A
# 새 Claude 인스턴스 (이전 맥락 없음)
review = independent_review(generated_code)  # 세션 B → 더 객관적!
```

### 14파일 PR 리뷰 멀티패스 구조

```python
# 시나리오: 14개 파일의 PR이 있음
# 단일 패스로는 주의력 분산 → 오류 놓침

def review_large_pr(pr_files: list[str]) -> dict:
    """멀티패스 코드 리뷰"""
    
    all_issues = []
    
    # Pass 1: 파일별 로컬 이슈 분석
    file_issues = {}
    for file_path in pr_files:
        file_content = read_file(file_path)
        issues = analyze_single_file(file_path, file_content)
        file_issues[file_path] = issues
        all_issues.extend(issues)
    
    # Pass 2: 파일 간 통합 이슈 분석 (별도 Claude 인스턴스)
    integration_issues = analyze_cross_file_issues(
        files=pr_files,
        individual_results=file_issues
        # 이 단계는 이전 파일별 결과를 입력으로 받되,
        # 생성 세션과는 독립적임
    )
    all_issues.extend(integration_issues)
    
    return {
        "file_issues": file_issues,
        "integration_issues": integration_issues,
        "summary": generate_summary(all_issues)
    }


def analyze_cross_file_issues(files: list, individual_results: dict) -> list:
    """크로스파일 데이터 흐름 분석"""
    
    # 개별 파일 결과를 컨텍스트로 제공
    context = "\n\n".join([
        f"=== {file} ===\n{result}"
        for file, result in individual_results.items()
    ])
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""
다음은 각 파일의 개별 분석 결과입니다:

{context}

이제 파일 간 데이터 흐름과 통합 이슈를 분석해주세요:
1. 여러 파일에 걸친 데이터 불일치
2. 파일 간 의존성 문제
3. 한 파일의 변경이 다른 파일에 미치는 영향
"""
        }]
    )
    
    return parse_integration_issues(response.content[0].text)
```

### 신뢰도 기반 라우팅

```python
def review_with_confidence(code: str) -> dict:
    """신뢰도 포함 리뷰 → 인간 검토 우선순위화"""
    
    response = client.messages.create(
        ...,
        messages=[{
            "role": "user",
            "content": f"""
코드를 리뷰하고 각 이슈에 신뢰도(0.0-1.0)를 포함하세요.
신뢰도 기준:
- 1.0: 확실한 버그 (재현 가능한 시나리오 있음)
- 0.7-0.9: 높은 확률의 이슈
- 0.4-0.6: 의심스러운 패턴
- 0.3 미만: 가능성 낮음 (보고하지 않는 것 권장)

```python
{code}
```
"""
        }]
    )
    
    issues = parse_issues_with_confidence(response)
    
    # 신뢰도 기반 라우팅
    high_confidence = [i for i in issues if i["confidence"] >= 0.8]
    needs_human_review = [i for i in issues if 0.4 <= i["confidence"] < 0.8]
    
    return {
        "auto_flagged": high_confidence,      # 자동 처리
        "human_review": needs_human_review,    # 인간 검토 필요
        "ignored": [i for i in issues if i["confidence"] < 0.4]
    }
```

---

## 📝 챕터 요약

- Batch API: 50% 비용 절감, 최대 24시간, SLA 없음 → 비차단 작업만
- 차단 워크플로우(pre-merge 체크)는 실시간 API 필수
- 자기 리뷰 = 편향 → 독립 Claude 인스턴스로 리뷰가 더 효과적
- 14파일 PR → 파일별 로컬 분석 + 크로스파일 통합 분석 (2패스)
- 신뢰도 점수로 인간 리뷰 우선순위 설정

---

> 🔗 다음 챕터: [컨텍스트 관리 전략](15_context_management.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: OpenAI Batch와 Codex 독립 리뷰 아키텍처

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | `codex review`와 `codex exec`로 즉시 repository review를 수행합니다. |
| **Codex app** | 여러 review thread와 worktree를 시각적으로 병렬 관리하고 diff에 comment할 때 app의 이점이 큽니다. |
| **Codex SDK** | 내부 review bot이나 CI가 Codex coding thread를 start/run/resume하도록 embedding할 때 사용합니다. |
| **OpenAI Agents SDK** | 여러 reviewer 역할을 agents-as-tools 또는 code orchestration으로 구성할 때 사용합니다. |

> **별도 OpenAI API 계층:** 대량 비차단 request는 OpenAI Batch API가 별도 계층입니다.

### 1. Batch API 대응

Anthropic Message Batches와 OpenAI Batch API의 설계 원칙은 유사합니다.

```text
즉각적인 응답이 필요하지 않음
+ 요청 간 독립성이 높음
+ 대량 처리
→ Batch API

사용자가 기다림
또는 merge/deploy gate
→ 실시간 API / codex exec
```

OpenAI Batch API도 24시간 completion window를 사용하며 표준 동기 호출보다 비용이 낮고 별도 rate-limit pool을 사용합니다. `/v1/responses` 요청을 JSONL로 제출할 수 있습니다.

### 2. Batch와 Codex CLI를 구분

```text
10,000개 문서를 야간 분류
→ OpenAI Batch API

현재 repository의 PR을 즉시 리뷰
→ /review 또는 codex review

CI에서 현재 checkout을 분석
→ codex exec
```

Codex CLI는 workspace를 탐색·수정하는 coding agent이고, Batch API는 대량 API inference transport입니다.

### 3. 독립 리뷰의 Codex 구현

가장 간단한 repository 리뷰:

```text
/review
```

비대화형:

```bash
codex review --uncommitted
codex review --base main
codex review --commit "$COMMIT_SHA"
```

팀 기준이 더 필요하면 Skill을 만들고 read-only reviewer subagent에 위임합니다.

```toml
# .codex/agents/reviewer.toml

name = "reviewer"
description = "Independent reviewer for correctness and regression risks."
sandbox_mode = "read-only"
model_reasoning_effort = "high"

developer_instructions = """
Review independently from the implementation thread.
Do not edit files.
Prioritize correctness, security, regressions, and missing tests.
Every finding needs a reachable path and file/line evidence.
"""
```

### 4. Multi-pass 권장 구조

```text
Pass 1 — local
- 변경 파일별 correctness
- validation, error handling
- local test gap

Pass 2 — integration
- cross-file contract mismatch
- state transition
- transaction boundary
- backward compatibility

Pass 3 — synthesis
- 중복 제거
- severity 재조정
- release blocker 판정
```

각 pass의 intermediate raw output을 main context에 전부 넣지 말고, subagent별 구조화 summary를 합치는 편이 낫습니다.

### 5. 모델 confidence만으로 자동 차단하지 않는다

LLM이 생성한 `confidence: 0.93`은 통계적으로 교정된 확률이라고 가정할 수 없습니다. 자동 merge gate는 다음처럼 객관적 조건을 사용합니다.

```text
Critical finding
AND reachable execution path
AND changed-line evidence
AND reproducible impact
→ merge block

그 외
→ human review queue
```


### 공식 문서

- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)
- [Codex subagents](https://developers.openai.com/codex/subagents)
- [Codex slash commands](https://developers.openai.com/codex/cli/slash-commands)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

# 14.1 Message Batches API

> 📅 2026년 04월 05일 기준  
> ⭐ 시험 핵심 — 특성 암기 필수

---

## Batch API 핵심 특성

```
비용: 표준 대비 50% 절감
처리 시간: 최대 24시간
SLA: 없음 (지연 허용)
최대 배치 크기: 요청당 최대 10,000개
```

---

## 언제 Batch API를 사용하는가?

```
✅ 적합:
- 야간 보고서 생성
- 주간 코드베이스 분석
- 대량 문서 분류
- 비실시간 데이터 처리

❌ 부적합:
- pre-merge 코드 체크 (즉각 응답 필요)
- 실시간 고객 지원
- 사용자가 대기하는 작업
```

---

## 구현

```python
import anthropic

client = anthropic.Anthropic()

# 배치 생성
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"doc-{i}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": f"문서 분류: {doc}"
                }]
            }
        }
        for i, doc in enumerate(documents)
    ]
)

print(f"배치 ID: {batch.id}")
print(f"상태: {batch.processing_status}")
# 비차단 — 나중에 결과 확인

# 결과 수집 (완료 후)
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(f"{result.custom_id}: {result.result.message.content[0].text}")
```

---

## Batch API vs 실시간 비교

| 항목 | Batch API | 실시간 API |
|------|----------|-----------|
| 비용 | 50% 절감 | 표준 |
| 응답 시간 | 최대 24시간 | 수 초 |
| SLA | 없음 | 있음 |
| 용도 | 비차단, 대량 | 실시간 |

---

## 야간 자동화 패턴

```python
# 매일 자정 코드베이스 분석
import schedule

def nightly_analysis():
    files = get_all_python_files()
    batch_id = create_analysis_batch(files)
    save_batch_id(batch_id)  # 다음 날 결과 확인용

schedule.every().day.at("00:00").do(nightly_analysis)
```

---

> 🔗 다음: [14.2 멀티패스 리뷰 설계](14_2_multi_pass.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: OpenAI Batch API 코드 구현

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | 현재 checkout을 즉시 분석하는 작업에는 `codex exec`를 사용합니다. |
| **Codex app** | Batch transport를 대체하지 않습니다. 반복 desktop 작업은 Automations가 가능하지만 API Batch와 목적이 다릅니다. |
| **Codex SDK** | coding-focused batch-like workflow를 직접 scheduling할 수 있지만 OpenAI Batch API와 동일한 서비스는 아닙니다. |
| **OpenAI Agents SDK** | 복잡한 agent workflow 자체를 구성할 수 있으나 대량 비동기 transport는 Batch API를 사용합니다. |

> **별도 OpenAI API 계층:** 이 장의 primary 계층은 OpenAI Batch API입니다.

### 1. JSONL 입력 파일 생성

OpenAI Batch API는 요청 하나당 JSONL 한 줄을 사용합니다.

```python
import json
import os
from pathlib import Path

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")


def write_batch_input(
    documents: list[dict[str, str]],
    output_path: Path,
) -> None:
    with output_path.open("w", encoding="utf-8") as file:
        for document in documents:
            request = {
                "custom_id": document["id"],
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "model": MODEL,
                    "input": [
                        {
                            "role": "system",
                            "content": (
                                "Classify the document. "
                                "Return no unsupported facts."
                            ),
                        },
                        {
                            "role": "user",
                            "content": document["text"],
                        },
                    ],
                },
            }
            file.write(
                json.dumps(request, ensure_ascii=False) + "\n"
            )
```

`custom_id`는 결과 순서를 가정하지 않고 원래 입력과 매핑하기 위한 키입니다.

### 2. 업로드와 Batch 생성

```python
from openai import OpenAI

client = OpenAI()

batch_file = client.files.create(
    file=open("batch-input.jsonl", "rb"),
    purpose="batch",
)

batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/responses",
    completion_window="24h",
    metadata={
        "job": "nightly-document-classification",
        "schema_version": "1.0",
    },
)

print(batch.id)
```

### 3. 결과 처리 원칙

- 요청 순서와 결과 순서가 같다고 가정하지 않습니다.
- `custom_id`로 결과를 매핑합니다.
- 성공, 실패, 만료, 취소를 분리합니다.
- 실패한 항목만 별도 retry batch로 만듭니다.
- Batch 전체를 무조건 다시 제출하지 않습니다.

```python
def partition_results(rows: list[dict]) -> tuple[dict, dict]:
    succeeded: dict[str, dict] = {}
    failed: dict[str, dict] = {}

    for row in rows:
        custom_id = row["custom_id"]
        response = row.get("response")
        error = row.get("error")

        if response and response.get("status_code") == 200:
            succeeded[custom_id] = response
        else:
            failed[custom_id] = {
                "response": response,
                "error": error,
            }

    return succeeded, failed
```

### 4. SLA 설계

Batch는 “24시간 안에 끝날 수 있다”는 transport이지 실시간 queue가 아닙니다. 30시간 business SLA가 있다고 해서 단순히 6시간마다 중복 batch를 제출하면 중복 처리 위험이 생깁니다. 다음을 함께 설계합니다.

```text
submission cutoff
idempotency key
job state table
late-result handling
partial completion policy
retry batch
```

### 5. 적합하지 않은 경우

```text
PR merge 전에 5분 안에 결과 필요
고객 채팅 응답
결제 승인
사용자 요청에 대한 즉시 파일 수정
```

이 경우 Responses API 실시간 호출이나 `codex exec`를 사용합니다.


### 공식 문서

- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)

<!-- CODEX-ADDENDUM-END -->

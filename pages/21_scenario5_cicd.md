# Chapter 21: 시나리오 5 — CI/CD 통합

> 📅 2026년 04월 05일 기준  
> 🎯 실제 시험 시나리오 5 해설


[← Chapter 20](20_scenario4_developer_productivity.md) | [목차](../TOC.md) | [Chapter 22: 시나리오 6 →](22_scenario6_data_extraction.md)

---

## 시나리오 개요

> 당신은 DevOps 팀에서 Claude를 CI/CD 파이프라인에 통합하고 있습니다.
> 자동화된 코드 품질 검사, 보안 스캔, 테스트 분석을 구현합니다.
> 파이프라인은 완전 비대화형(headless)으로 실행되어야 합니다.

---

## 핵심 개념: 비대화형 모드

### -p (--print) 플래그

```bash
# CI/CD 환경에서 Claude Code 사용
# -p 플래그: 비대화형 단일 실행 모드

# 기본 사용법
claude -p "PR의 코드를 검토하고 문제점을 나열하세요"

# JSON 출력 (기계 처리 가능)
claude -p "보안 취약점을 분석하세요" --output-format json

# 스키마 강제 JSON 출력
claude -p "코드 분석" \
  --output-format json \
  --json-schema '{"type": "object", "properties": {"issues": {"type": "array"}, "score": {"type": "number"}}}'

# 파일 입력
claude -p "$(cat pr_diff.txt)를 분석하세요" --output-format json
```

### -p 플래그의 의미

```
일반 모드:            비대화형 모드 (-p):
┌─────────┐           ┌─────────┐
│ 사용자   │ ←대화→   │ 자동화   │
│ Claude  │           │ Claude  │
└─────────┘           └─────────┘
                      - 단일 요청/응답
                      - stdin/stdout
                      - CI/CD 파이프라인에 임베드
                      - 자동 종료
```

---

## GitHub Actions 통합

### 완전한 파이프라인 예시

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review Pipeline

on:
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize]

jobs:
  security-scan:
    name: Security Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # 전체 히스토리
      
      - name: Setup Claude Code
        run: npm install -g @anthropic-ai/claude-code
      
      - name: Get Changed Files
        id: changed
        run: |
          FILES=$(git diff --name-only origin/main...HEAD | tr '\n' ' ')
          echo "files=$FILES" >> $GITHUB_OUTPUT
      
      - name: Run Security Analysis
        id: security
        run: |
          RESULT=$(claude -p "
          다음 파일들의 보안 취약점을 분석하세요: ${{ steps.changed.outputs.files }}
          
          각 취약점에 대해 다음을 포함하세요:
          - 파일명과 라인 번호
          - 취약점 유형 (OWASP 기반)
          - 심각도 (critical/high/medium/low)
          - 수정 방법
          " --output-format json)
          echo "result=$RESULT" >> $GITHUB_OUTPUT
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      
      - name: Post Review Comment
        uses: actions/github-script@v7
        with:
          script: |
            const result = JSON.parse('${{ steps.security.outputs.result }}');
            const issues = result.issues || [];
            
            if (issues.length > 0) {
              const comment = issues.map(i => 
                `**${i.severity.toUpperCase()}**: ${i.file}:${i.line}\n${i.description}`
              ).join('\n\n');
              
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## 🔐 보안 분석 결과\n\n${comment}`
              });
            }
      
      - name: Fail on Critical Issues
        run: |
          RESULT='${{ steps.security.outputs.result }}'
          CRITICAL=$(echo $RESULT | jq '[.issues[] | select(.severity == "critical")] | length')
          
          if [ "$CRITICAL" -gt "0" ]; then
            echo "❌ 심각한 보안 취약점 발견: ${CRITICAL}개"
            exit 1
          fi
```

### 테스트 분석 파이프라인

```yaml
  test-analysis:
    name: Test Analysis
    runs-on: ubuntu-latest
    needs: security-scan
    steps:
      - name: Run Tests
        id: tests
        run: |
          pytest --json-report --json-report-file=test-results.json || true
      
      - name: Analyze Test Failures
        if: always()
        run: |
          if [ -f test-results.json ]; then
            FAILURES=$(cat test-results.json | jq '.failures')
            
            if [ "$FAILURES" != "[]" ]; then
              claude -p "
              다음 테스트 실패를 분석하고 수정 방법을 제안하세요:
              
              $(cat test-results.json | jq '.failures')
              
              각 실패에 대해:
              1. 실패 원인
              2. 관련 코드 파일
              3. 구체적인 수정 방법
              " --output-format json > failure-analysis.json
            fi
          fi
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Batch API 활용

### 대량 코드 분석

```python
import anthropic
import json

client = anthropic.Anthropic()

def batch_analyze_files(file_paths: list[str]) -> str:
    """Batch API로 여러 파일을 비용 효율적으로 분석"""
    
    # Batch API: 50% 비용 절감, 최대 24시간 처리
    # 적합: 비실시간, 비차단 작업
    # 부적합: pre-merge 체크 (즉각 응답 필요)
    
    requests = []
    for i, file_path in enumerate(file_paths):
        with open(file_path, 'r') as f:
            content = f.read()
        
        requests.append({
            "custom_id": f"analysis-{i}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": f"""파일 {file_path}의 코드 품질을 분석하세요:

{content}

JSON 형식으로 응답:
{{
  "complexity": "low|medium|high",
  "issues": [...],
  "improvements": [...]
}}"""
                }]
            }
        })
    
    # 배치 생성
    batch = client.messages.batches.create(requests=requests)
    print(f"배치 ID: {batch.id}, 상태: {batch.processing_status}")
    
    return batch.id


def get_batch_results(batch_id: str) -> dict:
    """배치 결과 수집"""
    
    results = {}
    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            custom_id = result.custom_id
            content = result.result.message.content[0].text
            results[custom_id] = json.loads(content)
    
    return results


# 야간 코드베이스 분석 (비차단 작업에 적합)
def nightly_analysis():
    import glob
    
    python_files = glob.glob("**/*.py", recursive=True)
    batch_id = batch_analyze_files(python_files)
    
    # 24시간 내 처리 완료, 실시간 대기 불필요
    print(f"야간 분석 시작: {batch_id}")
    print("내일 아침 결과를 확인하세요")
```

---

## 출력 형식 처리

### JSON 출력 파싱

```python
import subprocess
import json

def run_claude_analysis(prompt: str, schema: dict = None) -> dict:
    """Claude Code를 파이프라인에서 실행"""
    
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    
    if schema:
        cmd.extend(["--json-schema", json.dumps(schema)])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={"ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"]}
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Claude Code 실행 실패: {result.stderr}")
    
    return json.loads(result.stdout)


# 파이프라인에서 사용
analysis_schema = {
    "type": "object",
    "properties": {
        "score": {"type": "number", "minimum": 0, "maximum": 100},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                    "message": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "integer"}
                }
            }
        },
        "passed": {"type": "boolean"}
    },
    "required": ["score", "issues", "passed"]
}

result = run_claude_analysis(
    "변경된 코드의 품질을 분석하세요",
    schema=analysis_schema
)

print(f"품질 점수: {result['score']}/100")
print(f"합격: {result['passed']}")
```

---

## 시나리오 기반 예상 문제

### Q: CI/CD 비대화형 모드

상황: GitHub Actions에서 Claude Code를 실행하려고 합니다. 파이프라인이 Claude Code의 응답을 기다리다 타임아웃됩니다.

가장 먼저 확인해야 할 것은?

A) ANTHROPIC_API_KEY 환경 변수 설정 여부  
B) -p (--print) 플래그 사용 여부 — 비대화형 모드  
C) 네트워크 연결 문제  
D) 모델 이름 정확성  

정답: B — CI/CD 파이프라인에는 반드시 -p 플래그 사용 (비대화형 모드)

---

### Q: Batch API vs 실시간 처리

상황: 다음 두 작업 중 Batch API에 적합한 것은?

A) PR 머지 전 자동 코드 리뷰 (결과 즉시 필요)  
B) 매주 일요일 밤 전체 코드베이스 품질 분석 (다음 날 아침 확인)  

정답: B — Batch API는 비차단 작업(야간 분석, 주간 보고서)에 적합. pre-merge 체크는 즉각 응답이 필요하므로 부적합

---

## 📝 챕터 요약

| 개념 | 핵심 내용 |
|------|---------|
| -p 플래그 | CI/CD 비대화형 모드 필수 |
| --output-format json | 기계 처리 가능 출력 |
| --json-schema | 스키마 강제 적용 |
| Batch API | 50% 비용 절감, 24시간, 비차단 작업 |
| pre-merge 체크 | 실시간 필요 → Batch API 부적합 |

---

> 🔗 다음 챕터: [시나리오 6 — 데이터 추출 파이프라인](22_scenario6_data_extraction.md)

<!-- CODEX-ADDENDUM-START -->

---

## Codex/OpenAI 대응: `codex exec`, schema 출력, GitHub Action

> 기준일: **2026-08-19**  
> 이 절은 앞의 Claude 원문을 변경하지 않고, 동일한 원리를 Codex와 OpenAI 플랫폼에서 적용하는 방법만 추가합니다.  
> **Codex CLI / Codex app / Codex SDK / OpenAI Agents SDK**를 서로 다른 계층으로 구분합니다. 별도 데이터·모델 기능은 OpenAI API 계층으로 표시합니다.

### 이 장에서 구분할 네 계층

| 계층 | 이 장에서의 역할 |
|---|---|
| **Codex CLI** | 단순하고 shell-native한 CI에는 `codex exec`가 기본입니다. |
| **Codex app** | Automations로 scheduled desktop work와 review queue를 제공하지만 deterministic CI gate의 대체물로 보지 않습니다. |
| **Codex SDK** | thread resume, result object, 여러 coding turn이 필요한 CI/internal automation에 적합합니다. |
| **OpenAI Agents SDK** | CI 분석이 broader release-management agent workflow의 일부일 때 사용합니다. |

> **별도 OpenAI API 계층:** 대량 비차단 job에는 Batch API가 별도입니다.

### 1. Claude `-p`의 Codex 대응

```text
claude -p
→ codex exec
```

기본 분석:

```bash
codex exec \
  "Review the current checkout for release blockers"
```

Codex `exec`는 진행 정보를 stderr에, 최종 메시지를 stdout에 출력하는 비대화형 실행 경로입니다.

### 2. Sandbox를 최소 권한으로 선택

분석만:

```bash
codex exec \
  --sandbox read-only \
  "Review the current diff"
```

파일 수정:

```bash
codex exec \
  --sandbox workspace-write \
  "Fix the failing tests and run the relevant suite"
```

`danger-full-access`는 filesystem과 network 경계를 제거하므로 통제된 disposable environment가 아니면 사용하지 않습니다.

### 3. `--json`과 `--output-schema`

전체 event stream:

```bash
codex exec --json \
  "Analyze the current branch" \
  > codex-events.jsonl
```

최종 result schema:

```json
{
  "type": "object",
  "properties": {
    "passed": {"type": "boolean"},
    "critical_count": {"type": "integer", "minimum": 0},
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["critical", "warning", "suggestion"]
          },
          "file": {"type": "string"},
          "line": {"type": ["integer", "null"]},
          "message": {"type": "string"}
        },
        "required": ["severity", "file", "line", "message"],
        "additionalProperties": false
      }
    }
  },
  "required": ["passed", "critical_count", "findings"],
  "additionalProperties": false
}
```

```bash
codex exec \
  "Review the current changes" \
  --output-schema ./review-schema.json \
  -o ./review-result.json
```

CI gate는 JSONL event stream이 아니라 최종 schema output을 파싱하는 편이 단순합니다.

### 4. Exit code와 결과 의미를 분리

Codex process가 성공적으로 끝났다는 것과 review가 통과했다는 것은 다릅니다.

```bash
set -euo pipefail

codex exec \
  "Review the current changes" \
  --output-schema ./review-schema.json \
  -o ./review-result.json

critical_count="$(jq '.critical_count' review-result.json)"

if [ "$critical_count" -gt 0 ]; then
  echo "Critical findings detected: $critical_count"
  exit 1
fi
```

### 5. 공식 GitHub Action

```yaml
name: Codex Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Run Codex
        uses: openai/codex-action@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          prompt-file: .github/codex/prompts/review.md
          output-file: codex-output.md
          sandbox: read-only
```

공식 Action은 Codex 설치와 API proxy 실행을 포함해 key exposure를 줄이는 방향으로 설계되어 있습니다.

### 6. Secret scope

다음은 피합니다.

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

steps:
  - run: npm install
  - run: npm test
  - run: arbitrary-repo-script
  - run: codex exec ...
```

Checkout된 untrusted code와 같은 job 전체에 API key를 노출하면 dependency lifecycle script나 build script가 secret을 읽을 수 있습니다. Key는 Codex invocation에만 최소 범위로 전달합니다.

### 7. Batch API와 CI gate 구분

```text
PR merge 전 즉시 판정
→ codex exec / real-time API

매주 전체 저장소 offline 분석
→ OpenAI Batch API
```

Batch는 비용 효율적이지만 24시간 completion window이므로 immediate gate에 맞지 않습니다.

### 8. Prompt file을 version control

`.github/codex/prompts/review.md`:

```markdown
# Review scope

Review only changes between the PR branch and its base.

## Report only

- reachable correctness bugs
- exploitable security vulnerabilities
- behavior regressions
- missing tests for changed behavior

## Output

Every finding requires:
- severity
- file and line
- evidence
- impact
- fix

Do not report cosmetic style preferences.
```

Prompt, schema, fixture를 함께 versioning하면 review behavior 변경을 추적할 수 있습니다.



### 9. `codex exec`와 Codex SDK 선택 기준

| 상황 | 권장 |
|---|---|
| shell step 하나로 실행 | `codex exec` |
| final file/schema만 필요 | `codex exec -o`, `--output-schema` |
| 같은 coding thread를 여러 turn 이어감 | Codex SDK |
| thread ID 저장 후 다음 pipeline에서 resume | Codex SDK |
| 여러 Codex thread를 programmatically 병렬 관리 | Codex SDK |
| broader release agent와 approval/handoff | OpenAI Agents SDK |

### 10. TypeScript Codex SDK 기반 CI worker

```typescript
import { Codex } from "@openai/codex-sdk";

type ReviewResult = {
  threadId: string;
  response: string;
};

export async function runReview(): Promise<ReviewResult> {
  const codex = new Codex();
  const thread = codex.startThread();

  const result = await thread.run(
    [
      "Review the current checkout against main.",
      "Do not edit files.",
      "Report only reachable correctness, security,",
      "regression, and missing-test findings.",
    ].join("\n"),
  );

  const threadId = thread.id;
  if (!threadId) {
    throw new Error("Codex thread ID was not initialized");
  }

  return {
    threadId,
    response: result.finalResponse,
  };
}
```

SDK는 application object로 결과를 받기 쉽고, 후속 turn을 같은 thread에 보낼 수 있습니다.

```typescript
import { Codex } from "@openai/codex-sdk";

async function diagnoseThenProposeFix(): Promise<void> {
  const codex = new Codex();
  const thread = codex.startThread();

  const diagnosis = await thread.run(
    "Diagnose the CI failure"
  );
  console.log(diagnosis.finalResponse);

  const proposal = await thread.run(
    "Based on the diagnosis, propose the minimal fix"
  );
  console.log(proposal.finalResponse);
}

await diagnoseThenProposeFix();
```

### 11. Python Codex SDK worker

```python
from openai_codex import Codex, Sandbox


def run_ci_diagnosis() -> str:
    with Codex() as codex:
        thread = codex.thread_start(
            sandbox=Sandbox.read_only,
        )

        result = thread.run(
            "Diagnose the failing CI checks. Do not edit."
        )
        return result.final_response
```

### 12. Codex app Automations는 CI gate와 다르다

App의 Automations는 다음에 적합합니다.

```text
매일 issue triage
정기 CI failure 요약
daily release brief
주기적 bug scan
Automation 결과를 review queue에서 확인
```

하지만 merge gate는 다음 특성이 필요합니다.

```text
commit SHA에 고정
deterministic trigger
machine-readable result
exit code
required check
secret scope
reproducible log
```

따라서 App Automation을 GitHub required check의 직접 대체물로 설명하지 않습니다.

### 13. Agents SDK가 필요한 release workflow

```text
release manager agent
├─ CI 상태 조회
├─ policy 검사
├─ change-management approval
├─ Codex coding specialist에게 fix 요청
└─ 사람 승인 후 deploy tool 호출
```

이처럼 coding 외 business workflow가 결합될 때 Agents SDK가 상위 orchestration을 맡습니다.

### 공식 문서

- [Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [Codex GitHub Action](https://developers.openai.com/codex/github-action)
- [Codex sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [OpenAI Batch API](https://developers.openai.com/api/docs/guides/batch)

- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex app 발표](https://openai.com/index/introducing-the-codex-app/)
- [Codex desktop app 문서](https://developers.openai.com/codex/app)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
<!-- CODEX-ADDENDUM-END -->

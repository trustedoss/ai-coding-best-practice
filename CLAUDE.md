# AI 코딩 정책 규칙

## 라이선스 정책

### 허용 라이선스
- MIT, Apache 2.0, BSD (2-Clause, 3-Clause), ISC, Python-2.0, PSF

### 금지 라이선스
- GPL (v2, v3), AGPL, SSPL, EUPL, CDDL

### 주의 라이선스 (법무 검토 필요)
- LGPL, MPL, CPAL, EPL, EUPL

## 보안 정책

### 취약점 기준
- Critical: 즉시 수정 (허용 기간 없음)
- High: 1주일 이내 수정
- Medium 이하: 다음 스프린트 내 검토

### 금지 패턴
- API 키·토큰·비밀번호를 코드에 직접 하드코딩 금지
- `eval()`, `exec()`, `os.system()` 사용 금지
- SQL 쿼리 문자열 직접 조합 금지 — ORM 또는 파라미터 바인딩 사용
- 사용자 입력을 검증 없이 파일 경로·쉘 명령에 사용 금지

## 의존성 정책

- 새 패키지 추가 시 라이선스와 최신 안정 버전 확인 후 사용
- `requirements.txt`에 버전 고정 (pin) 필수
- 유지보수가 중단된 패키지 사용 금지

## 보안 시크릿 관리

- 환경 변수 또는 시크릿 관리 서비스(AWS Secrets Manager 등) 사용
- `.env` 파일은 `.gitignore`에 반드시 포함
- GitHub Actions에서는 `${{ secrets.NAME }}` 형식만 사용

## 테스트 정책

`tests/` 는 이 저장소의 완료 기준입니다. 에이전트가 만든 변경도 이 테스트를 통과해야 끝난 것으로 봅니다.

- 기능을 추가하거나 동작을 바꿀 때는 테스트를 먼저 작성하거나 합의한 뒤 구현합니다.
- 실패하는 테스트를 통과시키려고 테스트를 지우거나, `skip`·`xfail` 을 붙이거나, assert 를 약하게 바꾸지 않습니다. 테스트가 틀렸다고 판단되면 고치지 말고 사람에게 이유를 설명합니다.
- `tests/` 수정은 `.claude/settings.json` 에서 사람 승인을 받도록 되어 있고, PR 에서는 `test-integrity.yml` 이 약화를 탐지합니다.
- 라우트 핸들러는 얇게 두고 로직은 데코레이터 없는 함수로 둡니다. 단위 테스트와 변이 테스트(mutmut)가 그 함수에 닿아야 합니다.
- 외부 네트워크를 호출하는 코드는 테스트에서 `unittest.mock` 으로 대체합니다.

## 작업 방식

- 큰 작업은 계획을 먼저 제시하고 사람이 승인한 뒤 구현합니다.
- PR 하나는 400줄 이하를 목표로 나눕니다. 넘으면 PR 본문에 나눌 수 없는 이유를 적습니다.
- PR 템플릿의 AI 사용 항목에 사용한 도구와, 사람이 내린 결정을 적습니다.

## AI 에이전트·MCP 도구 정책

[5단계 전략](https://trustedoss.github.io/ai-coding/strategy)의 4c 단계를 이 저장소에 적용한 규칙입니다.
현재 승인된 MCP 서버는 없습니다 — `.mcp.json` 의 `mcpServers` 가 비어 있습니다.

### 파일로 강제되는 것

| 통제 | 설정 | 내용 |
|------|------|------|
| 서버 allowlist | `enabledMcpjsonServers: []` | `.mcp.json` 의 서버를 자동 승인하지 않음 |
| 커넥터 차단 | `disableClaudeAiConnectors: true` | claude.ai 커넥터가 세션에 자동 연결되지 않음 |
| 최소 권한 | `permissions.deny` | `.env`·`secrets/`·인증서·키 파일 읽기 차단 |
| 사람 승인 | `permissions.ask` | 외부 통신(`curl`·`wget`·WebFetch)과 되돌리기 어려운 작업(`git push`·`docker push`·`kubectl apply`) |

네 항목 모두 `.claude/settings.json` 에 있습니다.
`disableClaudeAiConnectors` 는 Claude Code v2.1.182 이상에서 동작합니다.

서버 allowlist 를 개인이 덮어쓸 수 없게 강제하려면 조직 관리 설정(`managed-settings.json`)의
`allowedMcpServers` 를 사용하세요. 저장소 설정만으로는 강제되지 않습니다.

### 절차로 지키는 것

파일로 표현할 수 없는 두 가지입니다. MCP 서버를 새로 추가할 때 아래를 수행하고 결과를 PR 본문에 남깁니다.

1. 도구 설명(tool description) 전문을 읽고 지시문이 섞여 있지 않은지 확인합니다
2. 서버가 접근하는 외부 엔드포인트와 내보내는 데이터를 확인하고, SBOM 의 `services` 에 등재합니다

### 서버를 추가하는 방법

`.mcp.json` 에 버전을 고정해 선언하고, `.claude/settings.json` 의 `enabledMcpjsonServers` 에 이름을 추가합니다.
`@latest` 나 버전 없는 선언은 금지합니다.

```json
{
  "mcpServers": {
    "example": {
      "command": "npx",
      "args": ["-y", "@scope/server-example@1.2.3"]
    }
  }
}
```

`.mcp.json` 을 저장소에 두는 이유는 서버 추가가 개인 설정(`~/.claude.json`)이 아니라
PR diff 에 드러나게 하기 위해서입니다.

자세한 배경은 [에이전트와 MCP 도구 거버넌스](https://trustedoss.github.io/ai-coding/agent-governance) 를 참고하세요.

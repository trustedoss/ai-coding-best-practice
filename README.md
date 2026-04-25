# AI 코딩 Best Practice

[![Secret Detection](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/secret-detection.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/secret-detection.yml)
[![SAST](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/sast.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/sast.yml)
[![CodeQL](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/codeql.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/codeql.yml)
[![OSS Policy](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/oss-policy.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/oss-policy.yml)
[![IaC Security](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/iac-security.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/iac-security.yml)
[![Container Security](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/container-security.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/container-security.yml)
[![DAST](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/dast.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/dast.yml)
[![AI Fuzzing](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/ai-fuzzing.yml/badge.svg)](https://github.com/trustedoss/ai-coding-best-practice/actions/workflows/ai-fuzzing.yml)

[Trusted OSS — AI 코딩 4단계 전략](https://trustedoss.github.io/ai-coding/strategy)을 모두 구현한 참조 저장소입니다.
fork해서 즉시 사용하거나, 설정 파일을 복사해 기존 프로젝트에 적용할 수 있습니다.

---

## 단계별 구현 현황

| 단계 | 내용 | 구현 파일 |
|------|------|-----------|
| 1단계 | 프롬프트 의존 | — (도구 불필요) |
| 2단계 | AI 규칙 내재화 | `CLAUDE.md`, `.cursorrules` |
| 3단계 | CI/CD 자동 차단 | `.github/workflows/` 전체 |
| 4단계 | 지속적 모니터링·자동 교정 | `dependabot.yml`, `renovate.json`, AI 퍼징, DAST |

---

## 3단계 CI/CD 구성 (전체)

| 워크플로우 | 도구 | 역할 | PR | Push/Main |
|------------|------|------|----|-----------|
| `secret-detection.yml` | Gitleaks | API 키·토큰 하드코딩 탐지 | ✅ | ✅ |
| `sast.yml` | Semgrep | SQL 인젝션·취약 패턴 탐지 | ✅ | — |
| `codeql.yml` | CodeQL | 심층 정적 분석 (주 1회 포함) | ✅ | ✅ |
| `oss-policy.yml` | syft + grype | CVE 스캔 + 라이선스 검사 | ✅ | — |
| `iac-security.yml` | Checkov | Dockerfile·K8s 보안 설정 검사 | ✅ | — |
| `container-security.yml` | Trivy | Docker 이미지 취약점 스캔 | ✅ | ✅ |
| `ai-review.yml` | Claude API | 의미론적 취약점 탐지 (비활성화) | 선택 | — |

## 4단계 지속적 모니터링·자동 교정

| 워크플로우 / 설정 | 도구 | 역할 | 실행 주기 |
|------------------|------|------|-----------|
| `dependabot.yml` | Dependabot | 의존성 업데이트 PR 자동 생성 | 주 1회 |
| `renovate.json` | Renovate | Critical 패치 자동 병합 | 즉시·주 1회 |
| `dast.yml` | OWASP ZAP | 배포 후 동적 취약점 스캔 (Soft fail) | Push to main |
| `ai-fuzzing.yml` | Claude + requests | AI 생성 엣지케이스로 5xx 탐지 | 주 1회 + Push |

---

## 빠른 시작

### 1. Fork

GitHub에서 이 저장소를 fork한 뒤 클론합니다.

```bash
git clone https://github.com/YOUR-ORG/ai-coding-best-practice.git
cd ai-coding-best-practice
```

### 2. PR을 열어 파이프라인 확인

```bash
git checkout -b test/pipeline-check
echo "# test" >> README.md
git commit -am "test: pipeline check"
git push origin test/pipeline-check
```

GitHub에서 PR을 생성하면 3단계 워크플로우 6개가 자동 실행됩니다.

### 3. GitHub Secrets 등록

| Secret 이름 | 용도 | 필수 여부 |
|-------------|------|-----------|
| `ANTHROPIC_API_KEY` | AI 코드 리뷰 (`ai-review.yml`), AI 퍼징 (`ai-fuzzing.yml`) | 선택 |

### 4. (선택) AI 코드 리뷰 활성화

`ai-review.yml` 에서 아래 줄을 제거합니다.

```yaml
if: false  # 이 줄 제거
```

---

## 커스터마이징

| 파일 | 수정 포인트 |
|------|------------|
| `CLAUDE.md` | 팀 라이선스 정책, 금지 패키지 목록 |
| `.cursorrules` | 도구별 규칙 조정 |
| `.grype.yaml` | 취약점 임계값 (`high` ↔ `critical`) |
| `.gitleaks.toml` | 조직 내부 패턴 예외 처리 추가 |
| `.semgrep.yml` | 언어·프레임워크별 룰셋 추가 |
| `renovate.json` | 자동 병합 범위, 업데이트 주기 |
| `dast.yml` | 안정화 후 `fail_action: true` 로 변경해 Hard fail 전환 |

---

## 관련 가이드

- [AI 코딩 4단계 전략](https://trustedoss.github.io/ai-coding/strategy)
- [30분 완성 Quick CI/CD](https://trustedoss.github.io/ai-coding/cicd-quick)
- [AI 보안 코드 리뷰](https://trustedoss.github.io/ai-coding/ai-security-review)
- [DevSecOps — 전사 파이프라인 설계](https://trustedoss.github.io/devsecops/pipeline-design)

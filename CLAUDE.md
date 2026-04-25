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

#!/usr/bin/env python3
"""
AI-assisted fuzzing script.
Claude가 앱 코드를 분석해 엣지케이스 입력을 생성하고,
실제 실행해서 5xx 오류·비정상 동작을 탐지한다.
"""
import anthropic
import requests
import json
import pathlib
import sys

BASE_URL = "http://localhost:8080"


def generate_fuzz_cases(app_code: str) -> list[dict]:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": (
                "아래 Flask 앱 코드를 분석해서 각 엔드포인트의 엣지케이스 입력을 JSON 배열로 생성하라.\n"
                "형식: [{\"endpoint\": \"/path\", \"params\": {\"key\": \"value\"}, \"description\": \"설명\"}, ...]\n"
                "탐지 목표: 500 에러 유발, 보안 취약점 탐지 (인젝션·경로 탐색·비정상 입력 등).\n"
                "최소 20개 케이스 생성. JSON 배열만 출력.\n\n"
                f"```python\n{app_code}\n```"
            )
        }]
    )

    text = response.content[0].text
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError("Claude 응답에서 JSON 배열을 찾을 수 없음")
    return json.loads(text[start:end])


def run_fuzz_cases(cases: list[dict]) -> list[dict]:
    results = []
    for case in cases:
        try:
            url = f"{BASE_URL}{case['endpoint']}"
            resp = requests.get(url, params=case.get("params", {}), timeout=5)
            result = {
                "endpoint": case["endpoint"],
                "params": case.get("params", {}),
                "description": case.get("description", ""),
                "status_code": resp.status_code,
                "passed": resp.status_code < 500,
            }
            if not result["passed"]:
                result["response_snippet"] = resp.text[:300]
        except Exception as e:
            result = {
                "endpoint": case["endpoint"],
                "params": case.get("params", {}),
                "description": case.get("description", ""),
                "status_code": -1,
                "passed": False,
                "error": str(e),
            }
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  [{status}] {case['endpoint']} {case.get('params', {})} → {result['status_code']}")
    return results


def main():
    app_code = pathlib.Path("src/app.py").read_text()

    print("Claude로 fuzz 케이스 생성 중...")
    cases = generate_fuzz_cases(app_code)
    print(f"{len(cases)}개 케이스 생성됨\n")

    print("fuzz 케이스 실행 중...")
    results = run_fuzz_cases(cases)

    failures = [r for r in results if not r["passed"]]
    report = {
        "total": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "failures": failures,
    }

    pathlib.Path("fuzz-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )

    print(f"\n결과: {report['passed']}/{report['total']} 통과")
    if failures:
        print(f"\n실패 {len(failures)}건:")
        for f in failures:
            print(f"  - {f['endpoint']} params={f['params']}: HTTP {f['status_code']}")
            if "description" in f:
                print(f"    설명: {f['description']}")
        sys.exit(1)
    else:
        print("모든 fuzz 케이스 통과")


if __name__ == "__main__":
    main()

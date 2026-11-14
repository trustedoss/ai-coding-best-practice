FROM python:3.15-slim

# The upstream image is rebuilt on its own schedule, so Debian security fixes
# can be available before a new python:3.14-slim tag ships. Apply them at build
# time so the image scan (container-security.yml) does not wait on upstream.
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# 런타임에는 패키지 관리자가 필요 없습니다. pip 를 남겨 두면 pip 가 번들한
# 라이브러리(msgpack, pkg_resources 등)까지 이미지의 공격 표면에 포함됩니다.
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m pip uninstall -y pip

COPY src/ ./src/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["python", "src/app.py"]

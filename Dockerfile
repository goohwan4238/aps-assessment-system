# 보안 강화된 Dockerfile
FROM python:3.12-alpine AS base

# 보안 업데이트 적용 및 한글 폰트 지원 패키지 설치
RUN apk update && apk upgrade && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    fontconfig \
    ttf-dejavu \
    curl \
    unzip \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# 비루트 사용자 생성
RUN addgroup -g 1000 appgroup && \
    adduser -D -s /bin/sh -u 1000 -G appgroup appuser

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY --chown=appuser:appgroup . .

# 한글 폰트 파일이 포함되어 있는지 확인
RUN ls -la /app/fonts/ || echo "폰트 디렉토리 없음"

# fonts 디렉토리 생성 및 권한 설정 (폰트 파일이 이미 복사됨)
RUN mkdir -p /app/fonts && \
    chown -R appuser:appgroup /app/fonts

# 데이터 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/data && \
    chown -R appuser:appgroup /app/data && \
    chmod 755 /app/data

# 비루트 사용자로 전환
USER appuser

# 포트 5000 노출
EXPOSE 5000

# 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 보안 강화된 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000')" || exit 1

# 애플리케이션 실행
CMD ["python", "app.py"]
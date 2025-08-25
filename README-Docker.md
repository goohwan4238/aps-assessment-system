# Docker로 APS 준비도 진단 시스템 실행하기

## 필요한 사전 준비

1. **Docker 설치**
   - Windows: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) 설치
   - 설치 후 Docker가 실행 중인지 확인: `docker --version`

## 실행 방법

### 방법 1: Docker Compose 사용 (권장)

```bash
# 1. 애플리케이션 빌드 및 실행
docker-compose up --build

# 2. 백그라운드에서 실행
docker-compose up -d --build

# 3. 실행 중인 컨테이너 확인
docker-compose ps

# 4. 로그 확인
docker-compose logs -f

# 5. 애플리케이션 중지
docker-compose down
```

### 방법 2: Docker 명령어 직접 사용

```bash
# 1. Docker 이미지 빌드
docker build -t aps-assessment:latest .

# 2. 컨테이너 실행
docker run -d -p 5000:5000 --name aps-assessment-app aps-assessment:latest

# 3. 실행 중인 컨테이너 확인
docker ps

# 4. 로그 확인
docker logs aps-assessment-app

# 5. 컨테이너 중지 및 제거
docker stop aps-assessment-app
docker rm aps-assessment-app
```

## 접속 방법

애플리케이션이 성공적으로 실행되면 웹 브라우저에서 다음 주소로 접속:

```
http://localhost:5000
```

## 데이터 영속성

- SQLite 데이터베이스는 컨테이너 내부의 `/app/data` 디렉토리에 저장됩니다
- `docker-compose.yml`에서 `./data:/app/data` 볼륨 마운트를 통해 호스트의 `data` 폴더와 연결됩니다
- 컨테이너를 재시작해도 데이터가 유지됩니다

## 환경 변수 설정

`docker-compose.yml` 파일에서 다음 환경 변수를 수정할 수 있습니다:

- `SECRET_KEY`: Flask 애플리케이션의 시크릿 키
- `FLASK_ENV`: 실행 환경 (production/development)

## 문제 해결

### 포트 충돌
```bash
# 다른 포트로 실행 (예: 8080 포트)
docker run -d -p 8080:5000 --name aps-assessment-app aps-assessment:latest
```

### 컨테이너 내부 접속
```bash
# 실행 중인 컨테이너에 접속
docker exec -it aps-assessment-app /bin/bash
```

### 이미지 및 컨테이너 정리
```bash
# 모든 컨테이너 중지
docker stop $(docker ps -q)

# 사용하지 않는 이미지 제거
docker image prune

# 사용하지 않는 컨테이너 제거
docker container prune
```
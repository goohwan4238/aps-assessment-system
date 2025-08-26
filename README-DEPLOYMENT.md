# APS 평가 시스템 - 자동 배포 설정

이 문서는 GitHub Actions를 사용한 자동 배포(CD) 설정에 대해 설명합니다.

## 배포 워크플로우

`main` 브랜치에 커밋이 푸시되면 자동으로 배포가 실행됩니다.

### 배포 과정

1. **코드 체크아웃**: 최신 코드를 가져옴
2. **Docker 이미지 빌드**: 새로운 Docker 이미지 생성
3. **서버 배포**: SSH를 통해 서버에 접속하여 배포 실행
4. **컨테이너 교체**: 기존 컨테이너를 중지하고 새 컨테이너 실행
5. **정리**: 임시 파일 및 이미지 정리

## GitHub Secrets 설정

GitHub 리포지토리의 Settings > Secrets and variables > Actions에서 다음 secrets를 설정해야 합니다:

### 필수 Secrets

| Secret Name | 설명 | 예시 |
|-------------|------|------|
| `HOST` | 배포 서버의 IP 주소 또는 도메인 | `192.168.1.100` 또는 `myserver.com` |
| `USERNAME` | SSH 접속용 사용자명 | `ubuntu`, `root` 등 |
| `SSH_PRIVATE_KEY` | SSH 접속용 개인키 | RSA 또는 ED25519 개인키 전체 내용 |

### 선택적 Secrets

| Secret Name | 설명 | 기본값 |
|-------------|------|--------|
| `PORT` | SSH 접속 포트 | `22` |

## SSH 키 생성 방법

### 1. SSH 키 페어 생성
```bash
# ED25519 키 생성 (권장)
ssh-keygen -t ed25519 -C "github-actions@yourdomain.com"

# 또는 RSA 키 생성
ssh-keygen -t rsa -b 4096 -C "github-actions@yourdomain.com"
```

### 2. 공개키를 서버에 등록
```bash
# 서버의 ~/.ssh/authorized_keys에 공개키 추가
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. 개인키를 GitHub Secrets에 등록
```bash
# 개인키 내용을 복사
cat ~/.ssh/id_ed25519

# 또는 클립보드에 복사 (macOS)
pbcopy < ~/.ssh/id_ed25519

# 또는 클립보드에 복사 (Linux)
xclip -sel clip < ~/.ssh/id_ed25519
```

복사한 개인키 전체 내용을 `SSH_PRIVATE_KEY` secret으로 등록합니다.

## 서버 요구사항

배포 대상 서버에는 다음이 설치되어 있어야 합니다:

- **Docker**: 컨테이너 실행을 위해 필요
- **curl**: 헬스체크용 (선택사항)

### Docker 설치 (Ubuntu 예시)
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
```

## 데이터 볼륨

배포 시 데이터베이스 파일을 보존하기 위해 Docker 볼륨을 사용합니다:

```bash
# 볼륨 생성 (자동으로 생성되지만 수동으로도 가능)
docker volume create aps-assessment-data

# 볼륨 확인
docker volume ls
docker volume inspect aps-assessment-data
```

## 수동 배포 (테스트용)

자동 배포를 테스트하기 전에 수동으로 배포를 확인할 수 있습니다:

```bash
# 1. 코드 가져오기
git clone https://github.com/your-username/aps-assessment-system.git
cd aps-assessment-system

# 2. 이미지 빌드
docker build -t assessment-aps-assessment:latest .

# 3. 기존 컨테이너 중지 (있다면)
docker stop aps-assessment-app 2>/dev/null || true
docker rm aps-assessment-app 2>/dev/null || true

# 4. 새 컨테이너 실행
docker run -d \
  --name aps-assessment-app \
  --restart unless-stopped \
  -p 5000:5000 \
  -v aps-assessment-data:/app/data \
  assessment-aps-assessment:latest

# 5. 상태 확인
docker ps
curl http://localhost:5000
```

## 트러블슈팅

### 배포 실패 시 확인사항

1. **SSH 연결 실패**
   - HOST, USERNAME, SSH_PRIVATE_KEY 확인
   - 서버 방화벽 설정 확인
   - SSH 서비스 실행 상태 확인

2. **Docker 명령 실패**
   - 서버에 Docker 설치 확인
   - 사용자가 docker 그룹에 속해있는지 확인
   - Docker 서비스 실행 상태 확인

3. **포트 충돌**
   - 5000 포트가 이미 사용 중인지 확인
   - 기존 컨테이너가 완전히 중지되었는지 확인

### 로그 확인

```bash
# GitHub Actions 로그는 GitHub 웹에서 확인

# 서버에서 컨테이너 로그 확인
docker logs aps-assessment-app

# 컨테이너 상태 확인
docker ps -a
```

## 보안 고려사항

- SSH 개인키는 절대 코드에 포함하지 말고 GitHub Secrets 사용
- 서버는 필요한 포트만 열어둘 것
- 정기적으로 SSH 키 교체 권장
- Docker 이미지 스캔 도구 사용 권장

## 추가 기능

필요에 따라 다음 기능을 추가할 수 있습니다:

- **슬랙/디스코드 알림**: 배포 성공/실패 알림
- **롤백 기능**: 이전 버전으로 자동 롤백
- **멀티 환경**: 개발/스테이징/프로덕션 환경별 배포
- **모니터링**: 헬스체크 및 성능 모니터링
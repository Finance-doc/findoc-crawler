# Python 3.13 버전 기반 이미지 사용
FROM python:3.13-slim

# 작업 디렉터리 생성
WORKDIR /app

# 필요한 라이브러리 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 스크립트 실행
CMD ["python", "crawler.py"]
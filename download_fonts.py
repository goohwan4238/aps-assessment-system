#!/usr/bin/env python3
"""
한글 폰트를 다운로드하는 스크립트
Google Fonts에서 Noto Sans KR 폰트를 다운로드합니다.
"""
import os
import requests
import zipfile
from pathlib import Path

def download_noto_sans_kr():
    """Google Fonts에서 Noto Sans KR 폰트 다운로드"""
    
    # 폰트 디렉토리 생성
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    print("Noto Sans KR 폰트를 다운로드합니다...")
    
    # Google Fonts API를 통해 Noto Sans KR 다운로드
    font_url = "https://fonts.google.com/download?family=Noto%20Sans%20KR"
    
    try:
        response = requests.get(font_url, stream=True)
        response.raise_for_status()
        
        zip_path = font_dir / "NotoSansKR.zip"
        
        # ZIP 파일 다운로드
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"폰트가 다운로드되었습니다: {zip_path}")
        
        # ZIP 파일 압축 해제
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(font_dir)
        
        # ZIP 파일 삭제
        os.remove(zip_path)
        
        print("폰트 압축 해제가 완료되었습니다.")
        
        # TTF 파일 찾기
        ttf_files = list(font_dir.glob("*.ttf"))
        if ttf_files:
            print(f"설치된 폰트 파일: {ttf_files}")
        else:
            print("TTF 파일을 찾을 수 없습니다. OTF 파일을 찾는 중...")
            otf_files = list(font_dir.glob("*.otf"))
            if otf_files:
                print(f"설치된 폰트 파일: {otf_files}")
    
    except Exception as e:
        print(f"폰트 다운로드 실패: {e}")
        print("대체 방법을 사용합니다...")
        create_fallback_font_info()

def create_fallback_font_info():
    """폰트 다운로드가 실패한 경우 대체 방안 정보 생성"""
    font_dir = Path("fonts")
    font_dir.mkdir(exist_ok=True)
    
    info_text = """
# 한글 폰트 설치 안내

폰트 자동 다운로드가 실패했습니다. 
다음 중 하나의 방법으로 한글 폰트를 설치하세요:

## 방법 1: 직접 다운로드
1. https://fonts.google.com/noto/specimen/Noto+Sans+KR 접속
2. "Download family" 클릭
3. 다운로드한 파일을 fonts/ 폴더에 압축 해제

## 방법 2: 시스템 폰트 사용
Docker 컨테이너에서는 DejaVu 폰트가 기본 제공됩니다.

## 방법 3: 웹폰트 CDN 사용 
애플리케이션에서 자동으로 설정됩니다.
"""
    
    with open(font_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(info_text)

if __name__ == "__main__":
    download_noto_sans_kr()
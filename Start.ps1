$ErrorActionPreference = "Stop"
#$Base = $PSScriptRoot
#Set-Location $Base
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath


try {
    Write-Host " 작업 경로: $Base"

    # 1. Python 존재 확인
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host " Python이 설치되어 있지 않습니다."
        Write-Host " https://www.python.org 다운로드 후 재실행하세요."
        Read-Host "엔터 누르면 종료"
        exit
    }

    # 2. 가상환경 생성
    Write-Host " venv 생성 중..."
    python -m venv .venv

    # 3. pip 업그레이드
    Write-Host " pip 업그레이드..."
    & "$Base\.venv\Scripts\python.exe" -m ensurepip
    & "$Base\.venv\Scripts\python.exe" -m pip install --upgrade pip

    # 4. 패키지 설치
    Write-Host " 패키지 설치 중..."
    & "$Base\.venv\Scripts\python.exe" -m pip install -r "$Base\requirements.txt"

    # 5. Streamlit 실행
    Write-Host " Streamlit 실행..."
    Start-Process "http://127.0.0.1:8501"

    & "$Base\.venv\Scripts\python.exe" -m streamlit run "$Base\StreamlitSub.py" --server.port 8501
}
catch {
    Write-Host " 에러 발생:"
    Write-Host $_
}

Read-Host "엔터 누르면 종료"
# 실행하기.ps1
# 목적: uv 런처 다운로드 -> 가상환경 생성 -> 패키지 설치 -> Streamlit 앱 실행

$ErrorActionPreference = "Stop"
$Base = $PSScriptRoot
Set-Location $Base

# 1) uv.exe 준비
$Uv = Join-Path $Base "uv.exe"
if (-not (Test-Path $Uv)) {
    Write-Host "uv 내려받는 중..."
    $Url = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.exe"
    Invoke-WebRequest -Uri $Url -OutFile $Uv
}

# 2) 가상환경 만들기 + 패키지 설치
.\uv.exe venv .venv --clear
.\.venv\Scripts\activate
pip install -r requirements.txt

# 3) 앱 실행
#$Proc = Start-Process -FilePath ".\.venv\Scripts\python.exe" `
#    -ArgumentList "-m streamlit run `"$Base\Streamlit.py`" --server.address 127.0.0.1 --server.port 8501" `
#    -WorkingDirectory $Base -PassThru
& "$Base\.venv\Scripts\python.exe" -m streamlit run "$Base\Streamlit.py" --server.port 8501

Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8501"

# 4) 앱 종료 시까지 대기
#Wait-Process -Id $Proc.Id



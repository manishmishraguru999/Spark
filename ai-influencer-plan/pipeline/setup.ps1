# BEAST pipeline one-click setup (Windows PowerShell).
# Run from the pipeline folder:  powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

Step "Checking Python 3.11+"
$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python not found. Install it:  winget install Python.Python.3.12  (then open a new terminal)" -ForegroundColor Yellow
    exit 1
}
& py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) { Write-Host "Python 3.11+ required." -ForegroundColor Yellow; exit 1 }

Step "Checking FFmpeg"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    $ans = Read-Host "FFmpeg not found. Install now with winget? (y/n)"
    if ($ans -eq "y") { winget install --id Gyan.FFmpeg -e; Write-Host "Open a NEW terminal and run setup.ps1 again."; exit 0 }
    exit 1
}

Step "Creating virtual environment"
if (-not (Test-Path "venv\Scripts\python.exe")) { & py -3 -m venv venv }
& venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

Step "Config"
if (-not (Test-Path "config.yaml")) {
    Copy-Item config.example.yaml config.yaml
    Write-Host "config.yaml created. Edit paths.root, telegram.allowed_chat_ids and platforms."
}

Step "Secrets (press Enter to skip any)"
foreach ($name in @("TELEGRAM_BOT_TOKEN", "SARVAM_API_KEY")) {
    if (-not [Environment]::GetEnvironmentVariable($name, "User")) {
        $val = Read-Host "$name"
        if ($val) { [Environment]::SetEnvironmentVariable($name, $val, "User"); Set-Item -Path "Env:$name" -Value $val }
    }
}

Step "Demo video (no Telegram, no publishing)"
& venv\Scripts\python.exe run_pipeline.py --config config.yaml --demo

Step "Doctor"
& venv\Scripts\python.exe run_pipeline.py --config config.yaml --doctor
Write-Host "`nDone. Fix any red items above, then start:  start_pipeline.bat" -ForegroundColor Green

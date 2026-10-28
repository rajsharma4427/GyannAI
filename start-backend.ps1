# Gyaan Loop — Backend Startup Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
Set-Location -Path $scriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  GYAAN LOOP — Fast-Track AI Math Tutor (FastAPI Backend)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[✓] Python found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Error "Python 3 is required but was not found on PATH. Please install Python 3.10+."
    exit 1
}

# 2. Configure Environment Defaults for Standalone / Mock Operation
$env:PYTHONPATH = $scriptDir
if (-not $env:AI_MOCK) { $env:AI_MOCK = "1" }
if (-not $env:AI_CACHE) { $env:AI_CACHE = "1" }
if (-not $env:DB_PATH) { $env:DB_PATH = "gyaan_loop.db" }
if (-not $env:CONTENT_DIR) { $env:CONTENT_DIR = "content" }

Write-Host "[i] AI Mock Mode: $env:AI_MOCK (1 = deterministic mock, 0 = LLM provider)" -ForegroundColor Yellow
Write-Host "[i] SQLite DB:    $env:DB_PATH" -ForegroundColor Yellow
Write-Host "[i] Content Dir:  $env:CONTENT_DIR" -ForegroundColor Yellow

# 3. Check / Install Python Dependencies
Write-Host "[i] Verifying Python dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt --quiet

# 4. Display URLs
Write-Host ""
Write-Host "Starting Uvicorn ASGI server..." -ForegroundColor Green
Write-Host "  -> API Root:      http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "  -> Health Check:  http://127.0.0.1:8000/health" -ForegroundColor Green
Write-Host "  -> OpenAPI Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the backend." -ForegroundColor Gray
Write-Host ""

# 5. Launch FastAPI backend
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

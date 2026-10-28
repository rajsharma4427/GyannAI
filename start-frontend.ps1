# Gyaan Loop — Frontend Startup Script (Windows PowerShell)
$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$frontendDir = Join-Path $scriptDir "frontend"
Set-Location -Path $frontendDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  GYAAN LOOP — Student Experience (React + TypeScript UI)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Node.js and npm
try {
    $nodeVer = node --version 2>&1
    $npmVer = npm --version 2>&1
    Write-Host "[✓] Node.js found: $nodeVer" -ForegroundColor Green
    Write-Host "[✓] npm found:     v$npmVer" -ForegroundColor Green
} catch {
    Write-Error "Node.js and npm are required. Please install Node.js v18+."
    exit 1
}

# 2. Check / Copy .env
$envFile = Join-Path $frontendDir ".env"
$envExample = Join-Path $frontendDir ".env.example"
if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Write-Host "[i] Initializing frontend .env from .env.example..." -ForegroundColor Yellow
    Copy-Item $envExample $envFile
}

# 3. Check node_modules
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[i] Installing frontend dependencies (npm ci)..." -ForegroundColor Cyan
    npm ci
}

# 4. Display URLs
Write-Host ""
Write-Host "Starting Vite development server..." -ForegroundColor Green
Write-Host "  -> Local UI:      http://localhost:5173" -ForegroundColor Green
Write-Host "  -> Backend API:   http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the frontend." -ForegroundColor Gray
Write-Host ""

# 5. Launch Vite dev server
npm run dev

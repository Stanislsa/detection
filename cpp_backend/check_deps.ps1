# Check C++ Dependencies Status

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  C++ Dependencies Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Visual Studio Build Tools
Write-Host "[1/3] Visual Studio Build Tools..." -ForegroundColor Cyan
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    $vsInstall = & $vsWhere -latest -property installationPath
    if ($vsInstall) {
        Write-Host "OK: Installed" -ForegroundColor Green
        $vsSize = (Get-ChildItem "C:\Program Files (x86)\Microsoft Visual Studio" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  Size: $([math]::Round($vsSize, 2)) MB" -ForegroundColor White
    } else {
        Write-Host "ERROR: Not installed" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Not installed" -ForegroundColor Red
}

# Check CMake
Write-Host ""
Write-Host "[2/3] CMake..." -ForegroundColor Cyan
$cmake = Get-Command cmake -ErrorAction SilentlyContinue
if ($cmake) {
    Write-Host "OK: Installed" -ForegroundColor Green
    $cmakeVersion = & cmake --version
    Write-Host "  Version: $cmakeVersion" -ForegroundColor White
} else {
    Write-Host "ERROR: Not installed" -ForegroundColor Red
}

# Check ONNX Runtime
Write-Host ""
Write-Host "[3/3] ONNX Runtime..." -ForegroundColor Cyan
if (Test-Path "C:\fall_detection_deps\onnxruntime") {
    Write-Host "OK: Installed" -ForegroundColor Green
    $onnxSize = (Get-ChildItem "C:\fall_detection_deps\onnxruntime" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  Size: $([math]::Round($onnxSize, 2)) MB" -ForegroundColor White
} else {
    Write-Host "ERROR: Not installed" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause

# Build portable Windows exe for NCE2 Sentence Components
# Usage: powershell -ExecutionPolicy Bypass -File scripts/build_exe.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "Installing dependencies..."
pip install -q -r requirements.txt -r requirements-dev.txt

Write-Host "Building exe..."
pyinstaller --noconfirm --windowed --name nce2_sentence_components `
  --add-data "data;data" `
  --add-data "nce2_export/assets;nce2_export/assets" `
  --add-data "config/ai.json.example;config" `
  --hidden-import PyQt6 `
  nce2_gui/main.py

$Dist = Join-Path $Root "dist\nce2_sentence_components"
Write-Host ""
Write-Host "Build complete: $Dist\nce2_sentence_components.exe"
Write-Host ""
Write-Host "Deploy checklist:"
Write-Host "  1. Copy nce_txt/第二册/ next to the exe (user-provided lesson txt)"
Write-Host "  2. Optional: copy config/ai.json for AI pre-annotation"
Write-Host "  3. Run nce2_sentence_components.exe"

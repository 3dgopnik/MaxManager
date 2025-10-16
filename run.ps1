param()
$ErrorActionPreference = "Stop"

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!(Test-Path $py)) { throw "Virtualenv Python not found: $py" }
Write-Host "Using Python: $py"

Write-Host "Installing/validating dependencies..."
& $py -m pip install -r "$PSScriptRoot\requirements.txt" | Out-Host

Write-Host "Starting MaxManager..."
& $py "$PSScriptRoot\src\main.py"

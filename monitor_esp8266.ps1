$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$env:PLATFORMIO_CORE_DIR = Join-Path $ProjectRoot ".platformio"

$PythonExe = "D:\New folder (16)\python\python.exe"
$PioExe = "pio"
$pioCommand = Get-Command pio -ErrorAction SilentlyContinue

if ($pioCommand) {
    $PioExe = $pioCommand.Source
} else {
    $UserPioExe = Join-Path $env:APPDATA "Python\Python312\Scripts\pio.exe"
    if (Test-Path $UserPioExe) {
        $PioExe = $UserPioExe
    } else {
        throw "Chua tim thay PlatformIO CLI. Chay: & '$PythonExe' -m pip install platformio"
    }
}

Write-Host "Dang mo Serial Monitor ESP8266 baud 9600..."
Write-Host "Neu khong thay log, bam nut RESET tren ESP8266."
& $PioExe device monitor -b 9600

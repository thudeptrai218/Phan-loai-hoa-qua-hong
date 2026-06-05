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

Write-Host "Dang upload code Arduino Uno..."
Write-Host "Luu y: thao day D0/RX va D1/TX khoi Arduino Uno truoc khi upload."
& $PioExe run -e uno -t upload
Write-Host "Da upload Arduino Uno xong."

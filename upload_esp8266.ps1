param(
    [string]$Port = "",
    [int]$Retries = 3
)

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

$uploadArgs = @("run", "-e", "nodemcuv2", "-t", "upload")
$ports = & $PioExe device list 2>$null
$espPort = if ($Port) { $Port } else { $null }

Write-Host "Danh sach cong hien co:"
if ($ports) {
    $ports | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "Khong doc duoc danh sach cong COM."
}

if (!$espPort) {
    foreach ($line in $ports) {
        if ($line -match "^(COM\d+)") {
            $port = $Matches[1]
            if ($line -match "USB|UART|CH340|CH341|CP210|Silicon|Serial|NodeMCU|ESP") {
                $espPort = $port
                break
            }
            if (!$espPort) {
                $espPort = $port
            }
        }
    }
}

if ($espPort) {
    Write-Host "Tu dong chon cong ESP8266: $espPort"
    $uploadArgs += @("--upload-port", $espPort)
} else {
    Write-Host "Khong tu tim thay cong COM. PlatformIO se tu chon cong neu co the."
}

Write-Host "Dang upload code ESP8266..."
Write-Host "Neu dang mo Serial Monitor, hay tat Serial Monitor truoc khi upload."

for ($attempt = 1; $attempt -le $Retries; $attempt++) {
    Write-Host "Lan thu $attempt/$Retries..."
    & $PioExe @uploadArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Da upload ESP8266 xong. Hay reset ESP8266 va xem Serial Monitor neu can."
        exit 0
    }

    Write-Host "Upload that bai lan $attempt. Rut/cam lai USB hoac bam RESET tren ESP8266 neu can."
    Start-Sleep -Seconds 2
}

throw "Upload ESP8266 that bai. Neu loi 'could not open port' hoac 'semaphore timeout': dong Serial Monitor, rut/cam lai USB, thu cong COM khac bang .\upload_esp8266.ps1 -Port COMx, cai lai driver CH340/CP2102, hoac doi cap USB data."

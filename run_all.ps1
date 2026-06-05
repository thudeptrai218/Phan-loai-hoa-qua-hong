param(
    [switch]$UploadUno,
    [switch]$UploadEsp8266,
    [switch]$UploadOnly,
    [string]$Esp8266Port = "",
    [switch]$SkipHardware,
    [string]$DroidCamIp = "172.20.10.3",
    [string]$Esp8266Ip = "192.168.4.1",
    [string]$Esp8266Url = "",
    [double]$ServoCooldownSeconds = 2.0,
    [double]$ServoFailCooldownSeconds = 8.0,
    [int]$ServoStableFrames = 3,
    [double]$Esp8266TimeoutSeconds = 0.35,
    [switch]$NoAutoDiscoverEsp8266
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
$env:PLATFORMIO_CORE_DIR = Join-Path $ProjectRoot ".platformio"

$PythonExe = "D:\New folder (16)\python\python.exe"
if (!(Test-Path $PythonExe)) {
    throw "Khong tim thay Python: $PythonExe"
}

if (!(Test-Path "runs\detect\rotten_fruit\weights\best.pt")) {
    throw "Khong tim thay model runs\detect\rotten_fruit\weights\best.pt. Hay train model truoc."
}

if (!$SkipHardware -and ($UploadUno -or $UploadEsp8266)) {
    $PioExe = "pio"
    $pioCommand = Get-Command pio -ErrorAction SilentlyContinue
    if ($pioCommand) {
        $PioExe = $pioCommand.Source
    } else {
        $UserPioExe = Join-Path $env:APPDATA "Python\Python312\Scripts\pio.exe"
        if (Test-Path $UserPioExe) {
            $PioExe = $UserPioExe
        } else {
            throw "Chua tim thay PlatformIO CLI. Hay cai PlatformIO IDE trong VS Code hoac chay: & '$PythonExe' -m pip install platformio"
        }
    }

    if ($UploadUno) {
        Write-Host "Dang upload code Arduino Uno..."
        & $PioExe run -e uno -t upload
        if ($LASTEXITCODE -ne 0) {
            throw "Upload Arduino Uno that bai."
        }
    }

    if ($UploadEsp8266) {
        Write-Host "Dang upload code ESP8266..."
        $uploadArgs = @("run", "-e", "nodemcuv2", "-t", "upload")
        $ports = & $PioExe device list 2>$null
        $espPort = if ($Esp8266Port) { $Esp8266Port } else { $null }

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
        }

        & $PioExe @uploadArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Upload ESP8266 that bai. Da giam upload_speed=115200 va resetmethod=nodemcu. Neu van loi, board/cap/driver khong auto boot duoc: thao RX/TX voi Arduino, doi cap USB data, hoac giu FLASH/BOOT khi terminal hien Connecting."
        }
    }
}

if ($UploadOnly) {
    Write-Host "Da upload xong. Khong chay Flask server vi ban dung -UploadOnly."
    exit 0
}

$env:DROIDCAM_IP = $DroidCamIp
if (!$Esp8266Url) {
    $Esp8266Url = "http://$Esp8266Ip/control"
}

$env:ESP8266_IP = $Esp8266Ip
$env:ESP8266_URL = $Esp8266Url
$env:AUTO_DISCOVER_ESP8266 = if ($NoAutoDiscoverEsp8266) { "0" } else { "1" }
$env:ENABLE_HARDWARE = if ($SkipHardware) { "0" } else { "1" }
$env:SERVO_COOLDOWN_SECONDS = "$ServoCooldownSeconds"
$env:SERVO_FAIL_COOLDOWN_SECONDS = "$ServoFailCooldownSeconds"
$env:SERVO_STABLE_FRAMES = "$ServoStableFrames"
$env:ESP8266_TIMEOUT_SECONDS = "$Esp8266TimeoutSeconds"

Write-Host ""
Write-Host "Dang chay Flask web..."
Write-Host "Web: http://127.0.0.1:6003"
Write-Host "DroidCam IP: $env:DROIDCAM_IP"
Write-Host "ESP8266 URL: $env:ESP8266_URL"
Write-Host "Auto discover ESP8266: $env:AUTO_DISCOVER_ESP8266"
Write-Host "Servo cooldown: $env:SERVO_COOLDOWN_SECONDS s"
Write-Host "Servo fail cooldown: $env:SERVO_FAIL_COOLDOWN_SECONDS s"
Write-Host "Stable frames: $env:SERVO_STABLE_FRAMES"
Write-Host ""

& $PythonExe server.py

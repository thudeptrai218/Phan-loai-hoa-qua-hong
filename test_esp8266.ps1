param(
    [string]$Esp8266Ip = "",
    [string]$Subnet = "192.168.100",
    [switch]$Scan
)

$ErrorActionPreference = "Stop"

function Test-OneEsp8266 {
    param([string]$Ip)

    $baseUrl = "http://$Ip"
    Write-Host "Kiem tra ESP8266: $baseUrl"

    try {
        $ping = Invoke-WebRequest "$baseUrl/ping" -UseBasicParsing -TimeoutSec 3
        Write-Host "PING OK:" $ping.Content

        $servo1 = Invoke-WebRequest "$baseUrl/control?servo=1" -UseBasicParsing -TimeoutSec 3
        Write-Host "SERVO 1:" $servo1.Content

        Start-Sleep -Seconds 1

        $servo2 = Invoke-WebRequest "$baseUrl/control?servo=2" -UseBasicParsing -TimeoutSec 3
        Write-Host "SERVO 2:" $servo2.Content

        Write-Host "ESP8266 OK: $Ip"
        return $true
    } catch {
        Write-Host "Khong ket noi duoc ESP8266 tai $Ip"
        Write-Host $_.Exception.Message
        return $false
    }
}

if ($Scan) {
    Write-Host "Dang scan $Subnet.1 -> $Subnet.254 de tim /ping ..."
    for ($i = 1; $i -le 254; $i++) {
        $ip = "$Subnet.$i"
        try {
            $response = Invoke-WebRequest "http://$ip/ping" -UseBasicParsing -TimeoutSec 1
            if ($response.Content -like "*ESP8266 OK*") {
                Write-Host "Tim thay ESP8266: $ip"
                Write-Host $response.Content
                exit 0
            }
        } catch {
        }
    }

    Write-Host "Khong tim thay ESP8266 tren subnet $Subnet.x"
    Write-Host "Hay mo Serial Monitor cua ESP8266 baud 9600 de xem IP that."
    exit 1
}

if (!$Esp8266Ip) {
    throw "Hay truyen -Esp8266Ip 192.168.x.x hoac dung -Scan -Subnet 192.168.x"
}

$ok = Test-OneEsp8266 -Ip $Esp8266Ip
if (!$ok) {
    Write-Host ""
    Write-Host "Cach xu ly nhanh:"
    Write-Host "1. Mo Serial Monitor ESP8266 baud 9600."
    Write-Host "2. Reset ESP8266 va xem dong: WiFi OK. ESP8266 IP: ..."
    Write-Host "3. Dam bao laptop va ESP8266 cung Wi-Fi."
    Write-Host "4. Test lai bang: .\test_esp8266.ps1 -Esp8266Ip IP_THAT"
    Write-Host "5. Neu khong biet IP, thu: .\test_esp8266.ps1 -Scan -Subnet 192.168.100"
    exit 1
}

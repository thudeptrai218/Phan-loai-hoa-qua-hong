# He thong phan loai qua tuoi va qua hong

Du an xay dung he thong nhan dien qua tuoi/qua hong bang YOLO, hien thi ket qua tren web Flask va dieu khien servo thong qua ESP8266 + Arduino Uno.

## 1. Chuc nang chinh

- Nhan dien 2 lop: `Qua Hong` va `Qua Tuoi`.
- Lay camera tu DroidCam tren dien thoai.
- Hien thi video truc tiep tren giao dien web.
- Luu lich su nhan dien va thong ke so qua tuoi/qua hong.
- Gui lenh dieu khien servo toi ESP8266.
- ESP8266 chuyen lenh qua Serial cho Arduino Uno.
- Arduino Uno dieu khien 2 servo:
  - Servo 1: gat qua hong.
  - Servo 2: gat qua tuoi.
- Co trang thai phan cung tren web: lenh gan nhat, phan hoi OK, loi ket noi.
- Co co che chong spam lenh servo khi nhan dien lien tuc.

## 2. Cong nghe su dung

| Thanh phan | Vai tro |
|---|---|
| Python | Xu ly AI va Flask server |
| Ultralytics YOLO | Nhan dien qua tuoi/qua hong |
| OpenCV | Doc camera va ve bounding box |
| Flask | Web dashboard |
| DroidCam | Camera tu dien thoai |
| Roboflow | Quan ly dataset va export YOLOv8 |
| ESP8266 | Nhan lenh HTTP tu Flask |
| Arduino Uno | Dieu khien servo |
| PlatformIO | Nap code Arduino/ESP8266 bang VS Code |

## 3. Cau truc thu muc

```text
Phan-Loai-Trai-Cay-main/
├── server.py
├── train_model.py
├── download_roboflow_dataset.py
├── run_all.ps1
├── upload_esp8266.ps1
├── upload_uno.ps1
├── monitor_esp8266.ps1
├── test_esp8266.ps1
├── requirements.txt
├── platformio.ini
├── Templates/
│   └── web_dashboard.html
├── src/
│   ├── arduino_uno/
│   │   └── main.cpp
│   └── esp8266_node/
│       └── main.cpp
├── servo/
│   └── servo.ino
├── esp8266/
│   └── esp8266.ino
├── runs/
│   └── detect/rotten_fruit/weights/best.pt
└── traicay-1/
```

## 4. Yeu cau cai dat

### Python

Project dang dung Python tai:

```powershell
D:\New folder (16)\python\python.exe
```

Cai thu vien:

```powershell
& 'D:\New folder (16)\python\python.exe' -m pip install -r requirements.txt
```

### PlatformIO

Cai PlatformIO CLI:

```powershell
& 'D:\New folder (16)\python\python.exe' -m pip install platformio
```

Hoac cai extension `PlatformIO IDE` trong VS Code.

## 5. Train model YOLO

Dataset Roboflow cua project gom 2 nhan:

```text
0: Qua Hong
1: Qua Tuoi
```

Tai dataset Roboflow:

```powershell
$env:ROBOFLOW_API_KEY='API_KEY_CUA_BAN'
$env:ROBOFLOW_VERSION='1'
& 'D:\New folder (16)\python\python.exe' download_roboflow_dataset.py
```

Train model:

```powershell
& 'D:\New folder (16)\python\python.exe' train_model.py
```

Model sau khi train can nam tai:

```text
runs/detect/rotten_fruit/weights/best.pt
```

## 6. Cau hinh DroidCam

IP DroidCam mac dinh:

```text
172.20.10.3
```

Port mac dinh:

```text
4747
```

URL camera:

```text
http://172.20.10.3:4747/video
```

Neu IP DroidCam thay doi:

```powershell
.\run_all.ps1 -DroidCamIp IP_MOI
```

## 7. Nap code phan cung

### Nap ESP8266

Thao day RX/TX giua ESP8266 va Arduino truoc khi upload.

```powershell
.\upload_esp8266.ps1
```

Neu can chi dinh cong COM:

```powershell
.\upload_esp8266.ps1 -Port COM3
```

Mo Serial Monitor ESP8266:

```powershell
.\monitor_esp8266.ps1
```

### Nap Arduino Uno

Thao day D0/RX va D1/TX khoi Arduino Uno truoc khi upload.

```powershell
.\upload_uno.ps1
```

## 8. Dau day phan cung

### ESP8266 voi Arduino Uno

```text
ESP8266 TX  -> Arduino RX D0
ESP8266 GND -> Arduino GND
```

Neu noi Arduino TX ve ESP8266 RX:

```text
Arduino TX D1 -> mach chia ap 5V ve 3.3V -> ESP8266 RX
```

Khuyen nghi mach chia ap:

```text
Arduino TX D1 ---- R1 1k ----+---- ESP8266 RX
                             |
                            R2 2k
                             |
                            GND
```

### Arduino Uno voi servo

```text
Servo qua hong signal -> Arduino D9
Servo qua tuoi signal -> Arduino D10
Servo VCC             -> nguon ngoai 5V
Servo GND             -> GND chung
```

Tat ca GND phai noi chung:

```text
Arduino GND
ESP8266 GND
Nguon servo GND
```

## 9. Chay chuong trinh

Chay tat ca:

```powershell
.\run_all.ps1
```

Mo web:

```text
http://127.0.0.1:6003
```

Chay web khong gui lenh phan cung:

```powershell
.\run_all.ps1 -SkipHardware
```

Doi IP DroidCam:

```powershell
.\run_all.ps1 -DroidCamIp 172.20.10.3
```

Doi IP ESP8266:

```powershell
.\run_all.ps1 -Esp8266Ip 192.168.4.1
```

## 10. Test ESP8266

Test theo IP:

```powershell
.\test_esp8266.ps1 -Esp8266Ip 192.168.4.1
```

Hoac test bang trinh duyet:

```text
http://192.168.4.1/ping
http://192.168.4.1/control?servo=1
http://192.168.4.1/control?servo=2
```

## 11. Nguyen ly dieu khien

| Ket qua YOLO | Class | Lenh gui ESP8266 | Arduino | Servo |
|---|---:|---|---|---|
| Qua Hong | 0 | `servo=1` | D9 | Gat qua hong |
| Qua Tuoi | 1 | `servo=2` | D10 | Gat qua tuoi |

Server co co che:

- Chi gui lenh khi ket qua on dinh nhieu frame lien tiep.
- Cooldown moi servo de tranh gat lien tuc.
- Neu ESP8266 loi, tam dung gui lai trong vai giay.
- Gui lenh ESP8266 bang worker nen de DroidCam khong bi dung.

## 12. Loi thuong gap

### DroidCam khong hien hinh

- Kiem tra DroidCam da mo tren dien thoai.
- Kiem tra IP co dung `172.20.10.3` khong.
- Thu mo URL:

```text
http://172.20.10.3:4747/video
```

### ESP8266 timeout

- Kiem tra ESP8266 da nap code.
- Test:

```powershell
.\test_esp8266.ps1 -Esp8266Ip 192.168.4.1
```

- Kiem tra laptop co cung mang voi ESP8266 khong.

### Upload ESP8266 that bai

Doc huong dan:

```text
HUONG_DAN_FIX_UPLOAD_ESP8266.md
```

Thu:

```powershell
.\upload_esp8266.ps1 -Port COM3
```

### Servo khong quay

- Kiem tra nguon ngoai 5V.
- Kiem tra GND chung.
- Kiem tra signal D9/D10.
- Test:

```text
http://IP_ESP8266/control?servo=1
http://IP_ESP8266/control?servo=2
```

## 13. Ghi chu

Dataset hien tai con nho, nen can bo sung them anh qua tuoi va qua hong trong nhieu dieu kien anh sang, goc chup va nen khac nhau de tang do chinh xac khi demo thuc te.

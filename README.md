<h2 align="center">
    <a href="https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin">
        🎓 Khoa Công nghệ Thông tin - Trường Đại học Đại Nam
    </a>
</h2>

<h2 align="center">
    Thành phố thông minh và Nông nghiệp thông minh
</h2>

<div align="center">
    <p align="center">
        <img src="logo/aiotlab_logo.png" alt="AIoTLab Logo" width="170"/>
        <img src="logo/fitdnu_logo.png" alt="FIT DNU Logo" width="180"/>
        <img src="logo/dnu_logo.png" alt="Dai Nam University Logo" width="200"/>
    </p>

[![AIoTLab](https://img.shields.io/badge/AIoTLab-Green?style=for-the-badge)](https://www.facebook.com/DNUAIoTLab)
[![Faculty of Information Technology](https://img.shields.io/badge/Faculty%20of%20Information%20Technology-Blue?style=for-the-badge)](https://dainam.edu.vn/vi/khoa-cong-nghe-thong-tin)
[![DaiNam University](https://img.shields.io/badge/DaiNam%20University-Orange?style=for-the-badge)](https://dainam.edu.vn)

</div>

# 🍎 HỆ THỐNG PHÂN LOẠI QUẢ TƯƠI VÀ QUẢ HỎNG

## 📖 Giới thiệu

Dự án xây dựng hệ thống nhận diện và phân loại **quả tươi** và **quả hỏng** bằng mô hình YOLO, hiển thị kết quả trên giao diện Web Flask và điều khiển cơ cấu phân loại tự động thông qua ESP8266 kết hợp Arduino Uno.

Hệ thống thuộc lĩnh vực **Nông nghiệp thông minh (Smart Agriculture)**, giúp tự động hóa quá trình phân loại nông sản, giảm sức lao động thủ công và nâng cao hiệu quả sản xuất.

---

## 🎯 Chức năng chính

- Nhận diện 2 lớp:
  - `Quả Hỏng`
  - `Quả Tươi`
- Thu nhận hình ảnh từ DroidCam trên điện thoại.
- Hiển thị video trực tiếp trên giao diện Web.
- Hiển thị Bounding Box và độ tin cậy của mô hình.
- Lưu lịch sử nhận diện.
- Thống kê số lượng quả tươi và quả hỏng.
- Gửi lệnh điều khiển Servo tới ESP8266.
- ESP8266 chuyển tiếp lệnh tới Arduino Uno qua Serial.
- Arduino điều khiển Servo phân loại sản phẩm.
- Hiển thị trạng thái phần cứng trên giao diện Web.
- Chống gửi lệnh Servo liên tục khi nhận diện nhiều khung hình liên tiếp.

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Vai trò |
|------------|----------|
| Python | Xử lý AI và Server |
| Flask | Web Dashboard |
| OpenCV | Xử lý hình ảnh |
| Ultralytics YOLO | Nhận diện đối tượng |
| Roboflow | Quản lý Dataset |
| DroidCam | Camera điện thoại |
| ESP8266 | Gateway IoT |
| Arduino Uno | Điều khiển Servo |
| PlatformIO | Nạp chương trình |

---

## 📂 Cấu trúc thư mục

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
│   └── detect/
│       └── rotten_fruit/
│           └── weights/
│               └── best.pt
└── traicay-1/
```

---

## ⚙️ Cài đặt môi trường

### Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

### Cài đặt PlatformIO

```bash
pip install platformio
```

Hoặc cài đặt Extension:

```text
PlatformIO IDE
```

trong Visual Studio Code.

---

## 🤖 Huấn luyện mô hình

### Dataset

```text
0 : Quả Hỏng
1 : Quả Tươi
```

### Tải Dataset từ Roboflow

```powershell
$env:ROBOFLOW_API_KEY="YOUR_API_KEY"
$env:ROBOFLOW_VERSION="1"

python download_roboflow_dataset.py
```

### Huấn luyện

```powershell
python train_model.py
```

Sau khi huấn luyện thành công:

```text
runs/detect/rotten_fruit/weights/best.pt
```

---

## 📷 Cấu hình DroidCam

Ví dụ:

```text
IP   : 172.20.10.3
Port : 4747
```

URL Camera:

```text
http://172.20.10.3:4747/video
```

---

## 🔌 Kết nối phần cứng

### ESP8266 ↔ Arduino Uno

```text
ESP8266 TX  -> Arduino RX (D0)

ESP8266 GND -> Arduino GND
```

Nếu kết nối ngược chiều:

```text
Arduino TX (D1)
      ↓
Mạch chia áp
      ↓
ESP8266 RX
```

### Arduino Uno ↔ Servo

```text
Servo Quả Hỏng Signal -> D9

Servo Quả Tươi Signal -> D10

Servo VCC             -> Nguồn 5V ngoài

Servo GND             -> GND chung
```

---

## 🚀 Nạp chương trình

### ESP8266

```powershell
.\upload_esp8266.ps1
```

Chỉ định COM:

```powershell
.\upload_esp8266.ps1 -Port COM3
```

### Arduino Uno

```powershell
.\upload_uno.ps1
```

---

## ▶️ Chạy hệ thống

Khởi động toàn bộ:

```powershell
.\run_all.ps1
```

Mở trình duyệt:

```text
http://127.0.0.1:6003
```

Chạy không kết nối phần cứng:

```powershell
.\run_all.ps1 -SkipHardware
```

---

## 🔍 Kiểm tra ESP8266

```powershell
.\test_esp8266.ps1
```

Hoặc truy cập trực tiếp:

```text
http://192.168.4.1/ping

http://192.168.4.1/control?servo=1

http://192.168.4.1/control?servo=2
```

---

## ⚡ Nguyên lý hoạt động

| Kết quả YOLO | Class | Lệnh ESP8266 | Arduino | Servo |
|--------------|--------|--------------|----------|--------|
| Quả Hỏng | 0 | servo=1 | D9 | Gạt quả hỏng |
| Quả Tươi | 1 | servo=2 | D10 | Gạt quả tươi |

### Quy trình xử lý

1. Camera gửi hình ảnh.
2. YOLO nhận diện đối tượng.
3. Flask nhận kết quả từ YOLO.
4. Flask gửi lệnh HTTP tới ESP8266.
5. ESP8266 gửi lệnh Serial tới Arduino.
6. Arduino điều khiển Servo.
7. Quả được phân loại vào đúng khay.

---

## ❌ Một số lỗi thường gặp

### DroidCam không hiển thị

Kiểm tra:

```text
http://IP_DROIDCAM:4747/video
```

### ESP8266 Timeout

```powershell
.\test_esp8266.ps1
```

### Servo không hoạt động

- Kiểm tra nguồn ngoài 5V.
- Kiểm tra GND chung.
- Kiểm tra dây tín hiệu D9 và D10.
- Kiểm tra kết nối Serial.

---

## 📈 Hướng phát triển

- Tăng kích thước Dataset.
- Nhận diện nhiều loại trái cây hơn.
- Lưu lịch sử vào Database.
- Xây dựng Dashboard IoT thời gian thực.
- Kết nối Cloud.
- Phân loại nhiều mức độ hư hỏng.
- Triển khai trên dây chuyền sản xuất thực tế.

---

## 👨‍💻 Nhóm thực hiện

**Khoa Công nghệ Thông tin**  
**Trường Đại học Đại Nam**

**Học phần:** Thành phố thông minh và Nông nghiệp thông minh

---

⭐ Nếu thấy dự án hữu ích, hãy để lại một Star cho Repository.

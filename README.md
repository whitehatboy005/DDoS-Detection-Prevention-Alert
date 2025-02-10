# 🚀 DDoS Attack Detection & Prevention with Telegram Alert System

This repository contains a powerful tool for detecting potential DDoS attacks based on high request frequency from the same IP address. The system monitors traffic, detects anomalies, and sends real-time alerts to a Telegram bot.

## 📌 Features:
1. **Real-Time DDoS Detection** – Monitors excessive requests from the same IP within a short time frame.
2. **Telegram Alert System** – Sends alerts with IP and **WHOIS details** (ISP, location, ASN).
3. **Spam Prevention** – Implements a **5-minute cooldown** per IP to avoid redundant notifications.
4. **Configurable Thresholds** – Easily adjust detection limits via `config.env`.
#
## Instructions
To get Chat ID visit [@GetMyChatID_Bot](https://t.me/GetMyChatID_Bot) Now you will copy the chat Id and config it.
To access the bot [@DDoS Detection Alert](http://t.me/DDoS_Detect_Alertbot) and START it.

## Result
![Screenshot 2025-02-10 175301](https://github.com/user-attachments/assets/45a6a5f2-dc8c-4a64-bcee-ec07ab29ccbb)
## UI Interface for statistics
![Screenshot 2025-02-10 175136](https://github.com/user-attachments/assets/c305e8eb-de3d-43ff-b064-6158bdcb5b7a)
#
![Screenshot 2025-02-10 175142](https://github.com/user-attachments/assets/ee06c15f-3be7-448d-bea3-75424b892728)
## Telegram Bot Alert
![Screenshot 2025-02-10 175338](https://github.com/user-attachments/assets/63a5b09f-2cf4-4568-95b3-19b6706a7b30)

## ⚙️ Installation:
### 1️⃣ Clone the Repository:
```bash
git clone https://github.com/whitehatboy005/DDoS-Detection-Prevention-Alert.git
cd DDoS-Detection-Prevention-Alert
```
## 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
## 3️⃣ Configure Environment Variables for Windows
```bash
notepad config.env
```
## Configure Environment Variables for Linux
```bash
nano config.env
```
## Ensure start the bot
Start it --> [@DDoS Detection Alert](http://t.me/DDoS_Detect_Alertbot)
#
## 🚀 Run the main Program
```bash
python main.py
```
## 🛠️ How It Works:
- Tracks request frequency per IP.
- If an IP exceeds the `THRESHOLD`, an alert is triggered.
- Sends a Telegram notification with **WHOIS** data.
- Blocks repeated alerts from the same IP for 5 minutes.

## Contribution:
**Contributions are welcome! If you have any suggestions for improvements or bug fixes, feel free to submit a pull request.**

## License
This project is licensed under the terms of the [MIT license](LICENSE.md).

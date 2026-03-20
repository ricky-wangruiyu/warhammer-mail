import requests
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import smtplib
import os

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587

# ------------------- 全部使用 GitHub 可以访问的中文站 -------------------
def get_img():
    try:
        url = "https://imgapi.cn/api.php?lb=meizi"
        return requests.head(url, allow_redirects=True).url
    except:
        return "https://i.imgur.com/7V7lN.jpg"

def get_joke():
    try:
        url = "https://v.api.aa1.cn/api/duanzi/index.php"
        return requests.get(url).text.strip()
    except:
        return "WAAAGH!"

def get_char():
    try:
        url = "https://warhammer40k.fandom.com/zh/wiki/Special:Random"
        r = requests.get(url, timeout=10)
        s = BeautifulSoup(r.text, "html.parser")
        title = s.find("h1").get_text(strip=True)
        p = s.find("p").get_text(strip=True)[:400]
        return f"【{title}】{p}"
    except:
        return "【帝皇】人类的守护者，端坐黄金王座万年之久"

def get_news():
    try:
        url = "https://www.warhammer-community.com/zh-hans"
        r = requests.get(url, timeout=10)
        s = BeautifulSoup(r.text, "html.parser")
        arr = [x.get_text(strip=True) for x in s.find_all("h3")]
        return " • ".join(arr[:3])
    except:
        return "新模型 • 新剧情 • 新战役"

# ------------------- 发送 -------------------
def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    html = f'''
<html>
<body style="background:#111; color:#fff; padding:20px;">
<div style="max-width:700px; margin:auto; background:#1a1a1a; border-radius:10px;">
<img src="{img}" style="width:100%;">
<div style="padding:25px;">
<h2 style="color:#d4af37; text-align:center;">⚔️ 战锤日报 {day}</h2>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📜 战锤段子</h3>
<p>{get_joke()}</p>
</div>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">⚡ 人物志</h3>
<p>{get_char()}</p>
</div>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📰 官方新闻</h3>
<p>{get_news()}</p>
</div>
<p style="text-align:center; color:#777;">为了帝皇</p>
</div>
</div>
</body>
</html>
'''
    msg = MIMEMultipart()
    msg["Subject"] = f"战锤日报 {day}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.starttls()
        s.login(SENDER_EMAIL, EMAIL_AUTH_CODE)
        s.send_message(msg)
    print("OK")

if __name__ == "__main__":
    send()

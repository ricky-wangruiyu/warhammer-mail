import requests
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import smtplib
import os

# 邮箱配置
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587

# -------------------------- 全部使用 GitHub 能访问的国外稳定源 --------------------------

# 战锤图片
def get_img():
    try:
        url = "https://api.waifu.im/search?included_tags=warhammer_40k"
        data = requests.get(url, timeout=10).json()
        return data["images"][0]["url"]
    except:
        return "https://i.imgur.com/7V7lN.jpg"

# 战锤趣味内容（实时爬取 Reddit）
def get_joke():
    try:
        url = "https://www.reddit.com/r/Grimdank/hot.json?limit=30"
        data = requests.get(url, timeout=10).json()
        titles = [x["data"]["title"] for x in data["data"]["children"]]
        return random.choice(titles)
    except:
        return "The Emperor protects... but sometimes the internet does not."

# 战锤人物（实时爬取 英文维基）
def get_char():
    try:
        url = "https://warhammer40k.fandom.com/wiki/Special:Random"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find("h1").get_text(strip=True)
        para = soup.find("p").get_text(strip=True)[:400]
        return f"[{name}]\n{para}..."
    except:
        return "A great warrior of the Imperium."

# 战锤官方新闻（实时爬取 GW 官网）
def get_news():
    try:
        url = "https://www.warhammer-community.com/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        heads = [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]
        return "\n• ".join(heads[:3])
    except:
        return "New models are coming soon."

# -------------------------- 发送邮件 --------------------------
def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    
    html = f'''
<html>
<body style="background:#111; color:#fff; padding:20px;">
<div style="max-width:700px; margin:auto; background:#1a1a1a; border-radius:10px;">
<img src="{img}" style="width:100%;">
<div style="padding:25px;">
<h2 style="color:#d4af37; text-align:center;">⚔️ Warhammer Daily {day}</h2>

<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📜 Quote</h3>
<p>{get_joke()}</p>
</div>

<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">⚡ Character</h3>
<p>{get_char()}</p>
</div>

<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📰 News</h3>
<p>• {get_news()}</p>
</div>

<p style="text-align:center; color:#777;">For the Emperor!</p>
</div>
</div>
</body>
</html>
'''

    msg = MIMEMultipart()
    msg["Subject"] = f"⚔️ Warhammer Daily {day}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.starttls()
        s.login(SENDER_EMAIL, EMAIL_AUTH_CODE)
        s.send_message(msg)
    print("✅ SUCCESS")

if __name__ == "__main__":
    send()

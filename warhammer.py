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

# 获取战锤美图
def get_img():
    try:
        url = "https://wallhaven.cc/search?q=warhammer%2040k&sorting=random"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.find("img", class_="lazyload")
        return img["data-src"] if img else "https://i.imgur.com/7V7lN.jpg"
    except:
        return "https://i.imgur.com/7V7lN.jpg"

# 战锤趣闻（换中文源，更稳）
def get_joke():
    try:
        url = "https://www.bilibili.com/read/cv/105877870/"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
        valid = [t for t in paragraphs if len(t) > 10 and len(t) < 100]
        return random.choice(valid) if valid else "战锤的幽默需要细细品味..."
    except:
        return "WAAAGH! 兽人觉得一切都是笑话!"

# 战锤人物
def get_char():
    try:
        url = "https://warhammer40k.fandom.com/zh/wiki/Special:随机"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find("h1").get_text()
        paragraphs = soup.find_all("p")
        desc = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50:
                desc = text[:380]
                break
        return f"【{name}】\n{desc}..."
    except:
        return "人物资料被审判庭没收。"

# 战锤新闻
def get_news():
    try:
        url = "https://www.warhammer-community.com/zh-hans"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]
        return "\n• ".join(titles[:3])
    except:
        return "GW正在制作新模型。"

# 发送HTML邮件
def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    
    html = f'''
<html>
<body style="background:#111; color:#fff; padding:20px;">
<div style="max-width:700px; margin:auto; background:#1a1a1a; border-radius:10px;">
<img src="{img}" style="width:100%;">
<div style="padding:25px;">
<h2 style="color:#d4af37; text-align:center;">⚔️ 战锤每日日报 {day}</h2>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📜 战锤趣闻</h3>
<p>{get_joke()}</p>
</div>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">⚡ 战锤人物志</h3>
<p>{get_char()}</p>
</div>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📰 最新官方消息</h3>
<p>• {get_news()}</p>
</div>
<p style="text-align:center; color:#777;">为了帝皇 | 全自动发送</p>
</div>
</div>
</body>
</html>
'''

    msg = MIMEMultipart()
    msg["Subject"] = f"⚔️ 战锤日报 {day}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(SENDER_EMAIL, EMAIL_AUTH_CODE)
            s.send_message(msg)
        print("✅ 发送成功")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    send()

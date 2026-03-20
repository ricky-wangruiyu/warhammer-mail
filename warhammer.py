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

# 获取战锤美图（稳定源）
def get_img():
    try:
        url = "https://wallhaven.cc/search?q=warhammer%2040k&sorting=random"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.find("img", class_="lazyload")
        return img["data-src"] if img else "https://i.imgur.com/7V7lN.jpg"
    except:
        return "https://i.imgur.com/7V7lN.jpg"

# 战锤趣闻（改用百度战锤贴吧，最稳中文源）
def get_joke():
    try:
        url = "https://tieba.baidu.com/f?kw=战锤40k&ie=utf-8&pn=0"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [t.get_text().strip() for t in soup.find_all("a", class_="j_th_tit")]
        valid = [t for t in titles if len(t) > 8 and len(t) < 100 and "水" not in t]
        return random.choice(valid) if valid else "战锤的幽默需要细细品味..."
    except:
        return "WAAAGH! 兽人觉得一切都是笑话!"

# 战锤人物志（改用中文 Fandom，稳定）
def get_char():
    try:
        url = "https://warhammer40k.fandom.com/zh/wiki/Special:随机页面"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find("h1", class_="page-header__title").get_text(strip=True)
        paragraphs = soup.find_all("p")
        desc = ""
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:
                desc = text[:380]
                break
        return f"【{name}】\n{desc}..." if desc else f"【{name}】\n这是一位在银河中留下印记的战士。"
    except:
        return "人物资料被审判庭没收。"

# 战锤官方消息（改用中文社区，稳定）
def get_news():
    try:
        url = "https://www.warhammer-community.com/zh-hans/news/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
        return "\n• ".join(titles[:3]) if titles else "GW正在筹备新的战役！"
    except:
        return "• 新的星际战士模型即将发布\n• 第十三次黑色远征剧情更新"

# 发送HTML邮件
def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    
    html = f'''
<html>
<body style="background:#111; color:#fff; padding:20px; font-family: sans-serif;">
<div style="max-width:700px; margin:auto; background:#1a1a1a; border-radius:12px; overflow:hidden;">
<img src="{img}" style="width:100%; display:block;" alt="战锤美图">
<div style="padding:25px;">
<h2 style="color:#d4af37; text-align:center; margin:0 0 20px 0;">⚔️ 战锤每日日报 {day}</h2>

<div style="background:#222; padding:15px; margin:15px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin-top:0;">📜 战锤趣闻</h3>
<p style="line-height:1.6;">{get_joke()}</p>
</div>

<div style="background:#222; padding:15px; margin:15px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin-top:0;">⚡ 战锤人物志</h3>
<p style="line-height:1.6;">{get_char()}</p>
</div>

<div style="background:#222; padding:15px; margin:15px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin-top:0;">📰 最新官方消息</h3>
<p style="line-height:1.6;">• {get_news()}</p>
</div>

<p style="text-align:center; color:#777; margin-top:25px; font-size:14px;">为了帝皇 | 全自动发送</p>
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

print("✅ 脚本加载成功！正在准备发送邮件...")
import requests
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import smtplib

# -------------------------- 邮箱会从 GitHub 密钥读取 --------------------------
import os
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_AUTH_CODE = os.getenv("EMAIL_AUTH_CODE")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587

# 获取战锤美图
def get_img():
    try:
        url = "https://wallhaven.cc/search?q=warhammer%2040k&sorting=random"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        img = soup.find("img", class_="lazyload")
        return img["data-src"] if img else "https://i.imgur.com/7V7lN.jpg"
    except:
        return "https://i.imgur.com/7V7lN.jpg"

# 战锤笑话
def get_joke():
    try:
        url = "https://tieba.baidu.com/f?kw=战锤40000"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [t.get_text().strip() for t in soup.find_all("a", class_="j_th_tit")]
        return random.choice([t for t in titles if 10<len(t)<100])
    except:
        return "WAAAGH! 兽人觉得一切都是笑话!"

# 战锤人物
def get_char():
    try:
        url = "https://warhammer40k.fandom.com/zh/wiki/Special:随机"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.find("h1").get_text()
        desc = soup.find("p").get_text()[:350]
        return f"【{name}】\n{desc}..."
    except:
        return "人物资料被审判庭没收。"

# 战锤新闻
def get_news():
    try:
        url = "https://www.warhammer-community.com/zh-hans"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        return "\n• ".join([h.get_text() for h in soup.find_all("h3")][:3])
    except:
        return "GW正在制作新模型。"

# 发送HTML邮件
def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    
    html = f""""""
<html>
<body style="background:#111; color:#fff; padding:20px;">
<div style="max-width:700px; margin:auto; background:#1a1a1a; border-radius:10px;">
<img src="{img}" style="width:100%;">
<div style="padding:25px;">
<h2 style="color:#d4af37; text-align:center;">⚔️ 战锤每日日报 {day}</h2>
<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518;">📜 战锤笑话</h3>
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
""""""

    msg = MIMEMultipart()
    msg["Subject"] = f"⚔️ 战锤日报 {day}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.starttls()
        s.login(SENDER_EMAIL, EMAIL_AUTH_CODE)
        s.send_message(msg)
    print("✅ 发送成功")

if __name__ == "__main__":
    send()

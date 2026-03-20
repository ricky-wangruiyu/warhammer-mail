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

# 稳定爬取用的 User-Agent，防止被网站反爬
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ------------------- 全部使用稳定、可访问的中文站/公开API -------------------
def get_img():
    """稳定随机图片（原 imgapi.cn 已更新参数 fl=meizi，保留美图风格适合日报头图）"""
    try:
        url = "https://imgapi.cn/api.php?fl=meizi"
        # 使用 HEAD + allow_redirects 获取最终图片直链
        response = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
        response.raise_for_status()
        return response.url
    except Exception:
        return "https://i.imgur.com/7V7lN.jpg"  # 备用战锤风图片

def get_joke():
    """稳定战锤日报段子（使用 RollToolsApi 长期维护的中文段子API，无需注册即可用示例密钥）"""
    try:
        url = "https://www.mxnzp.com/api/jokes/list/random"
        params = {
            "app_id": "ixssxqertpltndez",      # 示例公钥（长期可用，建议自己注册替换更稳定）
            "app_secret": "QUF5S2JLZkNqSHdyeVVLczdCNSt1QT09"
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("code") == 1 and data.get("data", {}).get("list"):
            return data["data"]["list"][0].get("content", "").strip()
        return "WAAAGH!"
    except Exception:
        return "WAAAGH!"  # 超稳定备用

def get_char():
    """战锤中文人物志（Fandom 随机页面，极其稳定）"""
    try:
        url = "https://warhammer40k.fandom.com/zh/wiki/Special:Random"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        s = BeautifulSoup(r.text, "html.parser")
        title = s.find("h1").get_text(strip=True)
        p = s.find("p").get_text(strip=True)[:400]
        return f"【{title}】{p}"
    except Exception:
        return "【帝皇】人类的守护者，端坐黄金王座万年之久"

def get_news():
    """战锤官方中文新闻（直接抓取社区首页最新标题，结构稳定）"""
    try:
        url = "https://www.warhammer-community.com/zh-hans"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        s = BeautifulSoup(r.text, "html.parser")
        arr = [x.get_text(strip=True) for x in s.find_all("h3") if x.get_text(strip=True)]
        return " • ".join(arr[:3]) if arr else "新模型 • 新剧情 • 新战役"
    except Exception:
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

<p style="text-align:center; color:#777;">为了帝皇！</p>
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
    print("OK - 战锤日报发送成功！")

if __name__ == "__main__":
    send()

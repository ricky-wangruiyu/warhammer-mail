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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

def get_img():
    """随机美图（或战锤风图片）"""
    try:
        # imgapi.cn 当前参数 fl=meizi 仍有效
        url = "https://imgapi.cn/api.php?fl=meizi"
        resp = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=8)
        resp.raise_for_status()
        if 'image' in resp.headers.get('Content-Type', ''):
            return resp.url
    except:
        pass
    # 多源 fallback
    fallbacks = [
        "https://i.imgur.com/7V7lN.jpg",
        "https://picsum.photos/800/600?random=" + str(random.randint(1,1000))
    ]
    return random.choice(fallbacks)

def get_joke():
    """中文段子 - 使用 aa1.cn 的公开笑话接口（无需key，稳定）"""
    try:
        url = "https://v.api.aa1.cn/api/duanzi/index.php?type=json"
        r = requests.get(url, headers=HEADERS, timeout=8)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and 'text' in data:
            return data['text'].strip()
        elif isinstance(data, list) and data:
            return data[0].strip()
    except:
        pass
    # 极简备用段子池（可自行扩展）
    backups = [
        "为什么绿皮兽人总是喊 WAAAGH!? 因为他们连 'hello' 都不会说。",
        "帝皇：我坐在王座上思考人类的未来…… 智障原体：爸！我要吃薯片！",
        "混沌邪神最怕什么？怕被举报侵权。"
    ]
    return random.choice(backups)

def get_char():
    """战锤人物志 - Fandom 随机中文页（极稳）"""
    try:
        url = "https://warhammer40k.fandom.com/zh/wiki/Special:Random"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title_tag = soup.find("h1", {"id": "firstHeading"}) or soup.find("h1")
        p_tag = soup.find("div", {"class": "mw-parser-output"}).find("p", recursive=False) if soup.find("div", {"class": "mw-parser-output"}) else soup.find("p")
        
        title = title_tag.get_text(strip=True) if title_tag else "未知英雄"
        intro = p_tag.get_text(strip=True)[:380] if p_tag else ""
        return f"【{title}】{intro}"
    except:
        return "【帝皇】人类的守护者，端坐黄金王座万年之久，默默承受着帝国的重担。"

def get_news():
    """战锤新闻 - 改用 warhammer-community 主站最新文章（英文但标题可读，fallback中文描述）"""
    try:
        url = "https://www.warhammer-community.com/news/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        titles = [h.get_text(strip=True) for h in soup.select("article h3") if h.get_text(strip=True)]
        if titles:
            return " • ".join(titles[:3])
    except:
        pass
    # 中文 fallback（可替换成 RSS 或其他聚合）
    return "新杀戮周刊更新 • 最新战团涂装展示 • 40k 平衡数据调整"

def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    
    html = f'''
<html>
<body style="background:#111; color:#fff; padding:20px; font-family: sans-serif;">
<div style="max-width:700px; margin:auto; background:#1a1a1a; border-radius:10px; overflow:hidden;">
<img src="{img}" style="width:100%; display:block;">
<div style="padding:25px;">
<h2 style="color:#d4af37; text-align:center; margin:0 0 20px;">⚔️ 战锤日报 {day}</h2>

<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin-top:0;">📜 今日段子</h3>
<p style="margin:8px 0;">{get_joke()}</p>
</div>

<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin-top:0;">⚡ 人物志</h3>
<p style="margin:8px 0;">{get_char()}</p>
</div>

<div style="background:#222; padding:15px; margin:10px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin-top:0;">📰 官方/社区新闻</h3>
<p style="margin:8px 0;">{get_news()}</p>
</div>

<p style="text-align:center; color:#777; margin:20px 0 0;">为了帝皇！荣耀归于人类！</p>
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

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_AUTH_CODE)
            server.send_message(msg)
        print("战锤日报发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    send()

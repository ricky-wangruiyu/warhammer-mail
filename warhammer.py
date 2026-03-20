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
    try:
        url = "https://imgapi.cn/api.php?fl=meizi"
        resp = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=8)
        if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type', ''):
            return resp.url
    except:
        pass
    fallbacks = [
        "https://picsum.photos/800/600?random=" + str(random.randint(1, 9999)),
        "https://i.imgur.com/7V7lN.jpg"
    ]
    return random.choice(fallbacks)

def get_joke():
    try:
        # vvhan.com 免费中文笑话 API（当前可用，无需 key）
        url = "https://api.vvhan.com/api/joke"
        r = requests.get(url, headers=HEADERS, timeout=8)
        r.raise_for_status()
        joke = r.text.strip()
        if joke and len(joke) > 5:
            return joke
    except:
        pass
    
    # 战锤主题备用段子（增强趣味）
    warhammer_jokes = [
        "为什么绿皮兽人从不怕死？因为他们觉得 'WAAAGH!' 就是重生口号。",
        "帝皇对原体们说：你们要团结！智障原体：爸，那我先去吃薯片团结一下。",
        "混沌邪神开会：今天谁去诱惑人类？恐虐：我去砍！色孽：我去撩！奸奇：我先改规则……纳垢：我先咳嗽传染。",
        "太空狼人最讨厌什么？剃须刀广告。",
        "为什么泰伦虫族吃不饱？因为它们总在 'devour' 但从不 'checkout'。"
    ]
    return random.choice(warhammer_jokes)

def get_char():
    try:
        # 换成英文 Fandom 主站随机（内容仍是战锤，稳定）
        url = "https://warhammer40k.fandom.com/wiki/Special:Random"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        title_tag = soup.find("h1", id="firstHeading") or soup.find("h1")
        content_div = soup.find("div", id="mw-content-text")
        p_tag = content_div.find("p", recursive=False) if content_div else soup.find("p")
        
        title = title_tag.get_text(strip=True) if title_tag else "未知战锤英雄"
        intro = (p_tag.get_text(strip=True)[:380] + "...") if p_tag else "一位在第41千年中奋战的传奇存在。"
        return f"【{title}】{intro}"
    except:
        return "【帝皇】人类的守护者，端坐黄金王座万年之久，默默承受着帝国的重担与痛苦。"

def get_news():
    try:
        # 用官方 zh-hans 主站（当前有新闻订阅提示，可提取相关）
        url = "https://warhammer40000.com/zh-hans"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        # 提取可能的新闻/更新标题（h2/h3 或链接文本）
        titles = []
        for tag in soup.find_all(["h2", "h3", "a"]):
            text = tag.get_text(strip=True)
            if text and len(text) > 5 and "订阅" not in text and "新闻" not in text:
                titles.append(text)
        if titles:
            return " • ".join(titles[:3])
        
        # 备用：从其他社区源提取
        alt_url = "https://info-gamesrustw.com.tw/home/news/%E6%88%B0%E9%8E%8A40K%E5%8D%81%E7%89%88"
        r_alt = requests.get(alt_url, headers=HEADERS, timeout=8)
        soup_alt = BeautifulSoup(r_alt.text, "html.parser")
        alt_titles = [li.get_text(strip=True) for li in soup_alt.find_all("li") if "Posted" in li.get_text()]
        if alt_titles:
            return " • ".join(alt_titles[:3])
    except:
        pass
    
    return "新 Codex 更新 • 最新模型预览 • 平衡调整与战役扩展"

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

<div style="background:#222; padding:15px; margin:15px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin:0 0 10px;">📜 今日段子</h3>
<p style="margin:0;">{get_joke()}</p>
</div>

<div style="background:#222; padding:15px; margin:15px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin:0 0 10px;">⚡ 人物志</h3>
<p style="margin:0;">{get_char()}</p>
</div>

<div style="background:#222; padding:15px; margin:15px 0; border-radius:8px;">
<h3 style="color:#f5c518; margin:0 0 10px;">📰 官方/社区新闻</h3>
<p style="margin:0;">{get_news()}</p>
</div>

<p style="text-align:center; color:#777; margin:25px 0 0;">为了帝皇！荣光归于人类！</p>
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
        print(f"战锤日报 {day} 发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")

if __name__ == "__main__":
    send()

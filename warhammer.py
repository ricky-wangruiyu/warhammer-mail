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
    """战锤40k 相关图片（随机从可靠来源）"""
    warhammer_images = [
        "https://i.imgur.com/0ZxK8.jpg",   # 示例：太空陆战队
        "https://i.imgur.com/mcSOzKa.gif", # 动画示例
        "https://warhammer40k.fandom.com/wiki/Special:FilePath/Ultramarines.jpg",  # Ultramarines
        "https://warhammercommunity.com/wp-content/uploads/2025/xx/some-image.jpg"  # 可替换最新
    ]
    try:
        # 尝试用随机参数从 picsum 或 unsplash-like，但加 warhammer 关键词（实际用固定更稳）
        return random.choice(warhammer_images + [
            f"https://picsum.photos/seed/warhammer40k{random.randint(1,100)}/800/600"
        ])
    except:
        return random.choice(warhammer_images)

def get_joke():
    """随机中文笑话 - 用一言API (hitokoto)，tag=joke 或随机"""
    try:
        url = "https://v1.hitokoto.cn/?c=j"  # c=j 为 joke 类，中文短句笑话
        r = requests.get(url, headers=HEADERS, timeout=6)
        r.raise_for_status()
        data = r.json()
        return data.get("hitokoto", "为了帝皇，干就完了！").strip()
    except:
        # 极少 fallback
        return random.choice([
            "绿皮兽人为什么不怕死？因为他们觉得死了还能再WAAAGH！",
            "帝皇：我守护人类一万年…… 原体：爸，我饿了。",
            "混沌四神开趴体，奸奇负责改规则，纳垢负责带病毒。"
        ])

def get_char():
    """战锤人物志 - Fandom 随机（英文主站稳定）"""
    try:
        url = "https://warhammer40k.fandom.com/wiki/Special:Random"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        title = soup.find("h1", id="firstHeading")
        title_text = title.get_text(strip=True) if title else "未知的帝皇战士"
        
        content = soup.find("div", id="mw-content-text")
        first_p = content.find("p") if content else None
        intro = first_p.get_text(strip=True)[:380] + "..." if first_p else "在第41千年中为人类而战的传奇。"
        
        return f"【{title_text}】{intro}"
    except:
        return "【帝皇】人类的守护者，端坐黄金王座万年之久，默默承受着帝国的重担与无尽痛苦。"

def get_news():
    """官方新闻 - 从 warhammer-community 主页提取最新标题"""
    try:
        url = "https://www.warhammer-community.com/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        titles = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"]) if h.get_text(strip=True) and len(h.get_text(strip=True)) > 8]
        unique_titles = list(dict.fromkeys(titles))  # 去重
        if unique_titles:
            return " • ".join(unique_titles[:3])
    except:
        pass
    return "新军团涂装公布 • Codex 更新预告 • 社区周末展示"

def send():
    img = get_img()
    day = datetime.now().strftime("%Y-%m-%d")
    
    # 绿色调：主文字 #00ff41 (荧光绿)，标题 #39ff14，背景保持暗
    html = f'''
<html>
<body style="background:#0d1117; color:#00ff41; padding:20px; font-family: 'Microsoft YaHei', sans-serif;">
<div style="max-width:720px; margin:auto; background:#161b22; border-radius:12px; overflow:hidden; border:1px solid #238636;">
<img src="{img}" style="width:100%; display:block;" alt="战锤40k 图像">
<div style="padding:30px 25px;">
<h2 style="color:#39ff14; text-align:center; margin:0 0 25px; font-size:2em;">⚔️ 战锤日报 {day}</h2>

<div style="background:#0d1117; padding:18px; margin:15px 0; border-radius:10px; border-left:4px solid #238636;">
<h3 style="color:#00ff9d; margin:0 0 12px;">📜 今日段子</h3>
<p style="margin:0; line-height:1.6;">{get_joke()}</p>
</div>

<div style="background:#0d1117; padding:18px; margin:15px 0; border-radius:10px; border-left:4px solid #238636;">
<h3 style="color:#00ff9d; margin:0 0 12px;">⚡ 人物志</h3>
<p style="margin:0; line-height:1.6;">{get_char()}</p>
</div>

<div style="background:#0d1117; padding:18px; margin:15px 0; border-radius:10px; border-left:4px solid #238636;">
<h3 style="color:#00ff9d; margin:0 0 12px;">📰 官方/社区新闻</h3>
<p style="margin:0; line-height:1.6;">{get_news()}</p>
</div>

<p style="text-align:center; color:#58a700; margin:30px 0 0; font-size:1.1em;">为了帝皇！荣光归于人类！</p>
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
        print(f"战锤日报 {day} 已发送！")
    except Exception as e:
        print(f"发送失败: {e}")

if __name__ == "__main__":
    send()

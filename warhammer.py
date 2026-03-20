import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 邮箱配置
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
AUTH_CODE = os.environ.get("EMAIL_AUTH_CODE")

def send_email():
    try:
        # 邮件内容
        msg = MIMEMultipart()
        msg["Subject"] = "✅ 战锤日报测试成功！"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        html = """
        <h1>为了帝皇！</h1>
        <p>你的自动邮件已经成功部署！明天8点会自动发送战锤美图+笑话+人物志！</p>
        """
        msg.attach(MIMEText(html, "html", "utf-8"))

        # 发送
        with smtplib.SMTP("smtp.qq.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, AUTH_CODE)
            server.send_message(msg)
        
        print("✅ 发送成功！")
    except Exception as e:
        print(f"❌ 错误：{e}")

if __name__ == "__main__":
    send_email()

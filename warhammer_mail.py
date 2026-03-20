import os
os.environ['HTTP_PROXY'] = 'http://proxy-server:port' # 如果需要
os.environ['HTTPS_PROXY'] = 'http://proxy-server:portimport os
import smtplib
import random
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

# 配置
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
EMAIL_FROM = os.environ.get('EMAIL_FROM')
EMAIL_TO = os.environ.get('EMAIL_TO')

def get_warhammer_image():
"""从 Reddit 获取战锤图片"""
url = 'https://www.reddit.com/r/Warhammer/hot.json?limit=25'
headers = {'User-Agent': 'WarhammerMailBot/1.0'}

res = requests.get(url, headers=headers)
data = res.json()

posts = [
p['data'] for p in data['data']['children']
if p['data'].get('url_overridden_by_dest') and
p['data']['url_overridden_by_dest'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
]

if not posts:
raise Exception('未找到图片')

return random.choice(posts)

def download_image(url):
"""下载图片"""
res = requests.get(url)
return res.content

def send_email(post, image_data):
"""发送邮件"""
msg = MIMEMultipart('related')
msg['From'] = EMAIL_FROM
msg['To'] = EMAIL_TO
msg['Subject'] = '🎲 战锤图片'

html = f'''
<html>
<body>
<h2>🎲 {post['title']}</h2>
<p>作者：u/{post['author']}</p>
<p><a href="https://reddit.com{post['permalink']}">查看原帖</a></p>
<img src="cid:warhammer" style="max-width: 600px;" />
<hr/>
<p style="color: #666; font-size: 12px;">每小时自动发送 | Warhammer Mail Bot</p>
</body>
</html>
'''

msg.attach(MIMEText(html, 'html'))

img = MIMEImage(image_data, name='warhammer.jpg')
img.add_header('Content-ID', '<warhammer>')
msg.attach(img)

# 发送
server = smtplib.SMTP_SSL('smtp.qq.com', 465)
server.login(SMTP_USER, SMTP_PASS)
server.send_message(msg)
server.quit()

def main():
print('🎲 获取战锤图片...')
post = get_warhammer_image()

print(f'📷 下载：{post["title"]}')
image_data = download_image(post['url_overridden_by_dest'])

print('📧 发送邮件...')
send_email(post, image_data)

print('✅ 发送成功!')

if __name__ == '__main__':
main()

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")


def send(email):
    msg = MIMEMultipart()
    msg["Subject"] = "News"
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = email
    # msg['Cc'] = contacts

    html_part = MIMEMultipart(_subtype="related")
    # <!-- to comment in html -->
    # Lucida Handwriting
    msg_html = """
    <p>Test</p>
    """

    body = MIMEText(msg_html, _subtype="html")
    html_part.attach(body)

    msg.attach(html_part)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.send_message(msg)
    server.quit()


try:
    send(EMAIL_HOST_USER)
except Exception as e:
    print(e)

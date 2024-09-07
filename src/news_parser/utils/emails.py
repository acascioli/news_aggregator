import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown
from dotenv import load_dotenv
from utils.helper import (
    scrape_content,
    summarize_and_translate,
)

load_dotenv()

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")


def send(email, msg_html):
    msg = MIMEMultipart()
    msg["Subject"] = "News"
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = email
    # msg['Cc'] = contacts

    html_part = MIMEMultipart(_subtype="related")
    # <!-- to comment in html -->
    # Lucida Handwriting
    # msg_html = """
    # <p>Test</p>
    # """

    body = MIMEText(msg_html, _subtype="html")
    html_part.attach(body)

    msg.attach(html_part)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.send_message(msg)
    server.quit()


def compose_email(articles, n_news):
    first_articles = articles[:n_news]
    msg_html = ""
    # Loop through the selected articles and add their content to the message
    for article in first_articles:
        selected_article = article
        result = summarize_and_translate(
            scrape_content(selected_article[1].link)
        )

        # Convert the content from Markdown to HTML
        article_html = markdown.markdown(result.content)

        # Add the title and the converted HTML content to the email message
        msg_html += f"<h2>{selected_article[1].title}</h2>"
        msg_html += f"<h4>From: {selected_article[0]}</h4>"
        msg_html += article_html
        msg_html += "<hr class='solid'>"
    return msg_html

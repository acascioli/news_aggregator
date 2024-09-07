import os

import markdown
from dotenv import load_dotenv
from utils.emails import send
from utils.helper import (
    parse_RSS,
    scrape_content,
    summarize_and_translate,
)

load_dotenv()

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
n_news = 3

# Parse the RSS feed and select the first n_news articles
articles = parse_RSS()
first_articles = articles[:n_news]

# Start building the email message with a greeting
msg_html = ""

# Loop through the selected articles and add their content to the message
for article in first_articles:
    selected_article = article
    result = summarize_and_translate(scrape_content(selected_article[1].link))

    # Convert the content from Markdown to HTML
    article_html = markdown.markdown(result.content)

    # Add the title and the converted HTML content to the email message
    msg_html += f"<h2>{selected_article[1].title}</h2>"
    msg_html += f"<h4>From: {selected_article[0]}</h4>"
    msg_html += article_html
    msg_html += "<hr class='solid'>"

# Attempt to send the email
try:
    send(EMAIL_HOST_USER, msg_html)
except Exception as e:
    print(f"Failed to send email: {e}")

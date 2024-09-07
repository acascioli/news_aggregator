import json
import os

from dotenv import load_dotenv
from utils.emails import compose_email, send
from utils.helper import (
    parse_RSS,
)

load_dotenv()

with open("../../rss_feeds.json") as f:
    RSS_FEEDS = json.load(f)

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
n_news = 2

# Parse the RSS feed and select the first n_news articles
en_articles = parse_RSS(RSS_FEEDS, lan="en")
de_articles = parse_RSS(RSS_FEEDS, lan="de")

# Start building the email message with a greeting
msg_html = "<h1>English</h1>"
msg_html += compose_email(en_articles, n_news)
msg_html += "<h1>German</h1>"
msg_html += compose_email(de_articles, n_news)

# Attempt to send the email
try:
    send(RSS_FEEDS["email"], msg_html)
except Exception as e:
    print(f"Failed to send email: {e}")

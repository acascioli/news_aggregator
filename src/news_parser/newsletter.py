import json

from utils.emails import compose_email, send
from utils.helper import (
    parse_RSS,
)

with open("../../rss_feeds.json") as f:
    RSS_FEEDS = json.load(f)

with open("../../rss_feeds_m.json") as f:
    RSS_FEEDS_m = json.load(f)


def send_newsletter(RSS_FEEDS, de=False, n_news=2):
    # Parse the RSS feed and select the first n_news articles
    en_articles = parse_RSS(RSS_FEEDS, lan="en")
    msg_html = "<h1>English</h1>"
    msg_html += compose_email(en_articles, n_news)
    if de:
        de_articles = parse_RSS(RSS_FEEDS, lan="de")
        msg_html += "<h1>German</h1>"
        msg_html += compose_email(de_articles, n_news)

    # Attempt to send the email
    try:
        send(RSS_FEEDS["email"], msg_html)
    except Exception as e:
        print(f"Failed to send email: {e}")


# me
send_newsletter(RSS_FEEDS, de=True, n_news=2)
#
# m
send_newsletter(RSS_FEEDS_m, de=False, n_news=3)

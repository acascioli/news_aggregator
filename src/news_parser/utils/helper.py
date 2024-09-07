import os

import feedparser
import markdown
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def parse_RSS(RSS_FEEDS, lan=None):
    articles = []
    if lan:
        rss = RSS_FEEDS[lan]
    else:
        rss = RSS_FEEDS["en"] | RSS_FEEDS["de"]
    for source, feed in rss.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    articles = sorted(
        articles, key=lambda x: x[1].published_parsed, reverse=True
    )
    return articles


# Function to scrape the content of the news article from its URL
def scrape_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # This is highly dependent on the website structure; you might need to adjust these selectors.
    paragraphs = soup.find_all("p")
    content = " ".join([para.get_text() for para in paragraphs])

    return content


# Function to interact with OpenAI API
def summarize_and_translate(text):
    # Call the OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a translator and summarizer. ",
            },
            {
                "role": "system",
                "content": "Make sure to be consistent with the markdown style troughout the responses. ",
            },
            {"role": "user", "content": f"Text: {text}"},
            {
                "role": "user",
                "content": "Task 1: Summarize the above text in bullet points in the original language (source_language).",
            },
            {
                "role": "user",
                "content": "Task 2: Translate each bullet point into Italian.",
            },
            {
                "role": "user",
                "content": "Task 3: Identify any idioms or slang used in the original language and list them with an explanation in italian.",
            },
        ],
    )

    # Extract the response
    output = response.choices[0].message
    return output


def process_openai_output(result):
    task_1 = result.content.split("###")[1].split("\n\n")[1].split("\n")
    task_2 = result.content.split("###")[2].split("\n\n")[1].split("\n")
    task_3 = result.content.split("###")[3].split("\n\n")[1].split("\n")
    task_1 = [markdown.markdown(item) for item in task_1]
    task_2 = [markdown.markdown(item) for item in task_2]
    task_3 = [markdown.markdown(item) for item in task_3]
    return task_1, task_2, task_3

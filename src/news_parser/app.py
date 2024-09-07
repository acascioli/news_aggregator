import os

import feedparser
import markdown
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


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


app = Flask(__name__)

RSS_FEEDS = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "BBC News - World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC News - Health": "https://feeds.bbci.co.uk/news/health/rss.xml",
    "BBC News - Tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "BBC News - Science and Environment": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml?edition=uk",
    "Zeit": "https://newsfeed.zeit.de/index",
}


def parse_RSS():
    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    articles = sorted(
        articles, key=lambda x: x[1].published_parsed, reverse=True
    )
    return articles


@app.route("/")
def index():
    articles = parse_RSS()
    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template(
        "index.html",
        articles=paginated_articles,
        page=page,
        total_pages=total_articles // per_page + 1,
    )


@app.route("/search")
def search():
    query = request.args.get("q")

    articles = []
    for source, feed in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

    results = [
        article
        for article in articles
        if query.lower() in article[1].title.lower()
    ]

    return render_template("search_results.html", articles=results, query=query)


@app.route("/article/<article_title>")
def article(article_title):
    try:
        articles = parse_RSS()
        article_title = "".join(e for e in article_title if e.isalnum())
        current_title = "".join(e for e in articles[1][1].title if e.isalnum())
        for article in articles:
            current_title = "".join(e for e in article[1].title if e.isalnum())
            if current_title == article_title:
                selected_article = article[1]
                result = summarize_and_translate(
                    scrape_content(selected_article.link)
                )
                if result.content:
                    task_1 = (
                        result.content.split("###")[1]
                        .split("\n\n")[1]
                        .split("\n")
                    )
                    task_2 = (
                        result.content.split("###")[2]
                        .split("\n\n")[1]
                        .split("\n")
                    )
                    task_3 = (
                        result.content.split("###")[3]
                        .split("\n\n")[1]
                        .split("\n")
                    )
                    print(task_1)
                    task_1 = [markdown.markdown(item) for item in task_1]
                    print(task_1)
                    task_2 = [markdown.markdown(item) for item in task_2]
                    task_3 = [markdown.markdown(item) for item in task_3]
                    # print(task_3)
                    # if task_3[0][0] == 1:
                    #     task_3 = [item.split(". ")[-1] for item in task_3]
                    # else:
                    #     task_3 = [item.replace(" - ", ": ") for item in task_3]
                    return render_template(
                        "article.html",
                        title=selected_article.title,
                        link=selected_article.link,
                        summary=task_1,
                        translation=task_2,
                        idioms=task_3,
                    )
    except Exception as e:
        print(e)
        return "Something went wrong!"


if __name__ == "__main__":
    app.run(debug=True)

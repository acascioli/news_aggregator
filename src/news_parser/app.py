from flask import Flask, render_template, request
from utils.helper import (
    parse_RSS,
    process_openai_output,
    scrape_content,
    summarize_and_translate,
)

app = Flask(__name__)


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

    articles = parse_RSS()

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
        for article in articles:
            current_title = "".join(e for e in article[1].title if e.isalnum())
            if current_title == article_title:
                selected_article = article[1]
                result = summarize_and_translate(
                    scrape_content(selected_article.link)
                )
                if result.content:
                    task_1, task_2, task_3 = process_openai_output(result)
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

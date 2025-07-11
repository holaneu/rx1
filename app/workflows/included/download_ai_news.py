from app.workflows.core import workflow, Workflow
from app.tools.included import download_news_newsapi, save_to_file, json_db_add_entry, user_data_files_path
import json

@workflow()
def download_ai_news():
    """Downloads and saves recent AI-related news articles."""
    try:
        wf = Workflow()
        news = download_news_newsapi(query="openai OR mistral OR claude", lastDays=5, domains="techcrunch.com,thenextweb.com")
        if not news or not news.get("articles"):
            raise Exception("no news found")
        articles = news.get("articles", [])
        
        file_path = user_data_files_path("news.md")
        db_file_path = user_data_files_path("databases/news.json")
        for article in articles:
            article_readable = json.dumps(article, indent=2, ensure_ascii=False)
            json_db_add_entry(db_filepath=db_file_path, collection="entries", entry=article, add_createdat=False)
            save_to_file(file_path, article_readable + "\n\n-----\n", prepend=True)
        return wf.success_response(
            data=articles,
            msgBody=f"Downloaded {len(articles)} articles and saved to {file_path} and also to the database file {db_file_path}."
        )
    except Exception as e:
        return wf.error_response(error=e)

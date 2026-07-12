# Daily News Email Automation 📬📰

Automatically fetches the latest news from multiple RSS feeds, summarizes each article using OpenAI's GPT model, and sends a daily HTML email digest to one or multiple recipients. Fully implemented in Python.  

This project replicates the workflow from an n8n automation tutorial, but entirely in Python.

---

## Features ✅

- Fetch news from multiple RSS feeds (CNN, NYTimes, BBC, TechCrunch, etc.)
- Summarize each article using OpenAI GPT
- Format summaries into a clean HTML email
- Send emails via SMTP (Gmail)
- Schedule to run daily at a fixed time
- Supports sending to multiple recipients or BCC for privacy
- Jupyter Notebook compatible for testing

---

## Demo Screenshot

*(Optional: Add a screenshot of your email or script output here)*

---

## Requirements 🛠️

- Python 3.8+
- [OpenAI API key](https://platform.openai.com/)
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833?hl=en) enabled for SMTP

### Python Packages

```bash
pip install feedparser openai schedule python-dotenv

Setup ⚡

Clone the repository:

git clone https://github.com/yourusername/daily-news-email.git
cd daily-news-email


Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
EMAIL_TO=recipient1@gmail.com,recipient2@gmail.com


(Optional) Add or update RSS feeds in app.py:

RSS_FEEDS = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://techcrunch.com/feed/"
]

Usage 🚀
1. Run Once (for testing / Jupyter)
daily_news_job()


This will fetch news, summarize, and send a single email.

2. Run Daily (Production)
import schedule
import time

schedule.every().day.at("08:00").do(daily_news_job)

while True:
    schedule.run_pending()
    time.sleep(30)


The script will automatically send emails every day at 08:00.

Best Practices 💡

Limit articles per feed to reduce OpenAI costs:

def fetch_rss_feeds(feed_urls, limit=5):
    ...


Deduplicate articles to avoid sending the same news twice.

Use BCC if sending to multiple recipients to maintain privacy.

Consider batching or using an email service (SendGrid, SES) for large lists.

Folder Structure 📁
daily-news-email/
│
├─ app.py             # Main Python script
├─ feeds.txt          # Optional: list of RSS feed URLs
├─ .env               # Environment variables (not committed)
├─ README.md          # Project description
└─ requirements.txt   # Python dependencies

License 📝

MIT License. See LICENSE
 for details.

Acknowledgements 🙏

Inspired by n8n automation tutorials for daily news digest.

OpenAI GPT for summarizing articles.

Feedparser and Python smtplib for news fetching and email sending.

Contact 📬

Your Name – your.email@example.com

GitHub: https://github.com/yourusername


---

I can also create a **more visual version** with:

- **Screenshots of the email digest**
- **Sample RSS output**
- **Badges for Python version, license, and OpenAI API usage**

This makes the GitHub repo **look professional and attractive**.  

Do you want me to make that enhanced version?

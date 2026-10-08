from datetime import datetime

from flask import Flask, render_template

from news_digest import get_top_stories

app = Flask(__name__)


@app.route("/")
def home():
    stories = get_top_stories()
    updated = datetime.now().strftime("%H:%M")
    return render_template("index.html", stories=stories, updated=updated)
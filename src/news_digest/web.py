from flask import Flask
from markupsafe import escape

from news_digest import get_top_stories

app = Flask(__name__)


@app.route("/")
def home():
    html = """
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <h1>Good morning Nick</h1>
    <ol>
    """
    for story in get_top_stories():
        html += f"""
        <li>
            <a href="{escape(story['link'])}">{escape(story['title'])}</a>
            <br><small>{story['coverage']} outlets</small>
        </li>
        """
    html += "</ol>"
    return html
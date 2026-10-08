import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template

from news_digest import get_sections
from news_digest.summarize import add_summaries

REFRESH_MINUTES = 15

app = Flask(__name__)

# The latest results, filled in by the background thread below.
latest = {"sections": [], "updated": None}


def refresh_forever():
    while True:
        try:
            sections = get_sections()
            add_summaries(sections)
            latest["sections"] = sections
            latest["updated"] = datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M")
        except Exception as error:
            print("Refresh failed:", error)
        time.sleep(REFRESH_MINUTES * 60)


threading.Thread(target=refresh_forever, daemon=True).start()


@app.route("/")
def home():
    return render_template("index.html", sections=latest["sections"], updated=latest["updated"])

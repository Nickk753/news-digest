import os
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
            print("Refreshing news...", flush=True)
            sections = get_sections()
            add_summaries(sections)
            latest["sections"] = sections
            latest["updated"] = datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M")
            print("Refresh done.", flush=True)
            time.sleep(REFRESH_MINUTES * 60)
        except Exception as error:
            print("Refresh failed:", repr(error), flush=True)
            time.sleep(60)  # try again in a minute instead of waiting 15


# Which process started the background refresher. gunicorn can load this file
# in one process and then copy it into another to serve visitors; a thread does
# not survive that copy, so each serving process starts its own on first visit.
refresher_pid = None
refresher_lock = threading.Lock()


def start_refresher():
    global refresher_pid
    with refresher_lock:
        if refresher_pid != os.getpid():
            refresher_pid = os.getpid()
            threading.Thread(target=refresh_forever, daemon=True).start()


@app.route("/")
def home():
    start_refresher()
    return render_template("index.html", sections=latest["sections"], updated=latest["updated"])

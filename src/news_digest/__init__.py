import html
import socket
from concurrent.futures import ThreadPoolExecutor

import feedparser

# Give up on a slow news site after 10 seconds instead of waiting forever.
socket.setdefaulttimeout(10)

SECTIONS = {
    "World": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.theguardian.com/world/rss",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://rss.dw.com/rdf/rss-en-all",
        "https://feeds.skynews.com/feeds/rss/world.xml",
    ],
    "Business": [
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://www.theguardian.com/business/rss",
    ],
    "Romania Business": [
        "https://www.zf.ro/rss",
        "https://www.profit.ro/rss",
        "https://www.economica.net/rss",
        "https://www.biziday.ro/feed/",
        "https://hotnews.ro/feed/",
    ],
    "NYC": [
        "https://rss.nytimes.com/services/xml/rss/nyt/NYRegion.xml",
        "https://gothamist.com/feed",
        "https://www.amny.com/feed/",
        "https://nypost.com/metro/feed/",
    ],
    "Tech": [
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "https://www.wired.com/feed/rss",
    ],
    "Startups": [
        "https://techcrunch.com/category/startups/feed/",
        "https://techcrunch.com/category/venture/feed/",
        "https://news.crunchbase.com/feed/",
        "https://hnrss.org/frontpage",
    ],
    "AI": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "https://venturebeat.com/category/ai/feed/",
    ],
}

STORIES_PER_SECTION = 5

STOPWORDS = {"after", "over", "with", "from", "into", "about", "says", "said",
             "will", "than", "that", "this", "what", "when", "have", "were",
             "their", "they", "more", "years", "three", "your", "how", "here",
             "pentru", "este", "care", "acest", "aceasta", "această", "acum",
             "fost", "unui", "unei", "sunt", "după", "dintre", "foarte", "mult",
             "spre", "doar", "până", "când", "cele", "celor", "despre"}


def keywords(title):
    result = set()
    for word in title.lower().split():
        word = word.strip(".,:;?!'\"‘’“”")
        if len(word) > 3 and word not in STOPWORDS:
            result.add(word)
    return result


def same_story(a, b):
    return len(a["words"] & b["words"]) >= 2


def fetch_feed(section, url):
    feed = feedparser.parse(url)
    source = feed.feed.get("title", url)
    stories = []
    for entry in feed.entries[:10]:
        title = html.unescape(entry.get("title", ""))
        stories.append({
            "section": section,
            "source": source,
            "title": title,
            "link": entry.get("link", url),
            "description": entry.get("summary", "")[:500],
            "words": keywords(title),
        })
    return stories


def get_sections():
    jobs = []
    for section, urls in SECTIONS.items():
        for url in urls:
            jobs.append((section, url))

    # Download all feeds at the same time instead of one by one.
    with ThreadPoolExecutor(max_workers=16) as pool:
        results = pool.map(lambda job: fetch_feed(*job), jobs)
    stories = [story for feed_stories in results for story in feed_stories]

    # Importance = how many different outlets (in any section) cover the story.
    for story in stories:
        outlets = set()
        for other in stories:
            if same_story(story, other):
                outlets.add(other["source"])
        story["coverage"] = len(outlets)

    stories.sort(key=lambda s: s["coverage"], reverse=True)

    sections = []
    for name in SECTIONS:
        top = []
        for story in stories:
            if story["section"] != name:
                continue
            if any(same_story(story, picked) for picked in top):
                continue
            top.append(story)
            if len(top) == STORIES_PER_SECTION:
                break
        sections.append({"name": name, "stories": top})
    return sections


def main():
    print("Good morning Nick, here is your news")
    for section in get_sections():
        print()
        print("==", section["name"], "==")
        for story in section["stories"]:
            print(story["coverage"], "outlets -", story["title"])

import feedparser

def main():
    print("Good morning Nick, here is your news")
    feeds = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://www.theguardian.com/world/rss",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://feeds.washingtonpost.com/rss/world",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://feeds.skynews.com/feeds/rss/world.xml",
        "https://rss.dw.com/rdf/rss-en-all",
        "https://www.biziday.ro/feed/",
        "https://hotnews.ro/feed/",
        "https://www.antena3.ro/rss",
    ]
    for url in feeds:
        feed = feedparser.parse(url)
        print()
        print(feed.feed.get("title", url))
        for entry in feed.entries[:10]:
            print("-", entry.title)
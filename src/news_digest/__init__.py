import feedparser

def main():
    print("Good morning Nick, here is your news")
    feeds = [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.npr.org/1001/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    ]
    for url in feeds:
        feed = feedparser.parse(url)
        print()
        print(feed.feed.title)
        for entry in feed.entries[:10]:
            print("-", entry.title)
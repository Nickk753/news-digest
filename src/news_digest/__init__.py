import feedparser 

def main():
    print("Good morning Nick, here is your news")
    feed = feedparser.parse("https://feeds.bbci.co.uk/news/world/rss.xml")
    for entry in feed.entries[:5]:
        print("-", entry.title)
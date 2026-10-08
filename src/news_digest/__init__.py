import feedparser

STOPWORDS = {"after", "over", "with", "from", "into", "about", "says", "said",
             "will", "than", "that", "this", "what", "when", "have", "were",
             "their", "they", "more", "years", "three",
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


def shared(title_a, title_b):
    return keywords(title_a) & keywords(title_b)


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
    stories = []
    for url in feeds:
        feed = feedparser.parse(url)
        source = feed.feed.get("title", url)
        for entry in feed.entries[:10]:
            stories.append({"source": source, "title": entry.title})

    for story in stories:
        outlets = set()
        for other in stories:
            if len(shared(story["title"], other["title"])) >= 2:
                outlets.add(other["source"])
        story["coverage"] = len(outlets)

    stories.sort(key=lambda s: s["coverage"], reverse=True)

    top = []
    for story in stories:
        is_duplicate = False
        for picked in top:
            if len(shared(story["title"], picked["title"])) >= 2:
                is_duplicate = True
        if not is_duplicate:
            top.append(story)

    for story in top[:10]:
        print(story["coverage"], "outlets -", story["title"])
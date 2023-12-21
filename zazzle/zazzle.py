from quart import Quart, request
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from pprint import pprint

app = Quart(__name__)

# Async function to extract and clean text from HTML
async def extract_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text().split("\n")[0]

@app.route("/search")
async def read_items():
    query = request.args.get('q', default='crypto', type=str)
    length = request.args.get('length', default=-1, type=int)
    rss_url = f"https://feed.zazzle.com/rss?qs={quote_plus(query)}"
    feed = feedparser.parse(rss_url)
    output = []
    if length != -1:
        entries = entries[:length]

    for i, entry in enumerate(feed.entries):
        title = entry.title
        image_url = entry.media_content[0]['url']  # Assuming the first media_content is the large image
        description_html = entry.description
        short_description = await extract_text(description_html)
        url = entry.id
        price = entry.price
        formatted_entry = f"{i+1}. {title}, {short_description} ![gift]({image_url}) {url} {price}"
        output.append(formatted_entry)

    return '\n'.join(output)

@app.route('/', methods=['GET'])
def ready():
    return "ready"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10009)

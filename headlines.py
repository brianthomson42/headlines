# headlines.py
import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib.request

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'ft': 'https://www.ft.com/?edition=international&format=rss'}

DEFAULTS = {'publication': 'bbc',
            'city': 'London, UK'}

@app.route('/')
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    return render_template('home.html', articles=articles, weather=weather)


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])

    return feed['entries']


def get_weather(query):

    # Open Weather Map
    OWM_API_KEY = 'ba2f5defab3f680647625999aacf6ee1'

    api_url = 'http://api.openweathermap.org/data/2.5/weather?q={{}}&units=metric&appid={}' \
              .format(OWM_API_KEY)
    query = urllib.request.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description':parsed['weather'][0]['description'],
                   'temperature':parsed['main']['temp'],
                   'city':parsed['name'],
                   'country': parsed['sys']['country']}
    return weather


if __name__ == "__main__":
    app.run(port=5000, debug=True)

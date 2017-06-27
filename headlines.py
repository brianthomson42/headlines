# headlines.py
import datetime
import feedparser
from flask import Flask
from flask import make_response
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
            'city': 'London, UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'}

@app.route('/')
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = request.cookies.get('publication')
        if not publication:
            publication = DEFAULTS['publication']

    articles = get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    # get customized currency based on user input or default
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)

    response = make_response(render_template('home.html',
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie('publication', publication, expires=expires)
    response.set_cookie('city', city, expires=expires)
    response.set_cookie('currency_from', currency_from, expires=expires)
    response.set_cookie('currency_to', currency_to, expires=expires)

    return response


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


def get_rate(frm, to):

    # Open Exchange Rate
    OER_API_KEY = '24169dc1e2964d679d20ed18853b0a9e'
    api_url = 'https://openexchangerates.org//api/latest.json?app_id={}' \
              .format(OER_API_KEY)
    all_currency = urllib.request.urlopen(api_url).read()

    parsed = json.loads(all_currency).get('rates')
    from_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())

    return (to_rate/from_rate, parsed.keys())


if __name__ == "__main__":
    app.run(port=5000, debug=True)

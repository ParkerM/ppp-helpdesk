import random
import re
from time import strptime
from calendar import timegm
from urllib import quote
from util import timesince

from util import hook, http

from lxml import html


def text_content(html_string):
    return html.fromstring(html_string).text_content()

def format_time(time):
    since = '%s ago' % timesince.timesince(
        timegm(
            strptime(time, '%a %b %d %H:%M:%S +0000 %Y')
        )
    )

    return since

def randomcase_text_except_url(text):
    url = re.compile('(https://[^\s]+)', re.IGNORECASE)

    return ''.join(t if url.match(t) else randomcase_text(t) for t in url.split(text))

def randomcase_text(text):
    return "".join( random.choice([k.upper(), k ]) for k in text )

def rainbow_text(text):
    colors = [
      "00", "01", "02", "03", "04", "05", "06", "07",
      "07", "09", "10", "11", "12", "13", "14", "15"
    ]

    return "".join( "\x03%s%s" % (random.choice(colors) , k) for k in text )


@hook.api_key('twitter')
@hook.command
def donald(inp, reply=None, api_key=None):
    if not isinstance(api_key, dict) or any(key not in api_key for key in
                                            ('consumer', 'consumer_secret', 'access', 'access_secret')):
        return "error: api keys not set"

    inp = "realDonaldTrump"

    getting_id = False
    doing_search = False
    index_specified = False

    if re.match(r'^\d+$', inp):
        getting_id = True
        request_url = "https://api.twitter.com/1.1/statuses/show.json?id=%s" % inp
    else:
        try:
            inp, index = re.split('\s+', inp, 1)
            index = int(index)
            index_specified = True
        except ValueError:
            index = 0
        if index < 0:
            index = 0
        if index >= 20:
            return 'error: only supports up to the 20th tweet'

        if re.match(r'^#', inp):
            doing_search = True
            request_url = "https://api.twitter.com/1.1/search/tweets.json?q=%s" % quote(inp)
        else:
            request_url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s" % inp

    try:
        tweet = http.get_json(request_url, oauth=True, oauth_keys=api_key, tweet_mode="extended")
    except http.HTTPError, e:
        errors = {400: 'bad request (ratelimited?)',
                  401: 'unauthorized',
                  403: 'forbidden',
                  404: 'invalid user/id',
                  500: 'twitter is broken',
                  502: 'twitter is down ("getting upgraded")',
                  503: 'twitter is overloaded (lol, RoR)',
                  410: 'twitter shut off api v1.'}
        if e.code == 404:
            return 'error: invalid ' + ['username', 'tweet id'][getting_id]
        if e.code in errors:
            return 'error: ' + errors[e.code]
        return 'error: unknown %s' % e.code

    if doing_search:
        try:
            tweet = tweet["statuses"]
            if not index_specified:
                index = random.randint(0, len(tweet) - 1)
        except KeyError:
            return 'error: no results'

    if not getting_id:
        try:
            tweet = tweet[index]
        except IndexError:
            return 'error: not that many tweets found'

    if 'retweeted_status' in tweet:
        rt = tweet["retweeted_status"]
        rt_text = text_content(rt["full_text"]).replace('\n', ' ')
        text = "RT @%s %s" % (rt["user"]["screen_name"], rt_text)
    else:
        text = text_content(tweet["full_text"]).replace('\n', ' ')
    screen_name = tweet["user"]["screen_name"]
    time = tweet["created_at"]

    reply_text = format_time(time)
    reply_text += ' '

    text = randomcase_text_except_url(text)

    text_chunks = [ text[i : i + 10] for i in range(0, len(text), 10)]

    for chunk in text_chunks:
        formatted_chunk = rainbow_text(chunk)

        if len(reply_text) + len(formatted_chunk) > 420:
            reply(reply_text)
            reply_text = ''

        reply_text += formatted_chunk

    if len(reply_text) > 0:
        reply(reply_text)

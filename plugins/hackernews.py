from __future__ import unicode_literals

from lxml import html

from util import http, hook


def text_content(html_string):
    return html.fromstring(html_string).text_content()

@hook.regex(r'(?i)https://(?:www\.)?news\.ycombinator\.com\S*id=(\d+)')
def hackernews(match):
    base_api = 'https://hacker-news.firebaseio.com/v0/item/'
    entry = http.get_json(base_api + match.group(1) + ".json")

    if entry['type'] == "story":
        entry['title'] = text_content(entry['title'])
        return "{title} by {by} with {score} points and {descendants} comments ({url})".format(**entry)

    if entry['type'] == "comment":
        entry['text'] = text_content(entry['text'].replace('<p>', ' // '))
        return '"{text}" -- {by}'.format(**entry)

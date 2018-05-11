from __future__ import unicode_literals

import random
import re
from time import strptime, strftime
from urllib import quote
import unicodedata

from util import http, hook

import twitter

CURRENCY_SYMBOLS = {
    'USD': u'$',
    'CAD': u'$',
    'ETH': u"\u039E",
    'BTC': u"\u20BF",
    'RUB': u"\u20BD",
    'JPY': u"\u00A5",
    'CNY': u"\u00A5",
    'EUR': u"\u20AC",
    'AZN': u"\u20BC",
    'ILS': u"\u20AA",
    'THB': u"\u0E3F",
    'KRW': u"\u20A9",
    'KPW': u"\u20A9",
    'VND': u"\u20AB",
    'SEK': u'kr',
    'ZAR': u'R'
}

def get_coin_price(coin, priceBasis):
    coin = coin.upper()
    priceBasis = priceBasis.upper()

    response = http.get_json(
        'https://min-api.cryptocompare.com/data/pricemultifull',
        query_params={
            'fsyms': coin,
            'tsyms': priceBasis,
            'extraparams': 'ppp-helpdesk'
        }
    )

    if 'RAW' in response:
        return response['RAW'][coin][priceBasis]

    return None

@hook.command(autohelp=False)
def crypto(inp):
    coin, currency = (inp.split(' ', 1) +  [None] * 2)[:2]

    coin = (coin or 'BTC').upper()
    currency = (currency or 'USD').upper()

    response = get_coin_price(coin, currency)

    if response is None:
      return "Conversion of {coin:s} to {currency:s} not found".format(coin=coin, currency=currency)

    coin = response['FROMSYMBOL']
    currency = response['TOSYMBOL']
    last = response['PRICE']
    high = response['HIGH24HOUR']
    low = response['LOW24HOUR']

    if currency in CURRENCY_SYMBOLS:
      symbol = CURRENCY_SYMBOLS[currency]
    else:
      symbol = '%s ' % currency

    return (
           "{coin:s}/{currency:s}: \x0307{symbol:s}{last:.2f}\x0f - "
           "High: \x0307{symbol:s}{high:.2f}\x0f - "
           "Low: \x0307{symbol:s}{low:.2f}\x0f"
        ).format(
            coin=coin,
            currency=currency,
            symbol=symbol,
            last=last,
            high=high,
            low=low
        )


@hook.api_key('twitter')
@hook.command('btc', autohelp=False)
@hook.command('bitcoin', autohelp=False)
@hook.command('bit', autohelp=False)
@hook.command(autohelp=False)
def buttcoin(inp, api_key=None):
    ".bitcoin -- gets current exchange rate for bitcoins"

    currency = inp or 'USD'
    currency = currency.upper()

    buttcoin = twitter.twitter("buttcoin", api_key)
    buttcoin = unicodedata.normalize('NFKD', buttcoin)
    buttcoin = buttcoin.encode('ascii', 'replace')

    return "{message:s}  ---  {buttcoin:s}".format(
            buttcoin=buttcoin,
            message=crypto('BTC %s' % currency)
        )

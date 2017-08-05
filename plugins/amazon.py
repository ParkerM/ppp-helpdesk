import bottlenose
from lxml import etree
from util import hook, http

@hook.api_key('amazon')
@hook.command('amazon')
@hook.command('a')
def amazon(inp, api_key=None):
    if api_key is None or 'access_key' not in api_key or 'secret_key' not in api_key or 'associate_tag' not in api_key:
       return "missing API key"

    amazon = bottlenose.Amazon(api_key['access_key'], api_key['secret_key'], api_key['associate_tag'], Region='US')

    response = amazon.ItemSearch(Keywords=inp, SearchIndex='All', ResponseGroup='ItemAttributes,Offers')

    NS = '{http://webservices.amazon.com/AWSECommerceService/2013-08-01}'

    root = etree.fromstring(response)

    error = root.find('.//' + NS + 'Error')
    if error is not None:
        errorMsg = error.find(NS + 'Message').text
        return errorMsg

    item = root.find('.//' + NS + 'Item')  # First item in results
    asin = item.find(NS + 'ASIN').text

    itemAttributes = item.find(NS + 'ItemAttributes')
    title = itemAttributes.find(NS + 'Title').text

    try:
      new_price = item.find(NS + 'OfferSummary/' + NS + 'LowestNewPrice/' + NS + 'FormattedPrice').text
    except:
      new_price = None

    if new_price:
      return "\x02%s\x02 - New \x02%s\x02 - https://amzn.com/%s?tag=%s" % (title, new_price, asin, api_key['ASSOCIATE_TAG'])
    else:
      return "\x02%s\x02 - https://amzn.com/%s?tag=%s" % (title, asin, api_key['ASSOCIATE_TAG'])

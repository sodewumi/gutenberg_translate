from amazonproduct import API
from lxml import etree
import os


config = {
    'access_key': os.environ['ACCESS_KEY'],
    'secret_key': os.environ['SECRET_KEY'],
    'associate_tag': os.environ['ASSOCIATE_TAG'],
    'locale': 'us'
}

api = API(cfg=config)

items = api.item_search('Books', Publisher="O'Reilly")

for book in items:
    print '%s: "%s"' % (book.ItemAttributes.Author,
                        book.ItemAttributes.Title)
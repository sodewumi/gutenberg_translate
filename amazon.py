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
res = api.item_lookup("0486284735", SearchIndex='Books', IdType='ISBN')
# print "%s" % (res.ItemAttributes.Title)

for item in res.Items.Item:
    print '%s (%s) in group' % (
    item.ItemAttributes.Title, item.ASIN)



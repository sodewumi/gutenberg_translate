from amazonproduct import API
from lxml import etree
import os
from flask import flash, Flask, redirect, render_template, request, session, jsonify
from model import Book, User, Genre, Chapter, Paragraph, UserBook, Translation, connect_to_db, db
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
# import amazon
import jinja2
import re




config = {
    'access_key': os.environ['ACCESS_KEY'],
    'secret_key': os.environ['SECRET_KEY'],
    'associate_tag': os.environ['ASSOCIATE_TAG'],
    'locale': 'us'
}

api = API(cfg=config)

isbn_list = db.session.query(Book.isbn).all()
print isbn_list
# res = api.item_lookup("0486284735", "0553213458", "091406116X", "0393967972",
    # "0141441674", "0140449264", SearchIndex='Books', IdType='ISBN')
# print "%s" % (res.ItemAttributes.Title)

def book_lookup(isbn):
    res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN')
    for item in res.Items.Item:
        print '%s (%s) image=%s' % (
        item.ItemAttributes.Title, item.ASIN, item.SmallImage.URL)

# print res
print "hi"
# for item in res.Items.Item:
#     print '%s (%s) in group' % (
#     item.ItemAttributes.Title, item.ASIN)


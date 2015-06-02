# standard library modules
import re
import os
# third-party modules
import jinja2
import requests
from server import app
from amazonproduct import API
from flask import flash, Flask, redirect, render_template, request, session, jsonify, url_for
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
from lxml import etree
# my modules
from model import Book, Chapter, connect_to_db, db, Group, Paragraph



def foo():
    config = {
        'access_key': os.environ['ACCESS_KEY'],
        'secret_key': os.environ['SECRET_KEY'],
        'associate_tag': os.environ['ASSOCIATE_TAG'],
        'locale': 'us'
    }

    api = API(cfg=config)

    # isbn_list = db.session.query(Book.isbn).all()
    isbn_list = ["0486284735", "0553213458"]

    for isbn in isbn_list:
        res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN',
            ResponseGroup="Images, EditorialReview")
        print dir(res)
        for item in res.Items.Item:
            img_url = str(item.LargeImage.URL)
            print img_url
        product_review = res.Items.Item.EditorialReviews.EditorialReview.Content
        import pdb
        # pdb.set_trace()
        # print product_review.encode('utf-8')
        print etree.tostring(product_review, pretty_print=True)
        # print u' '.join((product_review)).encode('utf-8').strip()
        # print ','.join(str(v) for v in value_list)


if __name__ == "__main__":
    print "Hi ma"
    connect_to_db(app)
    foo()
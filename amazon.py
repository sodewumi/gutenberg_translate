# standard library modules
import re
import os
# third-party modules
import jinja2
import requests
from server import app
from amazonproduct import API
from flask import flash, Flask, redirect, render_template, request, session, jsonify, url_for
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
from lxml import etree
# my modules
from model import Book, Chapter, connect_to_db, db, Group, Paragraph

def book_ratings():

    book_ratings_response =requests.get("https://www.googleapis.com/books/v1/volumes?q='0486284735'+isbn:keyes&key="+ os.environ['GB_KEY'])
    print book_ratings_response
    import pbd
    book_ratings_response = book_ratings_response.json()
    book_ratings_list = book_ratings_response['books']

    for rating_dict in book_ratings_list:
        book_id = book_isbn_dict[rating_dict["isbn"]]
        book_obj = Book.query.get(book_id)
        book_obj.rating = rating_dict['average_rating']

        db.session.commit()

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

    book_ratings()
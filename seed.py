import requests
import server
from server import app
from flask import Flask
import os
from model import Book, connect_to_db, db
# standard library modules
import re
import os
# third-party modules
import jinja2
import requests
from amazonproduct import API
from flask import flash, Flask, redirect, render_template, request, session, jsonify, url_for
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
from lxml import etree
# my modules
from model import Book, Chapter, connect_to_db, db, Group, Paragraph, Translation, User, BookGroup, UserGroup

def amazon_setup():
    """
        Connects to amazon web services API
    """

    config = {
        'access_key': os.environ['ACCESS_KEY'],
        'secret_key': os.environ['SECRET_KEY'],
        'associate_tag': os.environ['ASSOCIATE_TAG'],
        'locale': 'us'
    }

    api = API(cfg=config)

    book_obj_list = Book.query.all()
    isbn_list = []
    for book_obj in book_obj_list:
        isbn_list.append(book_obj.isbn)

    return book_lookup(isbn_list, api)

def book_lookup(isbn_list, api):
    api_dict = {}

    for isbn in isbn_list:
        res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN',
            ResponseGroup="Images, Reviews")
        for item in res.Items.Item:
            img_url = str(item.LargeImage.URL)
            api_dict.setdefault(isbn, img_url)
    return aws_api_to_db(api_dict)

def aws_api_to_db(api_dict):

    for isbn in api_dict:
        book_obj = Book.query.filter_by(isbn=isbn).one()
        print book_obj, "a book obj *********************"
        book_obj.cover = api_dict[isbn]
    db.session.commit()

def book_ratings():
    book_isbn_tuple = db.session.query(Book.isbn, Book.book_id).all()
    book_isbn_dict = dict(book_isbn_tuple)
    isbn_str = ""
    for book_isbn in book_isbn_dict:
        isbn_str = isbn_str +","+ book_isbn
    isbn_str = isbn_str[1:]

    book_ratings_response =requests.get("https://www.goodreads.com/book/review_counts.json?format=json&isbns="+isbn_str+"&key="+ os.environ['GR_KEY'])
    book_ratings_response = book_ratings_response.json()
    book_ratings_list = book_ratings_response['books']

    for rating_dict in book_ratings_list:
        book_id = book_isbn_dict[rating_dict["isbn"]]
        book_obj = Book.query.get(book_id)
        book_obj.rating = rating_dict['average_rating']

        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    DebugToolbarExtension(app)
    # book_database()
    # book_ratings()
    # amazon_setup()
    app.run(debug=True)
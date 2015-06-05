import requests
from server import app
from flask import Flask
import os
from model import Book, connect_to_db, db
# standard library modules
# third-party modules
from amazonproduct import API
from flask import flash, Flask, redirect, render_template, request, session, jsonify, url_for
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
from lxml import etree
# my modules
from model import Book, Chapter, connect_to_db, db, Group, Paragraph, Translation, User, BookGroup, UserGroup


config = {
    'access_key': os.environ['ACCESS_KEY'],
    'secret_key': os.environ['SECRET_KEY'],
    'associate_tag': os.environ['ASSOCIATE_TAG'],
    'locale': 'us'
}

api = API(cfg=config)

def book_lookup(isbn):
    res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN',
        ResponseGroup="Images, Reviews")
    img_url = str(res.Items.Item[0].LargeImage.URL)
    return img_url

def set_book_cover():
    book_obj_list = Book.query.all()

    for book_obj in book_obj_list:
        book_obj.cover = book_lookup(book_obj.isbn)

    db.session.commit()

def book_ratings():
    book_isbn_tuple = db.session.query(Book.isbn, Book.book_id).all()
    book_isbn_dict = dict(book_isbn_tuple)
    isbn_str = ""
    for book_isbn in book_isbn_dict:
        isbn_str = isbn_str +","+ book_isbn
    isbn_str = isbn_str[1:]

    uri_root = "https://www.goodreads.com/book/review_counts.json?format=json&isbns="
    book_ratings_response =requests.get(uri_root+isbn_str+"&key="+ os.environ['GR_KEY'])
    book_ratings_response = book_ratings_response.json()
    book_ratings_list = book_ratings_response['books']

    for rating_dict in book_ratings_list:
        book_id = book_isbn_dict[rating_dict["isbn"]]
        book_obj = Book.query.get(book_id)
        book_obj.rating = rating_dict['average_rating']

        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    set_book_cover()
    book_ratings()
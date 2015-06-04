# standard library modules
import re
import os
# third-party modules
import jinja2
import requests
from server import app
import urllib2
from amazonproduct import API
from flask import flash, Flask, redirect, render_template, request, session, jsonify, url_for
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
from lxml import etree
# my modules
from model import Book, Chapter, connect_to_db, db, Group, Paragraph

import pprint
import sys
from apiclient.discovery import build


service = build('books', 'v1', developerKey='AIzaSyA8SlCjyJQnXa62wL2dZPk2hTZmC86X5tY')

request = service.volumes().list(source='public',
                                    orderBy='relevance',
                                    printType='books',
                                    langRestrict='en',
                                    isbn='0486284735',
                                    startIndex=0,
                                    maxResults=10,
                                    fields="items(volumeInfo(description,pageCount,categories,publishedDate,imageLinks/thumbnail,title,previewLink,industryIdentifiers,subtitle,authors,ratingsCount,mainCategory,averageRating))")

response = request.execute()


ratingsCount = book_dict.get('volumeInfo', {}).get('ratingsCount')
averageRatings = book_dict.get('volumeInfo', {}).get('averageRating')


# def book_ratings():
#     payload={"q":"+isbn:0486284735&key=AIzaSyA8SlCjyJQnXa62wL2dZPk2hTZmC86X5tY"}

#     book_ratings_response =requests.get("https://www.googleapis.com/books/v1/volumes", params=payload)
#     print book_ratings_response
#     # import pbd
#     book_ratings_response = book_ratings_response.json()
#     book_ratings_list = book_ratings_response['books']

#     for rating_dict in book_ratings_list:
#         book_id = book_isbn_dict[rating_dict["isbn"]]
#         book_obj = Book.query.get(book_id)
#         book_obj.rating = rating_dict['average_rating']

#         # db.session.commit()

# def foo():
#     config = {
#         'access_key': os.environ['ACCESS_KEY'],
#         'secret_key': os.environ['SECRET_KEY'],
#         'associate_tag': os.environ['ASSOCIATE_TAG'],
#         'locale': 'us'
#     }

#     api = API(cfg=config)

#     # isbn_list = db.session.query(Book.isbn).all()
#     isbn_list = ["0486284735", "0553213458"]

#     for isbn in isbn_list:
#         res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN',
#             ResponseGroup="Images, EditorialReview")
#         print dir(res)
#         for item in res.Items.Item:
#             img_url = str(item.LargeImage.URL)
#             print img_url
#         product_review = res.Items.Item.EditorialReviews.EditorialReview.Content
#         import pdb
#         # pdb.set_trace()
#         # print product_review.encode('utf-8')
#         print etree.tostring(product_review, pretty_print=True)
#         # print u' '.join((product_review)).encode('utf-8').strip()
#         # print ','.join(str(v) for v in value_list)


if __name__ == "__main__":
    pass
    # book_ratings()
import requests
import server
from server import app
from flask import Flask
import os
from model import Book, connect_to_db, db

# def book_ratings():
#     book_isbn_tuple = db.session.query(Book.book_id, Book.isbn).all()
#     book_isbn_dict = dict(book_isbn_tuple)
#     isbn_str = ""
#     for book_id, book_isbn in book_isbn_dict.values():
#         isbn_str = isbn_str +","+ book_isbn
#     isbn_str = isbn_str[1:]

#     return isbn_str

# print book_ratings()


response =requests.get("https://www.goodreads.com/book/review_counts.json?format=json&isbns=0486284735,0439708184&key="+ os.environ['GR_KEY'])
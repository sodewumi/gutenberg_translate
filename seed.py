# standard library modules
import requests
from server import app
import os
# third-party modules
from amazonproduct import API
from lxml import etree
# my modules
from model import Book, connect_to_db, db


config = {
    'access_key': os.environ['ACCESS_KEY'],
    'secret_key': os.environ['SECRET_KEY'],
    'associate_tag': os.environ['ASSOCIATE_TAG'],
    'locale': 'us'
}

api = API(cfg=config)


def seed_books():
    book_txt = open("books.txt")
    for line in book_txt:
        line = line.split("|")
        for i, info in enumerate(line):
            line[i] = info.decode("utf-8").strip()
        db.session.add(Book(gutenberg_extraction_num=line[0], name=line[1], author=line[2], isbn=line[3]))
    db.session.commit()

def book_lookup(isbn):
    isbn = isbn.strip()
    res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN',
        ResponseGroup="Images")
    img_url = str(res.Items.Item[0].LargeImage.URL)
    return img_url

def set_book_cover():
    book_obj_list = Book.query.all()
    # print book_obj_list
    # book_obj_list[1].cover = book_lookup("0553213458")
    for book_obj in book_obj_list:
        book_obj.cover = book_lookup(book_obj.isbn)

    db.session.commit()

def book_ratings():
    book_isbn_tuple = db.session.query(Book.isbn, Book.book_id).all()
    book_isbn_dict = {key.strip(): value for (key, value) in book_isbn_tuple}

    isbn_str = ""
    for book_isbn in book_isbn_dict:
        book_isbn = book_isbn.strip()
        isbn_str = isbn_str +","+ book_isbn
    isbn_str = isbn_str[1:]

    uri_root = "https://www.goodreads.com/book/review_counts.json?format=json&isbns="
    book_ratings_response =requests.get(uri_root+isbn_str+"&key="+ os.environ['GR_KEY'])
    book_ratings_response = book_ratings_response.json()
    book_ratings_list = book_ratings_response['books']

    for rating_dict in book_ratings_list:
        try:
            book_id = book_isbn_dict[str(rating_dict['isbn'])]
            book_obj = Book.query.get(book_id)
            book_obj.rating = rating_dict['average_rating']

            db.session.commit()
        except:
            print None


if __name__ == "__main__":
    connect_to_db(app)
    # seed_books()
    # set_book_cover()
    book_ratings()
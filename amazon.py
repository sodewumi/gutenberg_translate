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


app = Flask(__name__)
app.secret_key = 'will hook to .gitignore soon'
app.jinja_env .undefined = jinja2.StrictUndefined



config = {
    'access_key': os.environ['ACCESS_KEY'],
    'secret_key': os.environ['SECRET_KEY'],
    'associate_tag': os.environ['ASSOCIATE_TAG'],
    'locale': 'us'
}

api = API(cfg=config)

isbn_list = db.session.query(Book).all()


# res = api.item_lookup("0486284735", "0553213458", "091406116X", "0393967972",
#     "0141441674", "0140449264", SearchIndex='Books', IdType='ISBN')
# print "%s" % (res.ItemAttributes.Title)

# print res
# for item in res.Items.Item:
#     print '%s (%s) in group' % (
#     item.ItemAttributes.Title, item.ASIN)

if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    DebugToolbarExtension(app)
    # book_database()
    app.run(debug=True)



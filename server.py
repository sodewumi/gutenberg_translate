from flask import flash, Flask, redirect, render_template, request, session
import jinja2
from model import Book, User, Genre, Chapter, Paragraph, Translation, connect_to_db, db

app = Flask(__name__)
app.secret_key = 'will hook to .gitignore soon'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def display_homepage():
    """Return homepage."""
    return render_template("homepage.html")

@app.route("/profile")
def display_profile():
    """Return a user's profile page."""
    return render_template("profile.html")
 
@app.route("/explore")
def display_explore_books():
    """Return a full list of books from project gutenberg."""
    return render_template("explore_books.html")

@app.route("/description")
def display_book_description():
    """Return a description of the book."""

    return render_template("book_description.html")

@app.route("/translate")
def display_translation_page():
    """Return a translation page."""
    return render_template("translation_page.html", book = open_file())

def open_file():
    book_string = open("./books/pride_and_prejudice.txt").read()
    head_deliminator = "*** START OF THIS PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***"
    head_deliminator_idx = book_string.index(head_deliminator)
    tail_deliminator_idx = book_string.index("*** END OF THIS PROJECT GUTENBERG")

    book_string = book_string[head_deliminator_idx + len(head_deliminator) : tail_deliminator_idx]

    book_chapters = book_string.split("Chapter")

    for i in range(len(book_chapters)):
        book_chapters[i] = book_chapters[i].split('\n\n')

    return book_chapters





if __name__ == "__main__":
    app.run(debug=True)
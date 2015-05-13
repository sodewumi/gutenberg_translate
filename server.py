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

@app.route("/translate", methods=["GET"])
def display_translation_page():
    """Displays the first chapter of the book. Value currently starts at to zero"""
    book = open_file()
    number_of_chapters = len(book)
    

    return render_template("translation_page.html",
        book = book, number_of_chapters =number_of_chapters)

@app.route("/translate", methods=["POST"])
def display_chosen_chapter():
    """Displays the chapter the user wants to translate"""
    pass

def open_file():
    """
        Opens a file from my computer and converts it to a
         list of chapters and sublist of paragrpahs"""

    book_string = open("./books/pride_and_prejudice.txt").read()
    # doesn't get rid of text produced by anonymous volunteers
    head_deliminator = "*** START OF THIS PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***"
    head_deliminator_idx = book_string.index(head_deliminator)
    tail_deliminator_idx = book_string.index("*** END OF THIS PROJECT GUTENBERG")

    book_string = book_string[head_deliminator_idx + len(head_deliminator) : tail_deliminator_idx]
    book = {}
    book_chapters = book_string.split("Chapter")

    for i in range(len(book_chapters)):
        book_chapters[i] = book_chapters[i].split('\n\n')

    for c, chapters in enumerate(book_chapters):
        book.setdefault(c, chapters)

    return book_chapters

def book_database():
    """ Pushs newly created books into a database"""
    book = open_file()
    # haven't reseeded database to make sure chapters start at 1 and not 0)
    for c, chapters in enumerate(book, 1):
        db.session.add(Chapter(chapter_number=c, book_id=1))
        for paragrpahs in chapters:
            db.session.add(Paragraph(untranslated_paragraph=paragrpahs))

    db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
    connect_to_db(app)
    # book_database()

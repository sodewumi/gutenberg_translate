from flask import flash, Flask, redirect, render_template, request, session, jsonify
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
    """
        Displays the a chapter of the book. 
        When page first loads, chapter starts at 0.
    """
    number_of_chapters = db.session.query(Chapter).count()

    chapter_chosen = request.args.get("chapter_selection")

    # checks if the selection form has been submitted
    # connect to chapter_number
    if chapter_chosen:
        display_chapter = db.session.query(Paragraph).filter_by(chapter_id = chapter_chosen)
    else:
        display_chapter = db.session.query(Paragraph).filter_by(chapter_id = 0)

    return render_template("translation_page.html",
        number_of_chapters = number_of_chapters, 
        display_chapter = display_chapter, chapter_chosen=chapter_chosen)

@app.route("/save_text", methods=["POST"])
def save_translation_text():
    """
        Saves the text translation in the database
    """  
    translated_text = request.form['translated_text']
    paragraph_id = request.form["p_id"]
    
    print paragraph_id, '***********************'
    # db.session.query(Translation).filter_by(book_id=1, paragraph_id=)

    return jsonify({"status": "OK", "translated_text": translated_text})


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

    book_chapters = book_string.split("Chapter")

    for i in range(len(book_chapters)):
        book_chapters[i] = book_chapters[i].split('\n\n')

    return book_chapters

def book_database():
    """ Pushs newly created books into a database"""

    book = open_file()

    # I start at 0, because I want to copyright information to show
    for c, chapters in enumerate(book, 0):
        # change book_id in the future
        db.session.add(Chapter(chapter_number=c, book_id=1))
        for paragrpahs in chapters:
            db.session.add(Paragraph(untranslated_paragraph=paragrpahs, chapter_id=c))

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    # book_database()
    app.run(debug=True)


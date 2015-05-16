from flask import flash, Flask, redirect, render_template, request, session, jsonify
from model import Book, User, Genre, Chapter, Paragraph, Translation, connect_to_db, db
from flask_debugtoolbar import DebugToolbarExtension
import jinja2


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
    t_paragraphs_in_chapter_list = []
    # checks if the selection form has been submitted
    # connect to chapter_number
    if chapter_chosen:
        paragraphs_in_chapter_list = db.session.query(Paragraph).filter_by(chapter_id = chapter_chosen).all()

        print paragraphs_in_chapter_list, "*********"

        for paragraph in paragraphs_in_chapter_list:
            translated_paragraph = Translation.query.filter_by(
                user_id=1, 
                language="French", 
                paragraph_id=paragraph.paragraph_id).first()
            # print translated_paragraph, "*********"
            t_paragraphs_in_chapter_list.append(translated_paragraph)

        
        # print display_translations, "*************"
    else:
        paragraphs_in_chapter_list = db.session.query(Paragraph).filter_by(chapter_id = 0)
        t_paragraphs_in_chapter_list = db.session.query(Translation).filter_by(translation_id=1, language="French")
    return render_template("translation_page.html",
        number_of_chapters = number_of_chapters, 
        display_chapter = paragraphs_in_chapter_list, chapter_chosen=chapter_chosen, 
        display_translations=t_paragraphs_in_chapter_list)

@app.route("/save_text", methods=["POST"])
def save_translation_text():
    """
        Saves the text translation in the database
    """  
    translated_text = request.form['translated_text']
    paragraph_id_input = request.form["p_id"]
    
    # user id is 1
    # language is French
    #  still need to add this
    find_translated_text_in_db = db.session.query(Translation).filter_by(
        paragraph_id=paragraph_id_input, language="French").first()
    print find_translated_text_in_db, "db trans text ******************"

    if find_translated_text_in_db:
        updated_translation = db.session.query(Translation).filter_by(
            paragraph_id = paragraph_id_input).update({"translated_paragraph":translated_text, "user_id":1})
        db.session.commit()
        # UPDATE Translation SET translated_paragraph=translated_text, user_id=1 WHERE paragraph_id = paragraph_id_input
    else:
        print "it's saved to the database"
        new_translation_for_db = Translation(language="French",
            translated_paragraph=translated_text, paragraph_id=paragraph_id_input,
            user_id=1)
        db.session.add(new_translation_for_db)
        db.session.commit()
        # INSERT INTO Translation(language, translated_paragraph, paragraph_id, user_id)
        # VALUES ("French", translated_text, paragraph_id_input, 1)


    return jsonify({"status": "OK", "translated_text": translated_text, "order": paragraph_id_input})


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
    app.debug = True
    DebugToolbarExtension(app)
    # book_database()
    app.run(debug=True)


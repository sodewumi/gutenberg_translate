from flask import flash, Flask, redirect, render_template, request, session, jsonify
from model import Book, User, Genre, Chapter, Paragraph, Translation, connect_to_db, db
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
import jinja2
import re


app = Flask(__name__)
app.secret_key = 'will hook to .gitignore soon'
app.jinja_env .undefined = jinja2.StrictUndefined

@app.route("/", methods=["GET"])
def display_homepage():
    """Returns homepage."""
    return render_template("homepage.html")

@app.route("/login", methods=["POST"])
def login_user():
    """Logs in user"""
    username = request.form["username_input"]
    print username, "*********"
    password = request.form["password_input"]
    print password, "**********"
    user_object = User.query.filter(User.username == username).first()

    if user_object:
        if user_object.password == password:
            session["login"] = [username, user_object.user_id]
            flash("You logged in successfully")
            return render_template("explore_books.html")
        else:
            flash("Incorrect password. Try again.")
            return redirect("/")
    else:
        flash("""This username doesn't exist. Click Register if you would
            like to create an account.""")
        return redirect("/")


@app.route("/register", methods=["POST"])
def register_user():
    """Registers User"""

    register_email = request.form["email_input"]
    register_password = request.form["password_input"]
    register_username = request.form["username_input"]

    if User.query.filter(User.email == register_email).first():
        flash("A person has already registered with the email")
        return redirect("/")
    elif User.query.filter(User.username == register_username).first():
        flash("A person has already taken that username")
        return redirect("/")
    else:
        new_user = User(email=register_email, password=register_password,
                        username=register_username)
        db.session.add(new_user)
        db.session.commit()
        flash("Thanks for creating an account with Gutenberg Translate!")
        return render_template("explore_books.html")

    return render_template("registration_form.html")
    return render_template("/explore")

@app.route("/profile")
def display_profile():
    """Return a user's profile page."""
    
    return render_template("profile.html")
 
@app.route("/explore")
def display_explore_books():
    """Return a full list of books from project gutenberg."""

    all_book_objs = Book.query.all()

    return render_template("explore_books.html", all_book_objs=all_book_objs)


@app.route("/description/<int:gutenberg_extraction_number>", methods=["GET"])
def display_book_description(gutenberg_extraction_number):
    """Return a description of the book."""
    book_obj = Book.query.filter_by(gutenberg_extraction_num = gutenberg_extraction_number).one()
    return render_template("book_description.html", display_book = book_obj,
        gutenberg_extraction_number=gutenberg_extraction_number)


@app.route("/translate/<int:gutenberg_extraction_number>", methods=["GET"])
def submit_add_translation_form(gutenberg_extraction_number):
    """ 
        Takes information from add_book_form and adds it to the database.
        Renders /translate  
    """
    # add logic if they enter information improperly
    # collaborator_list = request.form["translation_collaborators_input"]
    # print collaborator_list, "*****************"
    #  don't know if I should keep here
    # translation_language = request.form["translation_language_input"]

    # gets book from project gutenberg
    book_text = open_file(gutenberg_extraction_number)

    # splits the book to a list of chapters
    chapter_list = split_chapters(book_text)
    print chapter_list
    # push chapter_list into a database
    book_database(chapter_list)

    book_to_translate= Book.query.filter_by(gutenberg_extraction_num = gutenberg_extraction_number)
    number_of_chapters = db.session.query(Chapter).count()
    paragraphs_in_chapter_list = db.session.query(Paragraph).filter_by(chapter_id = 1)

    return render_template("translation_page.html", number_of_chapters=number_of_chapters,
        display_chapter=paragraphs_in_chapter_list, chapter_chosen=None, display_translations=None)

def render_book():
    pass


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

        for paragraph in paragraphs_in_chapter_list:
            translated_paragraph = Translation.query.filter_by(
                user_id=1, 
                language="French", 
                paragraph_id=paragraph.paragraph_id).first()

            t_paragraphs_in_chapter_list.append(translated_paragraph)
    else:
        paragraphs_in_chapter_list = db.session.query(Paragraph).filter_by(chapter_id = 1)
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


def open_file(file_id):
    # move to book class
    """
        Opens a file from project gutenberg 
    """
    print "opened"
    return load_etext(file_id)

def split_chapters(full_text):


    book = strip_headers(full_text)

    chapter_list = re.split(ur'\n\bchapter\b \w+\.?', book, flags=re.IGNORECASE)
    paragraphs_in_chapter_list = []

    for i in range(len(chapter_list)):
        paragraphs_in_chapter_list.append(chapter_list[i].split('\n\n'))

    return paragraphs_in_chapter_list

def book_database(parsed_book):
    # move to book class
    """ Pushs newly created books into a database"""

    # I start at 0, because I want to copyright information to show
    for c, chapters in enumerate(parsed_book, 1):
        # change book_id in the future
        db.session.add(Chapter(chapter_number=c, book_id=1))
        for paragraphs in chapters:
            db.session.add(Paragraph(untranslated_paragraph=paragraphs, chapter_id=c))

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    DebugToolbarExtension(app)
    # book_database()
    app.run(debug=True)


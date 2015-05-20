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
            print session["login"], "***********"
            flash("You logged in successfully")
            return redirect("/explore")
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
        if register_email and register_password and register_username:
            new_user = User(email=register_email, password=register_password,
                            username=register_username)
            db.session.add(new_user)
            db.session.commit()
            flash("Thanks for creating an account with Gutenberg Translate!")
            return redirect("/explore")
        else:
            flash("Please fill out all fields")
            return redirect("/")

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
        Takes information from add_book_form and adds it to the database whenever
        a book has not yet to the book database.
        Renders /translate  
    """
    # logic for collaborators to be added later after MVP
    collaborator_list = request.args.get("translation_collaborators_input")
    translation_language = request.args.get("translation_language_input")

    book_id_tupple = db.session.query(Book.book_id).filter(
        Book.gutenberg_extraction_num == gutenberg_extraction_number).first()

    chapter_obj_list = db.session.query(Chapter).filter(
        Chapter.book_id == book_id_tupple[0]).all()
    
    # if the book text hasn't been put inside the database yet, run the process_book
    # function to get split, and push book into the database.
    if not chapter_obj_list:
        process_book(gutenberg_extraction_number)

    number_of_chapters = len(chapter_obj_list) + 1
    # a user can only traslate one book in one language at a time
    Userbook_obj = UserBook(user_id=session[u'login'][1],
        book_id=book_id_tupple[0], language=translation_language)

    paragraph_obj_list = render_untranslated_chapter(book_id_tupple[0], 0)
    db.session.add(Userbook_obj)
    db.session.commit()

    return render_template("translation_page.html", number_of_chapters=number_of_chapters,
        display_chapter=paragraph_obj_list, chapter_chosen=None,
        display_translations=None, book_id=book_id_tupple[0])

def render_untranslated_chapter(book_id, chosen_chap):
    """Shows the translated page chosen"""
    book_obj = Book.query.get(book_id)
    paragraph_obj_list = book_obj.chapters[chosen_chap].paragraphs

    return paragraph_obj_list


@app.route("/translate/<int:book_id>/render", methods=["GET"])
def display_translation_page(book_id):
    """
        Displays a chapter of the book. 
        When page first loads, chapter starts at 1.
    """
    chosen_chapter = int(request.args.get("chapter_selection"))

    # get the chapters associated with the book
    book_obj = Book.query.get(book_id)
    chapter_obj_list = book_obj.chapters
    user_id = session[u'login'][1]
    number_of_chapters = len(chapter_obj_list) + 1

    t_paragraphs_in_chapter_list = []

    # checks if the selection form has been submitted
    # connect to chapter_number
    if chosen_chapter:
        paragraph_obj_list = chapter_obj_list[chosen_chapter].paragraphs
        userbook_obj = db.session.query(UserBook).filter(
            UserBook.user_id==user_id,
            UserBook.book_id==book_obj.book_id).one()

        for paragraph in paragraph_obj_list:
            translated_paragraph = Translation.query.filter_by(
                userbook_id=userbook_obj.userbook_id, 
                language=userbook_obj.language, 
                paragraph_id=paragraph.paragraph_id).first()
            t_paragraphs_in_chapter_list.append(translated_paragraph)
    else:
        paragraph_obj_list = chapter_obj_list[0].paragraphs.all()
        userbook_obj = db.session.query(UserBook).filter(
            UserBook.user_id==user_id,
            UserBook.book_id==book_obj.book_id).one()

        for paragraph in paragraph_obj_list:
            translated_paragraph = Translation.query.filter_by(
                userbook_id=userbook_obj.userbook_id, 
                language=userbook_obj.language, 
                paragraph_id=paragraph.paragraph_id).first()
            t_paragraphs_in_chapter_list.append(translated_paragraph)

    return render_template("translation_page.html",
        number_of_chapters = number_of_chapters, 
        display_chapter = paragraph_obj_list, chapter_chosen=chosen_chapter, 
        display_translations=t_paragraphs_in_chapter_list, book_id=book_id)

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
    """
        Opens a file from project gutenberg 
    """
    print "opened"
    return load_etext(file_id)

def split_chapters(full_text):
    """
        Removes header and footer from project gutenberg book. 
        Makes a list of chapters, where each chapter is a sublist of paragraphs
    """
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

def process_book(guten_extract_num):
    """
        Loads a book from project gutenberg, splits the chapters, and pushes it to
        a database.
    """
    # gets book from project gutenberg
    book_text = open_file(guten_extract_num)

    # splits the book to a list of chapters
    chapter_list = split_chapters(book_text)

    # push chapter_list into a database
    book_database(chapter_list)


if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    DebugToolbarExtension(app)
    # book_database()
    app.run(debug=True)


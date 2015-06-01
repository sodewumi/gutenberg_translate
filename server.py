# standard library modules
import re
import os
# third-party modules
import jinja2
import requests
from amazonproduct import API
from flask import flash, Flask, redirect, render_template, request, session, jsonify, url_for
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from flask_debugtoolbar import DebugToolbarExtension
from lxml import etree
# my modules
from model import Book, Chapter, connect_to_db, db, Group, Paragraph, Translation, User, BookGroup, UserGroup


app = Flask(__name__)
app.secret_key = 'will hook to .gitignore soon'
app.jinja_env .undefined = jinja2.StrictUndefined
socketio = SocketIO(app)

@app.route("/", methods=["GET"])
def display_homepage():
    """Returns homepage."""
    return render_template("homepage.html")

@app.route("/login", methods=["POST"])
def login_user():
    """Logs in user. Adds user_id and username to session"""
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

@app.route("/logout")
def logout_user():
    """Remove login information from session"""
    session.pop(u'login')
    flash("You've successfully logged out. Goodbye.")
    return redirect("/")
    
@app.route("/profile/<int:user_id>")
def display_profile(user_id):
    """Return a user's profile page."""
    
    user_obj = User.query.filter(User.user_id == user_id).one()

    group_obj_list = user_obj.groups
    bookgroup_obj_dict = {}

    for i, group in enumerate(group_obj_list):
        bookgroup_obj_dict[i] = [group.group_name]
        bookgroup_obj_dict[i] = bookgroup_obj_dict[i].extend(group.bookgroups)
    
    return render_template("profile.html", bookgroup_obj_dict=bookgroup_obj_dict)
 
@app.route("/explore")
def display_explore_books():
    """Return a full list of books from project gutenberg."""

    all_book_objs = Book.query.all()
    # aws_api_to_db(amazon_setup(all_book_objs))
    return render_template("explore_books.html", all_book_objs=all_book_objs)


@app.route("/description/<int:gutenberg_extraction_number>", methods=["GET"])
def display_book_description(gutenberg_extraction_number):
    """
        *Return a description of the book: reviews, image, and excerpt
        *Displays other groups that the user is in that is translating that
            particular book. This includes: group names, usernames, and
            translation language
    """
    # 
    book_obj = Book.query.filter_by(gutenberg_extraction_num =
        gutenberg_extraction_number).one()

    # add to user class
    current_user = User.query.filter(User.user_id == session[u'login'][1]).one()
    
    # find group translation language
    current_groups_list = current_user.groups

    group_language_dict = {}
    for group in current_groups_list:
        language = group.bookgroups[0].language
        bookgroup_id = group.bookgroups[0].bookgroup_id

        group_language_dict.setdefault(group.group_id, [language])

        if bookgroup_id not in group_language_dict[group.group_id]:
            group_language_dict[group.group_id].append(bookgroup_id)

    # print good_reads(), "********************"
    return render_template("book_description.html", display_book = book_obj,
        gutenberg_extraction_number=gutenberg_extraction_number, 
        current_user=current_user, group_language_dict=group_language_dict)


@app.route("/check_user", methods=["POST"])
def check_user_exists():
    """
        Checks if user is in database. Returns True if user exists & False otherwise
    """
    username_input = request.form['collab_names']
    username_input = username_input.lower().strip()

    user_exists = User.query.filter_by(username = username_input).first()

    if user_exists:
        return jsonify({"collab_username": username_input})
    else:
        return jsonify({"collab_username": None})


def good_reads():
    uri = "https://www.goodreads.com/book/isbn?format=json&isbn=0486284735"
    response =requests.get(uri)
    return response.json()


@app.route("/translate/<int:gutenberg_extraction_number>", methods=["GET"])
def submit_add_translation_form(gutenberg_extraction_number):
    """ 
        Takes information from add_book_form and adds it to the database whenever
        a book has not yet to the book database.
        Book taken from book_explore.html
    """
    # add to usergroup
    # logic for collaborators to be added later after MVP
    group_name = request.args.get("group_name_input")
    translation_language = request.args.get("translation_language_input")

    collaborator_list = request.args.getlist("usernames")

    collaborators_user_objs = User.query.filter(
        User.username.in_(collaborator_list)
        ).all()

    # change to book obj
    book_id_tuple = db.session.query(Book.book_id).filter(
        Book.gutenberg_extraction_num == gutenberg_extraction_number).first()
    book_id = book_id_tuple[0]

    chapter_obj_list = db.session.query(Chapter).filter(
        Chapter.book_id == book_id).all()
    
    # if the book text hasn't been put inside the database yet, run the process_book
    # function to get split, and push book into the database.
    if not chapter_obj_list:
        process_book_chapters(gutenberg_extraction_number)
        chapter_obj_list = db.session.query(Chapter).filter(
            Chapter.book_id == book_id_tuple[0]).all()

    # create group
    new_group_obj = Group(group_name = group_name)

    db.session.add(new_group_obj)
    # create usergroup
    db.session.commit()
    new_usergroup_obj = UserGroup(user_id=session["login"][1],
                        group_id=new_group_obj.group_id)
    db.session.add(new_usergroup_obj)

    for a_collaborator in collaborators_user_objs:
        new_usergroup_obj = UserGroup(user_id=a_collaborator.user_id,
                            group_id=new_group_obj.group_id)
        db.session.add(new_usergroup_obj)
    db.session.commit()
    # create bookgroup
    new_bookgroup_obj = BookGroup(group_id=new_group_obj.group_id,
                        book_id=book_id, language=translation_language)
    db.session.add(new_bookgroup_obj)
    db.session.commit()

    return redirect(url_for(".display_translation_page", bookgroup_id_input = new_bookgroup_obj.bookgroup_id))


def render_untranslated_chapter(book_id, chosen_chap):
    """Shows the translated page chosen"""
    book_obj = Book.query.get(book_id)
    paragraph_obj_list = book_obj.chapters[chosen_chap].paragraphs

    return paragraph_obj_list

@app.route("/rendertranslations", methods=["GET"])
def display_translation_page():
    """
        Displays a chapter of the book. 
        When page first loads, chapter starts at 1.
    """
    # all arguments come from the book_group
    # bookgroup_obj = BookGroup.query.get(bookgroup_id)
    bookgroup_id = int(request.args["bookgroup_id_input"])
    bookgroup_obj = BookGroup.query.get(bookgroup_id)
    bookgroup_id = bookgroup_obj.bookgroup_id
    bookgroup_language = bookgroup_obj.language
    bookgroup_groupid = bookgroup_obj.group_id
    bookgroup_bookid = bookgroup_obj.book_id

    chosen_chapter = request.args.get("chapter_selection")
    if chosen_chapter:
        chosen_chapter = int(chosen_chapter)

    # get the chapters associated with the book
    book_obj = Book.query.get(bookgroup_bookid)
    chapter_obj_list = book_obj.chapters
    number_of_chapters = len(chapter_obj_list)

    # checks if the selection form has been submitted
    # connect to chapter_number
    if chosen_chapter:
        paragraph_obj_list = chapter_obj_list[chosen_chapter].paragraphs
        translated_paragraphs_list = find_trans_paragraphs( 
                paragraph_obj_list, bookgroup_id)
    else:
        paragraph_obj_list = chapter_obj_list[1].paragraphs
        translated_paragraphs_list = find_trans_paragraphs(
                paragraph_obj_list, bookgroup_id)
    return render_template("translation_page.html",
        number_of_chapters = number_of_chapters, 
        display_chapter = paragraph_obj_list, chapter_chosen=chosen_chapter, 
        display_translations=translated_paragraphs_list, book_id=bookgroup_bookid,
        language=bookgroup_language, book_obj=book_obj, group_id=bookgroup_groupid,
        bookgroup_id=bookgroup_id)

@socketio.on('connect', namespace='/rendertranslations')
def test_connect():
    emit('my response', {'connection_status': 'Connected'})

@socketio.on('joined', namespace='/rendertranslations')
def on_join(data):
    """
        Sent by clients when they enter a room.
    """
    username = session["login"][0]
    bookgroup_id = data["bookgroup_id"]
    chapter_number = data["chapter_number"]
    room = str(bookgroup_id) + "." + str(chapter_number)
    join_room(room)

    emit('joined_status', {'msg': username + " has entered room " + str(room)}, room=room)

@socketio.on('leave', namespace='/rendertranslations')
def on_leave(data):
    """
        Sent by clients when the leave a room
    """
    username = session["login"][0]
    bookgroup_id = data["bookgroup_id"]
    chapter_number = data["chapter_number"]
    room = str(bookgroup_id) + "." + str(chapter_number)
    leave_room(room)

    emit('joined_status', {'msg': username + " has left room " + str(room)}, room=room)


@socketio.on('value changed', namespace='/rendertranslations')
def translated_text_rt(message):
    """
        Sent by clients while they are translating a paragraph
    """

    emit('update text', message, broadcast=True)

@socketio.on('canceled translation', namespace='/rendertranslations')
def revert_text(message):
    """ Takes the last saved translation and renders it on the page if the clients
        cancels their translation
    """

    emit('render reverted text', message, broadcast=True)

@socketio.on('submit text', namespace='/rendertranslations')
def new_text(message):

    emit('render submitted text', message, broadcast=True)

def find_trans_paragraphs(paragraph_obj_list, bookgroup_id):
    """Finds the translated paragraphs per group"""

    paragraph_ids = [p.paragraph_id for p in paragraph_obj_list]

    translated_paragraphs = Translation.query.filter(
        Translation.bookgroup_id == bookgroup_id,
        Translation.paragraph_id.in_(paragraph_ids)
        ).all()

    return translated_paragraphs

@app.route("/save_text", methods=["POST"])
def save_translation_text():
    """
        Saves the text translation in the database
    """
    
    translated_text = request.form['translated_text']
    paragraph_id_input = int(request.form["p_id"])
    bookgroup_id_input = int(request.form["bg_id"])

    find_translated_text_in_db = db.session.query(Translation).filter_by(
        paragraph_id=paragraph_id_input, bookgroup_id=bookgroup_id_input).first()

    if find_translated_text_in_db:
        updated_translation = db.session.query(Translation).filter_by(
                                paragraph_id = paragraph_id_input,
                                bookgroup_id=bookgroup_id_input).update({
                                "translated_paragraph":translated_text})
        db.session.commit()
    else:
        new_translation_for_db = Translation(translated_paragraph=translated_text,
            paragraph_id=paragraph_id_input,
            bookgroup_id=bookgroup_id_input)
        db.session.add(new_translation_for_db)
        db.session.commit()

    return jsonify({"status": "OK", "translated_text": translated_text, "paragraph_id": paragraph_id_input})

@app.route("/in_translation", methods=["POST"])
def check_translation_in_progress():
    """
        Checks if another user is currently translating the paragraph the user has
        clicked on.
    """

    paragraph_id_input = int(request.form["p_id"])
    bookgroup_id_input = int(request.form["bg_id"])
    current_trans_text = request.form["current_trans_text"]
    translated_p_obj = db.session.query(Translation).filter_by(
        paragraph_id=paragraph_id_input, bookgroup_id=bookgroup_id_input).first()

    if not translated_p_obj:
        return jsonify({"status": "OK", "inProgress": False})
    else:
        if translated_p_obj.translated_paragraph == current_trans_text:
            return jsonify({"status": "OK", "inProgress": False})
        else:
            return jsonify({"status": "OK", "inProgress": True})

@app.route("/cancel_translation", methods=["POST"])
def last_saved_translations():
    """
        If the user cancels current translation, sends the last saved edit back
        to page.
    """
    paragraph_id_input = int(request.form["p_id"])
    bookgroup_id_input = int(request.form["bg_id"])
    translated_p_obj = db.session.query(Translation).filter_by(
        paragraph_id=paragraph_id_input, bookgroup_id=bookgroup_id_input).one()

    return jsonify({"status": "OK", "last_saved_trans": translated_p_obj.translated_paragraph, "paragraph_id":paragraph_id_input})



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

def book_database(parsed_book, book_obj):
    """ Pushs newly created books into a database"""

    book_id = book_obj.book_id

    # start at 1 to account the sqlite3 starts counting at 1
    for c, chapters in enumerate(parsed_book, 1):
        db.session.add(Chapter(chapter_number=c, book_id=book_id))
        db.session.commit()
        new_chapter_obj = Chapter.query.filter_by(chapter_number=c, 
            book_id=book_id).one()
        new_chapter_id = new_chapter_obj.chapter_id

        for paragraphs in chapters:
            db.session.add(Paragraph(untranslated_paragraph=paragraphs,
                chapter_id=new_chapter_id))

    db.session.commit()

def process_book_chapters(guten_extraction_number):
    """
        Loads a book from project gutenberg, splits the chapters, and pushes it to
        a database.
    """
    book_obj = Book.query.filter_by(gutenberg_extraction_num=guten_extraction_number).one()

    # gets book from project gutenberg
    book_text = open_file(guten_extraction_number)

    # splits the book to a list of chapters
    chapter_list = split_chapters(book_text)

    # push chapter_list into a database
    book_database(chapter_list, book_obj)

def amazon_setup(book_obj_list):
    """
        Connects to amazon web services API
    """

    config = {
        'access_key': os.environ['ACCESS_KEY'],
        'secret_key': os.environ['SECRET_KEY'],
        'associate_tag': os.environ['ASSOCIATE_TAG'],
        'locale': 'us'
    }

    api = API(cfg=config)

    # book_obj_list = Book.query.all()
    isbn_list = []
    for book_obj in book_obj_list:
        isbn_list.append(book_obj.isbn)

    return book_lookup(isbn_list, api)

def book_lookup(isbn_list, api):
    api_dict = {}

    for isbn in isbn_list:
        res = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN',
            ResponseGroup="Images, Reviews")
        for item in res.Items.Item:
            img_url = str(item.LargeImage.URL)
            api_dict.setdefault(isbn, img_url)
    return api_dict

def aws_api_to_db(api_dict):

    for isbn in api_dict:
        book_obj = Book.query.filter_by(isbn=isbn)
        book_obj.cover = api_dict[isbn]
    db.session.commit()

def book_ratings():
    book_isbn_tuple = db.session.query(Book.isbn, Book.book_id).all()
    book_isbn_dict = dict(book_isbn_tuple)
    isbn_str = ""
    for book_isbn in book_isbn_dict:
        isbn_str = isbn_str +","+ book_isbn
    isbn_str = isbn_str[1:]

    book_ratings_response =requests.get("https://www.goodreads.com/book/review_counts.json?format=json&isbns="+isbn_str+"&key="+ os.environ['GR_KEY'])
    book_ratings_response = book_ratings_response.json()
    book_ratings_list = book_ratings_response['books']

    for rating_dict in book_ratings_list:
        book_id = book_isbn_dict[rating_dict["isbn"]]
        book_obj = Book.query.get(book_id)
        book_obj.rating = rating_dict['average_rating']

        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    DebugToolbarExtension(app)
    # book_database()
    # book_ratings()
    # amazon_setup()
    socketio.run(app)
    app.run(debug=True)
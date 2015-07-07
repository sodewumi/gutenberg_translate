import os
# third-party modules
import jinja2
from flask import flash, Flask, jsonify,  redirect, render_template, request, session, url_for
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_debugtoolbar import DebugToolbarExtension

# my modules
from model import Book, Chapter, connect_to_db, db, Group, Translation, User, BookGroup, UserGroup
from process_gutenberg_books import processGutenBook
from helper import render_untranslated_chapter, find_trans_paragraphs, find_room



app = Flask(__name__)
app.secret_key = 'will hook to .gitignore soon'
app.jinja_env .undefined = jinja2.StrictUndefined
socketio = SocketIO(app)

print "************************"

################################################################################
    #Logins, Logouts, Register
################################################################################

@app.route("/", methods=["GET"])
def display_homepage():
    """Returns homepage."""
    return render_template("homepage.html")

@app.route("/login", methods=["POST"])
def login_user():
    """Logs in user. Adds user_id and username to session"""

    username = request.form["username_input"]
    username = username.strip().lower()
    password = request.form["password_input"]

    user_object = User.query.filter(User.username == username).first()

    if user_object:
        if user_object.password == password:
            session["login"] = [username, user_object.user_id]
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
            User.create_new_user(email=register_email, 
                                password=register_password,
                                username=register_username)
            flash("Thanks for creating an account with Gutenberg Translate! Please sign in")
            return redirect("/")
        else:
            flash("Please fill out all fields")
            return redirect("/")

@app.route("/logout")
def logout_user():
    """Remove login information from session"""

    session.pop('login')
    flash("You've successfully logged out. Goodbye.")
    return redirect("/")

################################################################################
    #Explore Books Page, Book Description Page, & Profile
################################################################################

@app.route("/explore")
@app.route("/explore/<int:page>")
def display_explore_books(page=1):
    """
        *Return a full list of books from project gutenberg.
    """

    all_book_objs = Book.query.paginate(page, 20, False)

    return render_template("explore_books.html", all_book_objs=all_book_objs)


@app.route("/description/<int:gutenberg_extraction_number>", methods=["GET"])
def display_book_description(gutenberg_extraction_number):
    """
        *Return a description of the book: reviews, image, and excerpt
        *Displays other groups that the user is in that is translating that
            particular book. This includes: group names, usernames, and
            translation language
    """
    
    user_session = session.get(u'login')

    if not user_session:
        flash("You need to sign in to view this page")
        return redirect("/")
    else:
        user_id = user_session[1]

    current_user_obj = User.query.filter(User.user_id == user_id).one()
    current_book_obj = Book.query.filter_by(gutenberg_extraction_num =
        gutenberg_extraction_number).one()

    book_obj_text = current_book_obj.excerpt_text()

    groups_translating = current_book_obj.user_groups_translating_book(
                         user_obj=current_user_obj, book_obj=current_book_obj)

    return render_template("book_description.html", display_book = current_book_obj,
                        gutenberg_extraction_number=gutenberg_extraction_number,
                        groups_list = groups_translating,
                        display_text = book_obj_text)


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

@app.route("/profile/<int:user_id>")
def display_profile(user_id):
    """Return a user's profile page."""
    
    user_obj = User.query.get(user_id)
    user_groups_list = user_obj.groups

    group_ids_list = [group.group_id for group in user_groups_list]

    usergroups_list = UserGroup.query.filter(UserGroup.group_id.in_(group_ids_list))
    user_ids_list = [usergroup.user_id for usergroup in usergroups_list]
    all_collaborators = User.query.filter(User.user_id.in_(user_ids_list),
                            User.user_id != user_obj.user_id)

    project_num = len(group_ids_list)
    return render_template("profile.html", username=user_obj.username,
            user_groups_list=user_groups_list, all_collaborators=all_collaborators,
            project_num = project_num)

################################################################################
    #Translation Page
################################################################################

@app.route("/translate/<int:gutenberg_extraction_number>", methods=["GET"])
def submit_add_translation_form(gutenberg_extraction_number):
    """ 
        Takes information from add_book_form and adds it to the database whenever
        a book has not yet to the book database.
        Book taken from book_explore.html
    """
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
        processed_book = processGutenBook(gutenberg_extraction_number)
        processed_book = processed_book.process_book_chapters()
        chapter_obj_list = db.session.query(Chapter).filter(
            Chapter.book_id == book_id_tuple[0]).all()

    new_bookgroup_obj = createNewGroup(group_name, collaborators_user_objs, book_id, translation_language)

    return redirect(url_for(".display_translation_page", bookgroup_id_input = new_bookgroup_obj.bookgroup_id))

def createNewGroup(new_group_name, new_collaborators_user_objs, book_id, translation_language):
    """
        Creates new UserGroups and BookGroup for database.
    """

    new_group_obj = Group(group_name = new_group_name)

    db.session.add(new_group_obj)
    # create usergroup
    db.session.commit()
    new_usergroup_obj = UserGroup(user_id=session["login"][1],
                        group_id=new_group_obj.group_id)
    db.session.add(new_usergroup_obj)

    for a_collaborator in new_collaborators_user_objs:
        new_usergroup_obj = UserGroup(user_id=a_collaborator.user_id,
                            group_id=new_group_obj.group_id)
        db.session.add(new_usergroup_obj)
    db.session.commit()
    # create bookgroup
    new_bookgroup_obj = BookGroup(group_id=new_group_obj.group_id,
                        book_id=book_id, language=translation_language)
    db.session.add(new_bookgroup_obj)
    db.session.commit()

    return new_bookgroup_obj

@app.route("/rendertranslations", methods=["GET"])
def display_translation_page():
    """
        Displays a chapter of the book. 
        When page first loads, chapter starts at 1.
    """

    user_session = session.get(u'login')
    
    if not user_session:
        flash("You need to sign in to view this page")
        return redirect("/")

    # all arguments come from the book_group
    # bookgroup_obj = BookGroup.query.get(bookgroup_id)
    bookgroup_id = int(request.args["bookgroup_id_input"])
    bookgroup_obj = BookGroup.query.get(bookgroup_id)
    bookgroup_id = bookgroup_obj.bookgroup_id
    bookgroup_language = bookgroup_obj.language
    bookgroup_groupid = bookgroup_obj.group_id
    bookgroup_bookid = bookgroup_obj.book_id

    group_name = Group.query.filter_by(group_id = bookgroup_groupid).one()
    group_name = group_name.group_name

    group_collab_users = bookgroup_obj.group.users
    collab_user_num = len(group_collab_users)

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
                paragraph_obj_list=paragraph_obj_list, bookgroup_id=bookgroup_id)
    else:
        if number_of_chapters == 1:
            paragraph_obj_list = chapter_obj_list[0].paragraphs
            translated_paragraphs_list =  find_trans_paragraphs(
                paragraph_obj_list=paragraph_obj_list, bookgroup_id=bookgroup_id)
        else:
            paragraph_obj_list = chapter_obj_list[1].paragraphs
            translated_paragraphs_list =  find_trans_paragraphs(
                    paragraph_obj_list=paragraph_obj_list, bookgroup_id=bookgroup_id)

    return render_template("translation_page.html",
        number_of_chapters = number_of_chapters, 
        display_chapter = paragraph_obj_list, chapter_chosen=chosen_chapter, 
        display_translations=translated_paragraphs_list, book_id=bookgroup_bookid,
        language=bookgroup_language, book_obj=book_obj, group_id=bookgroup_groupid,
        bookgroup_id=bookgroup_id, group_collab_users=group_collab_users,
        collab_user_num=collab_user_num, group_name=group_name)

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
        paragraph_id=paragraph_id_input, bookgroup_id=bookgroup_id_input).first()

    if translated_p_obj:
        return jsonify({"status": "OK", "last_saved_trans": translated_p_obj.translated_paragraph, "paragraph_id":paragraph_id_input})
    else:
        return jsonify({"status": "OK", "last_saved_trans": None, "paragraph_id":paragraph_id_input})

@app.route("/leave_group/<int:group_id_input>")
def leave_group(group_id_input):
    """
        Deletes a user from UserGroup after they decide to leave group
    """
    user_id = session['login'][1]
    user_usergroup = UserGroup.query.filter_by(user_id = user_id, group_id=group_id_input).one()
    db.session.delete(user_usergroup)
    db.session.commit()
    return redirect('/explore')

@app.route("/delete_group/<int:group_id_input>/<language_input>/<int:book_id_input>")
def delete_group(group_id_input, language_input, book_id_input):
    """
        Deletes the BookGroup, UserGroup, and Translations associated with the 
        last remaining translator of a project.
    """
    user_id = session['login'][1]
    user_usergroup = UserGroup.query.filter_by(
                    user_id = user_id, group_id=group_id_input).one()
    bookgroup_obj = BookGroup.query.filter_by(group_id=group_id_input,
                    language=language_input, book_id=book_id_input).one()
    bookgroup_id = bookgroup_obj.bookgroup_id

    db.session.delete(user_usergroup)
    db.session.delete(bookgroup_obj)
    for translation in bookgroup_obj.translations:
        db.session.delete(translation)

    db.session.commit()
    return redirect('/explore')

################################################################################
    #Socket-Routes: Connecting/Disconnecting & Joining/Leaving Rooms
################################################################################

@socketio.on('connect', namespace='/rendertranslations')
def test_connect():
    """
        Establishes a connection to Socket.IO
    """
    emit('my response', {'connection_status': 'Connected'})

@socketio.on("disconnect", namespace='/rendertranslations')
def disconnected():
    """
        Disconnects from Socket.IO
    """
    disconnect()

@socketio.on('joined', namespace='/rendertranslations')
def on_join(data):
    """
        Sent by clients when they enter a room.
    """
    username = session["login"][0]
    room = find_room(data["bookgroup_id"], data.get("chapter_number"))
    join_room(room)

    emit('joined_status', {'msg': username + " has entered room " + str(room)}, room=room)

@socketio.on('leave', namespace='/rendertranslations')
def on_leave(data):
    """
        Sent by clients when the leave a room
    """

    username = session["login"][0]
    room = find_room(data["bookgroup_id"], data.get("chapter_number"))
    leave_room(room)

    emit('leave_status', {'msg': username + " has left room " + str(room)}, room=room)

################################################################################
    #Socket-Routes: Handles real-time translations 
################################################################################

@socketio.on('value changed', namespace='/rendertranslations')
def translated_text_rt(data):
    """
        Sent by clients while they are translating a paragraph
    """
    room = find_room(data["bookgroup_id"], data.get("chapter_number"))
    emit('update text', data, broadcast=True, room=room)

@socketio.on('canceled translation', namespace='/rendertranslations')
def revert_text(data):
    """ 
        Takes the last saved translation and renders it on the page if the clients
        cancels their datatranslation
    """

    room = find_room(data["bookgroup_id"], data.get("chapter_number"))
    emit('render reverted text', data, broadcast=True, room=room)

@socketio.on('submit text', namespace='/rendertranslations')
def new_text(data):
    """ 
        Sends an update to all clients after a user submits a translation into
        the database.
    """

    room = find_room(data["bookgroup_id"], data.get("chapter_number"))
    emit('render submitted text', data, broadcast=True, room=room)

@socketio.on('remove button', namespace='/rendertranslations')
def hide_buttons(data):
    """
        Stops users from accessing the same paragraph if another client is 
        translating the same one.
    """

    room = find_room(data["bookgroup_id"], data.get("chapter_number"))
    emit('hide button', data, broadcast=True, room=room)


if __name__ == "__main__":
    connect_to_db(app)
    app.debug = True
    DebugToolbarExtension(app)
    # socketio.run(app)
    app.run(debug=True)



















from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(15), nullable=False, unique=True)
    # translations = db.relationship("Translation", backref="user")


class Group(db.Model):
    """Name and Id of all groups"""

    __tablename__ = "groups"

    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(30), nullable=False)


class UserGroup(db.Model):
    """Specifies which groups a user belongs to"""

    __tablename__ = "usergroups"

    usergroup_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    user = db.relationship("User", backref=db.backref("usergroups"))
    group = db.relationship("Group", backref=db.backref("usergroups"))
    children = db.relationship("UserGroup",
                backref=db.backref('parent', remote_side=[usergroup_id])
            )
    def __repr__(self):
        return "<UserGroup: usergroup_id=%d, user_id=%d, group_id=%d>" %(
            self.usergroup_id, self.user_id, self.group_id)

class Book(db.Model):

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(45))
    reviews = db.Column(db.String())
    rating = db.Column(db.Integer)
    cover = db.Column(db.String())
    genre_name = db.Column(db.String(10))
    gutenberg_extraction_num = db.Column(db.String(10))
    isbn = db.Column(db.String(10))
    chapters = db.relationship("Chapter", backref="book") 
    # genres = db.relationship("Genre", uselist=False, backref="book")

    def __repr__(self):
        return "<Book: book_id=%d, name=%s>" % (self.book_id, self.name)


class BookGroup(db.Model):

    __tablename__ = "bookgroups"

    bookgroup_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(15))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))
    book = db.relationship("Book", backref=db.backref("bookgroups"))
    group = db.relationship("Group", backref=db.backref("bookgroups"))
    translations = db.relationship("Translation", backref="bookgroups")

    def __repr__(self):
        return "<BookGroup: bookgroup_id=%d group_id=%d, book_id=%d, language=%s>" % (
           self.bookgroup_id, self.group_id, self.book_id, self.language) 


# class Genre(db.Model):

#     __tablename__ = "genres"

#     genre_name = db.Column(db.String(10), db.ForeignKey("books.book_id"), primary_key=True)


class Chapter(db.Model):

    __tablename__ = "chapters"

    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_number =db.Column(db.Integer)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))
    paragraphs = db.relationship("Paragraph", backref="chapter")

    def __repr__(self):
        return "<Chapter: chapter_id=%d, chapter_number=%d, book_id=%d>"\
            % (self.chapter_id, self.chapter_number, self.book_id)


class Paragraph(db.Model):

    __tablename__ = "paragraphs"

    paragraph_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    untranslated_paragraph = db.Column(db.String())
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.chapter_id"))
    translations = db.relationship("Translation", backref="paragraph")

    def __repr__(self):
        return "<Paragraph: paragraph_id=%d, chapter_id=%d>" %(self.paragraph_id, self.chapter_id)


class Translation(db.Model):

    __tablename__ = "translations"

    translation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    translated_paragraph = db.Column(db.String()) 
    paragraph_id = db.Column(db.Integer, db.ForeignKey("paragraphs.paragraph_id")) #fk
    bookgroup_id = db.Column(db.Integer, db.ForeignKey("bookgroups.bookgroup_id"))
    # user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    def __repr__(self):
        return """"<Translation: translation_id=%d, language=%s, paragraph_id=%d,
            user_id=%d""" %(self.translation_id, self.language, self.paragraph_id,\
                self.user_id)

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gutenberg_database.db'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)
    db.create_all()


if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."

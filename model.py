from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(15), nullable=False, unique=True)
    # translations = db.relationship("Translation", backref="user")


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
    genres = db.relationship("Genre", uselist=False, backref="book")

    def __repr__(self):
        return "<Book: book_id=%d, name=%s>" % (self.book_id, self.name)


class UserBook(db.Model):

    __tablename__ = "userbooks"

    userbook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))
    book = db.relationship("Book", backref=db.backref("userbooks"))
    user = db.relationship("User", backref=db.backref("userbooks"))
    translations = db.relationship("Translation", backref="userbooks")

    def __repr__(self):
        return "<UserBook: user_id=%d, book_id=%d, language=%s>" % (
            self.user_id, self.book_id, self.language) 


class Genre(db.Model):

    __tablename__ = "genres"

    genre_name = db.Column(db.String(10), db.ForeignKey("books.book_id"), primary_key=True)


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
    # get rid of language
    language = db.Column(db.String(15))
    translated_paragraph = db.Column(db.String()) 
    paragraph_id = db.Column(db.Integer, db.ForeignKey("paragraphs.paragraph_id")) #fk
    userbook_id = db.Column(db.Integer, db.ForeignKey("userbooks.userbook_id"))
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

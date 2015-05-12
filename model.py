from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(15), nullable=False, unique=True)


class Book(db.Model):

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(45))
    reviews = db.Column(db.String())
    rating = db.Column(db.Integer)
    cover = db.Column(db.String())
    genre_name = db.Column(db.String(10))

    


class Genre(db.Model):

    __tablename__ = "genres"

    genre_name = db.Column(db.String(10), primary_key=True)


class Chapter(db.Model):

    __tablename__ = "chapters"

    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_number =db.Column(db.Integer)
    book_id = db.Column(db.Integer) #fk


class Paragraph(db.Model):

    __tablename__ = "paragraphs"

    paragraph_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    untranslated_paragraph = db.Column(db.String())
    chapter_id = db.Column(db.Integer) #fk


class Translation(db.Model):

    __tablename__ = "translations"

    translation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(15))
    translated_paragraph = db.Column(db.String()) 
    paragraph_id = db.Column(db.Integer) #fk
    user_id = db.Column(db.Integer) #fk

if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    app.run(debug=True)
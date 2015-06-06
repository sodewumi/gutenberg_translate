from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(15), nullable=False, unique=True)
    groups = db.relationship("Group", backref=db.backref("users"),
            secondary="usergroups")

    @classmethod
    def create_new_user(cls, email, password, username):
        new_user = cls(email=email, password=password, username=username)
        db.session.add(new_user)
        db.session.commit()

    def __repr__(self):
        return "<User: username=%s, user_id=%d>" %(
            self.username, self.user_id)

class Group(db.Model):
    """Name and Id of all groups"""

    __tablename__ = "groups"

    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return "<Group: group_id=%d, group_name=%s" %(
            self.group_id, self.group_name)    


class UserGroup(db.Model):
    """Specifies which groups a user belongs to"""

    __tablename__ = "usergroups"

    usergroup_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    # user = db.relationship("UserGroup", backref=("users"))

    def __repr__(self):
        return "<UserGroup: usergroup_id=%d, user_id=%d, group_id=%d>" %(
            self.usergroup_id, self.user_id, self.group_id)

class Book(db.Model):

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(45))
    summary = db.Column(db.String())
    rating = db.Column(db.Integer)
    cover = db.Column(db.String())
    gutenberg_extraction_num = db.Column(db.String(10))
    isbn = db.Column(db.String(10))
    chapters = db.relationship("Chapter", backref="book")
    groups = db.relationship("Group", backref=db.backref("books"),
        secondary="bookgroups") 
    
    def excerpt_text(self):
        text_string = ""
        if len(self.chapters) > 0:
            if len(self.chapters) == 1:
                book_obj_paragraphs = self.chapters[0].paragraphs[0:3]
                for p in book_obj_paragraphs:
                   text_string += " " + p.untranslated_paragraph
            else:
                book_obj_paragraphs = self.chapters[1].paragraphs[0:3]
                for p in book_obj_paragraphs:
                   text_string += " " + p.untranslated_paragraph
            return text_string[0:250]
        else:
            return None

    def user_groups_translating_book(self, book_obj, user_obj):
        book_groups_list = book_obj.groups
        user_groups_list = user_obj.groups

        book_group_id_list = {group.group_id for group in book_groups_list}
        user_group_id_list = {group.group_id for group in user_groups_list}

        intersection = book_group_id_list & user_group_id_list
        groups_translating = Group.query.filter(Group.group_id.in_(intersection)).all()

        return groups_translating
    
    def __repr__(self):
        return "<Book: book_id=%d, name=%s>" % (self.book_id, self.name)


class BookGroup(db.Model):

    __tablename__ = "bookgroups"

    bookgroup_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    language = db.Column(db.String(15))
    group_id = db.Column(db.Integer, db.ForeignKey("groups.group_id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"))

    translations = db.relationship("Translation", backref="bookgroups")
    group = db.relationship("Group", backref=db.backref("bookgroups"))

    def __repr__(self):
        return "<BookGroup: bookgroup_id=%d group_id=%d, book_id=%d, language=%s>" % (
           self.bookgroup_id, self.group_id, self.book_id, self.language) 


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
    paragraph_id = db.Column(db.Integer, db.ForeignKey("paragraphs.paragraph_id"))
    bookgroup_id = db.Column(db.Integer, db.ForeignKey("bookgroups.bookgroup_id"))

    def find_trans_paragraphs(self, paragraph_obj_list, bookgroup_id):
        """Finds the translated paragraphs per group"""

        paragraph_ids = [p.paragraph_id for p in paragraph_obj_list]

        translated_paragraphs = self.query.filter(
                                self.bookgroup_id == bookgroup_id,
                                self.paragraph_id.in_(paragraph_ids)
                                ).all()
        return translated_paragraphs
        
    def __repr__(self):
        return """"<Translation: translation_id=%d, paragraph_id=%d,
            bookgroup_id=%d translated_paragraph=%s""" %(self.translation_id, self.paragraph_id,\
                self.bookgroup_id, self.translated_paragraph)

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
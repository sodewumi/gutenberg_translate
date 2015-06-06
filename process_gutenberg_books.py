from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
import re

from model import Book, Chapter, connect_to_db, db, Paragraph


class processGutenBook(object):

    def __init__ (self, file_id):
        self.file_id = file_id

    def open_file(self, file_id):
        """
            Opens a file from project gutenberg 
        """

        return load_etext(file_id)

    def split_chapters(self, full_text):
        """
            Removes header and footer from project gutenberg book. 
            Makes a list of chapters, where each chapter is a sublist of paragraphs
        """
        book = strip_headers(full_text)

        chapter_list = re.split(ur'\n\bchapter\b \w+\.?', book, flags=re.IGNORECASE)

        if len(chapter_list) < 2:
            print "hey"
            chapter_list = re.split(ur'\n[IVXCLM]+\n', book)
        paragraphs_in_chapter_list = []

        for i in range(len(chapter_list)):
            paragraphs_in_chapter_list.append(chapter_list[i].split('\n\n'))

        # return len(paragraphs_in_chapter_list)
        return paragraphs_in_chapter_list

    def book_database(self, parsed_book, book_obj):
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

    def process_book_chapters(self):
        """
            Loads a book from project gutenberg, splits the chapters, and pushes it to
            a database.
        """
        book_obj = Book.query.filter_by(gutenberg_extraction_num=self.file_id).one()

        # gets book from project gutenberg
        book_text = self.open_file(self.file_id)

        # splits the book to a list of chapters
        chapter_list = self.split_chapters(book_text)

        # push chapter_list into a database
        self.book_database(chapter_list, book_obj)
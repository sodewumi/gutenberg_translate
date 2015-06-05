from model import Book, Translation

def render_untranslated_chapter(book_id, chosen_chap):
    """Shows the translated page chosen"""
    book_obj = Book.query.get(book_id)
    paragraph_obj_list = book_obj.chapters[chosen_chap].paragraphs

    return paragraph_obj_list

def find_trans_paragraphs(paragraph_obj_list, bookgroup_id):
    """Finds the translated paragraphs per group"""

    paragraph_ids = [p.paragraph_id for p in paragraph_obj_list]

    translated_paragraphs = Translation.query.filter(
        Translation.bookgroup_id == bookgroup_id,
        Translation.paragraph_id.in_(paragraph_ids)
        ).all()

    return translated_paragraphs

def find_room(bookgroup_id, chapter_number):
    room = str(bookgroup_id) + "." + str(chapter_number)
    return room
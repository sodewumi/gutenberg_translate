from flask import session
from process_gutenberg_books import processGutenBook
from model import db, Book, BookGroup, Chapter, Group, Translation, UserGroup

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

def render_chosen_paragraphs(chosen_chapter, number_of_chapters, chapter_obj_list):
    """
        Renders all paragraphs associated with chosen chapter.
        If chapter has not been chosen, renders a the paragraphs associated
        with the chapter depending on if book has more than one chapter.
    """
    if chosen_chapter:
        paragraph_obj_list = chapter_obj_list[chosen_chapter].paragraphs
    else:
        if number_of_chapters == 1:
            paragraph_obj_list = chapter_obj_list[0].paragraphs
        else:
            paragraph_obj_list = chapter_obj_list[1].paragraphs

    return paragraph_obj_list

def retrieveText(book_id, gutenberg_extraction_number):
    """
        If the text doesn't already exist for the book, the paragraphs
        and chapters associated with said book are created.
    """

    chapter_obj_list = Chapter.query.filter_by(book_id = book_id).all()

    if not chapter_obj_list:
        processed_book = processGutenBook(gutenberg_extraction_number)
        processed_book = processed_book.process_book_chapters()
        chapter_obj_list = Chapter.query.filter_by(book_id = book_id).all()

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

def find_room(bookgroup_id, chapter_number):
    room = str(bookgroup_id) + "." + str(chapter_number)
    return room

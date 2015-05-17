import pytest
from server import open_file

def test_open_file():
    # pride and prejudice 42671 num Jane Austen
    # alice in wonderland 28885 roman Lewis Carroll
    # yellow wall paper 1952 none Charlotte Perkins Gilman
    # metamorphosis 5200 roman no ltr Franz Kafka
    # heart of darkness 219 roman no ltr Joseph Conrad
    
    gutenberg_book_num = (42671, 28885, 1952, 5200, 219)
    for a_book in gutenberg_book_num:
        book = open_file(a_book)
        assert book != None
        assert isinstance(book, basestring)



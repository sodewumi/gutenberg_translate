import pytest
from server import open_file

def test_open_file():
    # pride and prejudice 42671 num Jane Austen 0486284735
    # alice in wonderland 28885 roman Lewis Carroll 0553213458
    # yellow wall paper 1952 none Charlotte Perkins Gilman 091406116X
    # metamorphosis 5200 roman no ltr Franz Kafka 0393967972
    # heart of darkness 219 roman no ltr Joseph Conrad 0141441674
    # the count of monte cristo 1184 num with text 0140449264

    gutenberg_book_num = (42671, 28885, 1952, 5200, 219)
    for a_book in gutenberg_book_num:
        book = open_file(a_book)
        assert book != None
        assert isinstance(book, basestring)



"""Group H - Unit tests. Run with:  python -m pytest -v"""
import pytest

from book import Book
from member import Member
from library import Library
from issue_return import issue_book, return_book, MAX_BOOKS_PER_MEMBER
from search import search_by_title, search_by_author, search_by_isbn, only_available
from auth_system import authenticate, register_user, hash_password


@pytest.fixture
def lib():
    library = Library()
    library.add_book(Book("123", "Test Book", "Author One", 2))
    library.add_book(Book("456", "Another Story", "Author Two", 0))
    return library


@pytest.fixture
def member():
    return Member("M1", "Sam")


# ---- Book / Member ----
def test_book_attributes():
    b = Book("1", "T", "A", 3)
    assert (b.isbn, b.title, b.author, b.copies) == ("1", "T", "A", 3)


def test_book_negative_copies_rejected():
    with pytest.raises(ValueError):
        Book("1", "T", "A", -1)


def test_member_starts_with_no_books(member):
    assert member.borrowed_books == []


# ---- Library ----
def test_add_book(lib):
    assert "123" in lib.books


def test_add_duplicate_isbn_increases_copies(lib):
    lib.add_book(Book("123", "Test Book", "Author One", 3))
    assert lib.books["123"].copies == 5


def test_remove_book(lib):
    assert lib.remove_book("123") is True
    assert lib.remove_book("123") is False


def test_duplicate_member_rejected(lib, member):
    lib.add_member(member)
    with pytest.raises(ValueError):
        lib.add_member(Member("M1", "Other"))


# ---- Issue / Return ----
def test_issue_book_success(lib, member):
    ok, _ = issue_book(lib, "123", member)
    assert ok and lib.books["123"].copies == 1
    assert "123" in member.borrowed_books


def test_issue_unavailable_book_fails(lib, member):
    ok, _ = issue_book(lib, "456", member)
    assert not ok and member.borrowed_books == []


def test_issue_unknown_book_fails(lib, member):
    assert issue_book(lib, "999", member)[0] is False


def test_cannot_borrow_same_book_twice(lib, member):
    issue_book(lib, "123", member)
    assert issue_book(lib, "123", member)[0] is False


def test_borrow_limit(lib, member):
    for i in range(MAX_BOOKS_PER_MEMBER):
        lib.add_book(Book(f"x{i}", "t", "a", 1))
        assert issue_book(lib, f"x{i}", member)[0]
    lib.add_book(Book("extra", "t", "a", 1))
    assert issue_book(lib, "extra", member)[0] is False


def test_return_book_success(lib, member):
    issue_book(lib, "123", member)
    ok, _ = return_book(lib, "123", member)
    assert ok and lib.books["123"].copies == 2 and member.borrowed_books == []


def test_return_book_not_borrowed_fails(lib, member):
    assert return_book(lib, "123", member)[0] is False


# ---- Search ----
def test_search_by_title_case_insensitive(lib):
    assert [b.isbn for b in search_by_title(lib, "test")] == ["123"]


def test_search_by_author(lib):
    assert [b.isbn for b in search_by_author(lib, "two")] == ["456"]


def test_search_by_isbn(lib):
    assert search_by_isbn(lib, "123")[0].title == "Test Book"
    assert search_by_isbn(lib, "000") == []


def test_only_available(lib):
    assert [b.isbn for b in only_available(lib.list_books())] == ["123"]


# ---- Auth ----
def test_authenticate():
    db = {}
    register_user(db, "u", "pw", "member", "M1")
    assert authenticate("u", "pw", db) is True
    assert authenticate("u", "wrong", db) is False
    assert authenticate("nobody", "pw", db) is False


def test_password_not_stored_plaintext():
    db = {}
    register_user(db, "u", "pw")
    assert db["u"]["password"] != "pw"
    assert db["u"]["password"] == hash_password("pw")


def test_duplicate_user_rejected():
    db = {}
    register_user(db, "u", "pw")
    with pytest.raises(ValueError):
        register_user(db, "u", "pw2")

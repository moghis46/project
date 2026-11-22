"""Group D - Issue and Return module: updates availability on borrow/return."""

MAX_BOOKS_PER_MEMBER = 3


def issue_book(library, isbn, member):
    """Issue a book to a member.

    Returns:
        tuple[bool, str]: (success, message)
    """
    book = library.get_book(isbn)
    if book is None:
        return False, "Book not found."
    if book.copies <= 0:
        return False, "No copies available."
    if member.has_borrowed(isbn):
        return False, "Member already has this book."
    if len(member.borrowed_books) >= MAX_BOOKS_PER_MEMBER:
        return False, f"Borrow limit of {MAX_BOOKS_PER_MEMBER} books reached."
    book.copies -= 1
    member.borrowed_books.append(isbn)
    return True, f"'{book.title}' issued to {member.name}."


def return_book(library, isbn, member):
    """Return a book from a member.

    Returns:
        tuple[bool, str]: (success, message)
    """
    if not member.has_borrowed(isbn):
        return False, "Member has not borrowed this book."
    member.borrowed_books.remove(isbn)
    book = library.get_book(isbn)
    if book is not None:
        book.copies += 1
        return True, f"'{book.title}' returned by {member.name}."
    return True, "Book returned (it is no longer in the catalogue)."

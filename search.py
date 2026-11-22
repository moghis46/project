"""Group E - Search module: find books by title, author, or ISBN."""


def search_by_title(library, title):
    """Return books whose title contains `title` (case-insensitive)."""
    return [b for b in library.books.values() if title.lower() in b.title.lower()]


def search_by_author(library, author):
    """Return books whose author contains `author` (case-insensitive)."""
    return [b for b in library.books.values() if author.lower() in b.author.lower()]


def search_by_isbn(library, isbn):
    """Return a list with the book matching the exact ISBN (empty if none)."""
    book = library.get_book(isbn.strip())
    return [book] if book else []


def only_available(books):
    """Filter a list of books down to those with copies available."""
    return [b for b in books if b.copies > 0]

"""Group A - Book module: defines the structure of a book."""


class Book:
    """A book in the library.

    Attributes:
        isbn (str): Unique identifier of the book.
        title (str): Title of the book.
        author (str): Author of the book.
        copies (int): Number of copies currently available.
    """

    def __init__(self, isbn, title, author, copies):
        """Create a Book. Raises ValueError if copies is negative."""
        if copies < 0:
            raise ValueError("copies cannot be negative")
        self.isbn = str(isbn).strip()
        self.title = title
        self.author = author
        self.copies = copies

    def is_available(self):
        """Return True if at least one copy is available."""
        return self.copies > 0

    def __str__(self):
        return (f"[{self.isbn}] {self.title} by {self.author} "
                f"- {self.copies} copies available")

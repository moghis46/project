"""Group C - Library module: manages the book collection and member registry."""


class Library:
    """Holds all books (keyed by ISBN) and members (keyed by member_id)."""

    def __init__(self):
        """Create an empty library."""
        self.books = {}
        self.members = {}

    # ---- books ----
    def add_book(self, book):
        """Add a book. If the ISBN already exists, add to its copies."""
        if book.isbn in self.books:
            self.books[book.isbn].copies += book.copies
        else:
            self.books[book.isbn] = book

    def remove_book(self, isbn):
        """Remove a book by ISBN. Return True if removed, False if not found."""
        return self.books.pop(isbn, None) is not None

    def get_book(self, isbn):
        """Return the Book for an ISBN, or None."""
        return self.books.get(isbn)

    def list_books(self):
        """Return a list of all books."""
        return list(self.books.values())

    # ---- members ----
    def add_member(self, member):
        """Register a member. Raises ValueError if member_id already exists."""
        if member.member_id in self.members:
            raise ValueError(f"Member {member.member_id} already exists")
        self.members[member.member_id] = member

    def get_member(self, member_id):
        """Return the Member for an ID, or None."""
        return self.members.get(member_id)

    def list_members(self):
        """Return a list of all members."""
        return list(self.members.values())

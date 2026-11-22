"""Group B - Member module: manages library members."""


class Member:
    """A library member.

    Attributes:
        member_id (str): Unique member identifier.
        name (str): Member's name.
        borrowed_books (list[str]): ISBNs of books currently borrowed.
    """

    def __init__(self, member_id, name):
        """Create a Member with an empty borrowed_books list."""
        self.member_id = str(member_id).strip()
        self.name = name
        self.borrowed_books = []

    def has_borrowed(self, isbn):
        """Return True if the member currently holds the given ISBN."""
        return isbn in self.borrowed_books

    def __str__(self):
        books = ", ".join(self.borrowed_books) if self.borrowed_books else "none"
        return f"[{self.member_id}] {self.name} - borrowed: {books}"

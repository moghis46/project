"""Group G - Main application: graphical interface (tkinter) for the LMS.

Run with:  python library_management_system.py
Demo logins:  admin / admin123 (librarian)   alice / alice123 (member M001)
"""
import tkinter as tk
from tkinter import ttk, messagebox

from book import Book
from member import Member
from library import Library
from issue_return import issue_book, return_book
from search import search_by_title, search_by_author, search_by_isbn, only_available
from auth_system import authenticate, register_user, get_user, LIBRARIAN, MEMBER


def seed_data():
    """Create a library and user database with some demo data."""
    library = Library()
    library.add_book(Book("101", "Python Crash Course", "Eric Matthes", 3))
    library.add_book(Book("102", "Clean Code", "Robert C. Martin", 2))
    library.add_book(Book("103", "The Pragmatic Programmer", "Andrew Hunt", 1))
    library.add_member(Member("M001", "Alice"))
    library.add_member(Member("M002", "Bob"))
    user_db = {}
    register_user(user_db, "admin", "admin123", LIBRARIAN)
    register_user(user_db, "alice", "alice123", MEMBER, "M001")
    register_user(user_db, "bob", "bob123", MEMBER, "M002")
    return library, user_db


def report(ok, message):
    """Show a success or error popup for an operation result."""
    (messagebox.showinfo if ok else messagebox.showerror)(
        "Success" if ok else "Error", message)


# --------------------------------------------------------------------------
# Books tab (shared by librarians and members)
# --------------------------------------------------------------------------
class BooksTab(ttk.Frame):
    """Searchable table of books. Librarians get add/remove; members get borrow."""

    def __init__(self, parent, app, is_librarian):
        super().__init__(parent, padding=10)
        self.app = app
        self.is_librarian = is_librarian

        # search bar
        bar = ttk.Frame(self)
        bar.pack(fill="x")
        ttk.Label(bar, text="Search:").pack(side="left")
        self.term = tk.StringVar()
        entry = ttk.Entry(bar, textvariable=self.term, width=28)
        entry.pack(side="left", padx=5)
        entry.bind("<Return>", lambda e: self.refresh())
        self.field = tk.StringVar(value="Title")
        ttk.Combobox(bar, textvariable=self.field, width=8, state="readonly",
                     values=["Title", "Author", "ISBN"]).pack(side="left")
        self.avail = tk.BooleanVar()
        ttk.Checkbutton(bar, text="Available only", variable=self.avail,
                        command=self.refresh).pack(side="left", padx=8)
        ttk.Button(bar, text="Search", command=self.refresh).pack(side="left")
        ttk.Button(bar, text="Clear", command=self.clear).pack(side="left", padx=4)

        # table
        self.tree = ttk.Treeview(self, columns=("isbn", "title", "author", "copies"),
                                 show="headings", selectmode="browse")
        for col, text, width in (("isbn", "ISBN", 80), ("title", "Title", 280),
                                 ("author", "Author", 200), ("copies", "Copies", 70)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col != "title" else "w")
        self.tree.pack(fill="both", expand=True, pady=8)

        # actions
        if is_librarian:
            self._build_librarian_actions()
        else:
            ttk.Button(self, text="Borrow Selected Book",
                       command=self.borrow_selected).pack(anchor="e")

    def _build_librarian_actions(self):
        form = ttk.LabelFrame(self, text="Add a book", padding=8)
        form.pack(fill="x")
        self.new = {k: tk.StringVar() for k in ("isbn", "title", "author", "copies")}
        for i, (key, label, w) in enumerate((("isbn", "ISBN", 10), ("title", "Title", 22),
                                             ("author", "Author", 18), ("copies", "Copies", 6))):
            ttk.Label(form, text=label).grid(row=0, column=i * 2, padx=(6, 2))
            ttk.Entry(form, textvariable=self.new[key], width=w).grid(row=0, column=i * 2 + 1)
        ttk.Button(form, text="Add Book", command=self.add_book).grid(row=0, column=8, padx=8)
        ttk.Button(self, text="Remove Selected Book",
                   command=self.remove_selected).pack(anchor="e", pady=(8, 0))

    def refresh(self):
        """Reload the table using the current search settings."""
        lib, term = self.app.library, self.term.get().strip()
        if not term:
            books = lib.list_books()
        elif self.field.get() == "Title":
            books = search_by_title(lib, term)
        elif self.field.get() == "Author":
            books = search_by_author(lib, term)
        else:
            books = search_by_isbn(lib, term)
        if self.avail.get():
            books = only_available(books)
        self.tree.delete(*self.tree.get_children())
        for b in books:
            self.tree.insert("", "end", iid=b.isbn,
                             values=(b.isbn, b.title, b.author, b.copies))

    def clear(self):
        self.term.set("")
        self.avail.set(False)
        self.refresh()

    def selected_isbn(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a book first.")
            return None
        return sel[0]

    def add_book(self):
        isbn, title, author = (self.new[k].get().strip() for k in ("isbn", "title", "author"))
        copies = self.new["copies"].get().strip()
        if not (isbn and title and author):
            return messagebox.showerror("Error", "ISBN, title and author are required.")
        if not copies.isdigit():
            return messagebox.showerror("Error", "Copies must be a whole number.")
        self.app.library.add_book(Book(isbn, title, author, int(copies)))
        for var in self.new.values():
            var.set("")
        self.app.refresh_all()

    def remove_selected(self):
        isbn = self.selected_isbn()
        if isbn and messagebox.askyesno("Confirm", f"Remove book {isbn}?"):
            self.app.library.remove_book(isbn)
            self.app.refresh_all()

    def borrow_selected(self):
        isbn = self.selected_isbn()
        if isbn:
            report(*issue_book(self.app.library, isbn, self.app.current_member))
            self.app.refresh_all()


# --------------------------------------------------------------------------
# Librarian-only tabs
# --------------------------------------------------------------------------
class MembersTab(ttk.Frame):
    """List members and register new ones (with a login account)."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.tree = ttk.Treeview(self, columns=("id", "name", "books"),
                                 show="headings", selectmode="browse")
        for col, text, width in (("id", "Member ID", 90), ("name", "Name", 180),
                                 ("books", "Borrowed ISBNs", 300)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(0, 8))

        form = ttk.LabelFrame(self, text="Register new member", padding=8)
        form.pack(fill="x")
        self.v = {k: tk.StringVar() for k in ("id", "name", "user", "pw")}
        for i, (key, label) in enumerate((("id", "Member ID"), ("name", "Name"),
                                          ("user", "Username"), ("pw", "Password"))):
            ttk.Label(form, text=label).grid(row=0, column=i * 2, padx=(6, 2))
            ttk.Entry(form, textvariable=self.v[key], width=12,
                      show="*" if key == "pw" else "").grid(row=0, column=i * 2 + 1)
        ttk.Button(form, text="Register", command=self.register).grid(row=0, column=8, padx=8)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for m in self.app.library.list_members():
            self.tree.insert("", "end", iid=m.member_id,
                             values=(m.member_id, m.name, ", ".join(m.borrowed_books)))

    def register(self):
        member_id, name, user, pw = (self.v[k].get().strip() for k in ("id", "name", "user", "pw"))
        if not all((member_id, name, user, pw)):
            return messagebox.showerror("Error", "All fields are required.")
        if user in self.app.user_db:
            return messagebox.showerror("Error", "Username already exists.")
        try:
            self.app.library.add_member(Member(member_id, name))
        except ValueError as err:
            return messagebox.showerror("Error", str(err))
        register_user(self.app.user_db, user, pw, MEMBER, member_id)
        for var in self.v.values():
            var.set("")
        self.app.refresh_all()
        messagebox.showinfo("Success", f"Member {name} registered.")


class IssueReturnTab(ttk.Frame):
    """Issue or return a book for any member."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=20)
        self.app = app
        self.member_id, self.isbn = tk.StringVar(), tk.StringVar()
        ttk.Label(self, text="Member").grid(row=0, column=0, sticky="e", pady=6)
        self.member_box = ttk.Combobox(self, textvariable=self.member_id,
                                       state="readonly", width=30)
        self.member_box.grid(row=0, column=1, padx=8)
        ttk.Label(self, text="Book").grid(row=1, column=0, sticky="e", pady=6)
        self.book_box = ttk.Combobox(self, textvariable=self.isbn,
                                     state="readonly", width=30)
        self.book_box.grid(row=1, column=1, padx=8)
        btns = ttk.Frame(self)
        btns.grid(row=2, column=1, sticky="w", pady=12, padx=8)
        ttk.Button(btns, text="Issue Book", command=lambda: self.act(issue_book)).pack(side="left")
        ttk.Button(btns, text="Return Book", command=lambda: self.act(return_book)).pack(side="left", padx=8)

    def refresh(self):
        lib = self.app.library
        self.member_box["values"] = [f"{m.member_id} - {m.name}" for m in lib.list_members()]
        self.book_box["values"] = [f"{b.isbn} - {b.title}" for b in lib.list_books()]

    def act(self, func):
        if not self.member_id.get() or not self.isbn.get():
            return messagebox.showerror("Error", "Select both a member and a book.")
        member = self.app.library.get_member(self.member_id.get().split(" - ")[0])
        isbn = self.isbn.get().split(" - ")[0]
        report(*func(self.app.library, isbn, member))
        self.app.refresh_all()


# --------------------------------------------------------------------------
# Member-only tab
# --------------------------------------------------------------------------
class MyBooksTab(ttk.Frame):
    """Books the logged-in member currently has, with a Return button."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.tree = ttk.Treeview(self, columns=("isbn", "title", "author"),
                                 show="headings", selectmode="browse")
        for col, text, width in (("isbn", "ISBN", 80), ("title", "Title", 300),
                                 ("author", "Author", 200)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(0, 8))
        ttk.Button(self, text="Return Selected Book", command=self.return_selected).pack(anchor="e")

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for isbn in self.app.current_member.borrowed_books:
            book = self.app.library.get_book(isbn)
            self.tree.insert("", "end", iid=isbn, values=(
                isbn, book.title if book else "(removed)", book.author if book else ""))

    def return_selected(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("No selection", "Please select a book first.")
        report(*return_book(self.app.library, sel[0], self.app.current_member))
        self.app.refresh_all()


# --------------------------------------------------------------------------
# Application shell
# --------------------------------------------------------------------------
class App:
    """Owns the window, switches between login screen and main screen."""

    def __init__(self, root, library=None, user_db=None):
        self.root = root
        self.library, self.user_db = (library, user_db) if library else seed_data()
        self.current_member = None
        self.tabs = []
        root.title("Library Management System")
        root.geometry("900x580")
        root.minsize(760, 480)
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        self.show_login()

    def _clear(self):
        for child in self.container.winfo_children():
            child.destroy()
        self.tabs = []

    # ---- login screen ----
    def show_login(self):
        self._clear()
        outer = ttk.Frame(self.container)
        outer.place(relx=0.5, rely=0.45, anchor="center")
        ttk.Label(outer, text="Library Management System",
                  font=("TkDefaultFont", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 16))
        self.username, self.password = tk.StringVar(), tk.StringVar()
        ttk.Label(outer, text="Username").grid(row=1, column=0, sticky="e", pady=4)
        user_entry = ttk.Entry(outer, textvariable=self.username, width=24)
        user_entry.grid(row=1, column=1, padx=8)
        ttk.Label(outer, text="Password").grid(row=2, column=0, sticky="e", pady=4)
        pw_entry = ttk.Entry(outer, textvariable=self.password, show="*", width=24)
        pw_entry.grid(row=2, column=1, padx=8)
        pw_entry.bind("<Return>", lambda e: self.login())
        ttk.Button(outer, text="Login", command=self.login).grid(row=3, column=1, sticky="e", pady=12, padx=8)
        ttk.Label(outer, foreground="gray",
                  text="Demo: admin / admin123  |  alice / alice123").grid(row=4, column=0, columnspan=2)
        user_entry.focus()

    def login(self):
        username, password = self.username.get().strip(), self.password.get()
        if not authenticate(username, password, self.user_db):
            return messagebox.showerror("Login failed", "Invalid username or password.")
        user = get_user(username, self.user_db)
        if user["role"] == LIBRARIAN:
            self.show_main(LIBRARIAN, "Librarian")
        else:
            self.current_member = self.library.get_member(user["member_id"])
            if self.current_member is None:
                return messagebox.showerror("Error", "No member profile linked to this account.")
            self.show_main(MEMBER, self.current_member.name)

    # ---- main screen ----
    def show_main(self, role, display_name):
        self._clear()
        header = ttk.Frame(self.container, padding=(10, 6))
        header.pack(fill="x")
        ttk.Label(header, text=f"Logged in as: {display_name} ({role})",
                  font=("TkDefaultFont", 10, "bold")).pack(side="left")
        ttk.Button(header, text="Logout", command=self.logout).pack(side="right")

        notebook = ttk.Notebook(self.container)
        notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        if role == LIBRARIAN:
            pages = [("Books", BooksTab(notebook, self, True)),
                     ("Members", MembersTab(notebook, self)),
                     ("Issue / Return", IssueReturnTab(notebook, self))]
        else:
            pages = [("Browse Books", BooksTab(notebook, self, False)),
                     ("My Books", MyBooksTab(notebook, self))]
        for title, page in pages:
            notebook.add(page, text=title)
            self.tabs.append(page)
        self.refresh_all()

    def refresh_all(self):
        """Reload every visible tab so all screens stay in sync."""
        for tab in self.tabs:
            tab.refresh()

    def logout(self):
        self.current_member = None
        self.show_login()


def main():
    """Program entry point."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

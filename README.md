# Library Management System

A modular, object-oriented Library Management System in Python, built collaboratively by Groups A-H using GitHub.

## Run
```bash
python library_management_system.py      # start the GUI (needs tkinter, included with Python on Windows/macOS; Linux: sudo apt install python3-tk)
pip install pytest && python -m pytest -v # run the tests
```
Demo logins: `admin / admin123` (librarian), `alice / alice123` (member M001), `bob / bob123` (member M002).

## Modules and Owners
| Group | File | Responsibility |
|---|---|---|
| A | `book.py` | `Book` class |
| B | `member.py` | `Member` class |
| C | `library.py` | `Library` class (books + members) |
| D | `issue_return.py` | `issue_book`, `return_book` -> `(success, message)` |
| E | `search.py` | search by title / author / ISBN |
| F | `auth_system.py` | register / authenticate users |
| G | `library_management_system.py` | tkinter GUI, integration |
| H | `test_library.py` | unit tests |

## Shared Naming
`isbn`, `title`, `author`, `copies`, `member_id`, `borrowed_books`. Report any interface change to Group G immediately.

## Workflow
1. Clone: `git clone <repo-url>` then `git checkout -b group-x-name` (e.g. `group-a-book`)
2. Edit **only your own file(s)**, commit often.
3. Sync: `git fetch origin && git merge origin/main` (resolve conflicts if any)
4. Push: `git push -u origin group-x-name`
5. Open a Pull Request to `main` using the template. Tests must pass and 1 reviewer must approve.
6. Merge only after review (done by the repository owner).


import streamlit as st
import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect("library.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    quantity INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS members(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    member_type TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS issues(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    member_id INTEGER,
    issue_date TEXT,
    due_date TEXT,
    returned INTEGER DEFAULT 0
)
""")

conn.commit()

st.title("Library Management System")

menu = st.sidebar.selectbox("Menu", [
    "Add Book",
    "Search Books",
    "Delete Book",
    "Register Member",
    "Issue Book",
    "Return Book",
    "Overdue Books"
])

if menu == "Add Book":
    st.header("Add Book")

    title = st.text_input("Book Title")
    author = st.text_input("Author")
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Add Book"):
        if title.strip() and author.strip():
            cur.execute(
                "INSERT INTO books(title, author, quantity) VALUES(?,?,?)",
                (title, author, quantity)
            )
            conn.commit()
            st.success("Book added successfully")
        else:
            st.error("Enter book title and author")

elif menu == "Search Books":
    st.header("Search Books")

    search = st.text_input("Enter title or author")

    cur.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?",
        ("%" + search + "%", "%" + search + "%")
    )

    st.dataframe(
        [{"ID": r[0], "Title": r[1], "Author": r[2],
          "Quantity": r[3]} for r in cur.fetchall()],
        use_container_width=True
    )

elif menu == "Delete Book":
    st.header("Delete Book")

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    if books:
        book_id = st.selectbox(
            "Select Book",
            [b[0] for b in books],
            format_func=lambda x: next(
                f"{b[1]} by {b[2]}" for b in books if b[0] == x
            )
        )

        if st.button("Delete"):
            cur.execute(
                "SELECT COUNT(*) FROM issues WHERE book_id=? AND returned=0",
                (book_id,)
            )

            if cur.fetchone()[0] > 0:
                st.error("This book is currently issued")
            else:
                cur.execute("DELETE FROM issues WHERE book_id=?", (book_id,))
                cur.execute("DELETE FROM books WHERE id=?", (book_id,))
                conn.commit()
                st.success("Book deleted")
                st.rerun()
    else:
        st.info("No books available")

elif menu == "Register Member":
    st.header("Register Member")

    name = st.text_input("Member Name")
    member_type = st.selectbox("Member Type", ["Student", "Teacher"])

    if st.button("Register"):
        if name.strip():
            cur.execute(
                "INSERT INTO members(name, member_type) VALUES(?,?)",
                (name, member_type)
            )
            conn.commit()
            st.success("Member registered")
        else:
            st.error("Enter member name")

elif menu == "Issue Book":
    st.header("Issue Book")

    cur.execute("SELECT * FROM books WHERE quantity > 0")
    books = cur.fetchall()

    cur.execute("SELECT * FROM members")
    members = cur.fetchall()

    if books and members:
        book_id = st.selectbox(
            "Select Book",
            [b[0] for b in books],
            format_func=lambda x: next(
                b[1] for b in books if b[0] == x
            )
        )

        member_id = st.selectbox(
            "Select Member",
            [m[0] for m in members],
            format_func=lambda x: next(
                f"{m[1]} ({m[2]})" for m in members if m[0] == x
            )
        )

        if st.button("Issue"):
            member = next(m for m in members if m[0] == member_id)

            cur.execute(
                "SELECT COUNT(*) FROM issues WHERE member_id=? AND returned=0",
                (member_id,)
            )
            count = cur.fetchone()[0]

            limit = 3 if member[2] == "Student" else 5

            if count >= limit:
                st.error(f"Borrow limit is {limit} books")
            else:
                today = date.today()
                due = today + timedelta(days=14)

                cur.execute(
                    """INSERT INTO issues
                    (book_id, member_id, issue_date, due_date)
                    VALUES(?,?,?,?)""",
                    (book_id, member_id, str(today), str(due))
                )

                cur.execute(
                    "UPDATE books SET quantity=quantity-1 WHERE id=?",
                    (book_id,)
                )

                conn.commit()
                st.success(f"Book issued. Due date: {due}")
                st.rerun()
    else:
        st.warning("Add a book and register a member first")

elif menu == "Return Book":
    st.header("Return Book")

    cur.execute("""
        SELECT issues.id, books.title, members.name, issues.due_date
        FROM issues
        JOIN books ON books.id=issues.book_id
        JOIN members ON members.id=issues.member_id
        WHERE issues.returned=0
    """)

    issues = cur.fetchall()

    if issues:
        issue_id = st.selectbox(
            "Select Issued Book",
            [i[0] for i in issues],
            format_func=lambda x: next(
                f"{i[1]} - {i[2]} (Due: {i[3]})"
                for i in issues if i[0] == x
            )
        )

        if st.button("Return"):
            issue = next(i for i in issues if i[0] == issue_id)
            late_days = max(
                (date.today() - date.fromisoformat(issue[3])).days, 0
            )
            fine = late_days * 10

            cur.execute(
                "UPDATE issues SET returned=1 WHERE id=?",
                (issue_id,)
            )

            cur.execute(
                "UPDATE books SET quantity=quantity+1 WHERE id=?",
                (issue[0] and next(
                    b[0] for b in conn.execute(
                        "SELECT id, title FROM books"
                    ).fetchall() if b[1] == issue[1]
                ),)
            )

            conn.commit()
            st.success(f"Book returned. Fine: Rs. {fine}")
            st.rerun()
    else:
        st.info("No books are currently issued")

elif menu == "Overdue Books":
    st.header("Overdue Books")

    cur.execute("""
        SELECT books.title, members.name, issues.due_date
        FROM issues
        JOIN books ON books.id=issues.book_id
        JOIN members ON members.id=issues.member_id
        WHERE issues.returned=0 AND issues.due_date < ?
    """, (str(date.today()),))

    overdue = cur.fetchall()

    if overdue:
        for book, member, due in overdue:
            days = (date.today() - date.fromisoformat(due)).days
            st.write(
                f"Book: {book} | Member: {member} | "
                f"Due: {due} | Fine: Rs. {days * 10}"
            )
    else:
        st.success("No overdue books")

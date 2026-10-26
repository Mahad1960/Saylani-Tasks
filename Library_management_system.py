books = []
members = []
issued_books = []

def add_book():
    book_id = input("Enter Book ID: ")
    title = input("Enter Book Title: ")
    author = input("Enter Author Name: ")

    book = {
        "id": book_id,
        "title": title,
        "author": author
    }

    books.append(book)
    print("Book added successfully!")


def view_books():
    if not books:
        print("No books available.")
    else:
        print("\n--- Book List ---")
        for book in books:
            print("ID:", book["id"])
            print("Title:", book["title"])
            print("Author:", book["author"])
            print("-------------------")


def search_book():
    book_id = input("Enter Book ID to search: ")

    for book in books:
        if book["id"] == book_id:
            print("Book Found!")
            print("Title:", book["title"])
            print("Author:", book["author"])
            return

    print("Book not found.")


def add_member():
    member_id = input("Enter Member ID: ")
    name = input("Enter Member Name: ")

    member = {
        "id": member_id,
        "name": name
    }

    members.append(member)
    print("Member registered successfully!")


def view_members():
    if not members:
        print("No members registered.")
    else:
        print("\n--- Member List ---")
        for member in members:
            print("ID:", member["id"])
            print("Name:", member["name"])
            print("-------------------")


def issue_book():
    book_id = input("Enter Book ID to issue: ")
    member_id = input("Enter Member ID: ")

    book_exists = any(book["id"] == book_id for book in books)
    member_exists = any(member["id"] == member_id for member in members)

    if not book_exists:
        print("Book not found.")
    elif not member_exists:
        print("Member not found.")
    elif any(item["book_id"] == book_id for item in issued_books):
        print("Book is already issued.")
    else:
        issued_books.append({
            "book_id": book_id,
            "member_id": member_id
        })
        print("Book issued successfully!")


def return_book():
    book_id = input("Enter Book ID to return: ")

    for item in issued_books:
        if item["book_id"] == book_id:
            issued_books.remove(item)
            print("Book returned successfully!")
            return

    print("This book is not currently issued.")


while True:
    print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
    print("1. Add Book")
    print("2. View Books")
    print("3. Search Book")
    print("4. Register Member")
    print("5. View Members")
    print("6. Issue Book")
    print("7. Return Book")
    print("8. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_book()
    elif choice == "2":
        view_books()
    elif choice == "3":
        search_book()
    elif choice == "4":
        add_member()
    elif choice == "5":
        view_members()
    elif choice == "6":
        issue_book()
    elif choice == "7":
        return_book()
    elif choice == "8":
        print("Thank you for using the Library Management System!")
        break
    else:
        print("Invalid choice. Please try again.")

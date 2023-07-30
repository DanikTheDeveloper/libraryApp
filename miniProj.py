import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
import winsound 
import datetime
import math
import random

def play_sound():
    winsound.PlaySound('C:\\Windows\\Media\\Windows Information Bar.wav', winsound.SND_ASYNC)


current_user_id = None
login_window = None
main_window = None

def get_current_balance():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT Balance FROM Customers WHERE CustomerID=?", (current_user_id,))
    balance = cur.fetchone()[0]
    conn.close()
    return balance

def login():
    global current_user_id, login_window
    play_sound()
    user_id = simpledialog.askinteger("Login", "Enter your Customer ID:")
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT CustomerID FROM Customers WHERE CustomerID=?", (user_id,))
    if cur.fetchone():
        current_user_id = user_id
        login_window.destroy()  # Close the login screen
        main_screen()  # Show the main screen
    else:
        messagebox.showerror("Error", "Invalid Customer ID!")

def logout():
    global current_user_id, main_window
    current_user_id = None
    main_window.destroy()  # Close the main screen
    login_screen()  # Show the login screen

def add_balance():
    global current_user_id
    play_sound()
    amount = simpledialog.askfloat("Add Balance", "Enter amount to add:")
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Customers SET Balance = Balance + ? WHERE CustomerID=?", (amount, current_user_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"${amount} added to your balance!")
    update_balance_display()

def login_screen():
    global login_window
    login_window = tk.Tk()
    login_window.title("Library Application Login")

    login_window.configure(bg='#f0f8ff')
    
    lbl_title = tk.Label(login_window, text="Library Application", bg='#f0f8ff', font=("Arial", 24))
    lbl_title.pack(pady=20)

    # New label added below
    lbl_info = tk.Label(login_window, text="UserIDs are 1, 2, 3... as well as all other IDs in the app", bg='#f0f8ff', font=("Arial", 10))
    lbl_info.pack(pady=5)  # Pack it after your main title

    button_config = {
        'bg': '#007acc',
        'fg': 'white',
        'padx': 20,
        'pady': 10,
        'font': ('Arial', 12),
        'activebackground': '#005da2',
        'width': 20
    }

    btn_login = tk.Button(login_window, text="Login", command=login, **button_config)
    btn_login.pack(pady=10)

    login_window.mainloop()


def create_connection():
    try:
        conn = sqlite3.connect('library.db')
        return conn
    except sqlite3.Error as e:
        print(e)
        return None


def find_item():
    play_sound()
    item_name = simpledialog.askstring("Find Item", "Enter Item Name:")
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Items WHERE title=?", (item_name,))
    items = cur.fetchall()
    
    if items:
        messagebox.showinfo("Result", f"Found {items[0][1]} of type {items[0][2]}")
    else:
        messagebox.showerror("Error", "Item not found!")


def borrow_item():
    global current_user_id
    play_sound()
    itemID = simpledialog.askinteger("Borrow Item", "Enter Item ID:")
    
    today = datetime.date.today()
    due_date = today + datetime.timedelta(days=30)  # 30 days loan period
    
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT Stock FROM Items WHERE ItemID=?", (itemID,))
    item = cur.fetchone()
    if not item:
        messagebox.showerror("Error", "Item not found!")
        return

    stock = item[0]
    if stock <= 0:
        messagebox.showerror("Error", "Item out of stock!")
        return

    cur.execute("UPDATE Items SET Stock = Stock - 1 WHERE ItemID=?", (itemID,))
    cur.execute("INSERT INTO Loans (CustomerID, ItemID, LoanDate, DueDate, ReturnDate) VALUES (?, ?, ?, ?, NULL)", (current_user_id, itemID, today, due_date))
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Borrowed item {itemID}. Due on {due_date}")


def return_item():
    global current_user_id
    play_sound()
    itemID = simpledialog.askinteger("Return Item", "Enter Item ID:")

    today = datetime.date.today()

    conn = create_connection()
    cur = conn.cursor()

    # Check if the item was actually borrowed by the user
    cur.execute("SELECT LoanDate FROM Loans WHERE CustomerID=? AND ItemID=? AND ReturnDate IS NULL", (current_user_id, itemID))
    loan_record = cur.fetchone()
    
    if not loan_record:
        messagebox.showerror("Error", "Loan record not found or item already returned!")
        return

    loan_date_str = loan_record[0]
    loan_date_datetime = datetime.datetime.strptime(loan_date_str, '%Y-%m-%d')
    loan_date = loan_date_datetime.date()
    months_borrowed = math.ceil((today - loan_date).days / 30)
    fine = 10 * months_borrowed

    # Update the return date for the loan
    cur.execute("UPDATE Loans SET ReturnDate = ? WHERE CustomerID=? AND ItemID=?", (today, current_user_id, itemID))

    # Increase the stock by 1 for the returned item
    cur.execute("UPDATE Items SET Stock = Stock + 1 WHERE ItemID=?", (itemID,))

    conn.commit()
    conn.close()

    if fine > 0:
        # Deduct the fine from the user's balance
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("UPDATE Customers SET Balance = Balance - ? WHERE CustomerID=?", (fine, current_user_id))
        conn.commit()
        conn.close()

        # Update the balance on the main screen
        update_balance_display()

        messagebox.showinfo("Fine Due", f"You owe a fine of ${fine}. Your balance has been updated.")
    else:
        messagebox.showinfo("Success", "Book returned successfully!")


def update_balance_display():
    balance = get_current_balance()
    lbl_balance.config(text=f"Current Balance: ${balance:.2f}")

def donate_item():
    play_sound()

    # Gather the details of the item being donated
    item_type = simpledialog.askstring("Donate Item", "Enter Item Type (e.g., Book, DVD):")
    item_title = simpledialog.askstring("Donate Item", "Enter Title:")
    author_artist = simpledialog.askstring("Donate Item", "Enter Author/Artist:")
    publication_year = simpledialog.askinteger("Donate Item", "Enter Publication Year:")
    genre = simpledialog.askstring("Donate Item", "Enter Genre:")
    availability = "Yes"  # As it's being donated, we assume it's available immediately
    stock = 1  # A single item is being donated
    
    conn = create_connection()
    cur = conn.cursor()

    # Check if an item with the same title, author, and publication year already exists in the database
    cur.execute("SELECT ItemID, Stock FROM Items WHERE Title=? AND AuthorArtist=? AND PublicationYear=?", 
                (item_title, author_artist, publication_year))
    existing_item = cur.fetchone()
    
    if existing_item:
        # If it exists, just increase the stock for that item
        item_id = existing_item[0]
        current_stock = existing_item[1]
        cur.execute("UPDATE Items SET Stock = ? WHERE ItemID=?", (current_stock + 1, item_id))
    else:
        # If it doesn't exist, create a new entry for the item
        cur.execute("INSERT INTO Items (Type, Title, AuthorArtist, PublicationYear, Genre, Availability, Stock) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (item_type, item_title, author_artist, publication_year, genre, availability, stock))
    
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Success", f"Thank you for donating {item_title}!")

def find_event():
    play_sound()
    event_name = simpledialog.askstring("Find Event", "Enter Event Name:")
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Events WHERE name=?", (event_name,))
    events = cur.fetchall()
    
    if events:
        messagebox.showinfo("Result", f"Found event {events[0][1]} on date {events[0][2]}")
    else:
        messagebox.showerror("Error", "Event not found!")

def register_event():
    play_sound()
    
    eventID = simpledialog.askinteger("Register for Event", "Enter Event ID to register:")

    conn = create_connection()
    cur = conn.cursor()

    cur.execute("UPDATE Events SET Number_of_Attendees = Number_of_Attendees + 1 WHERE EventID=?", (eventID,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Registered for event {eventID}")

def ask_librarian():
    play_sound()

    query = simpledialog.askstring("Ask a Librarian", "Enter your query:")
    
    if query:
        random_employee = get_random_employee()
        conn = create_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO Queries (QueryText, CustomerID, EmployeeID) VALUES (?, ?, ?)", (query, current_user_id, random_employee))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Your query has been submitted! Librarian with ID {random_employee} will get back to you soon.")
    else:
        messagebox.showwarning("Warning", "Query not provided!")



def get_random_employee():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT EmployeeID FROM Events")
    all_employee_ids = [item[0] for item in cur.fetchall()]
    return random.choice(all_employee_ids)


def main_screen():
    global main_window, lbl_balance
    main_window = tk.Tk()
    main_window.title("Library Application")

    main_window.configure(bg='#f0f8ff')
    lbl_title = tk.Label(main_window, text="Library Application", bg='#f0f8ff', font=("Arial", 24))
    lbl_title.pack(pady=20)

    balance = get_current_balance()
    lbl_balance = tk.Label(main_window, text=f"Current Balance: ${balance:.2f}", bg='#f0f8ff', font=("Arial", 18))
    lbl_balance.pack(pady=10)

    button_config = {
        'bg': '#007acc',
        'fg': 'white',
        'padx': 20,
        'pady': 10,
        'font': ('Arial', 12),
        'activebackground': '#005da2',
        'width': 20
    }

    btn_find_item = tk.Button(main_window, text="Find Item", command=find_item, **button_config)
    btn_find_item.pack(pady=10)

    btn_borrow_item = tk.Button(main_window, text="Borrow Item", command=borrow_item, **button_config)
    btn_borrow_item.pack(pady=10)

    btn_return_item = tk.Button(main_window, text="Return Item", command=return_item, **button_config)
    btn_return_item.pack(pady=10)

    btn_donate_item = tk.Button(main_window, text="Donate Item", command=donate_item, **button_config)
    btn_donate_item.pack(pady=10)

    btn_find_event = tk.Button(main_window, text="Find Event", command=find_event, **button_config)
    btn_find_event.pack(pady=10)

    btn_register_event = tk.Button(main_window, text="Register for Event", command=register_event, **button_config)
    btn_register_event.pack(pady=10)

    btn_ask_librarian = tk.Button(main_window, text="Ask a Librarian", command=ask_librarian, **button_config)
    btn_ask_librarian.pack(pady=10)

    btn_add_balance = tk.Button(main_window, text="Add Balance", command=add_balance, **button_config)
    btn_add_balance.pack(pady=10)

    btn_logout = tk.Button(main_window, text="Logout", command=logout, **button_config)
    btn_logout.pack(pady=10)

    main_window.mainloop()

login_screen()

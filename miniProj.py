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
loans_label = None
balance_label = None

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
        item_data = items[0]
        info = (
            f"ItemID: {item_data[0]}\n"
            f"Type: {item_data[1]}\n"
            f"Title: {item_data[2]}\n"
            f"Author/Artist: {item_data[3]}\n"
            f"Publication Year: {item_data[4]}\n"
            f"Genre: {item_data[5]}\n"
            f"Availability: {item_data[6]}\n"
            f"Stock: {item_data[7]}\n"
        )
        messagebox.showinfo("Result", info)
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

    # Check if the user already has a loan for the same item which hasn't been returned yet
    cur.execute("SELECT * FROM Loans WHERE CustomerID=? AND ItemID=? AND ReturnDate IS NULL", (current_user_id, itemID))
    existing_loan = cur.fetchone()
    if existing_loan:
        messagebox.showinfo("Error", "You have already borrowed this item and haven't returned it. You cannot borrow the same item twice in a row.")
        return

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
    cur.execute("UPDATE Customers SET NumberOfLoans = NumberOfLoans + 1 WHERE CustomerID=?", (current_user_id,))

    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Borrowed item {itemID}. Due on {due_date}")
    update_loan_display()


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
    cur.execute("UPDATE Customers SET NumberOfLoans = NumberOfLoans - 1 WHERE CustomerID=?", (current_user_id,))

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
    update_balance_display()
    update_loan_display()


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
        event = events[0]
        messagebox.showinfo("Result", f"Found event {event[1]} in the room {event[2]}. Price: {event[5]} Audience: {event[4]} Attendees: {event[6]}/{event[7]}")
    else:
        messagebox.showerror("Error", "Event not found!")


def register_event():
    play_sound()
    
    # Step 1: Get the name of the currently logged-in user
    customer_name = get_logged_in_customer_name(current_user_id)
    if not customer_name:
        messagebox.showerror("Error", "There's an issue fetching the user details!")
        return

    eventID = simpledialog.askinteger("Register for Event", "Enter Event ID to register:")

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Events WHERE EventID=?", (eventID,))
    events = cur.fetchall()

    if not events:
        messagebox.showerror("Error", "Event not found!")
        return
    
    event = events[0]
    price = event[5]
    
    cur.execute("SELECT Balance FROM Customers WHERE Name=?", (customer_name,))
    customer = cur.fetchone()

    if not customer:
        messagebox.showerror("Error", "Customer not found!")
        return
    
    balance = customer[0]

    if balance < price:
        messagebox.showerror("Error", "Insufficient funds!")
        return

    new_balance = balance - price

    cur.execute("UPDATE Customers SET Balance=? WHERE Name=?", (new_balance, customer_name))
    cur.execute("UPDATE Events SET Number_of_Attendees = Number_of_Attendees + 1 WHERE EventID=?", (eventID,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Registered for event {event[2]}. New balance: {new_balance}")
    update_balance_display()

def get_logged_in_customer_name(customer_id):
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT Name FROM Customers WHERE CustomerID = ?", (customer_id,))
    name = cur.fetchone()

    conn.close()
    return name[0] if name else None


def get_logged_in_customer_name(customer_id):
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT Name FROM Customers WHERE CustomerID = ?", (customer_id,))
    name = cur.fetchone()

    conn.close()
    return name[0] if name else None

def volunteer_for_library():
    play_sound()

    # Get the logged in customer's name (assuming you have a variable 'logged_in_customer' storing this info)
    name = current_user_id

    conn = create_connection()
    cur = conn.cursor()
    
    # Check if the customer has already applied
    cur.execute("SELECT * FROM Employees WHERE Name = ? AND Type = 'Volunteering'", (name,))
    result = cur.fetchone()
    
    if result:
        # If result is not None, it means a record exists
        messagebox.showinfo("Already Applied", f"You've already applied for volunteering, {get_logged_in_customer_name(current_user_id)}.")
    else:
        # If no matching record, insert the customer into the Employees table as a volunteer
        cur.execute("INSERT INTO Employees (Name, Type) VALUES (?, 'Volunteering')", (name,))
        conn.commit()
        messagebox.showinfo("Success", f"Now you are a volunteer, {get_logged_in_customer_name(current_user_id)}.")
    
    conn.close()


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

def update_balance_display():
    global loans_label, balance_label

    # Fetch the updated balance and loans count
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT NumberOfLoans, Balance FROM Customers WHERE CustomerID = ?", (current_user_id,))
    data = cur.fetchone()
    number_of_loans = data[0]
    balance = data[1]
    conn.close()

    # Update the labels
    loans_label.config(text=f"Number of Loans: {number_of_loans}")
    balance_label.config(text=f"Balance: ${balance}")

def update_loan_display():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Loans WHERE CustomerID = ? AND ReturnDate IS NULL", (current_user_id,))
    data = cur.fetchone()
    number_of_loans = data[0]
    conn.close()

    # Update loans_var
    loans_var.set(f"Number of Loans: {number_of_loans}")

def main_screen():
    global main_window, loans_label, balance_label, loans_var
    main_window = tk.Tk()
    main_window.title("Library Application")
    
    loans_var = tk.StringVar()

    main_window.configure(bg='#f0f8ff')
    
    # Define default configurations
    default_label_config = {
        'bg': '#f0f8ff',
        'font': ('Arial', 12)
    }

    default_button_config = {
        'bg': '#007acc',
        'fg': 'white',
        'padx': 20,
        'pady': 10,
        'font': ('Arial', 12),
        'activebackground': '#005da2',
        'width': 20
    }

    lbl_title = tk.Label(main_window, text="Library Application", bg='#f0f8ff', font=("Arial", 24))
    lbl_title.pack(pady=20)

    name = get_logged_in_customer_name(current_user_id)

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT NumberOfLoans, Balance FROM Customers WHERE CustomerID = ?", (current_user_id,))
    data = cur.fetchone()
    number_of_loans = data[0]
    balance = data[1]
    conn.close()

    # Create labels for customer info with the default configuration
    customer_info_label = tk.Label(main_window, text=f"Customer: {name}", **default_label_config)
    customer_info_label.pack()

    loans_label = tk.Label(main_window, textvariable=loans_var, **default_label_config)
    loans_label.pack(pady=10)

    balance_label = tk.Label(main_window, text=f"Balance: ${balance}", **default_label_config)
    balance_label.pack()

    update_loan_display()

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

    btn_volunteer = tk.Button(main_window, text="Volunteer for Library", command=volunteer_for_library, **button_config)
    btn_volunteer.pack(pady=10)

    btn_add_balance = tk.Button(main_window, text="Add Balance", command=add_balance, **button_config)
    btn_add_balance.pack(pady=10)

    btn_logout = tk.Button(main_window, text="Logout", command=logout, **button_config)
    btn_logout.pack(pady=10)

    lbl_title = tk.Label(login_window, text="Library Application", **default_label_config)

    main_window.mainloop()

login_screen()

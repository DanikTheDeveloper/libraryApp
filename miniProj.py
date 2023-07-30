import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
import winsound 

def play_sound():
    winsound.PlaySound('C:\\Windows\\Media\\Windows Information Bar.wav', winsound.SND_ASYNC)


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
    play_sound()
    userID = simpledialog.askinteger("Borrow Item", "Enter your User ID:")
    itemID = simpledialog.askinteger("Borrow Item", "Enter Item ID:")
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Loans (CustomerID, ItemID, LoanDate, DueDate, ReturnDate) VALUES (?, ?, '2023-07-25', '2023-08-25')", (userID, itemID))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Borrowed item {itemID}")

def return_item():
    play_sound()
    userID = simpledialog.askinteger("Return Item", "Enter your User ID:")
    itemID = simpledialog.askinteger("Return Item", "Enter Item ID to return:")
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Loans WHERE userID=? AND itemID=?", (userID, itemID))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Returned item {itemID}")

def donate_item():
    play_sound()
    
    item_type = simpledialog.askstring("Donate Item", "Enter Item Type (e.g. book, CD, journal):")
    item_title = simpledialog.askstring("Donate Item", "Enter Item Title:")
    author_artist = simpledialog.askstring("Donate Item", "Enter Author/Artist:")
    publication_year = simpledialog.askinteger("Donate Item", "Enter Publication Year:")
    genre = simpledialog.askstring("Donate Item", "Enter Genre:")
    
    # Assuming all donated items start as 'Available' and with a stock of 1
    availability = 'Available'
    stock = 1
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Items (Type, Title, AuthorArtist, PublicationYear, Genre, Availability, Stock) VALUES (?, ?, ?, ?, ?, ?, ?)", (item_type, item_title, author_artist, publication_year, genre, availability, stock))
    
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
    userID = simpledialog.askinteger("Register for Event", "Enter your User ID:")
    eventID = simpledialog.askinteger("Register for Event", "Enter Event ID to register:")
    
    conn = create_connection()
    cur = conn.cursor()
    
    # Check if the user has already registered for the event
    cur.execute("SELECT * FROM EventRegistrations WHERE CustomerID=? AND EventID=?", (userID, eventID))
    registrations = cur.fetchall()
    
    if registrations:
        messagebox.showerror("Error", "You're already registered for this event!")
        return

    # Check if the event exists
    cur.execute("SELECT * FROM Events WHERE EventID=?", (eventID,))
    event_data = cur.fetchone()
    
    if not event_data:
        messagebox.showerror("Error", "The specified event does not exist!")
        return

    # Insert the registration into EventRegistrations
    cur.execute("INSERT INTO EventRegistrations (CustomerID, EventID, DateRegistered) VALUES (?, ?, date('now'))", (userID, eventID))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Success", f"Registered for event {eventID}")


def get_random_employee():
    """Fetch a random librarian (EmployeeID) from the database."""
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT EmployeeID FROM Events")
    all_employee_ids = [item[0] for item in cur.fetchall()]
    return random.choice(all_employee_ids)

def ask_librarian():
    play_sound()

    # Get the user ID
    userID = simpledialog.askinteger("Ask a Librarian", "Enter your User ID:")

    if userID is None:  # If the user closed the dialog or entered nothing
        return

    query = simpledialog.askstring("Ask a Librarian", "Enter your query:")
    
    if query:  # Check if the user provided a query (didn't just close the dialog box)
        random_employee = get_random_employee()
        conn = create_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO Queries (QueryText, UserID, EmployeeID) VALUES (?, ?, ?)", (query, userID, random_employee))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Your query has been submitted! Librarian with ID {random_employee} will get back to you soon.")
    else:
        messagebox.showwarning("Warning", "Query not provided!")

def main():
    root = tk.Tk()
    root.title("Library Application")

    root.configure(bg='#f0f8ff')  
    lbl_title = tk.Label(root, text="Library Application", bg='#f0f8ff', font=("Arial", 24))
    lbl_title.pack(pady=20)

    button_config = {
        'bg': '#007acc',
        'fg': 'white',
        'padx': 20,
        'pady': 10,
        'font': ('Arial', 12),
        'activebackground': '#005da2',
        'width': 20
    }

    btn_find_item = tk.Button(root, text="Find Item", command=find_item, **button_config)
    btn_find_item.pack(pady=10)

    btn_borrow_item = tk.Button(root, text="Borrow Item", command=borrow_item, **button_config)
    btn_borrow_item.pack(pady=10)

    btn_return_item = tk.Button(root, text="Return Item", command=return_item, **button_config)
    btn_return_item.pack(pady=10)

    btn_donate_item = tk.Button(root, text="Donate Item", command=donate_item, **button_config)
    btn_donate_item.pack(pady=10)

    btn_find_event = tk.Button(root, text="Find Event", command=find_event, **button_config)
    btn_find_event.pack(pady=10)

    btn_register_event = tk.Button(root, text="Register for Event", command=register_event, **button_config)
    btn_register_event.pack(pady=10)

    btn_ask_librarian = tk.Button(root, text="Ask a Librarian", command=ask_librarian, **button_config)
    btn_ask_librarian.pack(pady=10)

    root.mainloop()

main()

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
    cur.execute("SELECT * FROM Items WHERE name=?", (item_name,))
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
    cur.execute("INSERT INTO Borrowings (userID, itemID, borrow_date, due_date) VALUES (?, ?, '2023-07-25', '2023-08-25')", (userID, itemID))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Borrowed item {itemID}")

def return_item():
    play_sound()
    userID = simpledialog.askinteger("Return Item", "Enter your User ID:")
    itemID = simpledialog.askinteger("Return Item", "Enter Item ID to return:")
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Borrowings WHERE userID=? AND itemID=?", (userID, itemID))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Returned item {itemID}")

def donate_item():
    play_sound()
    item_name = simpledialog.askstring("Donate Item", "Enter Item Name:")
    item_type = simpledialog.askstring("Donate Item", "Enter Item Type (e.g. book, CD, journal):")
    
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Items (name, type) VALUES (?, ?)", (item_name, item_type))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Thank you for donating {item_name}!")

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
    # For simplicity, we're not adding a new table for event registration, but ideally, you'd want one.
    messagebox.showinfo("Success", f"Registered for event {eventID}")

def ask_librarian():
    play_sound()
    query = simpledialog.askstring("Ask a Librarian", "Enter your query:")
    # In a real-world scenario, this query would be stored and sent to librarians, but for now, we'll show a simple acknowledgment.
    messagebox.showinfo("Success", "Your query has been submitted! A librarian will get back to you soon.")

def main():
    root = tk.Tk()
    root.title("Library Application")

    # Design enhancements
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

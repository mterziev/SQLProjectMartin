import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                        item_id INTEGER PRIMARY KEY,
                        item_name TEXT NOT NULL,
                        price REAL NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY,
                        item_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        total_price REAL NOT NULL
                    )''')


def create_menu():
    menu_items = [
        ("Burger", 10.99),
        ("Pizza", 15.99),
        ("Fries", 4.99),
        ("Salad", 8.99),
        ("Pasta", 12.99),
        ("Coke", 2.99),
        ("Ice Cream", 3.99),
        ("Smoothie", 4.99),
        ("Noodles", 6.99)
    ]

    conn = sqlite3.connect("restaurant.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS menu")
    cursor.execute("CREATE TABLE menu (item_name TEXT, price REAL)")
    cursor.executemany("INSERT INTO menu VALUES (?, ?)", menu_items)

    conn.commit()
    conn.close()


def view_orders():
    def clear_all_orders():
        confirmation = messagebox.askquestion("Clear All Orders", "Are you sure you want to clear all orders?")
        if confirmation == "yes":
            cursor.execute("DELETE FROM orders")
            conn.commit()
            messagebox.showinfo("Orders Cleared", "All orders have been cleared.")
            # Close the current "View Orders" window
            orders_window.destroy()
            # Open a new "View Orders" window
            view_orders()

    def clear_order():
        selected_items = orders_table.selection()
        if not selected_items:
            messagebox.showinfo("Clear Order", "Please select an order to clear.")
            return

        confirmation = messagebox.askquestion("Clear Order", "Are you sure you want to clear the selected order?")
        if confirmation == "yes":
            for item in selected_items:
                order_id = orders_table.item(item, 'text')
                cursor.execute("DELETE FROM orders WHERE order_id=?", (order_id,))
            conn.commit()
            messagebox.showinfo("Order Cleared", "Selected order has been cleared.")
            # Close the current "View Orders" window
            orders_window.destroy()
            # Open a new "View Orders" window
            view_orders()

    orders_window = tk.Toplevel()
    orders_window.title("View Orders")
    orders_window.focus_force()

    # Create a Treeview widget to display the orders
    orders_table = ttk.Treeview(orders_window)
    orders_table['columns'] = ('Item Name', 'Quantity', 'Total Price')
    orders_table.heading('#0', text='Order ID')
    orders_table.column('#0', width=80)
    orders_table.heading('Item Name', text='Item Name')
    orders_table.column('Item Name', width=200)
    orders_table.heading('Quantity', text='Quantity')
    orders_table.column('Quantity', width=100)
    orders_table.heading('Total Price', text='Total Price')
    orders_table.column('Total Price', width=120)

    # Retrieve the orders from the database
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    total_price = 0  # Variable to hold the sum of total prices

    # Insert orders into the Treeview widget and calculate total price
    for order in orders:
        item_name = order[1]
        quantity = order[2]
        price = cursor.execute("SELECT price FROM menu WHERE item_name=?", (item_name,)).fetchone()[0]
        order_total_price = round(price * quantity, 2)  # Round the total price to two decimal places
        total_price += order_total_price
        orders_table.insert('', tk.END, text=order[0], values=(item_name, quantity, order_total_price))

    # Create a button to clear all orders
    clear_all_button = ttk.Button(orders_window, text="Clear All Orders", command=clear_all_orders)
    clear_all_button.pack(pady=10)

    # Create a button to clear an individual order
    clear_order_button = ttk.Button(orders_window, text="Clear Order", command=clear_order)
    clear_order_button.pack()

    # Pack the Treeview widget
    orders_table.pack(padx=10, pady=10)

    # Create a label to display the total price
    total_price_label = ttk.Label(orders_window, text=f"Total Price: ${round(total_price, 2):.2f}")
    total_price_label.pack(side=tk.BOTTOM, pady=10)

    # Configure the window size
    orders_window.geometry("550x400")

    # Start the main event loop
    orders_window.mainloop()


def place_order():
    # Retrieve and display the menu
    cursor.execute("SELECT item_name, price FROM menu")
    menu_items = cursor.fetchall()

    order_window = tk.Toplevel()
    order_window.title("Place Order")
    order_window.geometry("350x200")  # Set the size of the window
    order_window.focus_force()

    # Create a label and entry for selecting the item
    item_label = tk.Label(order_window, text="Select Item:")
    item_label.pack()

    item_entry = ttk.Combobox(order_window, values=[item[0] for item in menu_items])
    item_entry.pack()

    # Create a label and entry for entering the quantity
    quantity_label = tk.Label(order_window, text="Enter Quantity:")
    quantity_label.pack()

    quantity_entry = ttk.Entry(order_window)
    quantity_entry.pack()

    def add_to_order():
        item_name = item_entry.get()
        quantity = int(quantity_entry.get())

        if quantity <= 0:
            messagebox.showinfo("Invalid Quantity", "Please enter a positive quantity.")
            return

        # Retrieve the price of the selected item
        price = next((item[1] for item in menu_items if item[0] == item_name), None)
        if price is None:
            messagebox.showinfo("Invalid Item", "Please select a valid item from the menu.")
            return

        # Calculate the total price and round it to two decimal places
        total_price = price * quantity
        rounded_total_price = round(total_price, 2)

        # Insert the order into the database
        cursor.execute("INSERT INTO orders (item_name, quantity, total_price) VALUES (?, ?, ?)",
                       (item_name, quantity, rounded_total_price))
        conn.commit()

        # Show a confirmation message
        confirmation_text = f"Order placed:\n{quantity} {item_name}(s)\nTotal price: ${rounded_total_price:.2f}"
        confirmation_label.config(text=confirmation_text)

        # Clear the input fields
        item_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)

    # Create a button to add the order to the database
    add_button = ttk.Button(order_window, text="Add to Order", command=add_to_order)
    add_button.pack(pady=10)

    # Create a label for displaying the order confirmation
    confirmation_label = tk.Label(order_window, text="", font=("Arial", 12, "bold"), wraplength=250)
    confirmation_label.pack()


def view_menu():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price FROM menu")
    menu_items = cursor.fetchall()
    conn.close()

    root = tk.Tk()
    root.title("Menu")

    menu_label = tk.Label(root, text="Menu", font=("Arial", 16, "bold"))
    menu_label.pack(pady=20)

    for item in menu_items:
        item_name = item[0]
        price = item[1]
        item_label = tk.Label(root, text=f"{item_name}: ${price}")
        item_label.pack()

    back_button = ttk.Button(root, text="Back", command=root.destroy)
    back_button.pack(pady=20)

    root.mainloop()


def main():
    root = tk.Tk()
    root.title("Restaurant Ordering System")

    welcome_label = tk.Label(root, text="Welcome to our restaurant!", font=("Arial", 16, "bold"))
    welcome_label.pack(pady=20)

    menu_button = ttk.Button(root, text="View Menu", command=view_menu)
    menu_button.pack(pady=10)

    order_button = ttk.Button(root, text="Place Order", command=place_order)
    order_button.pack(pady=10)

    view_orders_button = ttk.Button(root, text="View Orders", command=view_orders)
    view_orders_button.pack(pady=10)

    root.mainloop()


# Create the tables if they don't exist
conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()

create_tables()
create_menu()

# Run the main function
main()

# Close the database connection
conn.close()

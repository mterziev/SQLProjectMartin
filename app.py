import sqlite3

from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)


def create_tables():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


def create_menu():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu")
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return

    menu_items = [
    ]
    cursor.executemany("INSERT INTO menu (item_name, price) VALUES (?, ?)", menu_items)
    conn.commit()
    conn.close()


def get_menu_items():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT item_name, price FROM menu")
    menu_items = cursor.fetchall()

    conn.close()

    return menu_items


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/menu')
def view_menu():
    menu_items = get_menu_items()
    return render_template('menu.html', menu_items=menu_items)


@app.route('/order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])

        if quantity <= 0:
            return "Invalid quantity. Please enter a positive number."

        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()

        cursor.execute("SELECT price FROM menu WHERE item_name=?", (item_name,))
        price = cursor.fetchone()[0]

        total_price = price * quantity

        cursor.execute("INSERT INTO orders (item_name, quantity, total_price) VALUES (?, ?, ?)",
                       (item_name, quantity, total_price))
        conn.commit()
        conn.close()

        return redirect(url_for('view_orders'))

    menu_items = get_menu_items()
    return render_template('place_order.html', menu_items=menu_items)


@app.route('/view_orders')
def view_orders():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    total_price = 0  # Variable to hold the sum of total prices

    for order in orders:
        item_name = order[1]
        quantity = order[2]
        cursor.execute("SELECT price FROM menu WHERE item_name=?", (item_name,))
        price = cursor.fetchone()[0]
        order_total_price = price * quantity
        total_price += order_total_price

    total_price = round(total_price, 2)  # Format total_price to 2 decimal places

    return render_template('view_orders.html', orders=orders, total_price=total_price)


def get_cursor():
    if 'cursor' not in g:
        conn = sqlite3.connect('restaurant.db')
        g.cursor = conn.cursor()
    return g.cursor


if __name__ == '__main__':
    create_tables()
    create_menu()
    app.run()

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ================= DATABASE =================
conn = sqlite3.connect("food_system.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    items TEXT,
    total REAL
)
""")

conn.commit()
conn.close()

# ================= MAIN =================
root = tk.Tk()
root.title("Smart Food Ordering & Queue System")
root.geometry("1000x600")

# ================= FRAMES =================
login_frame = tk.Frame(root)
register_frame = tk.Frame(root)
menu_frame = tk.Frame(root)

for frame in (login_frame, register_frame, menu_frame):
    frame.grid(row=0, column=0, sticky="nsew")

def show_frame(frame):
    frame.tkraise()

# ================= REGISTER =================
tk.Label(register_frame, text="Register", font=("Arial", 18)).pack(pady=10)

reg_user = tk.Entry(register_frame)
reg_pass = tk.Entry(register_frame, show="*")

tk.Label(register_frame, text="Username").pack()
reg_user.pack()

tk.Label(register_frame, text="Password").pack()
reg_pass.pack()

def register():
    try:
        conn = sqlite3.connect("food_system.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?)",
                       (reg_user.get(), reg_pass.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Registered Successfully")
        show_frame(login_frame)
    except:
        messagebox.showerror("Error", "User already exists")

tk.Button(register_frame, text="Register", command=register).pack(pady=5)
tk.Button(register_frame, text="Go to Login",
          command=lambda: show_frame(login_frame)).pack()

# ================= LOGIN =================
tk.Label(login_frame, text="Login", font=("Arial", 18)).pack(pady=10)

login_user = tk.Entry(login_frame)
login_pass = tk.Entry(login_frame, show="*")

tk.Label(login_frame, text="Username").pack()
login_user.pack()

tk.Label(login_frame, text="Password").pack()
login_pass.pack()

current_user = ""

def login():
    global current_user
    conn = sqlite3.connect("food_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (login_user.get(), login_pass.get()))
    result = cursor.fetchone()
    conn.close()

    if result:
        current_user = login_user.get()
        show_frame(menu_frame)
        display_orders()
    else:
        messagebox.showerror("Error", "Invalid login")

tk.Button(login_frame, text="Login", command=login).pack(pady=5)
tk.Button(login_frame, text="Create Account",
          command=lambda: show_frame(register_frame)).pack()

# ================= MENU =================
tk.Label(menu_frame, text="Food Ordering System",
         font=("Arial", 16, "bold")).pack(pady=5)

main_frame = tk.Frame(menu_frame)
main_frame.pack(fill="both", expand=True)

# ===== LEFT (MENU) =====
left_frame = tk.LabelFrame(main_frame, text="Menu", padx=10, pady=10)
left_frame.grid(row=0, column=0, padx=10, sticky="n")

menu_items = {
    "Burger": 2.5,
    "Pizza": 3.0,
    "Juice": 1.5,
    "Coffee": 1.0
}

items_vars = {}

for i, (item, price) in enumerate(menu_items.items()):
    tk.Label(left_frame, text=item).grid(row=i, column=0)
    tk.Label(left_frame, text=f"${price}").grid(row=i, column=1)

    qty = tk.IntVar(value=0)
    tk.Spinbox(left_frame, from_=0, to=10, textvariable=qty, width=5).grid(row=i, column=2)

    items_vars[item] = (qty, price)

# ===== RIGHT (ORDERS) =====
right_frame = tk.LabelFrame(main_frame, text="Queue", padx=10, pady=10)
right_frame.grid(row=0, column=1)

columns = ("Queue No", "User", "Items", "Total")
tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack()

# ================= FUNCTIONS =================
def place_order():
    order_list = []
    total = 0

    for item, (qty_var, price) in items_vars.items():
        qty = qty_var.get()
        if qty > 0:
            subtotal = qty * price
            order_list.append(f"{item} x{qty}")
            total += subtotal

    if not order_list:
        messagebox.showerror("Error", "Select items")
        return

    conn = sqlite3.connect("food_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (username, items, total) VALUES (?, ?, ?)",
                   (current_user, ", ".join(order_list), total))
    conn.commit()
    conn.close()

    show_invoice(order_list, total)
    display_orders()

def display_orders():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("food_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", tk.END, values=row)

def delete_order():
    selected = tree.focus()
    values = tree.item(selected, "values")

    if not values:
        messagebox.showerror("Error", "Select order")
        return

    conn = sqlite3.connect("food_system.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id=?", (values[0],))
    conn.commit()
    conn.close()

    display_orders()

def show_invoice(order_list, total):
    invoice = tk.Toplevel(root)
    invoice.title("Invoice")
    invoice.geometry("300x300")

    tk.Label(invoice, text="Invoice", font=("Arial", 16)).pack(pady=10)

    for item in order_list:
        tk.Label(invoice, text=item).pack()

    tk.Label(invoice, text=f"Total: ${total}", fg="green").pack(pady=10)

# ================= BUTTONS =================
btn_frame = tk.Frame(menu_frame)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Place Order", bg="green", fg="white",
          command=place_order).grid(row=0, column=0, padx=5)

tk.Button(btn_frame, text="Delete Order", bg="red", fg="white",
          command=delete_order).grid(row=0, column=1, padx=5)

tk.Button(btn_frame, text="Logout",
          command=lambda: show_frame(login_frame)).grid(row=0, column=2, padx=5)

# ================= START =================
show_frame(login_frame)
root.mainloop()


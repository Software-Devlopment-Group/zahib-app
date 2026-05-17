import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import datetime



conn = sqlite3.connect("food_orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food TEXT,
    price REAL,
    status TEXT,
    order_time TEXT
)
""")

conn.commit()

root = tk.Tk()
root.title("Food Ordering System")
root.geometry("550x650")
root.configure(bg="#f4f4f4")


main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=1)

canvas = tk.Canvas(
    main_frame,
    bg="#f4f4f4",
    highlightthickness=0
)

canvas.pack(side="left", fill="both", expand=1)

scrollbar = tk.Scrollbar(
    main_frame,
    orient="vertical",
    command=canvas.yview
)

scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

canvas.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

second_frame = tk.Frame(
    canvas,
    bg="#f4f4f4"
)

canvas.create_window(
    (0, 0),
    window=second_frame,
    anchor="nw"
)



tk.Label(
    second_frame,
    text="Food Ordering System",
    font=("Arial", 18, "bold"),
    bg="#f4f4f4",
    fg="#333"
).pack(pady=15)


prices = {
    "Burger": 2.5,
    "Pizza": 3,
    "Pasta": 2,
    "Juice": 1
}

cart = []


container = tk.Frame(
    second_frame,
    bg="#f4f4f4"
)

container.pack()


def add_item(item):

    cart.append(item)

    update_cart()


def food_card(parent, name, price, row, col):

    frame = tk.Frame(
        parent,
        bg="white",
        bd=3,
        relief="ridge",
        padx=8,
        pady=8
    )

    frame.grid(
        row=row,
        column=col,
        padx=10,
        pady=10
    )

    emoji = {
        "Burger": "🍔",
        "Pizza": "🍕",
        "Pasta": "🍝",
        "Juice": "🧃"
    }

    tk.Label(
        frame,
        text=emoji[name],
        font=("Arial", 22),
        bg="white"
    ).pack()

    tk.Label(
        frame,
        text=name,
        font=("Arial", 12, "bold"),
        fg="#333",
        bg="white"
    ).pack(pady=5)

    tk.Label(
        frame,
        text=f"{price} OMR",
        font=("Arial", 10, "bold"),
        fg="#4CAF50",
        bg="white"
    ).pack(pady=5)

    tk.Button(
        frame,
        text="Add to Cart",
        bg="#ff9800",
        fg="white",
        activebackground="#f57c00",
        activeforeground="white",
        font=("Arial", 10, "bold"),
        width=12,
        bd=0,
        padx=5,
        pady=5,
        cursor="hand2",
        command=lambda: add_item(name)
    ).pack(pady=5)


food_card(container, "Pasta", 2, 0, 0)
food_card(container, "Juice", 1, 0, 1)
food_card(container, "Burger", 2.5, 1, 0)
food_card(container, "Pizza", 3, 1, 1)


cart_frame = tk.Frame(
    second_frame,
    bg="white",
    bd=2,
    relief="ridge"
)

cart_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)



tk.Label(
    cart_frame,
    text="Selected Items",
    font=("Arial", 13, "bold"),
    bg="white",
    fg="#333"
).pack(pady=8)


listbox_frame = tk.Frame(
    cart_frame,
    bg="white"
)

listbox_frame.pack(pady=8)

scrollbar_list = tk.Scrollbar(listbox_frame)

scrollbar_list.pack(
    side="right",
    fill="y"
)

cart_listbox = tk.Listbox(
    listbox_frame,
    width=45,
    height=10,
    font=("Arial", 11),
    bd=1,
    relief="solid",
    yscrollcommand=scrollbar_list.set
)

cart_listbox.pack(side="left")

scrollbar_list.config(
    command=cart_listbox.yview
)


total_label = tk.Label(
    cart_frame,
    text="Total Price: 0 OMR",
    font=("Arial", 12, "bold"),
    bg="white",
    fg="green"
)

total_label.pack(pady=5)


def update_cart():

    cart_listbox.delete(0, tk.END)

    total = 0

    item_count = {}

    for item in cart:

        if item in item_count:

            item_count[item] += 1

        else:

            item_count[item] = 1

    for item, quantity in item_count.items():

        price = prices[item] * quantity

        total += price

        cart_listbox.insert(
            tk.END,
            f"{item} x{quantity} - {price} OMR"
        )

    total_label.config(
        text=f"Total Price: {total} OMR"
    )



def remove_item():

    selected = cart_listbox.curselection()

    if selected:

        index = selected[0]

        item_text = cart_listbox.get(index)

        item_name = item_text.split(" x")[0]

        cart.remove(item_name)

        update_cart()

    else:

        messagebox.showwarning(
            "Warning",
            "Please select an item to remove"
        )



def track_order():

    track_win = tk.Toplevel()

    track_win.title("Order Tracking")

    track_win.geometry("400x300")

    track_win.configure(bg="#f4f4f4")

    tk.Label(
        track_win,
        text="📦 Order Tracking",
        font=("Arial", 14, "bold"),
        bg="#f4f4f4"
    ).pack(pady=12)

    status_label = tk.Label(
        track_win,
        text="Preparing Order...",
        font=("Arial", 14),
        fg="orange",
        bg="#f4f4f4"
    )

    status_label.pack(pady=12)

    progress = ttk.Progressbar(
        track_win,
        orient="horizontal",
        length=300,
        mode="determinate"
    )

    progress.pack(pady=20)

    steps = [

        ("Preparing Order...", 20, "orange"),

        ("Cooking...", 50, "blue"),

        ("Ready for Pickup", 100, "green")
    ]

    i = 0

    def update_status():

        nonlocal i

        if i < len(steps):

            text, value, color = steps[i]

            status_label.config(
                text=text,
                fg=color
            )

            progress["value"] = value

            i += 1

            track_win.after(2000, update_status)

        else:

            messagebox.showinfo(
                "Completed",
                "Your order is Ready for pickup"
            )

    update_status()



def place_order():

    if not cart:

        messagebox.showwarning(
            "Warning",
            "Cart is empty!"
        )

        return

    for item in cart:

        cursor.execute(
            """
            INSERT INTO orders
            (food, price, status, order_time)
            VALUES (?, ?, ?, ?)
            """,

            (
                item,
                prices[item],
                "Queued",
                datetime.datetime.now().strftime("%H:%M")
            )
        )

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Order placed successfully"
    )

    track_order()

    cart.clear()

    update_cart()



button_frame = tk.Frame(
    cart_frame,
    bg="white"
)

button_frame.pack(pady=10)


tk.Button(
    button_frame,
    text="Place Order",
    width=18,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
    bd=0,
    pady=5,
    cursor="hand2",
    command=place_order
).grid(row=0, column=0, padx=10)



tk.Button(
    button_frame,
    text="Remove Selected Item",
    width=18,
    bg="#f44336",
    fg="white",
    font=("Arial", 10, "bold"),
    bd=0,
    pady=5,
    cursor="hand2",
    command=remove_item
).grid(row=0, column=1, padx=10)


root.mainloop()
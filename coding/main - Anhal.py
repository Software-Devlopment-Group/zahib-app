import tkinter as tk
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import winsound
import matplotlib.pyplot as plt
import datetime
import hashlib

# PATH

base_path = os.path.dirname(__file__)

def load_image(name):
    return ImageTk.PhotoImage(
        Image.open(os.path.join(base_path,"images",name)).resize((100,100))
    )

#DATABASE

conn = sqlite3.connect("orders.db")
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
    food TEXT,
    price REAL,
    status TEXT,
    rating INTEGER,
    time TEXT
)
""")

conn.commit()

current_user = ""

#REGISTER

def open_register():
    win = tk.Toplevel()
    win.title("Register")
    win.geometry("300x280")

    tk.Label(win,text="📝 Create Account",
             font=("Arial",14,"bold")).pack(pady=10)

    tk.Label(win,text="Username").pack()
    user = tk.Entry(win)
    user.pack()

    tk.Label(win,text="Password").pack()
    pwd = tk.Entry(win,show="*")
    pwd.pack()

    def register():
        try:
            hashed = hashlib.sha256(pwd.get().encode()).hexdigest()

            cursor.execute("INSERT INTO users VALUES (?,?)",(user.get(),hashed))
            conn.commit()
            messagebox.showinfo("Success","Account created ✅")
            win.destroy()
        except:
            messagebox.showerror("Error","User already exists ❌")

    tk.Button(win,text="Register",
              bg="#4CAF50",fg="white",
              command=register).pack(pady=10)

#LOGIN

def login():
    global current_user
    u = username_entry.get()
    p = password_entry.get()

    if u == "staff" and p == "admin":
        open_staff()
        return

    hashed = hashlib.sha256(p.encode()).hexdigest()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",(u,hashed))
    if cursor.fetchone():
        current_user = u
        open_menu()
    else:
        message.config(text="❌ Wrong login")

#MENU

def open_menu():
    win = tk.Toplevel()
    win.title("Menu")
    win.geometry("700x650")
    win.configure(bg="#f8f9fb")

    tk.Label(win,text=f"Welcome {current_user} 👋",
             bg="#f8f9fb").pack()

    tk.Label(win,text="🍔 Food Menu",
             font=("Arial",18,"bold"),
             bg="#f8f9fb").pack(pady=10)

    burger = load_image("1.jpeg")
    pizza = load_image("2.jpeg")
    pasta = load_image("3.jpeg")
    juice = load_image("4.jpeg")

    prices = {
        "Burger 🍔":1.5,
        "Pizza 🍕":2,
        "Pasta 🍝":2.5,
        "Juice 🧃":1
    }

    cart=[]

    container = tk.Frame(win,bg="#f8f9fb")
    container.pack()

    def add(item):
        cart.append(item)
        update_cart()

    def card(parent,img,name,price,row,col):
        f = tk.Frame(parent,bg="white",bd=1,relief="solid")
        f.grid(row=row,column=col,padx=15,pady=15)

        tk.Label(f,image=img,bg="white").pack()
        tk.Label(f,text=name,bg="white").pack()
        tk.Label(f,text=f"{price} OMR",bg="white",fg="green").pack()

        tk.Button(f,text="Add",bg="#4CAF50",fg="white",
                  command=lambda:add(name)).pack(pady=5)

    card(container,burger,"Burger 🍔",1.5,0,0)
    card(container,pizza,"Pizza 🍕",2,0,1)
    card(container,pasta,"Pasta 🍝",2.5,1,0)
    card(container,juice,"Juice 🧃",1,1,1)

    cart_box = tk.Frame(win,bg="white")
    cart_box.pack(fill="x",padx=20,pady=10)

    cart_text = tk.Label(cart_box,bg="white")
    cart_text.pack()

    def update_cart():
        total=0
        text=""
        for i in cart:
            total+=prices[i]
            text+=f"{i} - {prices[i]} OMR\n"
        text+=f"\nTotal: {total} OMR"
        cart_text.config(text=text)

    def order():
        
        if not cart:
            messagebox.showwarning("Warning","Cart empty ❗")
            return

        for i in cart:
            cursor.execute(
    "INSERT INTO orders (username,food,price,status,time) VALUES (?,?,?,?,?)",
    (current_user,i,prices[i],"Queued", datetime.datetime.now().strftime("%H"))

)
            

        conn.commit()
        open_tracking()
        cart.clear()
        update_cart()

    tk.Button(win,text="Place Order",
              bg="#ff5722",fg="white",
              command=order).pack(pady=10)

    tk.Button(win,text="📜 History",command=open_history).pack()

    win.images=[burger,pizza,pasta,juice]

#STAFF

def open_staff():
    win = tk.Toplevel()
    win.title("Staff Panel")
    win.geometry("400x500")

    tk.Label(win,text="👩‍🍳 Staff Panel",
             font=("Arial",14,"bold")).pack()

    display = tk.Text(win,height=12)
    display.pack()

    #LOAD
    def load():
        display.delete("1.0",tk.END)
        cursor.execute("SELECT username,food,status FROM orders")
        for row in cursor.fetchall():
            display.insert(tk.END,f"{row[0]} - {row[1]} ({row[2]})\n")

    #TOP ITEM

    def stats():
        cursor.execute("""
        SELECT food,COUNT(*) FROM orders
        GROUP BY food
        ORDER BY COUNT(*) DESC LIMIT 1
        """)
        r=cursor.fetchone()
        messagebox.showinfo("Top Item",f"{r[0]} 🔥 ({r[1]} orders)")

    #CHART

    def show_chart():
        cursor.execute("SELECT food, COUNT(*) FROM orders GROUP BY food")
        data = cursor.fetchall()

        foods = [row[0] for row in data]
        counts = [row[1] for row in data]

        import matplotlib.pyplot as plt
        plt.figure()
        plt.bar(foods, counts)
        plt.title("Most Ordered Food")
        plt.xlabel("Food")
        plt.ylabel("Orders")
        plt.show()

    #PEAK HOUR

    def peak_hour():
        cursor.execute("""
        SELECT time, COUNT(*) FROM orders
        GROUP BY time
        ORDER BY COUNT(*) DESC LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            messagebox.showinfo("Peak Hour 🔥",
                                f"Most orders at {result[0]}:00 ({result[1]} orders)")
        else:
            messagebox.showinfo("Info","No data yet")

    #AVG RATING 

    def avg_rating():
        cursor.execute("""
        SELECT food, AVG(rating) FROM orders
        WHERE rating IS NOT NULL
        GROUP BY food
        """)
        
        data = cursor.fetchall()
        
        text = ""
        for d in data:
            text += f"{d[0]} ⭐ {round(d[1],1)}\n"
        
        messagebox.showinfo("Average Rating ⭐", text)


    tk.Button(win,text="Load Orders",command=load).pack(pady=5)
    tk.Button(win,text="Top Item",command=stats).pack(pady=5)
    tk.Button(win,text="📊 Chart",command=show_chart).pack(pady=5)
    tk.Button(win,text="⭐ Avg Rating",command=avg_rating).pack(pady=5)
    tk.Button(win,text="⏰ Peak Hour",command=peak_hour).pack(pady=5)



def open_history():
    win = tk.Toplevel()
    win.title("Order History")

    cursor.execute("SELECT food,price,status,rating FROM orders WHERE username=?", (current_user,))
    rows = cursor.fetchall()

    text=""
    for r in rows:
        stars = "⭐" * r[3] if r[3] else "No rating"
        text += f"{r[0]} - {r[1]} OMR ({r[2]}) | {stars}\n"

    tk.Label(win,text=text).pack(padx=10,pady=10)



def open_tracking():
    win = tk.Toplevel()
    win.title("Order Tracking")
    win.geometry("400x500")
    win.configure(bg="#f8f9fb")

    tk.Label(win,
             text="👨‍🍳 Preparing your order",
             font=("Arial",16,"bold"),
             bg="#f8f9fb").pack(pady=10)

    status = tk.Label(win,
                      text="Preparing...",
                      font=("Arial",13),
                      fg="orange",
                      bg="#f8f9fb")
    status.pack(pady=5)
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status='Queued'")
    position = cursor.fetchone()[0]

    queue_label = tk.Label(win, text=f"📍 Your position in queue: {position}", 
                            bg="#f8f9fb",
                            font=("Arial",12))
    queue_label.pack(pady=5)


    #GIF

    gif_path = os.path.join(base_path, "images", "chef.gif")
    frames = []
    try:
        gif = Image.open(gif_path)
        while True:
            frames.append(ImageTk.PhotoImage(gif.copy().resize((200,200))))
            gif.seek(len(frames))
    except:
        print("GIF not found")

    gif_label = tk.Label(win, bg="#f8f9fb")
    gif_label.pack(pady=10)

    def animate(i=0):
        if frames:
            gif_label.config(image=frames[i])
            win.after(100, animate, (i+1) % len(frames))

    animate()

    #STEPS

    steps = ["👨‍🍳 Preparing...", "🍳 Cooking...", "🔥 Almost Ready...", "✅ Ready!"]
    i = 0

    def update():
        nonlocal i
        status.config(text=steps[i])
        i += 1

        if i == len(steps):
            winsound.PlaySound(os.path.join(base_path,"images","done.wav"), winsound.SND_FILENAME)
            messagebox.showinfo("Done","Your order is ready 🎉")

        
            show_rating()

        else:
            win.after(1500, update)

    update()

def show_rating():
    win = tk.Toplevel()
    win.title("Rate Order")
    win.geometry("400x300")
    win.configure(bg="#f8f9fb")

    tk.Label(win,
             text="⭐ Rate your experience",
             font=("Arial",16,"bold"),
             bg="#f8f9fb").pack(pady=15)

    selected = tk.IntVar()

    stars_frame = tk.Frame(win, bg="#f8f9fb")
    stars_frame.pack()

    stars = []

    def highlight(n):
        for i, star in enumerate(stars):
            if i < n:
                star.config(text="⭐", fg="gold")
            else:
                star.config(text="☆", fg="gray")

    def select(n):
        selected.set(n)
        highlight(n)

    for i in range(5):
        lbl = tk.Label(stars_frame,
                       text="☆",
                       font=("Arial",30),
                       bg="#f8f9fb",
                       cursor="hand2")
        lbl.grid(row=0, column=i, padx=5)

        lbl.bind("<Button-1>", lambda e, n=i+1: select(n))
        stars.append(lbl)

    def submit():
        if selected.get() == 0:
            messagebox.showwarning("Warning","Select rating ⭐")
            return

    
        cursor.execute("""
            UPDATE orders
            SET rating = ?
            WHERE id = (SELECT MAX(id) FROM orders WHERE username = ?)
        """, (selected.get(), current_user))

        conn.commit()

        messagebox.showinfo("Thank you 💛","Thanks for your feedback!")
        win.destroy()

    tk.Button(win,
              text="Submit",
              bg="#ff9800",
              fg="white",
              font=("Arial",12,"bold"),
              command=submit).pack(pady=20)


    #GIF

    gif_path = os.path.join(base_path, "images", "chef.gif")

    frames = []
    try:
        gif = Image.open(gif_path)
        while True:
            frames.append(ImageTk.PhotoImage(gif.copy().resize((200,200))))
            gif.seek(len(frames))
    except:
        print("⚠️ GIF not found")

    gif_label = tk.Label(win, bg="#f8f9fb")
    gif_label.pack(pady=10)

    #animation 

    def animate(i=0):
        if frames:
            gif_label.config(image=frames[i])
            win.after(100, animate, (i+1) % len(frames))

    animate()

    # Order prosses

    steps = ["👨‍🍳 Preparing...", "🍳 Cooking...", "🔥 Almost Ready...", "✅ Ready!"]
    i = 0

    def update():
        nonlocal i
        status.config(text=steps[i])
        i += 1

        if i == len(steps):
            winsound.PlaySound(os.path.join(base_path,"images","done.wav"), winsound.SND_FILENAME)
            messagebox.showinfo("Done","Your order is ready 🎉")
        else:
            win.after(1500, update)

    update()




#MAIN UI

root = tk.Tk()
root.title("zahib")
root.geometry("420x420")
root.configure(bg="#f8f9fb")

tk.Label(root,text="🍽 zahib",
         font=("Arial",18,"bold"),
         bg="#f8f9fb").pack(pady=15)

tk.Label(root,
         text="👤 User: Order food\n👩‍🍳 Staff: Manage orders",
         bg="#f8f9fb",fg="#555").pack()

card = tk.Frame(root,bg="white",bd=1,relief="solid")
card.pack(padx=30,pady=15,fill="both")

tk.Label(card,text="Username",bg="white").pack(pady=(10,5))
username_entry = tk.Entry(card)
username_entry.pack()

tk.Label(card,text="Password",bg="white").pack(pady=(10,5))
password_entry = tk.Entry(card,show="*")
password_entry.pack()

tk.Button(card,text="Login",
          bg="#4CAF50",fg="white",
          command=login).pack(pady=10)

tk.Button(card,text="Register",
          command=open_register).pack()

tk.Label(root,
         text="💡 Staff login: staff / admin",
         bg="#f8f9fb",fg="#888").pack()

message = tk.Label(root,text="",fg="red",bg="#f8f9fb")
message.pack()

root.mainloop()
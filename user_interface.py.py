import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


root = tk.Tk()
root.title("zahib System")
root.geometry("400x400")

 # store curent page  
current_frame = None

def clear_frame():
    global current_frame
    if current_frame is not None:
        current_frame.destroy()

# login

def show_login():
    global current_frame
    clear_frame()

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    current_frame = frame

    tk.Label(frame, text="Login", font=("Arial", 18)).pack(pady=20)

    username = tk.Entry(frame)
    username.pack(pady=5)

    password = tk.Entry(frame, show="*")
    password.pack(pady=5)

    def login():
        if username.get() == "admin" and password.get() == "1234":
            show_menu()
        else:
            tk.Label(frame, text="Login Failed", fg="red").pack()

    tk.Button(frame, text="Login", command=login).pack(pady=10)
    tk.Button(frame, text="Go to Register", command=show_register).pack()

# register 

def show_register():
    global current_frame
    clear_frame()

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    current_frame = frame

    tk.Label(frame, text="Register", font=("Arial", 18)).pack(pady=20)

    username = tk.Entry(frame)
    username.pack(pady=5)

    password = tk.Entry(frame, show="*")
    password.pack(pady=5)

    def register():
        print("Registered:", username.get())

    tk.Button(frame, text="Register", command=register).pack(pady=10)
    tk.Button(frame, text="Back to Login", command=show_login).pack()

# menu 

def show_menu():
    global current_frame
    clear_frame()

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)
    current_frame = frame

    tk.Label(frame, text="Main Menu", font=("Arial", 18)).pack(pady=20)

    tk.Button(frame, text="Browse Menu").pack(pady=5)
    tk.Button(frame, text="Place Order").pack(pady=5)
    tk.Button(frame, text="View Queue").pack(pady=5)
    

# start with login screen 

show_login()

root.mainloop()
import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import subprocess

class Scheduler:
    def __init__(self, root):
        self.root = root
        self.initialize_db()
        self.create_main_window()

    def initialize_db(self):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT NOT NULL,
                     password TEXT NOT NULL,
                     first_name TEXT NOT NULL,
                     middle_initial TEXT,
                     last_name TEXT NOT NULL,
                     birthday TEXT NOT NULL,
                     address TEXT NOT NULL,
                     contact_info TEXT NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS schedules (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER NOT NULL,
                     schedule_date TEXT NOT NULL,
                     start_time TEXT NOT NULL,
                     end_time TEXT NOT NULL,
                     FOREIGN KEY (user_id) REFERENCES users (id))''')

        conn.commit()
        conn.close()

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password")
            return
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            messagebox.showinfo("Login Info", "Login complete")
            if username == 'admin':
                self.open_admin_panel()
            else:
                # Write user info to a temporary file
                user_info_file = 'user_info.txt'
                with open(user_info_file, 'w') as f:
                    f.write(f"username: {user[1]}\n")
                    f.write(f"password: {user[2]}\n")
                    f.write(f"first_name: {user[3]}\n")
                    f.write(f"middle_initial: {user[4]}\n")
                    f.write(f"last_name: {user[5]}\n")
                    f.write(f"birthday: {user[6]}\n")
                    f.write(f"address: {user[7]}\n")
                    f.write(f"contact_info: {user[8]}\n")

                # Run face_recognition.py with the user info file path
                subprocess.Popen(["python", "face_recognition.py", user_info_file])
        else:
            messagebox.showwarning("Login Info", "Username and password do not exist")

    def open_admin_panel(self):
        admin_panel = tk.Toplevel(self.root)
        admin_panel.title("Admin Panel")

        tk.Label(admin_panel, text="Admin Panel").grid(row=0, column=0, columnspan=2)

        # Entry fields for last name and first name
        tk.Label(admin_panel, text="Last Name:").grid(row=1, column=0)
        entry_last_name = tk.Entry(admin_panel)
        entry_last_name.grid(row=1, column=1)

        tk.Label(admin_panel, text="First Name:").grid(row=2, column=0)
        entry_first_name = tk.Entry(admin_panel)
        entry_first_name.grid(row=2, column=1)

        # UI elements for adding schedule
        tk.Label(admin_panel, text="Schedule Date (YYYY-MM-DD):").grid(row=3, column=0)
        entry_schedule_date = tk.Entry(admin_panel)
        entry_schedule_date.grid(row=3, column=1)

        tk.Label(admin_panel, text="Start Time (HH:MM AM/PM):").grid(row=4, column=0)
        entry_start_time = tk.Entry(admin_panel)
        entry_start_time.grid(row=4, column=1)

        tk.Label(admin_panel, text="End Time (HH:MM AM/PM):").grid(row=5, column=0)
        entry_end_time = tk.Entry(admin_panel)
        entry_end_time.grid(row=5, column=1)

        tk.Button(admin_panel, text="Add Schedule", command=lambda: self.add_schedule(admin_panel, entry_last_name, entry_first_name, entry_schedule_date, entry_start_time, entry_end_time)).grid(row=6, columnspan=2)

        tk.Button(admin_panel, text="View Schedules", command=self.view_schedules).grid(row=7, columnspan=2)

    def add_schedule(self, admin_panel, entry_last_name, entry_first_name, entry_schedule_date, entry_start_time, entry_end_time):
        last_name = entry_last_name.get().strip()
        first_name = entry_first_name.get().strip()
        schedule_date = entry_schedule_date.get().strip()
        start_time = entry_start_time.get().strip()
        end_time = entry_end_time.get().strip()

        if not all([last_name, first_name, schedule_date, start_time, end_time]):
            messagebox.showwarning("Input Error", "All fields must be filled out")
            return

        try:
            start_time_formatted = datetime.strptime(start_time, '%I:%M %p').strftime('%H:%M')
            end_time_formatted = datetime.strptime(end_time, '%I:%M %p').strftime('%H:%M')
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid time format. Use HH:MM AM/PM (e.g., 5:00 AM)")
            return

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE last_name=? AND first_name=?", (last_name, first_name))
        result = c.fetchone()
        if result:
            user_id = result[0]
            try:
                c.execute("INSERT INTO schedules (user_id, schedule_date, start_time, end_time) VALUES (?, ?, ?, ?)",
                          (user_id, schedule_date, start_time_formatted, end_time_formatted))
                conn.commit()
                messagebox.showinfo("Schedule Added", "Schedule added successfully")
                admin_panel.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error adding schedule: {e}")
            finally:
                conn.close()
        else:
            messagebox.showwarning("User Not Found", "User with provided last name and first name not found")

    def view_schedules(self):
        pass

    def create_main_window(self):
        tk.Label(self.root, text="Username:").grid(row=0, column=0)
        self.entry_username = tk.Entry(self.root)
        self.entry_username.grid(row=0, column=1)

        tk.Label(self.root, text="Password:").grid(row=1, column=0)
        self.entry_password = tk.Entry(self.root, show='*')
        self.entry_password.grid(row=1, column=1)

        tk.Button(self.root, text="Login", command=self.login).grid(row=2, column=0)
        tk.Button(self.root, text="Register", command=self.register).grid(row=2, column=1)
        tk.Button(self.root, text="Admin", command=self.show_admin_login).grid(row=3, columnspan=2)

    def register(self):
        pass

    def show_admin_login(self):
        admin_login_window = tk.Toplevel(self.root)
        admin_login_window.title("Admin Login")

        tk.Label(admin_login_window, text="Admin Username:").grid(row=0, column=0)
        entry_admin_username = tk.Entry(admin_login_window)
        entry_admin_username.grid(row=0, column=1)

        tk.Label(admin_login_window, text="Admin Password:").grid(row=1, column=0)
        entry_admin_password = tk.Entry(admin_login_window, show='*')
        entry_admin_password.grid(row=1, column=1)

        tk.Button(admin_login_window, text="Login", command=lambda: self.admin_login(admin_login_window, entry_admin_username, entry_admin_password)).grid(row=2, columnspan=2)

    def admin_login(self, admin_login_window, entry_admin_username, entry_admin_password):
        admin_username = entry_admin_username.get().strip()
        admin_password = entry_admin_password.get().strip()
        if admin_username == 'admin' and admin_password == 'password':
            admin_login_window.destroy()
            self.open_admin_panel()
        else:
            messagebox.showwarning("Admin Login", "Invalid admin credentials")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Login and Registration")
    app = Scheduler(root)
    root.mainloop()

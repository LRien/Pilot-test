import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import subprocess
import os
import string
import random  # For generating OTP


class Scheduler:
    def __init__(self, root):
        self.root = root
        self.initialize_db()
        self.create_main_window()

    def initialize_db(self):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()

        # Create users table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        first_name TEXT,
                        middle_initial TEXT,
                        last_name TEXT,
                        birthday TEXT,
                        address TEXT,
                        contact_info TEXT,
                        email TEXT
                    )''')

        # Create schedules table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        schedule_date TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        subject TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )''')

        conn.commit()
        conn.close()

    def login(self):
        # Generate OTP and print it under the terminal
        otp_value = self.generate_otp()  # Generate OTP dynamically
        print(f"Generated OTP: {otp_value}")
        self.show_otp_window(otp_value)

    def generate_otp(self):
        digits = string.digits
        otp = ''.join(random.choice(digits) for i in range(6))  # 6-digit OTP
        return otp

    def show_otp_window(self, expected_otp):
        otp_window = tk.Toplevel(self.root)
        otp_window.title("OTP Verification")

        ttk.Label(otp_window, text="Enter OTP:", style="Large.TLabel").grid(row=0, column=0)
        entry_otp = ttk.Entry(otp_window, style="Large.TEntry")
        entry_otp.grid(row=0, column=1)

        ttk.Button(otp_window, text="Verify OTP", command=lambda: self.verify_otp(otp_window, entry_otp, expected_otp), style="Large.TButton").grid(row=1, columnspan=2, pady=10)

    def verify_otp(self, otp_window, entry_otp, expected_otp):
        entered_otp = entry_otp.get().strip()
        if entered_otp == expected_otp:
            otp_window.destroy()
            self.continue_login()
        else:
            messagebox.showwarning("OTP Verification", "Invalid OTP. Please try again.")

    def continue_login(self):
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
                self.show_user_schedule(username)
        else:
            messagebox.showwarning("Login Info", "Username and password do not exist")

    def show_user_schedule(self, username):
        schedules_window = tk.Toplevel(self.root)
        schedules_window.title(f"Schedules for {username}")

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT schedule_date, start_time, end_time, subject FROM schedules WHERE user_id=(SELECT id FROM users WHERE username=?)", (username,))
        schedules = c.fetchall()
        conn.close()

        if schedules:
            ttk.Label(schedules_window, text="Schedule Date", style="Large.TLabel").grid(row=0, column=0)
            ttk.Label(schedules_window, text="Start Time", style="Large.TLabel").grid(row=0, column=1)
            ttk.Label(schedules_window, text="End Time", style="Large.TLabel").grid(row=0, column=2)
            ttk.Label(schedules_window, text="Subject", style="Large.TLabel").grid(row=0, column=3)

            for index, schedule in enumerate(schedules, start=1):
                ttk.Label(schedules_window, text=schedule[0], style="Large.TLabel").grid(row=index, column=0)
                ttk.Label(schedules_window, text=schedule[1], style="Large.TLabel").grid(row=index, column=1)
                ttk.Label(schedules_window, text=schedule[2], style="Large.TLabel").grid(row=index, column=2)
                ttk.Label(schedules_window, text=schedule[3], style="Large.TLabel").grid(row=index, column=3)

            num_rows = len(schedules) + 1

            ttk.Button(schedules_window, text="Close", command=schedules_window.destroy, style="Large.TButton").grid(row=num_rows, columnspan=4, pady=10)
        else:
            ttk.Label(schedules_window, text="No schedules found.", style="Large.TLabel").grid(row=0, column=0)
            ttk.Button(schedules_window, text="Close", command=schedules_window.destroy, style="Large.TButton").grid(row=1, column=0, pady=10)

    def open_admin_panel(self):
        admin_panel = tk.Toplevel(self.root)
        admin_panel.title("Admin Panel")

        ttk.Label(admin_panel, text="Admin Panel", style="Large.TLabel").grid(row=0, column=0, columnspan=2)

        # Entry fields for last name and first name
        ttk.Label(admin_panel, text="Last Name:", style="Large.TLabel").grid(row=1, column=0)
        entry_last_name = ttk.Entry(admin_panel, style="Large.TEntry")
        entry_last_name.grid(row=1, column=1)

        ttk.Label(admin_panel, text="First Name:", style="Large.TLabel").grid(row=2, column=0)
        entry_first_name = ttk.Entry(admin_panel, style="Large.TEntry")
        entry_first_name.grid(row=2, column=1)

        # UI elements for adding schedule
        ttk.Label(admin_panel, text="Schedule Date (YYYY-MM-DD):", style="Large.TLabel").grid(row=3, column=0)
        entry_schedule_date = ttk.Entry(admin_panel, style="Large.TEntry")
        entry_schedule_date.grid(row=3, column=1)

        ttk.Label(admin_panel, text="Start Time (HH:MM AM/PM):", style="Large.TLabel").grid(row=4, column=0)
        entry_start_time = ttk.Entry(admin_panel, style="Large.TEntry")
        entry_start_time.grid(row=4, column=1)

        ttk.Label(admin_panel, text="End Time (HH:MM AM/PM):", style="Large.TLabel").grid(row=5, column=0)
        entry_end_time = ttk.Entry(admin_panel, style="Large.TEntry")
        entry_end_time.grid(row=5, column=1)

        # New entry field for subject
        ttk.Label(admin_panel, text="Subject:", style="Large.TLabel").grid(row=6, column=0)
        entry_subject = ttk.Entry(admin_panel, style="Large.TEntry")
        entry_subject.grid(row=6, column=1)

        ttk.Button(admin_panel, text="Add Schedule", command=lambda: self.add_schedule(admin_panel, entry_last_name, entry_first_name, entry_schedule_date, entry_start_time, entry_end_time, entry_subject), style="Large.TButton").grid(row=7, columnspan=2, pady=10)

        ttk.Button(admin_panel, text="View Schedules", command=self.view_schedules, style="Large.TButton").grid(row=8, columnspan=2, pady=10)

        ttk.Button(admin_panel, text="Back", command=admin_panel.destroy, style="Large.TButton").grid(row=9, column=0, pady=10)
        ttk.Button(admin_panel, text="Exit", command=self.root.quit, style="Large.TButton").grid(row=9, column=1, pady=10)

    def add_schedule(self, admin_panel, entry_last_name, entry_first_name, entry_schedule_date, entry_start_time, entry_end_time, entry_subject):
        last_name = entry_last_name.get().strip()
        first_name = entry_first_name.get().strip()
        schedule_date = entry_schedule_date.get().strip()
        start_time = entry_start_time.get().strip()
        end_time = entry_end_time.get().strip()
        subject = entry_subject.get().strip()  # Retrieve subject from entry widget

        if not all([last_name, first_name, schedule_date, start_time, end_time, subject]):
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
                c.execute("INSERT INTO schedules (user_id, schedule_date, start_time, end_time, subject) VALUES (?, ?, ?, ?, ?)",
                          (user_id, schedule_date, start_time_formatted, end_time_formatted, subject))
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
        schedules_window = tk.Toplevel(self.root)
        schedules_window.title("View Schedules")

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT users.last_name, users.first_name, schedules.schedule_date, schedules.start_time, schedules.end_time, schedules.subject FROM schedules INNER JOIN users ON schedules.user_id = users.id")
        schedules = c.fetchall()
        conn.close()

        if schedules:
            ttk.Label(schedules_window, text="Last Name", style="Large.TLabel").grid(row=0, column=0)
            ttk.Label(schedules_window, text="First Name", style="Large.TLabel").grid(row=0, column=1)
            ttk.Label(schedules_window, text="Schedule Date", style="Large.TLabel").grid(row=0, column=2)
            ttk.Label(schedules_window, text="Start Time", style="Large.TLabel").grid(row=0, column=3)
            ttk.Label(schedules_window, text="End Time", style="Large.TLabel").grid(row=0, column=4)
            ttk.Label(schedules_window, text="Subject", style="Large.TLabel").grid(row=0, column=5)

            for index, schedule in enumerate(schedules, start=1):
                ttk.Label(schedules_window, text=schedule[0], style="Large.TLabel").grid(row=index, column=0)
                ttk.Label(schedules_window, text=schedule[1], style="Large.TLabel").grid(row=index, column=1)
                ttk.Label(schedules_window, text=schedule[2], style="Large.TLabel").grid(row=index, column=2)
                ttk.Label(schedules_window, text=schedule[3], style="Large.TLabel").grid(row=index, column=3)
                ttk.Label(schedules_window, text=schedule[4], style="Large.TLabel").grid(row=index, column=4)
                ttk.Label(schedules_window, text=schedule[5], style="Large.TLabel").grid(row=index, column=5)

            # Calculate the number of rows needed for schedules plus one for the message label
            num_rows = len(schedules) + 1

            ttk.Button(schedules_window, text="Back", command=schedules_window.destroy, style="Large.TButton").grid(row=num_rows, column=0, pady=10)
            ttk.Button(schedules_window, text="Exit", command=self.root.quit, style="Large.TButton").grid(row=num_rows, column=1, pady=10)
        else:
            ttk.Label(schedules_window, text="No schedules found.", style="Large.TLabel").grid(row=0, column=0)
            ttk.Button(schedules_window, text="Back", command=schedules_window.destroy, style="Large.TButton").grid(row=1, column=0, pady=10)
            ttk.Button(schedules_window, text="Exit", command=self.root.quit, style="Large.TButton").grid(row=1, column=1, pady=10)

    def create_main_window(self):
        ttk.Label(self.root, text="Username:", style="Large.TLabel").grid(row=0, column=0)
        self.entry_username = ttk.Entry(self.root, style="Large.TEntry")
        self.entry_username.grid(row=0, column=1)

        ttk.Label(self.root, text="Password:", style="Large.TLabel").grid(row=1, column=0)
        self.entry_password = ttk.Entry(self.root, show='*', style="Large.TEntry")
        self.entry_password.grid(row=1, column=1)

        ttk.Button(self.root, text="Login", command=self.login, style="Large.TButton").grid(row=2, column=0, pady=10)
        ttk.Button(self.root, text="Register", command=self.register, style="Large.TButton").grid(row=2, column=1, pady=10)
        ttk.Button(self.root, text="Admin", command=self.show_admin_login, style="Large.TButton").grid(row=3, columnspan=2, pady=10)
        ttk.Button(self.root, text="Exit", command=self.root.quit, style="Large.TButton").grid(row=4, columnspan=2, pady=10)

    def register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")

        ttk.Label(register_window, text="Username:", style="Large.TLabel").grid(row=0, column=0)
        entry_username = ttk.Entry(register_window, style="Large.TEntry")
        entry_username.grid(row=0, column=1)

        ttk.Label(register_window, text="Password:", style="Large.TLabel").grid(row=1, column=0)
        entry_password = ttk.Entry(register_window, show='*', style="Large.TEntry")
        entry_password.grid(row=1, column=1)

        ttk.Label(register_window, text="Confirm Password:", style="Large.TLabel").grid(row=2, column=0)
        entry_confirm_password = ttk.Entry(register_window, show='*', style="Large.TEntry")
        entry_confirm_password.grid(row=2, column=1)

        ttk.Label(register_window, text="First Name:", style="Large.TLabel").grid(row=3, column=0)
        entry_first_name = ttk.Entry(register_window, style="Large.TEntry")
        entry_first_name.grid(row=3, column=1)

        ttk.Label(register_window, text="Middle Initial:", style="Large.TLabel").grid(row=4, column=0)
        entry_middle_initial = ttk.Entry(register_window, style="Large.TEntry")
        entry_middle_initial.grid(row=4, column=1)

        ttk.Label(register_window, text="Last Name:", style="Large.TLabel").grid(row=5, column=0)
        entry_last_name = ttk.Entry(register_window, style="Large.TEntry")
        entry_last_name.grid(row=5, column=1)

        ttk.Label(register_window, text="Birthday (YYYY-MM-DD):", style="Large.TLabel").grid(row=6, column=0)
        entry_birthday = ttk.Entry(register_window, style="Large.TEntry")
        entry_birthday.grid(row=6, column=1)

        ttk.Label(register_window, text="Address:", style="Large.TLabel").grid(row=7, column=0)
        entry_address = ttk.Entry(register_window, style="Large.TEntry")
        entry_address.grid(row=7, column=1)

        ttk.Label(register_window, text="Contact Info:", style="Large.TLabel").grid(row=8, column=0)
        entry_contact_info = ttk.Entry(register_window, style="Large.TEntry")
        entry_contact_info.grid(row=8, column=1)

        ttk.Label(register_window, text="Email:", style="Large.TLabel").grid(row=9, column=0)
        entry_email = ttk.Entry(register_window, style="Large.TEntry")
        entry_email.grid(row=9, column=1)

        ttk.Button(register_window, text="Register", command=lambda: self.perform_registration(register_window, entry_username, entry_password, entry_confirm_password, entry_first_name, entry_middle_initial, entry_last_name, entry_birthday, entry_address, entry_contact_info, entry_email), style="Large.TButton").grid(row=10, columnspan=2, pady=10)
        ttk.Button(register_window, text="Back", command=register_window.destroy, style="Large.TButton").grid(row=11, column=0, pady=10)
        ttk.Button(register_window, text="Exit", command=self.root.quit, style="Large.TButton").grid(row=11, column=1, pady=10)

    def perform_registration(self, register_window, entry_username, entry_password, entry_confirm_password, entry_first_name, entry_middle_initial, entry_last_name, entry_birthday, entry_address, entry_contact_info, entry_email):
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        confirm_password = entry_confirm_password.get().strip()
        first_name = entry_first_name.get().strip()
        middle_initial = entry_middle_initial.get().strip()
        last_name = entry_last_name.get().strip()
        birthday = entry_birthday.get().strip()
        address = entry_address.get().strip()
        contact_info = entry_contact_info.get().strip()
        email = entry_email.get().strip()

        # Check if all fields are filled out
        if not all([username, password, confirm_password, first_name, last_name, birthday, address, contact_info, email]):
            messagebox.showwarning("Input Error", "All fields must be filled out")
            return

        # Check if password meets strength requirements
        if not (any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c in string.punctuation for c in password)):
            messagebox.showwarning("Password Error", "Password must contain at least one uppercase letter, one lowercase letter, and one special character")
            return

        # Check if passwords match
        if password != confirm_password:
            messagebox.showwarning("Password Error", "Passwords do not match")
            return

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, first_name, middle_initial, last_name, birthday, address, contact_info, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (username, password, first_name, middle_initial, last_name, birthday, address, contact_info, email))
            conn.commit()
            messagebox.showinfo("Registration Complete", "Registration successful")

            # Create a folder under Faces directory with the user's last name
            folder_name = f"Faces/{last_name}"
            os.makedirs(folder_name, exist_ok=True)

            # Run face_capture.py with the folder name
            subprocess.Popen(["python", "face_capture.py", folder_name])

            register_window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error registering user: {e}")
        finally:
            conn.close()


    def show_admin_login(self):
        admin_login_window = tk.Toplevel(self.root)
        admin_login_window.title("Admin Login")

        ttk.Label(admin_login_window, text="Admin Username:", style="Large.TLabel").grid(row=0, column=0)
        entry_admin_username = ttk.Entry(admin_login_window, style="Large.TEntry")
        entry_admin_username.grid(row=0, column=1)

        ttk.Label(admin_login_window, text="Admin Password:", style="Large.TLabel").grid(row=1, column=0)
        entry_admin_password = ttk.Entry(admin_login_window, show='*', style="Large.TEntry")
        entry_admin_password.grid(row=1, column=1)

        ttk.Button(admin_login_window, text="Login", command=lambda: self.admin_login(admin_login_window, entry_admin_username, entry_admin_password), style="Large.TButton").grid(row=2, columnspan=2, pady=10)
        ttk.Button(admin_login_window, text="Back", command=admin_login_window.destroy, style="Large.TButton").grid(row=3, column=0, pady=10)
        ttk.Button(admin_login_window, text="Exit", command=self.root.quit, style="Large.TButton").grid(row=3, column=1, pady=10)

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

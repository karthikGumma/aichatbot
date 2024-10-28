import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("C:/Karthik/hackthon_jntu/database.db")
cursor = conn.cursor()

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Login")
        self.root.geometry("500x500")

        self.chat_window = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', width=60, height=20)
        self.chat_window.pack(pady=10)

        self.entry_field = tk.Entry(self.root, width=40)
        self.entry_field.pack(pady=5)
        self.entry_field.bind("<Return>", self.handle_user_input)

        self.send_button = tk.Button(self.root, text="Send", command=self.handle_user_input)
        self.send_button.pack(pady=5)

        self.user_type = None
        self.chat_state = "initial"
        self.login_details = {}  # Initialize the login_details dictionary

        self.add_bot_message("Welcome! Please select a login type: Student, Faculty, or Admin.")

    def add_bot_message(self, message):
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, f"Bot: {message}\n")
        self.chat_window.config(state='disabled')
        self.chat_window.yview(tk.END)

    def add_user_message(self, message):
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, f"You: {message}\n")
        self.chat_window.config(state='disabled')
        self.chat_window.yview(tk.END)

    def handle_user_input(self, event=None):
        user_input = self.entry_field.get().strip()
        self.entry_field.delete(0, tk.END)

        if user_input:
            self.add_user_message(user_input)
            self.process_input(user_input)

    def process_input(self, user_input):
        if self.chat_state == "initial":
            self.select_login_type(user_input)
        elif self.chat_state == "login_or_create":
            if user_input.lower() == "login":
                self.chat_state = "login"
                self.start_login()
            elif user_input.lower() == "create":
                self.chat_state = "create"
                self.start_account_creation()
            else:
                self.add_bot_message("Invalid choice. Please type 'Login' or 'Create'.")
        elif self.chat_state == "login":
            self.collect_login_details(user_input)
        elif self.chat_state == "create":
            self.collect_creation_details(user_input)
        elif self.chat_state == "ask_details":
            self.handle_student_detail_request(user_input)
        elif self.chat_state == "faculty_action":
            self.handle_faculty_action(user_input)
        elif self.chat_state == "view_student":
            self.collect_student_username(user_input)
        elif self.chat_state == "table_selection":
            self.select_table(user_input)
        elif self.chat_state == "update":
            self.collect_update_details(user_input)
        elif self.chat_state == "admin_login":
            self.collect_admin_password(user_input)

    def select_login_type(self, user_input):
        user_input = user_input.lower()
        if user_input in ["student", "faculty", "admin"]:
            self.user_type = user_input.capitalize()
            self.chat_state = "login_or_create"
            self.add_bot_message(f"{self.user_type} selected. Do you want to 'Login' or 'Create' an account?")
        else:
            self.add_bot_message("Invalid choice. Please select 'Student', 'Faculty', or 'Admin'.")

    def start_login(self):
        if self.user_type == "Admin":
            self.chat_state = "admin_login"
            self.add_bot_message("Please enter the admin password:")
        else:
            self.add_bot_message("Please enter your username:")
            self.login_details.clear()  # Clear previous login details

    def collect_login_details(self, user_input):
        if self.user_type == "Admin":
            self.collect_admin_password(user_input)
        elif "username" not in self.login_details:
            self.login_details["username"] = user_input
            self.add_bot_message("Please enter your password:")
        elif "password" not in self.login_details:
            self.login_details["password"] = user_input
            self.perform_login()

    def collect_admin_password(self, user_input):
        if user_input == "1234":
            self.display_all_data()
        else:
            self.add_bot_message("Invalid password. Please try again.")

    def perform_login(self):
        try:
            if self.user_type == "Admin":
                cursor.execute("SELECT * FROM admin WHERE password=?", (self.login_details["password"],))
            else:
                cursor.execute(f"SELECT * FROM {self.user_type.lower()} WHERE username=? AND password=?", 
                               (self.login_details["username"], self.login_details["password"]))

            if cursor.fetchone():
                self.add_bot_message(f"{self.user_type} login successful!")
                if self.user_type == "Student":
                    self.chat_state = "ask_details"
                    self.ask_student_detail_request()
                elif self.user_type == "Faculty":
                    self.chat_state = "faculty_action"
                    self.add_bot_message("Would you like to 'View' or 'Update' student details?")
            else:
                self.add_bot_message("Invalid credentials.")
        except Exception as e:
            self.add_bot_message(f"Database Error: {str(e)}")

    def display_all_data(self):
        try:
            # Assuming you have multiple tables to display
            tables = ["student_marks", "student_credits", "student_attendance", "admin"]
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                data = cursor.fetchall()

                if data:
                    table_message = f"Details from {table}:\n"
                    for row in data:
                        table_message += f"{row}\n"  # Adjust this to format as needed
                    self.add_bot_message(table_message)
                else:
                    self.add_bot_message(f"No data found in {table}.")

            self.add_bot_message("All data displayed successfully.")
        except Exception as e:
            self.add_bot_message(f"Error retrieving data: {str(e)}")

    def ask_student_detail_request(self):
        self.add_bot_message("What details do you want to check? (marks, credits, attendance, or type 'end' to finish)")

    def handle_student_detail_request(self, user_input):
        if user_input.lower() == "end":
            self.add_bot_message("Session ended. Thank you!")
            self.reset_state()
            return
        
        if user_input.lower() == "marks":
            self.display_student_marks(self.login_details["username"])
        elif user_input.lower() == "credits":
            self.display_student_credits(self.login_details["username"])
        elif user_input.lower() == "attendance":
            self.display_student_attendance(self.login_details["username"])
        else:
            self.add_bot_message("Invalid choice. Please type 'marks', 'credits', 'attendance', or 'end'.")

        if user_input.lower() != "end":
            self.ask_student_detail_request()

    def handle_faculty_action(self, user_input):
        if user_input.lower() == "view":
            self.add_bot_message("Please select a table: (student_marks, student_credits, student_attendance)")
            self.chat_state = "table_selection"
        elif user_input.lower() == "update":
            self.add_bot_message("Please select a table to update: (student_marks, student_credits, student_attendance)")
            self.chat_state = "update_table_selection"
        else:
            self.add_bot_message("Invalid choice. Please type 'View' or 'Update'.")

    def select_table(self, user_input):
        valid_tables = ["student_marks", "student_credits", "student_attendance"]
        if user_input.lower() in valid_tables:
            self.selected_table = user_input.lower()
            self.add_bot_message(f"You selected {self.selected_table}. Please enter the student's username:")
            self.chat_state = "view_student"
        else:
            self.add_bot_message("Invalid table. Please select from: student_marks, student_credits, student_attendance.")

    def collect_student_username(self, user_input):
        self.student_username = user_input
        self.display_student_details()

    def display_student_details(self):
        try:
            cursor.execute(f"SELECT * FROM {self.selected_table} WHERE username=?", (self.student_username,))
            student_data = cursor.fetchone()

            if student_data:
                student_message = f"Details for {self.student_username} in {self.selected_table}:\n"
                for index, value in enumerate(student_data):
                    student_message += f"Column {index}: {value}\n"  # Adjust this line to fit your actual data structure
                self.add_bot_message(student_message)
            else:
                self.add_bot_message("No details found for this student in the selected table.")

            # Ask if they want to view or update again
            self.add_bot_message("Would you like to 'View' another student or 'Update' this student's details?")
            self.chat_state = "faculty_action"  # Return to faculty action state
        except Exception as e:
            self.add_bot_message(f"Error retrieving student details: {str(e)}")
        finally:
            self.reset_state()  # Reset state after completing the action

    def display_student_marks(self, username):
        try:
            cursor.execute("SELECT * FROM student_marks WHERE username=?", (username,))
            marks = cursor.fetchone()
            if marks:
                self.add_bot_message(f"Marks for {username}: {marks}")
            else:
                self.add_bot_message(f"No marks found for {username}.")
        except Exception as e:
            self.add_bot_message(f"Error retrieving marks: {str(e)}")

    def display_student_credits(self, username):
        try:
            cursor.execute("SELECT * FROM student_credits WHERE username=?", (username,))
            credits = cursor.fetchone()
            if credits:
                self.add_bot_message(f"Credits for {username}: {credits}")
            else:
                self.add_bot_message(f"No credits found for {username}.")
        except Exception as e:
            self.add_bot_message(f"Error retrieving credits: {str(e)}")

    def display_student_attendance(self, username):
        try:
            cursor.execute("SELECT * FROM student_attendance WHERE username=?", (username,))
            attendance = cursor.fetchone()
            if attendance:
                self.add_bot_message(f"Attendance for {username}: {attendance}")
            else:
                self.add_bot_message(f"No attendance record found for {username}.")
        except Exception as e:
            self.add_bot_message(f"Error retrieving attendance: {str(e)}")

    def collect_update_details(self, user_input):
        self.add_bot_message("Please enter the attribute you want to update:")
        self.chat_state = "update_attribute"

    def reset_state(self):
        self.chat_state = "initial"
        self.user_type = None
        self.login_details.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()

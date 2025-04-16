import tkinter as tk
from tkinter import messagebox

class UserGUI:
    def __init__(self):
        self.user_data = {}

    def get_user_input(self, symbols):
        def submit():
            # Collect and validate all inputs
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Name is required.")
                return
            if len(name) < 3:  # Example validation for name length
                messagebox.showerror("Input Error", "Name must be at least 3 characters long.")
                return
            email = email_entry.get().strip()
            if not email:
                messagebox.showerror("Input Error", "Email is required.")
                return
            if "@" not in email or "." not in email:  # Basic email validation
                messagebox.showerror("Input Error", "Invalid email format.")
                return
            if len(email) < 5:  
                
                messagebox.showerror("Input Error", "Email must be at least 5 characters long.")
                return
            
            account_id = account_entry.get().strip()
            if not account_id:
                messagebox.showerror("Input Error", "Account ID is required.")
                return
            if not account_id.isdigit():
                messagebox.showerror("Input Error", "Account ID must be numeric.")
                return
            if len(account_id) < 5:
                messagebox.showerror("Input Error", "Account ID must be at least 5 digits long.")
                return
            password = password_entry.get().strip()
            if not password:
                messagebox.showerror("Input Error", "Password is required.")
                return
            if len(password) < 8 or len(password)>16:  # Example validation for password length
                messagebox.showerror("Input Error", "Password must be at least 8  and less than characters long .")
                return

            if not all([name, email, account_id, password]):
                messagebox.showerror("Input Error", "All fields are required.")
                return

            self.user_data = {
                "symbols": symbols,
                "name": name,
                "email": email,
                "account_id": account_id,
                "password": password,
            }
            root.destroy()  # Close the popup

        root = tk.Tk()
        root.title("Trading Bot Setup")
        root.geometry("600x600")
        root.resizable(False, False)

        row = 0
        tk.Label(root, text="Your Symbols:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1

        # Display symbols
        tk.Label(root, text=", ".join(symbols)).grid(row=row, column=0, columnspan=2, pady=(10, 10))
        row += 1

        # Input fields
        tk.Label(root, text="Name:").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        name_entry = tk.Entry(root)
        name_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        tk.Label(root, text="Email:").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        email_entry = tk.Entry(root)
        email_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        tk.Label(root, text="Account ID:").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        account_entry = tk.Entry(root)
        account_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        tk.Label(root, text="Password:").grid(row=row, column=0, sticky="e", padx=10, pady=5)
        password_entry = tk.Entry(root, show="*")
        password_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        # Submit button
        submit_btn = tk.Button(root, text="Start Bot", command=submit)
        submit_btn.grid(row=row, column=0, columnspan=2, pady=15)

        root.mainloop()
        return self.user_data

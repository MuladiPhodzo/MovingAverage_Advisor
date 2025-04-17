import tkinter as tk
from tkinter import messagebox

class UserGUI:
    def __init__(self):
        self.user_data = {}

    def get_user_input(self):
        def submit():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Name is required.")
                return
            if len(name) < 3:
                messagebox.showerror("Input Error", "Name must be at least 3 characters long.")
                return
            
            server = server_entry.get().strip()
            if not server:
                messagebox.showerror("Input Error", "server is required.")
                return
            
            volume = volume_entry.get().strip()
            if not volume:
                messagebox.showerror("Input Error", "volume is required.")
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
            if len(password) < 8 or len(password) > 16:
                messagebox.showerror("Input Error", "Password must be between 8 and 16 characters long.")
                return

            self.user_data = {
                "name": name,
                "volume": volume,
                ''"server": server,	
                "account_id": account_id,
                "password": password,
            }
            root.destroy()

        root = tk.Tk()
        root.title("Trading Bot Setup")
        window_width = 400
        window_height = 400

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.configure(bg="#f4f4f4")

        main_frame = tk.Frame(root, bg="#f4f4f4")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        label_style = {"font": ("Segoe UI", 10), "bg": "#f4f4f4", "fg": "#333"}
        entry_style = {"bg": "#fff", "fg": "#000", "relief": "flat", "width": 30}

        header_style = {"font": ("Segoe UI", 14, "bold"), "bg": "#f4f4f4", "fg": "#333"}
        tk.Label(main_frame, text="🚀 Trading Bot Setup", **header_style).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(main_frame, text="Name:", **label_style).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        name_entry = tk.Entry(main_frame, **entry_style)
        name_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(main_frame, text="server:", **label_style).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        server_entry = tk.Entry(main_frame, **entry_style)
        server_entry.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(main_frame, text="Volume:", **label_style).grid(row=4, column=0, sticky="e", padx=10, pady=5)
        volume_entry = tk.Entry(main_frame, **entry_style)
        volume_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(main_frame, text="Account ID:", **label_style).grid(row=5, column=0, sticky="e", padx=10, pady=5)
        account_entry = tk.Entry(main_frame, **entry_style)
        account_entry.grid(row=5, column=1, padx=10, pady=5)

        tk.Label(main_frame, text="Password:", **label_style).grid(row=6, column=0, sticky="e", padx=10, pady=5)
        password_entry = tk.Entry(main_frame, show="*", **entry_style)
        password_entry.grid(row=6, column=1, padx=10, pady=5)

        submit_btn = tk.Button(main_frame,
                               text="Start Bot",
                               command=submit,
                               bg="#007acc",
                               fg="white",
                               font=("Segoe UI", 10, "bold"),
                               relief="raised",
                               bd=2,
                               padx=10,
                               pady=5)
        submit_btn.grid(row=7, column=0, columnspan=2, pady=(20, 10))

        root.mainloop()
        return self.user_data

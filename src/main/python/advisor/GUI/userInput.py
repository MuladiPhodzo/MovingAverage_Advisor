import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import queue
from advisor.Logs import Logger as logs


class TextRedirector:
    def __init__(self, log_window):
        self.log_window = log_window

    def write(self, string):
        self.log_window.queue.put(string)

    def flush(self):
        pass


class LogWindow:
    
    def __init__(self, master, quit):
        self.window = tk.Toplevel(master) if master else tk.Tk()
        self.window.title("📢 Bot Logs")
        self.window.geometry("800x600")

        self.log_area = ScrolledText(self.window, wrap=tk.WORD, width=100, height=40, bg="#1e1e1e", fg="#00ff00")
        self.log_area.pack(padx=10, pady=10)
        
        self.stop_button = tk.Button(self.window, text="Stop Bot", command=self.quit,
                  bg="#ff4c4c", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="raised", bd=2, padx=10, pady=5)
        
        self.stop_button.pack(pady=(0, 10))
        self.queue = queue.Queue()
        self.poll_queue()
        self.redirector = TextRedirector(self)
        
    def poll_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.log_area.insert(tk.END, message)
                self.log_area.see(tk.END)
        except queue.Empty:
            pass
        self.window.after(100, self.poll_queue)


    def quit(self):
        print("🛑 Stopping bot and closing app...")
        UserGUI.should_run = False
        self.window.quit()
class UserGUI:
    def __init__(self):
        self.user_data = {}
        self.root = tk.Tk()
        self.root.title("Trading Bot Setup")
        self.should_run = None
        # Set up GUI window
        self.setup_gui()
        
        
        # # Initialize logger window
        # self.log_window = LogWindow(None, self.quit)
        # print(f'intializing user GUI......')
        # sys.stdout = self.log_window.redirector
        # sys.stderr = self.log_window.redirector
        
        
        
        

    def setup_gui(self):
        print('setting up GUI.....')
        window_width = 500
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg="#f4f4f4")

        main_frame = tk.Frame(self.root, bg="#f4f4f4")
        main_frame.pack(pady=20)

        label_style = {"font": ("Segoe UI", 10), "bg": "#f4f4f4", "fg": "#333"}
        entry_style = {"bg": "#fff", "fg": "#000", "relief": "flat", "width": 30}

        tk.Label(main_frame, text="🚀 Trading Bot Setup", font=("Segoe UI", 14, "bold"),
                 bg="#f4f4f4", fg="#333").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Input fields
        print('indexing fields.......')
        fields = [("Server", "server_entry"), ("Volume", "volume_entry"),
                  ("Account ID", "account_entry"), ("Password", "password_entry")]
        
        for idx, (label, attr) in enumerate(fields, 1):
            tk.Label(main_frame, text=f"{label}:", **label_style).grid(row=idx, column=0, sticky="e", padx=10, pady=5)
            entry = tk.Entry(main_frame, **entry_style)
            if label == "Password":
                entry.config(show="*")
            entry.grid(row=idx, column=1, padx=10, pady=5)
            setattr(self, attr, entry)
            
        tk.Button(main_frame, text="Skip", command=self.skip,
                  bg="#ffcc00", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="raised", bd=2, padx=10, pady=5).grid(row=idx + 1, column=0, columnspan=2, pady=(20, 5))

        # Buttons
        tk.Button(main_frame, text="Start Bot", command=self.submit,
                  bg="#007acc", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="raised", bd=2, padx=10, pady=5).grid(row=idx + 2, column=0, columnspan=2, pady=(20, 5))

        

    def submit(self):
        
        server = self.server_entry.get().strip()
        volume = self.volume_entry.get().strip()
        account_id = self.account_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validations
        if not server or not volume:
            messagebox.showerror("Input Error", "Server and Volume are required.")
            return None
        if not account_id.isdigit() or len(account_id) < 5:
            messagebox.showerror("Input Error", "Valid Account ID is required.")
            return None
        if not password or not (8 <= len(password) <= 16):
            messagebox.showerror("Input Error", "Password must be 8–16 characters.")
            return None

        self.user_data = {
            "volume": volume,
            "server": server,
            "account_id": account_id,
            "password": password,
        }

        # Log in to MetaTrader
        # print('awaiting MT5 handshake')
        # client = Advisor.MetaTrader5Client()
        # if not client.logIn(self.user_data):
        #     messagebox.showerror("Login Error", "Failed to connect to MetaTrader 5.")
        #     return

        
        self.root.withdraw()
        self.should_run = True
        logs.FileLogger(self.user_data)
        return self.user_data
    
    def skip(self):
        self.user_data = None
        self.root.withdraw()
        self.should_run = True
        logs.FileLogger(self.user_data)
        return self.user_data
    
    def quit(self):
        print("🛑 Stopping bot and closing app...")
        self.root.quit()


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = UserGUI(root)
#     root.mainloop()

import customtkinter as ctk
from tkinter import messagebox
import csv
import os
from ui_theme import Colors


class TransactionFrame(ctk.CTkFrame):
    """
    ATM Transaction Screen (Physical ATM Kiosk UI)
    """

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")

        self.controller = controller
        self.user_id = None  # Set when user logs in
        self.user_name = "User"

        # Fonts
        self.monitor_font = ctk.CTkFont(family="Courier New", size=24, weight="bold")
        self.title_font = ctk.CTkFont(family="Courier New", size=32, weight="bold")
        self.button_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")

        # =====================================================
        # MAIN ATM SCREEN WRAPPER
        # =====================================================
        self.main_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.main_wrapper.pack(expand=True, fill="both", padx=40, pady=40)

        # Configure Grid (Left Buttons | Center Monitor | Right Buttons)
        self.main_wrapper.grid_columnconfigure(0, weight=1)
        self.main_wrapper.grid_columnconfigure(1, weight=3)
        self.main_wrapper.grid_columnconfigure(2, weight=1)

        # =====================================================
        # LEFT BUTTONS PANEL
        # =====================================================
        self.left_panel = ctk.CTkFrame(self.main_wrapper, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=10, pady=20)

        ctk.CTkButton(
            self.left_panel,
            text="< WITHDRAW",
            width=200,
            height=80,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.DARK_GRAY_TK,
            hover_color=Colors.PRIMARY_TK,
            border_width=2,
            border_color=Colors.PRIMARY_TK,
            command=self.withdraw_window
        ).pack(pady=30)

        ctk.CTkButton(
            self.left_panel,
            text="< FAST CASH",
            width=200,
            height=80,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.DARK_GRAY_TK,
            hover_color=Colors.PRIMARY_TK,
            border_width=2,
            border_color=Colors.PRIMARY_TK,
            # Placeholder for fast cash
            command=lambda: messagebox.showinfo("Info", "Fast Cash under maintenance.")
        ).pack(pady=30)

        # =====================================================
        # CENTER MONITOR SCREEN
        # =====================================================
        self.monitor_frame = ctk.CTkFrame(
            self.main_wrapper,
            fg_color="#0a192f",  # Deep ATM blue screen color
            border_width=4,
            border_color="#1f2c47",
            corner_radius=15
        )
        self.monitor_frame.grid(row=0, column=1, sticky="nsew", padx=20)

        # Monitor Content
        self.welcome_label = ctk.CTkLabel(
            self.monitor_frame,
            text="WELCOME TO SMART ATM",
            font=self.title_font,
            text_color="#64ffda"  # Cyan phosphor text
        )
        self.welcome_label.pack(pady=(60, 20))

        ctk.CTkLabel(
            self.monitor_frame,
            text="PLEASE SELECT A TRANSACTION",
            font=self.monitor_font,
            text_color="#ffffff"
        ).pack(pady=20)

        ctk.CTkLabel(
            self.monitor_frame,
            text="[ Use the side buttons to navigate ]",
            font=ctk.CTkFont(family="Courier New", size=16),
            text_color="#8892b0"
        ).pack(side="bottom", pady=40)

        # =====================================================
        # RIGHT BUTTONS PANEL
        # =====================================================
        self.right_panel = ctk.CTkFrame(self.main_wrapper, fg_color="transparent")
        self.right_panel.grid(row=0, column=2, sticky="ns", padx=10, pady=20)

        ctk.CTkButton(
            self.right_panel,
            text="DEPOSIT >",
            width=200,
            height=80,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.DARK_GRAY_TK,
            hover_color=Colors.PRIMARY_TK,
            border_width=2,
            border_color=Colors.PRIMARY_TK,
            command=self.deposit_window
        ).pack(pady=30)

        ctk.CTkButton(
            self.right_panel,
            text="BALANCE >",
            width=200,
            height=80,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.DARK_GRAY_TK,
            hover_color=Colors.PRIMARY_TK,
            border_width=2,
            border_color=Colors.PRIMARY_TK,
            command=self.balance_window
        ).pack(pady=30)

        # =====================================================
        # BOTTOM ROW: SECURE LOGOUT
        # =====================================================
        ctk.CTkButton(
            self,
            text="SECURE LOGOUT / CANCEL",
            width=300,
            height=60,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.DANGER_TK,
            hover_color="#c0392b",
            command=self.logout
        ).pack(side="bottom", pady=30)


    # =====================================================
    # SET ACTIVE USER
    # =====================================================
    def set_user(self, user_id):
        self.user_id = user_id
        
        # Pull name for display
        if user_id in self.controller.data:
            self.user_name = self.controller.data[user_id].get("name", "User")
        else:
            self.user_name = "User"
            
        self.welcome_label.configure(text=f"WELCOME, {self.user_name.upper()}")

    # =====================================================
    # CSV HELPERS
    # =====================================================
    def get_balance(self):
        file_path = os.path.join("Details", "Details.csv")

        if not os.path.exists(file_path):
            return 0.0

        with open(file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == self.user_id:
                    return float(row[3])
        return 0.0

    def update_balance(self, new_balance):
        file_path = os.path.join("Details", "Details.csv")
        rows = []

        with open(file_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

        for row in rows:
            if row and row[0] == self.user_id:
                row[3] = str(new_balance)

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    # =====================================================
    # WITHDRAW WINDOW (MODAL)
    # =====================================================
    def withdraw_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Withdraw")
        win.geometry("400x300")
        win.grab_set()  

        ctk.CTkLabel(
            win,
            text="Enter Amount",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(40, 20))

        amount_entry = ctk.CTkEntry(
            win,
            font=ctk.CTkFont(size=22),
            width=240,
            height=50,
            justify="center"
        )
        amount_entry.pack(pady=10)

        def withdraw():
            try:
                amount = float(amount_entry.get())
            except:
                messagebox.showerror("Error", "Invalid amount")
                return

            balance = self.get_balance()

            if amount <= 0:
                messagebox.showerror("Error", "Invalid amount")
                return

            if amount > balance:
                messagebox.showerror("Error", "Insufficient balance")
                return

            new_balance = balance - amount
            self.update_balance(new_balance)

            messagebox.showinfo(
                "Transaction Success",
                f"Please take your cash: ₹{amount:.2f}\nRemaining Balance: ₹{new_balance:.2f}"
            )
            win.destroy()

        ctk.CTkButton(
            win,
            text="Confirm Withdrawal",
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=Colors.SUCCESS_TK,
            hover_color="#27ae60",
            command=withdraw
        ).pack(pady=20)

    # =====================================================
    # DEPOSIT WINDOW (MODAL)
    # =====================================================
    def deposit_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Deposit")
        win.geometry("400x300")
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Enter Deposit Amount",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(40, 20))

        amount_entry = ctk.CTkEntry(
            win,
            font=ctk.CTkFont(size=22),
            width=240,
            height=50,
            justify="center"
        )
        amount_entry.pack(pady=10)

        def deposit():
            try:
                amount = float(amount_entry.get())
            except:
                messagebox.showerror("Error", "Invalid amount")
                return

            if amount <= 0:
                messagebox.showerror("Error", "Invalid amount")
                return

            balance = self.get_balance()
            new_balance = balance + amount

            self.update_balance(new_balance)

            messagebox.showinfo(
                "Transaction Success",
                f"Successfully Deposited: ₹{amount:.2f}\nNew Balance: ₹{new_balance:.2f}"
            )
            win.destroy()

        ctk.CTkButton(
            win,
            text="Insert Cash",
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=Colors.SUCCESS_TK,
            hover_color="#27ae60",
            command=deposit
        ).pack(pady=20)

    # =====================================================
    # BALANCE WINDOW (MODAL)
    # =====================================================
    def balance_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Balance Inquiry")
        win.geometry("400x300")
        win.grab_set()

        balance = self.get_balance()

        ctk.CTkLabel(
            win,
            text="Current Balance",
            font=ctk.CTkFont(family="Courier New", size=22),
            text_color=Colors.GRAY_TK   # ✅ move here
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            win,
            text=f"₹{balance:.2f}",
            font=ctk.CTkFont(family="Courier New", size=48, weight="bold"),
            text_color=Colors.SUCCESS_TK   # ✅ move here
        ).pack(pady=(0, 40))

        ctk.CTkButton(
            win,
            text="Close",
            width=180,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=Colors.GRAY_TK,
            hover_color="#7f8c8d",
            command=win.destroy
        ).pack()

    # =====================================================
    # LOGOUT
    # =====================================================
    def logout(self):
        
        self.user_id=None
        self.controller.show_frame("welcome")

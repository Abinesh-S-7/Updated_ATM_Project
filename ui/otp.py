import customtkinter as ctk
from tkinter import messagebox
from ui_theme import Colors
from auth.otp_verify import verify_otp

class OTPFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.user_id = None
        
        # Self Card (similar to LoginFrame)
        self.card = ctk.CTkFrame(
            self,
            fg_color=Colors.DARK_GRAY_TK,
            corner_radius=15
        )
        self.card.pack(expand=True, padx=20, pady=20, ipadx=40, ipady=40)
        
        # Status Label inside card
        self.status_label = ctk.CTkLabel(
            self.card,
            text="Biometric Timeout",
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color=Colors.DANGER_TK
        )
        self.status_label.pack(pady=(0, 10))

        ctk.CTkLabel(
            self.card,
            text="An OTP has been sent to your phone for verification.\n(valid for 5 minutes)",
            font=ctk.CTkFont(family="Helvetica", size=15),
            text_color=Colors.WHITE_TK
        ).pack(pady=(0, 20))
        
        self.otp_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Enter OTP",
            font=ctk.CTkFont(family="Helvetica", size=18),
            justify="center",
            width=240,
            height=45,
            corner_radius=8,
            border_color=Colors.GRAY_TK
        )
        self.otp_entry.pack(pady=15)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Verify OTP",
            width=150,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            fg_color=Colors.PRIMARY_TK,
            hover_color="#00b8e6",
            command=self.verify
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=120,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            fg_color=Colors.GRAY_TK,
            hover_color="#808080",
            command=self.cancel
        ).pack(side="left", padx=10)
        
    def set_user(self, user_id):
        self.user_id = user_id
        self.otp_entry.delete(0, 'end')

    def verify(self):
        otp = self.otp_entry.get().strip()
        if not otp:
            messagebox.showwarning("Warning", "Please enter the OTP")
            return
            
        if verify_otp(otp):
            messagebox.showinfo("Success", "OTP Verified Successfully!")
            self.controller.start_transaction(self.user_id)
        else:
            messagebox.showerror("Error", "Invalid or Expired OTP")
            self.otp_entry.delete(0, 'end')
            
    def cancel(self):
        self.otp_entry.delete(0, 'end')
        self.controller.show_frame("welcome")

import customtkinter as ctk
import time
from datetime import datetime
from tensorflow.keras.models import load_model

from ui_theme import theme, Colors
from data.storage import load_data

from auth.otp_verify import send_otp_sms, verify_otp

from ui.welcome import WelcomeFrame
from ui.login import LoginFrame
from ui.register import RegisterFrame
from ui.transaction import TransactionFrame
from ui.otp import OTPFrame


class ATMApp:
    """
    Main Controller for ATM System
    """

    def __init__(self, root):

        # =====================================================
        # WINDOW SETUP
        # =====================================================
        self.root = root
        self.root.title(theme.window_name)
        self.root.geometry("900x600")
        self.root.configure(bg=Colors.DARK_GRAY_TK)

        # =====================================================
        # LOAD USER DATA
        # =====================================================
        self.data = load_data()

        # =====================================================
        # LOAD MASK MODEL
        # =====================================================
        self.model_input_size = (224, 224)

        try:
            self.mask_model = load_model(
                "models/mask_detector_model.h5",
                compile=False
            )
            print("✅ Mask model loaded")
        except Exception as e:
            print("⚠ Mask model not loaded:", e)
            self.mask_model = None

        # =====================================================
        # GLOBAL TOP BAR
        # =====================================================
        self.top_bar = ctk.CTkFrame(
            self.root,
            height=60,
            fg_color=Colors.DARK_GRAY_TK,
            corner_radius=0
        )
        self.top_bar.pack(fill="x", side="top")
        
        # Branding Title
        ctk.CTkLabel(
            self.top_bar,
            text="🏦 AI-Powered Smart ATM",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=Colors.PRIMARY_TK
        ).pack(side="left", padx=20, pady=15)
        
        # Live Clock
        self.clock_label = ctk.CTkLabel(
            self.top_bar,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=16),
            text_color=Colors.WHITE_TK
        )
        self.clock_label.pack(side="right", padx=20, pady=15)
        
        # Start Clock Update Loop
        self.update_clock()

        # =====================================================
        # MAIN CONTAINER
        # =====================================================
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        self.main_container.pack(fill="both", expand=True)

        # =====================================================
        # CREATE FRAMES
        # =====================================================
        self.frames = {}

        self.frames["welcome"] = WelcomeFrame(
            self.main_container,
            self
        )

        self.frames["login"] = LoginFrame(
            self.main_container,
            self
        )

        self.frames["register"] = RegisterFrame(
            self.main_container,
            self
        )

        self.frames["transaction"] = TransactionFrame(
            self.main_container,
            self
        )

        self.frames["otp"] = OTPFrame(
            self.main_container,
            self
        )

        # Stack frames on top of each other
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        # Show welcome screen first
        self.show_frame("welcome")

    # =====================================================
    # DYNAMIC CLOCK
    # =====================================================
    def update_clock(self):
        """Updates the top bar clock every second"""
        current_time = datetime.now().strftime("%Y-%m-%d  %I:%M:%S %p")
        self.clock_label.configure(text=current_time)
        self.root.after(1000, self.update_clock)

    # =====================================================
    # NAVIGATION
    # =====================================================
    def show_frame(self, name):
        """
        Bring selected frame to front
        """
        frame = self.frames[name]
        frame.tkraise()

    # =====================================================
    # START TRANSACTION AFTER VERIFICATION
    # =====================================================
    def start_transaction(self, user_id):
        """
        Called after successful face/OTP verification
        """

        transaction_frame = self.frames["transaction"]
        transaction_frame.set_user(user_id)

        self.show_frame("transaction")

    # =====================================================
    # OTP CALLBACK
    # =====================================================
    def otp_verification(self, user_id, data):
        """
        Called when face verification fails/times out
        """
        # Get phone number from database (or fallback)
        user_info = data.get(str(user_id), {})
        phone = user_info.get("phone", "+916380825972")
        
        # Actually send the SMS
        send_otp_sms(phone)
        
        # Switch to the new embedded OTP frame
        otp_frame = self.frames["otp"]
        otp_frame.set_user(user_id)
        self.show_frame("otp")
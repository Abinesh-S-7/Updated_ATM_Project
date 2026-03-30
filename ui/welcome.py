import customtkinter as ctk
from ui_theme import Colors


class WelcomeFrame(ctk.CTkFrame):
    """
    Welcome Screen for ATM System (Single-pane Centralized Hardware UI)
    """

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # ==============================
        # Fonts
        # ==============================
        self.title_font = ctk.CTkFont(family="Helvetica", size=36, weight="bold")
        self.subtitle_font = ctk.CTkFont(family="Courier New", size=18, weight="bold")
        self.cta_font = ctk.CTkFont(family="Helvetica", size=18, weight="bold")

        # ==============================
        # Main Layout (Centered Pane)
        # ==============================
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=40, pady=20)

        # --------------------------------------------------
        # CENTRAL ATM HARDWARE SIMULATOR
        # --------------------------------------------------
        self.center_frame = ctk.CTkFrame(
            main_container, 
            fg_color="#18181c",  # Dark metallic ATM casing
            corner_radius=20,
            border_width=4,
            border_color="#2b2b36"
        )
        self.center_frame.pack(expand=True, padx=40, pady=20, ipadx=40, ipady=10)

        # Vertical Centering inside Frame
        hardware_container = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        hardware_container.pack(expand=True, fill="both")

        # 1. BIOMETRIC FACE SCANNER
        scanner_container = ctk.CTkFrame(hardware_container, fg_color="transparent")
        scanner_container.pack(pady=(20, 15), fill="x", padx=40)
        
        ctk.CTkLabel(scanner_container, text="BIOMETRIC SCANNER", font=self.subtitle_font, text_color="#555566").pack()
        
        self.scanner_lens = ctk.CTkFrame(scanner_container, width=80, height=80, corner_radius=40, fg_color="#050508", border_width=3, border_color="#333344")
        self.scanner_lens.pack(pady=10)
        self.scanner_lens.pack_propagate(False)
        
        # Center camera lens
        ctk.CTkFrame(self.scanner_lens, width=40, height=40, corner_radius=20, fg_color="#0a0a12", border_width=2, border_color="#111122").place(relx=0.5, rely=0.5, anchor="center")

        # Scanning laser line (simulated)
        self.scanner_led = ctk.CTkFrame(self.scanner_lens, width=12, height=12, corner_radius=6, fg_color=Colors.DANGER_TK) 
        self.scanner_led.place(relx=0.8, rely=0.2, anchor="center")

        # 2. CARD READER SLOT (CLICKABLE BUTTON)
        card_container = ctk.CTkFrame(hardware_container, fg_color="transparent")
        card_container.pack(pady=(15, 15), fill="x", padx=40)
        
        ctk.CTkLabel(
            card_container, 
            text="INSERT CARD TO BEGIN SECURE LOGIN", 
            font=self.cta_font, 
            text_color=Colors.PRIMARY_TK
        ).pack()
        
        # We use a CTkButton themed exactly like a card slot!
        self.slot_btn = ctk.CTkButton(
            card_container, 
            text=">           - - - - - [ | ] - - - - -           <", 
            text_color="#000000",
            font=ctk.CTkFont("Helvetica", 18, "bold"),
            width=280, 
            height=60, 
            fg_color="#111115", 
            hover_color="#1f1f26",
            corner_radius=8, 
            border_width=3, 
            border_color="#333344",
            command=self.go_login
        )
        self.slot_btn.pack(pady=10)
        
        # Blinking card LED indicator
        self.card_led = ctk.CTkFrame(self.slot_btn, width=16, height=16, corner_radius=8, fg_color=Colors.SUCCESS_TK)
        self.card_led.place(relx=0.1, rely=0.5, anchor="center")

        # 3. NFC / CONTACTLESS READER
        nfc_container = ctk.CTkFrame(hardware_container, fg_color="transparent")
        nfc_container.pack(pady=(5, 10), fill="x", padx=40)
        
        ctk.CTkLabel(nfc_container, text="CONTACTLESS", font=self.subtitle_font, text_color="#555566").pack()
        nfc_logo = ctk.CTkLabel(nfc_container, text="((( • )))", font=ctk.CTkFont("Helvetica", 28, "bold"), text_color=Colors.SUCCESS_TK)
        nfc_logo.pack(pady=0)

        # 4. CASH DISPENSER
        cash_container = ctk.CTkFrame(hardware_container, fg_color="transparent")
        cash_container.pack(pady=(0, 20), fill="x", padx=40)
        
        ctk.CTkLabel(cash_container, text="CASH DISPENSER", font=self.subtitle_font, text_color="#555566").pack()
        dispenser_slot = ctk.CTkFrame(cash_container, width=220, height=20, fg_color="#020202", corner_radius=2, border_width=4, border_color="#1a1a24")
        dispenser_slot.pack(pady=5)

        # =====================================================
        # REGISTER BUTTON (NEW USER)
        # =====================================================
        register_container = ctk.CTkFrame(hardware_container, fg_color="transparent")
        register_container.pack(side="bottom", pady=(10, 20))

        ctk.CTkButton(
            register_container,
            text="New User? Register Here",
            width=240,
            height=45,
            corner_radius=8,
            font=self.cta_font,
            fg_color=Colors.WARNING_TK,   # Orange/gold distinct registration color
            hover_color="#d35400",
            text_color="#ffffff",
            command=self.go_register
        ).pack()

        # Start LED Animation Loop
        self.led_state = True
        self.blink_leds()

    # =====================================================
    # NAVIGATION
    # =====================================================
    def go_login(self):
        self.controller.show_frame("login")

    def go_register(self):
        self.controller.show_frame("register")

    # =====================================================
    # ANIMATIONS
    # =====================================================
    def blink_leds(self):
        if not self.winfo_exists():
            return

        if self.led_state:
            self.scanner_led.configure(fg_color=Colors.DANGER_TK)
            self.card_led.configure(fg_color=Colors.SUCCESS_TK)
        else:
            self.scanner_led.configure(fg_color="#550000") # Dim red
            self.card_led.configure(fg_color="#005500") # Dim green
            
        self.led_state = not self.led_state
        self.after(600, self.blink_leds)
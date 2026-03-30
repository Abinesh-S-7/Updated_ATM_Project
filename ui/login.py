import customtkinter as ctk
from tkinter import messagebox
from ui_theme import Colors
import time
from vision.verification_cam import verify_face


class LoginFrame(ctk.CTkFrame):
    """
    Login Screen for ATM System (Dynamic Premium UI)
    """

    def __init__(self, parent, controller):

        super().__init__(parent, fg_color="transparent")

        self.controller = controller

        # ==============================
        # Fonts
        # ==============================
        self.header_font = ctk.CTkFont(family="Helvetica", size=32, weight="bold")
        self.label_font = ctk.CTkFont(family="Helvetica", size=14)
        self.entry_font = ctk.CTkFont(family="Helvetica", size=15)
        self.button_font = ctk.CTkFont(family="Helvetica", size=15, weight="bold")

        # ==============================
        # MAIN FORM CARD
        # ==============================
        self.card = ctk.CTkFrame(
            self,
            fg_color=Colors.DARK_GRAY_TK,
            corner_radius=15
        )
        self.card.pack(expand=True, padx=20, pady=20, ipadx=40, ipady=40)

        # Title
        ctk.CTkLabel(
            self.card,
            text="Secure Login",
            font=self.header_font,
            text_color=Colors.PRIMARY_TK
        ).pack(pady=(0, 30))

        # Inputs Wrap
        input_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        input_frame.pack(pady=10)

        # -------------------- Card Number --------------------
        ctk.CTkLabel(
            input_frame,
            text="Card Number",
            font=self.label_font,
            text_color=Colors.WHITE_TK
        ).grid(row=0, column=0, padx=(0, 20), pady=15, sticky="e")

        self.card_entry = ctk.CTkEntry(
            input_frame,
            font=self.entry_font,
            width=240,
            height=40,
            corner_radius=8,
            border_color=Colors.GRAY_TK
        )
        self.card_entry.grid(row=0, column=1, pady=15, sticky="w")

        # -------------------- PIN --------------------
        ctk.CTkLabel(
            input_frame,
            text="PIN Code",
            font=self.label_font,
            text_color=Colors.WHITE_TK
        ).grid(row=1, column=0, padx=(0, 20), pady=15, sticky="e")

        self.pin_entry = ctk.CTkEntry(
            input_frame,
            font=self.entry_font,
            width=240,
            height=40,
            corner_radius=8,
            border_color=Colors.GRAY_TK,
            show="*"
        )
        self.pin_entry.grid(row=1, column=1, pady=15, sticky="w")

        # Error Message Label
        self.message_label = ctk.CTkLabel(
            self.card,
            text="",
            text_color=Colors.DANGER_TK,
            font=ctk.CTkFont(family="Helvetica", size=12)
        )
        self.message_label.pack(pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(pady=(20, 0))

        ctk.CTkButton(
            btn_frame,
            text="Proceed securely",
            width=180,
            height=45,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.PRIMARY_TK,
            hover_color="#00b8e6",
            command=self.login
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Back",
            width=150,
            height=45,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.GRAY_TK,
            hover_color="#808080",
            command=self.go_back
        ).pack(side="left", padx=10)


        # =====================================================
        # CAMERA FEED CARD (Hidden Initially)
        # =====================================================
        self.cam_card = ctk.CTkFrame(
            self,
            fg_color=Colors.DARK_GRAY_TK,
            corner_radius=15
        )
        
        ctk.CTkLabel(
            self.cam_card,
            text="Biometric Verification",
            font=self.header_font,
            text_color=Colors.PRIMARY_TK
        ).pack(pady=(20, 10))
        
        self.cam_instruction = ctk.CTkLabel(
            self.cam_card,
            text="Analyzing facial markers... Please remove mask if worn.",
            font=self.label_font,
            text_color=Colors.WHITE_TK
        )
        self.cam_instruction.pack(pady=(0, 10))

        # This label will hold the actual Image Feed
        self.cam_label = ctk.CTkLabel(self.cam_card, text="")
        self.cam_label.pack(pady=10, padx=20)


    # =====================================================
    # LOGIN LOGIC & BIOMETRICS
    # =====================================================
    def login(self):

        card_no = self.card_entry.get().strip()
        pin = self.pin_entry.get().strip()

        # ---------- Basic Validation ----------
        if not card_no or not pin:
            self.message_label.configure(text="Please enter Card Number and PIN")
            return

        if card_no not in self.controller.data:
            self.message_label.configure(text="Invalid Card Number")
            return

        if self.controller.data[card_no]["password"] != pin:
            self.message_label.configure(text="Invalid PIN")
            return

        # =====================================================
        # TRANSITION TO CAMERA VIEW
        # =====================================================
        self.card.pack_forget()                      # Hide form
        self.cam_card.pack(expand=True, pady=20)     # Show camera card
        self.update()                                # Force UI refresh

        # Add a tiny delay to ensure smooth native feeling
        time.sleep(0.3)

        # =====================================================
        # VERIFICATION LOGIC 
        # (This will render the face box inside self.cam_label)
        # =====================================================
        result = verify_face(
            app=self.controller,
            user_id=card_no,
            ui_label=self.cam_label        # Pipe stream native to widget!
        )

        self.cam_card.pack_forget()
        self.clear_fields()
        
        # Natively repack the form so logout returns correctly
        self.card.pack(expand=True, padx=20, pady=20, ipadx=40, ipady=40)

        if result is True:
            messagebox.showinfo("Success", "Login Successful!")
            self.controller.start_transaction(card_no)
        elif result == "otp":
            self.controller.otp_verification(card_no, self.controller.data)
        else:
            # Verification failed, cancelled, or error 
            pass

    # =====================================================
    # UTILS
    # =====================================================
    def go_back(self):
        self.clear_fields()
        self.controller.show_frame("welcome")

    def clear_fields(self):
        self.card_entry.delete(0, 'end')
        self.pin_entry.delete(0, 'end')
        self.message_label.configure(text="")
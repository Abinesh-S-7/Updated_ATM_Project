import customtkinter as ctk
from tkinter import messagebox
from ui_theme import Colors
from vision.registration_cam import take_images
from data.storage import save_data


class RegisterFrame(ctk.CTkFrame):
    """
    Registration Screen for ATM System (Dynamic Premium UI)
    Interactive Multi-Step Wizard
    """

    def __init__(self, parent, controller):

        super().__init__(parent, fg_color="transparent")

        self.controller = controller

        # ==============================
        # Fonts
        # ==============================
        self.header_font = ctk.CTkFont(family="Helvetica", size=32, weight="bold")
        self.label_font = ctk.CTkFont(family="Helvetica", size=18)
        self.entry_font = ctk.CTkFont(family="Helvetica", size=18)
        self.button_font = ctk.CTkFont(family="Helvetica", size=16, weight="bold")

        self.current_step = 0

        # ==============================
        # MAIN FORM CARD
        # ==============================
        self.card = ctk.CTkFrame(
            self,
            fg_color=Colors.DARK_GRAY_TK,
            corner_radius=15
        )
        self.card.pack(expand=True, padx=20, pady=20, ipadx=40, ipady=30)

        # Title
        self.title_label = ctk.CTkLabel(
            self.card,
            text="",
            font=self.header_font,
            text_color=Colors.PRIMARY_TK
        )
        self.title_label.pack(pady=(0, 20))

        # Container for Steps
        self.step_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.step_container.pack(fill="both", expand=True, pady=10)

        # Error Message Label
        self.message_label = ctk.CTkLabel(
            self.card,
            text="",
            text_color=Colors.DANGER_TK,
            font=ctk.CTkFont(family="Helvetica", size=14)
        )
        self.message_label.pack(pady=5)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_frame.pack(pady=(10, 0))

        self.back_btn = ctk.CTkButton(
            self.btn_frame,
            text="Cancel",
            width=130,
            height=45,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.GRAY_TK,
            hover_color="#808080",
            command=self.go_back_step
        )
        self.back_btn.pack(side="left", padx=10)

        self.next_btn = ctk.CTkButton(
            self.btn_frame,
            text="Next",
            width=130,
            height=45,
            corner_radius=8,
            font=self.button_font,
            fg_color=Colors.PRIMARY_TK,
            hover_color="#00b8e6",
            command=self.go_next_step
        )
        self.next_btn.pack(side="left", padx=10)

        # =====================================================
        # BUILD STEPS
        # =====================================================
        self.steps = []
        self.entries = {}

        self.build_step_name()
        self.build_step_mobile()
        self.build_step_account()
        self.build_step_credentials()

        self.update_ui_for_step()

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
            text="Biometric Registration",
            font=self.header_font,
            text_color=Colors.PRIMARY_TK
        ).pack(pady=(20, 10))
        
        self.cam_instruction = ctk.CTkLabel(
            self.cam_card,
            text="Please look directly at the camera. Gathering 100 facial markers...",
            font=self.label_font,
            text_color=Colors.WHITE_TK
        )
        self.cam_instruction.pack(pady=(0, 10))

        # This label will hold the actual Image Feed
        self.cam_label = ctk.CTkLabel(self.cam_card, text="")
        self.cam_label.pack(pady=10, padx=20)


    # =====================================================
    # WIZARD PAGES
    # =====================================================
    def build_step_name(self):
        f = ctk.CTkFrame(self.step_container, fg_color="transparent")
        ctk.CTkLabel(f, text="Enter Your Full Name:", font=self.label_font, text_color=Colors.WHITE_TK).pack(pady=10)
        self.entries["name"] = ctk.CTkEntry(f, font=self.entry_font, width=300, height=45, corner_radius=8, border_color=Colors.GRAY_TK, justify="center")
        self.entries["name"].pack(pady=10)
        self.steps.append({"frame": f, "title": "Welcome"})

    def build_step_mobile(self):
        f = ctk.CTkFrame(self.step_container, fg_color="transparent")
        ctk.CTkLabel(f, text="Enter Your 10-Digit Mobile Number:", font=self.label_font, text_color=Colors.WHITE_TK).pack(pady=10)
        self.entries["mobile"] = ctk.CTkEntry(f, font=self.entry_font, width=300, height=45, corner_radius=8, border_color=Colors.GRAY_TK, justify="center")
        self.entries["mobile"].pack(pady=10)
        self.steps.append({"frame": f, "title": "Contact Info"})

    def build_step_account(self):
        f = ctk.CTkFrame(self.step_container, fg_color="transparent")
        ctk.CTkLabel(f, text="Enter Target Account Number:", font=self.label_font, text_color=Colors.WHITE_TK).pack(pady=5)
        self.entries["account"] = ctk.CTkEntry(f, font=self.entry_font, width=300, height=40, corner_radius=8, border_color=Colors.GRAY_TK, justify="center")
        self.entries["account"].pack(pady=5)
        
        ctk.CTkLabel(f, text="Enter Initial Deposit Amount ($):", font=self.label_font, text_color=Colors.WHITE_TK).pack(pady=(20, 5))
        self.entries["deposit"] = ctk.CTkEntry(f, font=self.entry_font, width=300, height=40, corner_radius=8, border_color=Colors.GRAY_TK, justify="center")
        self.entries["deposit"].pack(pady=5)
        self.steps.append({"frame": f, "title": "Account Setup"})

    def build_step_credentials(self):
        f = ctk.CTkFrame(self.step_container, fg_color="transparent")
        ctk.CTkLabel(f, text="Enter New 16-Digit Card No:", font=self.label_font, text_color=Colors.WHITE_TK).pack(pady=5)
        self.entries["card"] = ctk.CTkEntry(f, font=self.entry_font, width=300, height=40, corner_radius=8, border_color=Colors.GRAY_TK, justify="center")
        self.entries["card"].pack(pady=5)
        
        ctk.CTkLabel(f, text="Create strongly secured 4-Digit PIN:", font=self.label_font, text_color=Colors.WHITE_TK).pack(pady=(20, 5))
        self.entries["pin"] = ctk.CTkEntry(f, font=self.entry_font, width=300, height=40, corner_radius=8, border_color=Colors.GRAY_TK, show="*", justify="center")
        self.entries["pin"].pack(pady=5)
        self.steps.append({"frame": f, "title": "ATM Credentials"})


    # =====================================================
    # WIZARD MECHANICS
    # =====================================================
    def update_ui_for_step(self):
        """Show only the active frame and update titles & buttons."""
        self.message_label.configure(text="")

        for step in self.steps:
            step["frame"].pack_forget()

        current = self.steps[self.current_step]
        self.title_label.configure(text=current["title"])
        current["frame"].pack(expand=True, fill="both")

        # Buttons state
        if self.current_step == 0:
            self.back_btn.configure(text="Cancel")
        else:
            self.back_btn.configure(text="Back")

        if self.current_step == len(self.steps) - 1:
            self.next_btn.configure(text="Register Face")
        else:
            self.next_btn.configure(text="Next")


    def validate_current_step(self):
        """Ensure inputs match rigid requirements before proceeding."""
        if self.current_step == 0:
            name = self.entries["name"].get().strip()
            if not name:
                return False, "Your name cannot be empty."

        elif self.current_step == 1:
            mobile = self.entries["mobile"].get().strip()
            if not mobile.isdigit() or len(mobile) != 10:
                return False, "Mobile number must be exactly 10 digits."

        elif self.current_step == 2:
            acc = self.entries["account"].get().strip()
            dep = self.entries["deposit"].get().strip()
            if not acc or not acc.isalnum():
                return False, "Please enter a valid Account Number."
            try:
                val = float(dep)
                if val < 0:
                    raise ValueError
            except:
                return False, "Initial Deposit must be a positive numeric value."

        elif self.current_step == 3:
            card = self.entries["card"].get().strip()
            pin = self.entries["pin"].get().strip()
            if not card.isdigit():
                return False, "Card number must be strictly numeric."
            if card in self.controller.data:
                return False, "Card number already exists in system!"
            if not pin.isdigit() or len(pin) != 4:
                return False, "PIN must be exactly 4 numeric digits."

        return True, ""


    def go_next_step(self):
        is_valid, error_msg = self.validate_current_step()
        if not is_valid:
            self.message_label.configure(text=error_msg)
            return

        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_ui_for_step()
        else:
            self.submit()

    def go_back_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_ui_for_step()
        else:
            # Go all the way back to main menu
            self.controller.show_frame("welcome")


    # =====================================================
    # SUBMIT & CAMERA
    # =====================================================
    def submit(self):
        self.message_label.configure(text="")
        
        self.card.pack_forget()                      # Hide wizard form
        self.cam_card.pack(expand=True, pady=20)     # Show camera card
        self.update()                                # Force UI refresh

        name = self.entries["name"].get().strip()
        mobile = self.entries["mobile"].get().strip()
        account_no = self.entries["account"].get().strip()
        deposit = self.entries["deposit"].get().strip()
        card_no = self.entries["card"].get().strip()
        pin = self.entries["pin"].get().strip()

        result, message = take_images(
            app=self.controller,
            user_id=card_no,
            name=name,
            phone=mobile,
            deposit=deposit,
            pin=pin,
            ui_label=self.cam_label
        )

        self.cam_card.pack_forget()

        if result != 1:
            self.card.pack(expand=True, padx=20, pady=20, ipadx=40, ipady=30)
            self.message_label.configure(text=message)
            return

        # =====================================================
        # SAVE USER DATA
        # =====================================================
        self.controller.data[card_no] = {
            "password": pin,
            "phone_number": mobile,
            "name": name,
            "account_no": account_no,
            "balance": float(deposit)
        }

        save_data(self.controller.data)

        messagebox.showinfo("Registration Status", "Registration Successful!\nYour biometric face ID and accounts have been configured securely.")

        self.clear_fields()
        self.card.pack(expand=True, padx=20, pady=20, ipadx=40, ipady=30)
        self.controller.show_frame("welcome")


    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, 'end')
        self.message_label.configure(text="")
        self.current_step = 0
        self.update_ui_for_step()
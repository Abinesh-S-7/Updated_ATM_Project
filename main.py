import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import customtkinter as ctk
from ui.app import ATMApp
# Modern App Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
app = ATMApp(root)
root.mainloop()
import cv2
import numpy as np

# Color Theme
class Colors:
    # RGB values for OpenCV
    PRIMARY = (0, 120, 255)      # Blue
    SUCCESS = (0, 255, 0)        # Green
    WARNING = (0, 165, 255)      # Orange
    DANGER = (0, 0, 255)         # Red
    WHITE = (255, 255, 255)      # White
    BLACK = (0, 0, 0)            # Black
    GRAY = (128, 128, 128)       # Gray
    DARK_GRAY = (64, 64, 64)     # Dark Gray
    LIGHT_BLUE = (255, 200, 100) # Light Blue
    PURPLE = (255, 0, 255)       # Purple

    # Hex values for Tkinter
    @staticmethod
    def rgb_to_hex(rgb):
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    # Tkinter colors (Vibrant Fintech Theme)
    PRIMARY_TK = "#00d2ff"       # Neon Cyan
    SUCCESS_TK = "#00e676"       # Neon Green
    WARNING_TK = "#ffaa00"       # Vibrant Amber
    DANGER_TK = "#ff1744"        # Neon Red
    WHITE_TK = "#ffffff"         # White
    BLACK_TK = "#000000"         # Pitch Black
    GRAY_TK = "#b0b0b0"          # Light Gray
    DARK_GRAY_TK = "#15151e"     # Deep Sleek Card Background
    BACKGROUND_TK = "#0d0d12"    # Very Dark Void Background
    LIGHT_BLUE_TK = "#3498db"    # Standard Light Blue
    PURPLE_TK = "#d500f9"        # Neon Purple

# Font Styles
class Fonts:
    TITLE = cv2.FONT_HERSHEY_SIMPLEX
    SUBTITLE = cv2.FONT_HERSHEY_DUPLEX
    BODY = cv2.FONT_HERSHEY_SIMPLEX
    SMALL = cv2.FONT_HERSHEY_SIMPLEX

class UITheme:
    def __init__(self):
        self.window_name = "ATM Security System"
        self.window_size = (1280, 720)
        self.status_bar_height = 50
        self.instruction_bar_height = 60
        self.overlay_alpha = 0.7

    def create_overlay(self, frame, region, color):
        """Create a semi-transparent overlay"""
        overlay = frame.copy()
        cv2.rectangle(overlay, region[0], region[1], color, -1)
        cv2.addWeighted(overlay, self.overlay_alpha, frame, 1 - self.overlay_alpha, 0, frame)
        return frame

    def draw_status_bar(self, frame, status, status_type="info"):
        """Draw status bar with theme"""
        # Determine color based on status type
        color_map = {
            "info": Colors.PRIMARY,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "danger": Colors.DANGER
        }
        color = color_map.get(status_type, Colors.PRIMARY)

        # Create status bar overlay
        region = ((0, 0), (frame.shape[1], self.status_bar_height))
        frame = self.create_overlay(frame, region, Colors.DARK_GRAY)

        # Draw status text
        cv2.putText(frame, f"Status: {status}", (20, 35),
                    Fonts.TITLE, 1, color, 2)
        return frame

    def draw_instructions(self, frame, instructions):
        """Draw instructions panel with theme"""
        # Create instruction bar overlay
        region = ((0, frame.shape[0] - self.instruction_bar_height),
                 (frame.shape[1], frame.shape[0]))
        frame = self.create_overlay(frame, region, Colors.DARK_GRAY)

        # Draw instructions
        for i, instruction in enumerate(instructions):
            y_pos = frame.shape[0] - 20 - (i * 25)
            cv2.putText(frame, instruction, (20, y_pos),
                       Fonts.BODY, 0.7, Colors.WHITE, 2)
        return frame

    def draw_face_box(self, frame, top, right, bottom, left, name, is_verified=False):
        """Draw face box with theme"""
        color = Colors.SUCCESS if is_verified else Colors.DANGER
        
        # Draw main box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw name background
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        # Draw name
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    Fonts.SUBTITLE, 1.0, Colors.WHITE, 1)
        return frame

    def draw_verification_box(self, frame, message):
        """Draw verification message box"""
        # Calculate box dimensions
        text_size = cv2.getTextSize(message, Fonts.TITLE, 0.7, 2)[0]
        box_width = text_size[0] + 40
        box_height = text_size[1] + 40
        
        # Calculate box position (centered)
        x = (frame.shape[1] - box_width) // 2
        y = (frame.shape[0] - box_height) // 2
        
        # Draw box background
        region = ((x, y), (x + box_width, y + box_height))
        frame = self.create_overlay(frame, region, Colors.DARK_GRAY)
        
        # Draw message
        text_x = x + 20
        text_y = y + box_height - 20
        cv2.putText(frame, message, (text_x, text_y),
                    Fonts.TITLE, 0.7, Colors.WHITE, 2)
        return frame

    def draw_progress_bar(self, frame, progress, message=""):
        """Draw progress bar with theme"""
        bar_width = 400
        bar_height = 30
        x = (frame.shape[1] - bar_width) // 2
        y = (frame.shape[0] - bar_height) // 2
        
        # Draw background
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                     Colors.DARK_GRAY, -1)
        
        # Draw progress
        progress_width = int(bar_width * progress)
        cv2.rectangle(frame, (x, y), (x + progress_width, y + bar_height),
                     Colors.PRIMARY, -1)
        
        # Draw message if provided
        if message:
            text_x = x + (bar_width - cv2.getTextSize(message, Fonts.BODY, 0.7, 2)[0][0]) // 2
            text_y = y - 10
            cv2.putText(frame, message, (text_x, text_y),
                       Fonts.BODY, 0.7, Colors.WHITE, 2)
        return frame

    def draw_countdown(self, frame, seconds, message=""):
        """Draw countdown timer with theme"""
        text = f"{message} {seconds}s" if message else f"{seconds}s"
        text_size = cv2.getTextSize(text, Fonts.TITLE, 1, 2)[0]
        x = (frame.shape[1] - text_size[0]) // 2
        y = (frame.shape[0] - text_size[1]) // 2
        
        cv2.putText(frame, text, (x, y), Fonts.TITLE, 1, Colors.WARNING, 2)
        return frame

    def draw_transaction_screen(self, frame, options):
        """Draw transaction screen with theme"""
        # Create main overlay
        frame = self.create_overlay(frame, ((0, 0), (frame.shape[1], frame.shape[0])), Colors.DARK_GRAY)
        
        # Draw title
        title = "Select Transaction"
        title_size = cv2.getTextSize(title, Fonts.TITLE, 1.5, 2)[0]
        title_x = (frame.shape[1] - title_size[0]) // 2
        cv2.putText(frame, title, (title_x, 100), Fonts.TITLE, 1.5, Colors.WHITE, 2)
        
        # Draw options
        for i, option in enumerate(options):
            y = 200 + (i * 60)
            cv2.putText(frame, f"{i+1}. {option}", (frame.shape[1]//4, y),
                       Fonts.SUBTITLE, 1, Colors.PRIMARY, 2)
        
        return frame

# Create global theme instance
theme = UITheme() 
"""
Settings Screen
Application settings and preferences
"""

import customtkinter as ctk
from .base_screen import BaseScreen

class SettingsScreen(BaseScreen):
    """Settings and preferences screen"""
    
    def setup_ui(self):
        """Setup the settings screen UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header frame with title and back button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(20, 10), sticky="ew", padx=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Quay lại",
            width=100,
            height=35,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#666666",
            hover_color="#777777",
            command=self.go_back
        )
        back_btn.grid(row=0, column=0, sticky="w")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Cài Đặt",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=1, pady=(0, 20))
        
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Settings sections
        self.create_appearance_section(content_frame)
        self.create_app_section(content_frame)
    
    def create_appearance_section(self, parent):
        """Create appearance settings section"""
        # Appearance section
        appearance_frame = ctk.CTkFrame(parent)
        appearance_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        appearance_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            appearance_frame,
            text="🎨 Giao Diện",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 15))
        
        # Theme mode
        ctk.CTkLabel(
            appearance_frame,
            text="Chế độ:",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        theme_var = ctk.StringVar(value="dark")
        theme_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=["light", "dark", "system"],
            variable=theme_var,
            command=self.change_theme
        )
        theme_menu.grid(row=1, column=1, sticky="w", padx=20, pady=5)
        
        # Spacer
        ctk.CTkLabel(appearance_frame, text="").grid(row=2, column=0, pady=10)
    
    def create_app_section(self, parent):
        """Create app settings section"""
        # App section
        app_frame = ctk.CTkFrame(parent)
        app_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        app_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            app_frame,
            text="⚙️ Ứng Dụng",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 15))
        
        # Auto-save
        auto_save_var = ctk.BooleanVar(value=True)
        auto_save_checkbox = ctk.CTkCheckBox(
            app_frame,
            text="Tự động lưu cài đặt",
            variable=auto_save_var
        )
        auto_save_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)
        
        # Check updates
        check_updates_var = ctk.BooleanVar(value=False)
        check_updates_checkbox = ctk.CTkCheckBox(
            app_frame,
            text="Kiểm tra cập nhật tự động",
            variable=check_updates_var
        )
        check_updates_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=5)
        
        # About button
        about_btn = ctk.CTkButton(
            app_frame,
            text="📋 Thông tin ứng dụng",
            command=self.show_about,
            height=35
        )
        about_btn.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 20))
    
    def change_theme(self, theme):
        """Change application theme"""
        ctk.set_appearance_mode(theme)
    
    def show_about(self):
        """Show about dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thông tin")
        dialog.geometry("400x300")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Content
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # App info
        ctk.CTkLabel(
            content_frame,
            text="KingGodCastle AIO",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            content_frame,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            content_frame,
            text="Unity Project Editor & XAPK Converter",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            content_frame,
            text="'Tôi chả hiểu sao tôi làm app này' - NOwL",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color="#888888"
        ).pack(pady=(20, 0))
        
        # Close button
        close_btn = ctk.CTkButton(
            content_frame,
            text="Đóng",
            command=dialog.destroy,
            width=100
        )
        close_btn.pack(pady=(30, 20))
    
    def go_back(self):
        """Navigate back to previous screen"""
        if self.main_window:
            self.main_window.go_back()

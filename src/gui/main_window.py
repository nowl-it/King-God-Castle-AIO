"""
Main Window
The main application window with navigation and screen management
"""

from tkinter import Menu
import customtkinter as ctk
import sys, os
from typing import Dict, Type
from src.screens import XAPKInstallScreen, EditorWindow, SettingsScreen, BaseScreen
from src.utils.config import ConfigManager


class MainWindow:
    """Main application window with modern floating design"""

    def __init__(self):
        self.config = ConfigManager()

        # Configure CustomTkinter
        ctk.set_appearance_mode(self.config.get_theme_setting("theme.mode", "dark"))
        ctk.set_default_color_theme(
            self.config.get_theme_setting("theme.color_theme", "blue")
        )

        # Create main window
        self.root: ctk.CTk = ctk.CTk()

        self.setup_window()

        # Screen management
        self.screens: Dict[str, BaseScreen] = {}
        self.current_screen = None
        self.navigation_stack = []  # Track navigation history

        # Initialize UI
        self.setup_ui()
        self.setup_screens()

        # Show initial screen
        self.show_screen("unity_editor")

    def setup_menubar(self):
        """Create a professional menu bar using tkinter Menu"""
        # Create main menubar with dark theme
        menubar = Menu(
            self.root,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
            borderwidth=0,
            relief="flat",
        )
        self.root.config(menu=menubar)

        # File Menu
        file_menu = Menu(
            menubar,
            tearoff=0,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
        )
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="New Project", command=self.new_project, accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="Open Project", command=self.open_project, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="Recent Projects", command=self.show_recent_projects
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Settings", command=self.show_settings, accelerator="Ctrl+,"
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit", command=self.on_closing, accelerator="Ctrl+Q"
        )

        # View Menu
        view_menu = Menu(
            menubar,
            tearoff=0,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
        )
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(
            label="Unity Editor", command=lambda: self.show_screen("unity_editor")
        )
        view_menu.add_command(
            label="XAPK Installer",
            command=lambda: self.show_screen("xapk_install"),
        )
        view_menu.add_separator()
        view_menu.add_command(
            label="Toggle Fullscreen", command=self.toggle_fullscreen, accelerator="F11"
        )
        view_menu.add_command(label="Reset Layout", command=self.reset_layout)
        view_menu.add_separator()
        view_menu.add_command(
            label="Zoom In", command=self.zoom_in, accelerator="Ctrl++"
        )
        view_menu.add_command(
            label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-"
        )
        view_menu.add_command(
            label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0"
        )

        # Tools Menu
        tools_menu = Menu(
            menubar,
            tearoff=0,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
        )
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Asset Ripper", command=self.open_asset_ripper)
        tools_menu.add_command(label="Unity Hub", command=self.open_unity_hub)
        tools_menu.add_separator()
        tools_menu.add_command(label="Install & Setup XAPK", command=self.extract_xapk)
        tools_menu.add_command(
            label="Build Project", command=self.build_project, accelerator="Ctrl+B"
        )
        tools_menu.add_separator()
        tools_menu.add_command(
            label="Package Manager", command=self.open_package_manager
        )
        tools_menu.add_command(
            label="Version Control", command=self.open_version_control
        )

        # Project Menu
        project_menu = Menu(
            menubar,
            tearoff=0,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
        )
        menubar.add_cascade(label="Project", menu=project_menu)
        project_menu.add_command(
            label="Project Settings", command=self.show_project_settings
        )
        project_menu.add_command(
            label="Build Settings", command=self.show_build_settings
        )
        project_menu.add_separator()
        project_menu.add_command(label="Import Package", command=self.import_package)
        project_menu.add_command(label="Export Package", command=self.export_package)
        project_menu.add_separator()
        project_menu.add_command(
            label="Refresh Assets", command=self.refresh_assets, accelerator="Ctrl+R"
        )
        project_menu.add_command(label="Reimport All", command=self.reimport_all)

        # Window Menu
        window_menu = Menu(
            menubar,
            tearoff=0,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
        )
        menubar.add_cascade(label="Window", menu=window_menu)
        window_menu.add_command(
            label="Minimize", command=self.minimize_window, accelerator="Ctrl+M"
        )
        window_menu.add_command(label="Maximize", command=self.maximize_window)
        window_menu.add_separator()
        window_menu.add_command(
            label="Always on Top", command=self.toggle_always_on_top
        )
        window_menu.add_command(label="Transparency", command=self.adjust_transparency)

        # Help Menu
        help_menu = Menu(
            menubar,
            tearoff=0,
            background="#2d2d2d",
            foreground="#e0e0e0",
            activebackground="#404040",
            activeforeground="#ffffff",
        )
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(
            label="Documentation", command=self.show_documentation, accelerator="F1"
        )
        help_menu.add_command(
            label="Keyboard Shortcuts",
            command=self.show_shortcuts,
            accelerator="Ctrl+/",
        )
        help_menu.add_command(label="Tutorials", command=self.show_tutorials)
        help_menu.add_separator()
        help_menu.add_command(label="Report Bug", command=self.report_bug)
        help_menu.add_command(label="Feature Request", command=self.feature_request)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_command(label="About", command=self.show_about)

    def create_menu_buttons(self, parent):
        """Create menu buttons for the menubar"""
        menu_data = [
            (
                "File",
                [
                    ("New Project", self.new_project),
                    ("Open Project", self.open_project),
                    ("separator", None),
                    ("Settings", self.show_settings),
                    ("separator", None),
                    ("Exit", self.on_closing),
                ],
            ),
            (
                "View",
                [
                    ("Unity Editor", lambda: self.show_screen("unity_editor")),
                    ("XAPK Installer", lambda: self.show_screen("xapk_install")),
                    ("separator", None),
                    ("Toggle Fullscreen", self.toggle_fullscreen),
                    ("Reset Layout", self.reset_layout),
                ],
            ),
            (
                "Tools",
                [
                    ("Asset Ripper", self.open_asset_ripper),
                    ("Unity Hub", self.open_unity_hub),
                    ("separator", None),
                    ("Extract XAPK", self.extract_xapk),
                    ("Build Project", self.build_project),
                ],
            ),
            (
                "Help",
                [
                    ("Documentation", self.show_documentation),
                    ("Keyboard Shortcuts", self.show_shortcuts),
                    ("separator", None),
                    ("Check Updates", self.check_updates),
                    ("About", self.show_about),
                ],
            ),
        ]

        for i, (menu_title, menu_items) in enumerate(menu_data):
            menu_btn = self.create_menu_dropdown(parent, menu_title, menu_items)
            menu_btn.grid(row=0, column=i, padx=2, pady=2)

    def create_menu_dropdown(self, parent, title, menu_items):
        """Create a dropdown menu button"""
        menu_btn = ctk.CTkButton(
            parent,
            text=title,
            width=60,
            height=24,
            font=ctk.CTkFont(size=11, weight="normal"),
            fg_color="transparent",
            hover_color="#404040",
            text_color="#e0e0e0",
            border_width=0,
            corner_radius=3,
        )

        def show_dropdown():
            # Hide other dropdowns first
            self.hide_menu_dropdowns()

            # Create dropdown window
            dropdown = ctk.CTkToplevel(self.root)
            dropdown.withdraw()
            dropdown.overrideredirect(True)
            dropdown.configure(fg_color="#2d2d2d", pady=2)
            dropdown.wm_attributes("-topmost", True)

            # Create menu items
            for idx, (item_text, command) in enumerate(menu_items):
                if item_text == "separator":
                    sep = ctk.CTkFrame(dropdown, height=1, fg_color="#404040")
                    sep.pack(fill="x", padx=8, pady=2)
                else:
                    item_btn = ctk.CTkButton(
                        dropdown,
                        text=item_text,
                        height=26,
                        font=ctk.CTkFont(size=10),
                        fg_color="transparent",
                        hover_color="#404040",
                        text_color="#e8e8e8",
                        anchor="w",
                        command=lambda cmd=command, dw=dropdown: self.execute_menu_command(
                            cmd, dw
                        ),
                    )
                    item_btn.pack(fill="x", padx=4, pady=2)

            # Position dropdown
            btn_x = menu_btn.winfo_rootx()
            btn_y = menu_btn.winfo_rooty() + menu_btn.winfo_height() + 5
            dropdown.geometry(f"+{btn_x}+{btn_y}")

            # Show dropdown
            dropdown.deiconify()
            dropdown.lift()

            # Store reference
            setattr(menu_btn, "_dropdown", dropdown)
            menu_btn.configure(fg_color="#404040")

            # Close dropdown on click outside
            def close_on_click(event):
                try:
                    dropdown.destroy()
                    menu_btn.configure(fg_color="transparent")
                    self.root.unbind("<Button-1>")
                except:
                    pass

            self.root.after(
                100, lambda: self.root.bind("<Button-1>", close_on_click, add="+")
            )

        menu_btn.configure(command=show_dropdown)
        return menu_btn

    def hide_menu_dropdowns(self):
        """Hide all open menu dropdowns"""
        try:
            for child in self.root.winfo_children():
                if isinstance(child, ctk.CTkToplevel) and hasattr(
                    child, "wm_overrideredirect"
                ):
                    try:
                        child.destroy()
                    except:
                        pass
        except:
            pass

    def execute_menu_command(self, command, dropdown_window):
        """Execute menu command and close dropdown"""
        try:
            dropdown_window.destroy()
        except:
            pass

        if command:
            try:
                command()
            except Exception as e:
                print(f"Menu command error: {e}")

    def setup_window(self):
        """Configure the main window"""
        # Window properties
        self.root.title(self.config.get_app_setting("app_name", "King God Castle AIO"))

        # Window size and position
        width = self.config.get_app_setting("window.default_width", 1200)
        height = self.config.get_app_setting("window.default_height", 800)

        # Center window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Window behavior
        min_width = self.config.get_app_setting("window.min_width", 800)
        min_height = self.config.get_app_setting("window.min_height", 600)
        self.root.minsize(min_width, min_height)

        # Floating window (always on top) - default behavior
        if self.config.get_app_setting("window.floating", True):
            self.root.attributes("-topmost", True)
            self.root.attributes("-type", "utility")

        # Transparency
        transparency = self.config.get_app_setting("window.transparency", 0.95)
        self.root.attributes("-alpha", transparency)

        # Protocol handlers
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Setup the main user interface"""
        # Menu bar (tkinter Menu doesn't take grid space)
        self.setup_menubar()

        # Configure grid - main content uses full space since Menu doesn't use grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(
            0, weight=1
        )  # Back to row 0 since Menu doesn't use grid

        # Don't create sidebar initially - it will be created when needed
        self.sidebar = None

        # Create main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(
            row=0, column=1, sticky="nsew", padx=0, pady=0
        )  # Back to row 0
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def update_layout_for_screen(self, screen_id: str):
        """Update layout based on screen requirements"""
        # Check if this screen should hide sidebar
        hide_sidebar = self.config.get_app_setting(
            f"screens.{screen_id}.hide_sidebar", False
        )

        if hide_sidebar:
            # Hide sidebar if it exists and expand main frame
            if self.sidebar:
                self.sidebar.grid_remove()
            self.root.grid_columnconfigure(0, weight=0)
            self.root.grid_columnconfigure(1, weight=1)
            self.main_frame.grid(
                row=0,  # Back to row 0 since Menu doesn't use grid
                column=0,
                columnspan=2,
                sticky="nsew",
                padx=0,
                pady=0,
            )

    def setup_screens(self):
        """Initialize all application screens"""
        screen_classes: Dict[str, Type[BaseScreen]] = {
            "unity_editor": EditorWindow,
            "xapk_install": XAPKInstallScreen,
            "settings": SettingsScreen,
        }

        for screen_id, screen_class in screen_classes.items():
            if screen_id == "unity_editor":
                # Unity Editor screen needs special initialization
                screen = screen_class(
                    self.main_frame, main_window=self, unity_project_path=None
                )
            else:
                screen = screen_class(self.main_frame, main_window=self)
            screen.grid(row=0, column=0, sticky="nsew")
            screen.grid_remove()  # Hide initially
            self.screens[screen_id] = screen

    def show_screen(self, screen_id: str, add_to_history: bool = True):
        """Show a specific screen"""
        if screen_id not in self.screens:
            print(f"Warning: Screen '{screen_id}' not found")
            return

        # Update layout for this screen
        self.update_layout_for_screen(screen_id)

        # Add current screen to navigation stack if switching to different screen
        if add_to_history and self.current_screen and self.current_screen != screen_id:
            self.navigation_stack.append(self.current_screen)

        # Hide current screen
        if self.current_screen:
            self.screens[self.current_screen].grid_remove()
            self.screens[self.current_screen].on_hide()

        # Show new screen
        self.screens[screen_id].grid()
        self.screens[screen_id].on_show()
        self.current_screen = screen_id

    def on_closing(self):
        """Handle window closing"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        finally:
            sys.exit(0)

    def go_back(self):
        """Navigate back to previous screen"""
        if self.navigation_stack:
            previous_screen = self.navigation_stack.pop()
            self.show_screen(previous_screen, add_to_history=False)
        else:
            # If no history, go to default screen (unity_editor)
            self.show_screen("unity_editor", add_to_history=False)

    def run(self):
        """Start the application main loop"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            print(f"Application error: {e}")
            self.on_closing()

    # Menu Action Methods
    def new_project(self):
        """Create a new project"""
        print("📁 New Project - Opening project wizard...")
        # TODO: Implement project creation wizard

    def open_project(self):
        """Open an existing Unity project and show in editor screen"""
        from tkinter import filedialog
        import os

        project_folder = filedialog.askdirectory(title="Chọn thư mục dự án Unity")
        if not project_folder:
            print("⚠️ Đã hủy chọn dự án")
            return
        # Kiểm tra hợp lệ
        project_settings = os.path.join(
            project_folder, "ProjectSettings", "ProjectVersion.txt"
        )
        if not os.path.exists(project_settings):
            print("❌ Thư mục đã chọn không phải là dự án Unity hợp lệ")
            print("💡 Hãy chọn thư mục chứa file ProjectSettings/ProjectVersion.txt")
            return
        # Load project vào EditorWindow
        editor = self.screens.get("unity_editor")
        load_project_method = getattr(editor, "load_project", None)
        if editor and callable(load_project_method):
            load_project_method(project_folder)
            print(f"✅ Đã mở dự án Unity: {os.path.basename(project_folder)}")
            print(f"📂 Đường dẫn: {project_folder}")
            self.show_screen("unity_editor")
        else:
            print(
                "❌ Không tìm thấy màn hình Unity Editor hoặc phương thức load_project"
            )

    def show_settings(self):
        """Show application settings"""
        print("⚙️ Opening Settings...")
        self.show_screen("settings")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        print("🖥️ Toggling fullscreen...")
        # TODO: Implement fullscreen toggle

    def reset_layout(self):
        """Reset window layout to default"""
        print("🔄 Resetting layout...")
        # TODO: Reset window size and position

    def open_asset_ripper(self):
        """Open Asset Ripper tool"""
        print("🎨 Opening Asset Ripper...")
        # TODO: Launch Asset Ripper

    def open_unity_hub(self):
        """Open Unity Hub"""
        print("🎮 Opening Unity Hub...")
        # TODO: Launch Unity Hub

    def extract_xapk(self):
        """Extract XAPK files"""
        print("📱 Opening XAPK Extractor...")
        self.show_screen("xapk_install")

    def build_project(self):
        """Build the current project"""
        print("🔨 Building project...")
        # TODO: Implement project build

    def show_documentation(self):
        """Show documentation"""
        print("📖 Opening documentation...")
        # TODO: Open documentation in browser

    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        print("⌨️ Showing keyboard shortcuts...")
        # TODO: Show shortcuts dialog

    def check_updates(self):
        """Check for application updates"""
        print("🔄 Checking for updates...")
        # TODO: Implement update checker

    def show_about(self):
        """Show about dialog"""
        print("ℹ️ About King God Castle AIO")
        # TODO: Show about dialog with version info

    # Additional Menu Action Methods
    def show_recent_projects(self):
        """Show recent projects list"""
        print("📁 Showing recent projects...")
        # TODO: Implement recent projects dialog

    def zoom_in(self):
        """Zoom in the interface"""
        print("🔍+ Zooming in...")
        # TODO: Implement zoom functionality

    def zoom_out(self):
        """Zoom out the interface"""
        print("🔍- Zooming out...")
        # TODO: Implement zoom functionality

    def reset_zoom(self):
        """Reset zoom to default"""
        print("🔍 Resetting zoom...")
        # TODO: Reset zoom to 100%

    def open_package_manager(self):
        """Open package manager"""
        print("📦 Opening package manager...")
        # TODO: Implement package manager

    def open_version_control(self):
        """Open version control interface"""
        print("🔧 Opening version control...")
        # TODO: Implement version control

    def show_project_settings(self):
        """Show project settings"""
        print("⚙️ Opening project settings...")
        # TODO: Implement project settings dialog

    def show_build_settings(self):
        """Show build settings"""
        print("🔨 Opening build settings...")
        # TODO: Implement build settings dialog

    def import_package(self):
        """Import unity package"""
        print("📥 Importing package...")
        # TODO: Implement package import

    def export_package(self):
        """Export unity package"""
        print("📤 Exporting package...")
        # TODO: Implement package export

    def refresh_assets(self):
        """Refresh project assets"""
        print("🔄 Refreshing assets...")
        # TODO: Implement asset refresh

    def reimport_all(self):
        """Reimport all assets"""
        print("🔄 Reimporting all assets...")
        # TODO: Implement reimport all

    def minimize_window(self):
        """Minimize main window"""
        print("⬇️ Minimizing window...")
        self.root.iconify()

    def maximize_window(self):
        """Toggle maximize window"""
        print("⬆️ Maximizing window...")
        # Get current state
        if self.root.state() == "zoomed":
            self.root.state("normal")
        else:
            self.root.state("zoomed")

    def toggle_always_on_top(self):
        """Toggle always on top mode"""
        current_state = self.root.attributes("-topmost")
        self.root.attributes("-topmost", not current_state)
        status = "enabled" if not current_state else "disabled"
        print(f"📌 Always on top {status}")

    def adjust_transparency(self):
        """Adjust window transparency"""
        print("🔄 Adjusting transparency...")
        # TODO: Implement transparency slider dialog

    def show_tutorials(self):
        """Show tutorials"""
        print("🎓 Opening tutorials...")
        # TODO: Open tutorials in browser

    def report_bug(self):
        """Report a bug"""
        print("🐛 Opening bug report...")
        # TODO: Open bug report form

    def feature_request(self):
        """Submit feature request"""
        print("💡 Opening feature request...")
        # TODO: Open feature request form

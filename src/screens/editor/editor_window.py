import os
import datetime
import subprocess
import platform
import glob
import json
from tkinter import filedialog
import customtkinter as ctk
from ..base_screen import BaseScreen


class ResizableFrame(ctk.CTkFrame):
    """Frame that can be resized by dragging its border"""

    def __init__(
        self, parent, orientation="vertical", min_size=100, max_size=500, **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.orientation = orientation  # "vertical" for width, "horizontal" for height
        self.min_size = min_size
        self.max_size = max_size
        self.is_dragging = False
        self.start_pos = 0
        self.start_size = 0

    def create_resize_handle(self, side="right"):
        """Create a resize handle on the specified side"""
        handle = None
        if side == "right":
            handle = ctk.CTkFrame(
                self,
                width=4,
                fg_color="#555555",
                corner_radius=0,
                cursor="sb_h_double_arrow",
            )
            handle.pack(side="right", fill="y")
        elif side == "bottom":
            handle = ctk.CTkFrame(
                self,
                height=4,
                fg_color="#555555",
                corner_radius=0,
                cursor="sb_v_double_arrow",
            )
            handle.pack(side="bottom", fill="x")

        if handle:
            handle.bind("<Button-1>", self.start_resize)
            handle.bind("<B1-Motion>", self.on_resize)
            handle.bind("<ButtonRelease-1>", self.stop_resize)
        return handle

    def start_resize(self, event):
        self.is_dragging = True
        if self.orientation == "vertical":
            self.start_pos = event.x_root
            self.start_size = self.winfo_width()
        else:
            self.start_pos = event.y_root
            self.start_size = self.winfo_height()

    def on_resize(self, event):
        if not self.is_dragging:
            return

        if self.orientation == "vertical":
            delta = event.x_root - self.start_pos
            new_size = max(self.min_size, min(self.max_size, self.start_size + delta))
            self.configure(width=new_size)
        else:
            delta = event.y_root - self.start_pos
            new_size = max(self.min_size, min(self.max_size, self.start_size + delta))
            self.configure(height=new_size)

    def stop_resize(self, event):
        self.is_dragging = False


class EditorWindow(BaseScreen):
    def __init__(self, parent, main_window=None, unity_project_path=None):
        self.unity_project_path = unity_project_path

        # UI state variables
        self.sidebar_width = 280
        self.bottom_height = 150
        self.bottom_collapsed = False
        self.explorer_collapsed = False
        self.min_sidebar_width = 150
        self.max_sidebar_width = 500
        self.min_bottom_height = 100
        self.max_bottom_height = 400

        # Auto-load last project if no project specified
        if not self.unity_project_path:
            self.unity_project_path = self.load_last_project()

        super().__init__(parent, main_window=main_window)

    def toggle_bottom_panel(self):
        """Toggle bottom panel collapse/expand"""
        print(f"Toggle bottom panel called - collapsed: {self.bottom_collapsed}")
        self.bottom_collapsed = not self.bottom_collapsed
        if hasattr(self, "bottom_container"):
            if self.bottom_collapsed:
                self.bottom_container.grid_remove()
                if hasattr(self, "bottom_collapse_btn"):
                    self.bottom_collapse_btn.configure(text="▲")
                print("Bottom panel hidden")
            else:
                columnspan = 2 if self.has_project() else 1
                self.bottom_container.grid(
                    row=2, column=0, columnspan=columnspan, sticky="ew", padx=0, pady=0
                )
                if hasattr(self, "bottom_collapse_btn"):
                    self.bottom_collapse_btn.configure(text="▼")
                print("Bottom panel shown")
        return "break"

    def toggle_explorer(self):
        """Toggle explorer section collapse/expand"""
        self.explorer_collapsed = not self.explorer_collapsed
        if hasattr(self, "explorer_content"):
            if self.explorer_collapsed:
                self.explorer_content.grid_remove()
                if hasattr(self, "explorer_collapse_btn"):
                    self.explorer_collapse_btn.configure(text="▶")
                # When explorer is collapsed, no weight changes needed
                if hasattr(self, "sidebar_frame"):
                    self.sidebar_frame.grid_rowconfigure(
                        0, weight=0
                    )  # Explorer collapsed
            else:
                self.explorer_content.grid(
                    row=1, column=0, sticky="nsew", padx=0, pady=0
                )
                if hasattr(self, "explorer_collapse_btn"):
                    self.explorer_collapse_btn.configure(text="▼")
                # When explorer is expanded, it takes available space
                if hasattr(self, "sidebar_frame"):
                    self.sidebar_frame.grid_rowconfigure(
                        0, weight=1
                    )  # Explorer expands

    def resize_sidebar(self, new_width):
        """Resize sidebar width"""
        self.sidebar_width = max(
            self.min_sidebar_width, min(self.max_sidebar_width, new_width)
        )
        if hasattr(self, "sidebar_frame"):
            self.sidebar_frame.configure(width=self.sidebar_width)
            self.main_container.grid_columnconfigure(
                0, weight=0, minsize=self.sidebar_width
            )

    def resize_bottom_panel(self, new_height):
        """Resize bottom panel height"""
        self.bottom_height = max(
            self.min_bottom_height, min(self.max_bottom_height, new_height)
        )
        if hasattr(self, "bottom_frame"):
            self.bottom_frame.configure(height=self.bottom_height)

    def get_config_file_path(self):
        """Get path to config file for storing last project"""
        config_dir = os.path.expanduser("~/.kinggodcastle")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "last_project.json")

    def save_last_project(self, project_path):
        """Save last opened project path"""
        try:
            config_data = {
                "last_project_path": str(project_path),
                "last_opened": datetime.datetime.now().isoformat(),
            }
            with open(self.get_config_file_path(), "w") as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save last project: {e}")

    def load_last_project(self):
        """Load last opened project path"""
        try:
            config_file = self.get_config_file_path()
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config_data = json.load(f)
                    project_path = config_data.get("last_project_path")
                    if project_path and os.path.exists(project_path):
                        return project_path
        except Exception as e:
            print(f"Warning: Could not load last project: {e}")
        return None

    def clear_last_project(self):
        """Clear saved last project"""
        try:
            config_file = self.get_config_file_path()
            if os.path.exists(config_file):
                os.remove(config_file)
                self.add_output_message("🗑️ Đã xóa dự án đã lưu")
        except Exception as e:
            print(f"Warning: Could not clear last project: {e}")

    def has_project(self):
        """Check if project is loaded and exists"""
        return self.unity_project_path and os.path.exists(str(self.unity_project_path))

    def get_project_name(self):
        """Get project name or return default text"""
        if self.has_project():
            return os.path.basename(str(self.unity_project_path))
        return "Chưa chọn dự án"

    def setup_ui(self):
        """Set up VSCode-like Editor interface"""
        # Configure main grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Check if we auto-loaded a project and notify user
        if self.has_project():
            project_name = self.get_project_name()
            self.add_output_message(
                f"🔄 Đã tự động tải dự án từ phiên trước: {project_name}"
            )
            self.add_output_message(f"📂 Đường dẫn: {self.unity_project_path}")

        # Main container with VSCode-like colors
        self.main_container = ctk.CTkFrame(
            self, fg_color="#1e1e1e"
        )  # VSCode dark background
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(
            1, weight=1
        )  # Make main content area expandable (row 1 again)

        # Dynamic column configuration based on project state
        if self.has_project():
            self.main_container.grid_columnconfigure(
                0, weight=0, minsize=self.sidebar_width
            )  # Left sidebar
            self.main_container.grid_columnconfigure(1, weight=1)  # Main editor area
        else:
            self.main_container.grid_columnconfigure(0, weight=1)  # Full width editor

        # Left sidebar (only if project loaded)
        if self.has_project():
            self.setup_left_sidebar(self.main_container)

        # Main editor area
        self.setup_editor_area(self.main_container)

        # Bottom panel (terminal/output like VSCode)
        self.setup_bottom_panel(self.main_container)

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the editor"""
        print("Setting up keyboard shortcuts...")

        # Get the top level window for global shortcuts
        top_level = self.winfo_toplevel()
        print(f"Top level widget: {top_level}")

        # Bind shortcuts to toplevel window for global access
        top_level.bind("<Control-j>", self.on_ctrl_j)
        top_level.bind("<Control-e>", self.on_ctrl_e)  # Explorer toggle

        # Also bind to self for redundancy
        self.bind("<Control-j>", self.on_ctrl_j)
        self.bind("<Control-e>", self.on_ctrl_e)

        # Make sure this widget can receive focus
        self.focus_set()

        # Set initial focus after a delay
        self.after(100, lambda: self.focus_force())
        print("Keyboard shortcuts setup complete")

    def on_ctrl_j(self, event):
        """Handle Ctrl+J shortcut"""
        print("Ctrl+J pressed!")
        self.toggle_bottom_panel()
        return "break"

    def on_ctrl_e(self, event):
        """Handle Ctrl+E shortcut - Toggle Explorer"""
        print("Ctrl+E pressed!")
        self.toggle_explorer()
        return "break"

    # Menu action methods (placeholders)
    def new_project(self):
        """Create new project"""
        self.add_output_message("🆕 New Project - Feature coming soon!")

    def open_project(self):
        """Open existing Unity project"""
        project_folder = filedialog.askdirectory(
            title="Chọn thư mục dự án Unity", initialdir=os.path.expanduser("~")
        )

        if project_folder:
            # Check if it's a valid Unity project
            if self.is_unity_project(project_folder):
                self.unity_project_path = project_folder

                # Save this project as the last opened project
                self.save_last_project(project_folder)

                self.add_output_message(
                    f"✅ Đã tải dự án Unity: {os.path.basename(project_folder)}"
                )
                self.add_output_message(f"📂 Đường dẫn: {project_folder}")

                # Refresh UI to show project and sidebar
                self.refresh_layout()

                # Update main window if available
                if self.main_window:
                    self.main_window.unity_project_path = project_folder
            else:
                self.add_output_message(
                    "❌ Thư mục đã chọn không phải là dự án Unity hợp lệ"
                )
                self.add_output_message(
                    "💡 Hãy chọn thư mục chứa file ProjectSettings/ProjectVersion.txt"
                )
        else:
            self.add_output_message("⚠️ Đã hủy chọn dự án")

    def save_project(self):
        """Save current project"""
        self.add_output_message("💾 Save Project - Feature coming soon!")

    def export_game(self):
        """Export game"""
        self.add_output_message("📤 Export Game - Feature coming soon!")

    def close_application(self):
        """Close application"""
        self.add_output_message("❌ Closing application...")
        if hasattr(self, "main_window") and self.main_window:
            self.main_window.quit()

    def build_game(self):
        """Build game"""
        self.add_output_message("🎮 Build Game - Feature coming soon!")

    def run_game(self):
        """Run game"""
        self.add_output_message("🏃 Run Game - Feature coming soon!")

    def clean_project(self):
        """Clean project"""
        self.add_output_message("🧹 Clean Project - Feature coming soon!")

    def show_project_settings(self):
        """Show project settings"""
        self.add_output_message("⚙️ Project Settings - Feature coming soon!")

    def open_asset_ripper(self):
        """Open Asset Ripper"""
        self.add_output_message("🎨 Asset Ripper - Feature coming soon!")

    def open_xapk_installer(self):
        """Open XAPK Installer"""
        self.add_output_message("📱 Opening XAPK Installer...")
        if self.main_window:
            self.main_window.show_screen("xapk_install")

    def show_preferences(self):
        """Show preferences"""
        self.add_output_message("🔧 Preferences - Feature coming soon!")

    def show_theme_settings(self):
        """Show theme settings"""
        self.add_output_message("🎨 Theme Settings - Feature coming soon!")

    def show_documentation(self):
        """Show documentation"""
        self.add_output_message("📖 Documentation - Feature coming soon!")

    def show_support(self):
        """Show support"""
        self.add_output_message("🆘 Support - Feature coming soon!")

    def setup_left_sidebar(self, parent):
        """Create redesigned left sidebar with resize functionality"""
        # Container for sidebar + resize handle
        self.sidebar_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.sidebar_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_container.grid_columnconfigure(0, weight=1)
        self.sidebar_container.grid_columnconfigure(1, weight=0)
        self.sidebar_container.grid_rowconfigure(0, weight=1)

        # Resizable sidebar frame
        self.sidebar_frame = ResizableFrame(
            self.sidebar_container,
            width=self.sidebar_width,
            fg_color="#252526",
            corner_radius=0,
            orientation="vertical",
            min_size=self.min_sidebar_width,
            max_size=self.max_sidebar_width,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_propagate(False)
        # Simple 1-row layout:
        # Row 0: Explorer (takes full space)
        self.sidebar_frame.grid_rowconfigure(0, weight=1)  # Explorer expandable
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        # Create resize handle
        resize_handle = ctk.CTkFrame(
            self.sidebar_container,
            width=4,
            fg_color="#555555",
            corner_radius=0,
            cursor="sb_h_double_arrow",
        )
        resize_handle.grid(row=0, column=1, sticky="ns", padx=0, pady=0)
        resize_handle.grid_propagate(False)

        # Bind resize events
        resize_handle.bind("<Button-1>", self.start_sidebar_resize)
        resize_handle.bind("<B1-Motion>", self.on_sidebar_resize)
        resize_handle.bind("<ButtonRelease-1>", self.stop_sidebar_resize)

        # Setup sidebar content
        self.setup_file_explorer(self.sidebar_frame)

    def start_sidebar_resize(self, event):
        """Start resizing sidebar"""
        self.resize_start_x = event.x_root
        self.resize_start_width = self.sidebar_frame.winfo_width()

    def on_sidebar_resize(self, event):
        """Handle sidebar resize"""
        delta = event.x_root - self.resize_start_x
        new_width = max(
            self.min_sidebar_width,
            min(self.max_sidebar_width, self.resize_start_width + delta),
        )
        self.sidebar_frame.configure(width=new_width)
        self.sidebar_width = new_width
        self.main_container.grid_columnconfigure(0, weight=0, minsize=new_width)

    def stop_sidebar_resize(self, event):
        """Stop resizing sidebar"""
        pass

    def setup_file_explorer(self, parent):
        """Create simplified file explorer"""
        explorer_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e", corner_radius=0)
        explorer_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        explorer_frame.grid_rowconfigure(1, weight=1)
        explorer_frame.grid_columnconfigure(0, weight=1)

        # Enable focus for mouse events
        explorer_frame.focus_set()

        # Header
        header_frame = ctk.CTkFrame(
            explorer_frame, height=45, fg_color="#37373d", corner_radius=0
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        heroes_list = self.load_heroes_from_folder()
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"HEROES ({len(heroes_list)})",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#cccccc",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        # Collapse button for explorer
        self.explorer_collapse_btn = ctk.CTkButton(
            header_frame,
            text="▼",
            width=20,
            height=20,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color="#cccccc",
            hover_color="#404040",
            command=self.toggle_explorer,
        )
        self.explorer_collapse_btn.grid(row=0, column=1, sticky="e", padx=5, pady=10)

        # File tree area (collapsible content)
        self.explorer_content = ctk.CTkScrollableFrame(
            explorer_frame,
            fg_color="#1e1e1e",
            scrollbar_button_color="#404040",
            scrollbar_button_hover_color="#555555",
        )
        self.explorer_content.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Enable mouse wheel scrolling for explorer content
        self.bind_mousewheel_to_widget(self.explorer_content)

        # Set focus when mouse enters explorer area
        def on_enter(event):
            self.explorer_content.focus_set()

        def on_leave(event):
            pass  # Keep focus for now

        explorer_frame.bind("<Enter>", on_enter)
        self.explorer_content.bind("<Enter>", on_enter)

        self.populate_simple_file_tree(self.explorer_content)

    def bind_mousewheel_to_widget(self, widget):
        """Bind mouse wheel events to a widget for scrolling"""

        def on_mousewheel(event):
            # For CTkScrollableFrame, we need to scroll the internal canvas
            try:
                if hasattr(widget, "_parent_canvas") and widget._parent_canvas:
                    canvas = widget._parent_canvas
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif hasattr(widget, "_scrollable_frame") and hasattr(
                    widget._scrollable_frame, "master"
                ):
                    # Try to find the canvas in CTkScrollableFrame
                    for child in widget.winfo_children():
                        if hasattr(child, "yview_scroll"):
                            child.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            break
                elif hasattr(widget, "yview_scroll"):
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass  # Silently ignore errors
            return "break"

        def on_mousewheel_linux(event):
            # Linux mouse wheel events (Button-4 = scroll up, Button-5 = scroll down)
            try:
                scroll_direction = -1 if event.num == 4 else 1
                if hasattr(widget, "_parent_canvas") and widget._parent_canvas:
                    canvas = widget._parent_canvas
                    canvas.yview_scroll(scroll_direction, "units")
                elif hasattr(widget, "_scrollable_frame") and hasattr(
                    widget._scrollable_frame, "master"
                ):
                    # Try to find the canvas in CTkScrollableFrame
                    for child in widget.winfo_children():
                        if hasattr(child, "yview_scroll"):
                            child.yview_scroll(scroll_direction, "units")
                            break
                elif hasattr(widget, "yview_scroll"):
                    widget.yview_scroll(scroll_direction, "units")
            except:
                pass  # Silently ignore errors
            return "break"

        # Bind mouse wheel events
        widget.bind("<MouseWheel>", on_mousewheel)
        widget.bind("<Button-4>", on_mousewheel_linux)
        widget.bind("<Button-5>", on_mousewheel_linux)

        # Also bind to the widget and its frame
        def bind_recursive(w):
            try:
                w.bind("<MouseWheel>", on_mousewheel)
                w.bind("<Button-4>", on_mousewheel_linux)
                w.bind("<Button-5>", on_mousewheel_linux)
                # Bind to children after a delay
                w.after(
                    50,
                    lambda: [
                        bind_recursive(child)
                        for child in w.winfo_children()
                        if child.winfo_exists()
                    ],
                )
            except:
                pass

        # Initial binding and delayed recursive binding
        widget.after(100, lambda: bind_recursive(widget))

    def load_heroes_from_folder(self):
        """Load heroes from Assets/01_Fx/1_Hero folder"""
        try:
            project_path = str(self.unity_project_path)
            heroes_folder = os.path.join(project_path, "Assets", "01_Fx", "1_Hero")

            if not os.path.exists(heroes_folder):
                self.add_output_message(
                    f"⚠️ Heroes folder not found: Assets/01_Fx/1_Hero"
                )
                return []

            heroes_data = []

            # Get all subfolders in the hero folder
            try:
                hero_folders = [
                    d
                    for d in os.listdir(heroes_folder)
                    if os.path.isdir(os.path.join(heroes_folder, d))
                ]

                self.add_output_message(
                    f"📁 Found {len(hero_folders)} hero folders in Assets/01_Fx/1_Hero"
                )

                for i, hero_folder in enumerate(sorted(hero_folders)):
                    # Extract hero name from folder name
                    hero_name_id = (
                        hero_folder.replace(" (", "(").replace(")", "").split("(")
                    )

                    hero_id = hero_name_id[0] if len(hero_name_id) > 1 else ""
                    hero_name = (
                        hero_name_id[1] if len(hero_name_id) > 1 else hero_name_id[0]
                    ).capitalize()

                    hero_data = {
                        "id": hero_id,
                        "name": hero_name,
                        "folder": hero_folder,
                    }

                    heroes_data.append(hero_data)

            except (PermissionError, OSError) as e:
                self.add_output_message(f"❌ Error reading heroes folder: {str(e)}")
                return []

            return heroes_data

        except Exception as e:
            self.add_output_message(f"❌ Error loading heroes: {str(e)}")
            return []

    def populate_simple_file_tree(self, parent):
        """Populate heroes list from Assets/01_Fx/1_Hero folder"""
        if not self.has_project() or not self.unity_project_path:
            # Show placeholder when no project
            no_project_label = ctk.CTkLabel(
                parent,
                text="📁 Chọn dự án để xem heroes",
                font=ctk.CTkFont(size=10),
                text_color="#888888",
            )
            no_project_label.pack(padx=10, pady=20)
            return

        # Load heroes from Assets/01_Fx/1_Hero folder
        heroes_data = self.load_heroes_from_folder()

        if not heroes_data:
            # Show message when no heroes found
            no_heroes_label = ctk.CTkLabel(
                parent,
                text="⚔️ Không tìm thấy heroes trong Assets/01_Fx/1_Hero",
                font=ctk.CTkFont(size=10),
                text_color="#f48771",
            )
            no_heroes_label.pack(padx=10, pady=20)
            return

        # Heroes list
        for hero in heroes_data:
            # Hero frame
            hero_frame = ctk.CTkFrame(parent, fg_color="#3d3d3d", corner_radius=4)
            hero_frame.pack(fill="x", padx=4, pady=6)
            hero_frame.grid_columnconfigure(1, weight=1)

            # Hero info container
            info_frame = ctk.CTkFrame(hero_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=3)
            info_frame.grid_columnconfigure(0, weight=1)

            # Hero name and ID
            name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            name_frame.grid(row=0, column=0, sticky="ew")
            name_frame.grid_columnconfigure(0, weight=1)

            name_label = ctk.CTkLabel(
                name_frame,
                text=hero["name"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#ffffff",
                anchor="w",
            )
            name_label.grid(row=0, column=0, sticky="w")

            id_label = ctk.CTkLabel(
                name_frame,
                text=hero["id"],
                font=ctk.CTkFont(size=9),
                text_color="#888888",
                anchor="e",
            )
            id_label.grid(row=0, column=1, sticky="e", padx=(5, 0))

            # Add click handler for hero selection
            def bind_hero_click(widget, hero_data):
                """Bind click event to widget and all its children"""
                widget.bind("<Button-1>", lambda e, h=hero_data: self.select_hero(h))
                for child in widget.winfo_children():
                    bind_hero_click(child, hero_data)

            bind_hero_click(hero_frame, hero)

    def select_hero(self, hero):
        """Handle hero selection"""
        self.add_output_message(f"⚔️ Selected Hero: {hero['name']} ({hero['id']})")

    def setup_explorer_section(self, parent):
        """Create file explorer section"""
        explorer_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        explorer_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=(2, 1))
        explorer_frame.grid_rowconfigure(1, weight=1)
        explorer_frame.grid_columnconfigure(0, weight=1)

        # Explorer header
        header_frame = ctk.CTkFrame(explorer_frame, height=30, fg_color="#37373d")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        # Explorer title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📁 EXPLORER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#cccccc",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # File tree
        tree_frame = ctk.CTkScrollableFrame(explorer_frame, fg_color="#1e1e1e")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Populate file tree
        self.populate_file_tree(tree_frame)

    def setup_project_info_section(self, parent):
        """Create project info section"""
        info_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        info_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=(1, 2))
        info_frame.grid_rowconfigure(1, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)

        # Info header
        header_frame = ctk.CTkFrame(info_frame, height=30, fg_color="#37373d")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        # Info title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 PROJECT INFO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#cccccc",
        )
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Project details
        details_frame = ctk.CTkFrame(info_frame, fg_color="#1e1e1e")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Populate project info
        self.populate_project_info(details_frame)

    def populate_file_tree(self, parent):
        """Populate file explorer tree"""
        if not self.has_project() or not self.unity_project_path:
            return

        import os

        project_path = str(self.unity_project_path)

        try:
            # Show main project folders
            main_folders = ["Assets", "Packages", "ProjectSettings", "UserSettings"]

            for folder in main_folders:
                folder_path = os.path.join(project_path, folder)
                if os.path.exists(folder_path):
                    folder_btn = ctk.CTkButton(
                        parent,
                        text=f"📁 {folder}",
                        height=25,
                        font=ctk.CTkFont(size=10),
                        fg_color="transparent",
                        hover_color="#404040",
                        anchor="w",
                        command=lambda f=folder: self.open_folder_in_explorer(f),
                    )
                    folder_btn.pack(fill="x", padx=5, pady=1)

                    # Show some subfolders for Assets
                    if folder == "Assets" and os.path.isdir(folder_path):
                        try:
                            subfolders = [
                                d
                                for d in os.listdir(folder_path)
                                if os.path.isdir(os.path.join(folder_path, d))
                            ][:5]
                            for subfolder in subfolders:
                                sub_btn = ctk.CTkButton(
                                    parent,
                                    text=f"  📂 {subfolder}",
                                    height=20,
                                    font=ctk.CTkFont(size=9),
                                    fg_color="transparent",
                                    hover_color="#404040",
                                    anchor="w",
                                    command=lambda sf=subfolder: self.open_subfolder_in_explorer(
                                        sf
                                    ),
                                )
                                sub_btn.pack(fill="x", padx=10, pady=1)
                        except PermissionError:
                            pass
        except Exception as e:
            error_label = ctk.CTkLabel(
                parent,
                text=f"❌ Error loading files: {str(e)[:50]}...",
                font=ctk.CTkFont(size=9),
                text_color="#f48771",
            )
            error_label.pack(padx=5, pady=5)

    def populate_project_info(self, parent):
        """Populate project information"""
        if not self.has_project() or not self.unity_project_path:
            return

        project_name = self.get_project_name()
        project_path = str(self.unity_project_path)

        # Project name
        name_label = ctk.CTkLabel(
            parent,
            text=f"Name: {project_name}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#4ec9b0",
            anchor="w",
        )
        name_label.pack(fill="x", padx=5, pady=2)

        # Project path (truncated)
        path_display = project_path
        if len(path_display) > 30:
            path_display = "..." + path_display[-30:]

        path_label = ctk.CTkLabel(
            parent,
            text=f"Path: {path_display}",
            font=ctk.CTkFont(size=9),
            text_color="#cccccc",
            anchor="w",
        )
        path_label.pack(fill="x", padx=5, pady=1)

        # Unity version (if available)
        try:
            import os

            version_file = os.path.join(
                project_path, "ProjectSettings", "ProjectVersion.txt"
            )
            if os.path.exists(version_file):
                with open(version_file, "r") as f:
                    content = f.read()
                    if "m_EditorVersion:" in content:
                        version = (
                            content.split("m_EditorVersion:")[1].strip().split("\n")[0]
                        )
                        version_label = ctk.CTkLabel(
                            parent,
                            text=f"Unity: {version}",
                            font=ctk.CTkFont(size=9),
                            text_color="#f48771",
                            anchor="w",
                        )
                        version_label.pack(fill="x", padx=5, pady=1)
        except Exception:
            pass

        # Quick actions
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", padx=5, pady=(10, 5))

        open_btn = ctk.CTkButton(
            actions_frame,
            text="📂 Open Folder",
            height=25,
            font=ctk.CTkFont(size=9),
            fg_color="#0e639c",
            hover_color="#1177bb",
            command=self.open_project_folder,
        )
        open_btn.pack(fill="x", pady=1)

        unity_btn = ctk.CTkButton(
            actions_frame,
            text="🎮 Open Unity",
            height=25,
            font=ctk.CTkFont(size=9),
            fg_color="#FF9800",
            hover_color="#ffaa33",
            command=self.open_in_unity,
        )
        unity_btn.pack(fill="x", pady=1)

    def open_folder_in_explorer(self, folder_name):
        """Open specific folder in file explorer"""
        self.add_output_message(f"📁 Opening {folder_name} folder...")
        # Could implement actual folder opening here

    def open_subfolder_in_explorer(self, subfolder_name):
        """Open specific subfolder in file explorer"""
        self.add_output_message(f"📂 Opening {subfolder_name} subfolder...")
        # Could implement actual subfolder opening here

    def refresh_layout(self):
        """Refresh the entire layout when project state changes"""
        # Destroy all current widgets except toolbar
        for widget in self.winfo_children():
            if hasattr(widget, "grid_info") and widget.grid_info().get("row") != 0:
                widget.destroy()

        # Recreate the layout
        self.setup_ui()

    def create_tooltip(self, widget, text):
        """Create a simple tooltip effect"""

        def on_enter(event):
            self.add_output_message(f"💡 {text}")

        def on_leave(event):
            pass  # Could clear tooltip if needed

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def show_project_info(self):
        """Show project information"""
        if self.has_project():
            project_name = self.get_project_name()
            self.add_output_message(f"📁 Dự án hiện tại: {project_name}")
            self.add_output_message(f"📂 Đường dẫn: {self.unity_project_path}")
        else:
            self.add_output_message("⚠️ Chưa có dự án nào được chọn")

    def refresh_project(self):
        """Refresh project view"""
        if self.has_project():
            self.add_output_message("🔄 Đang làm mới dự án...")
            self.setup_ui()  # Refresh the entire UI
            self.add_output_message("✅ Đã làm mới dự án thành công")
        else:
            self.add_output_message("⚠️ Chưa có dự án để làm mới")

    def show_help(self):
        """Show help information"""
        self.add_output_message("Editor Help:")
        self.add_output_message("   Mở dự án: Chọn thư mục dự án Unity")
        self.add_output_message("   XAPK: Chuyển đổi file XAPK thành dự án Unity")
        self.add_output_message("   Mở thư mục: Mở thư mục dự án trong file manager")
        self.add_output_message("   Unity Editor: Khởi động Unity Editor với dự án")
        self.add_output_message("   Phân tích: Phân tích cấu trúc dự án")

    def show_file_menu(self):
        """Show File menu dropdown"""
        self.create_dropdown_menu(
            "File",
            [
                ("📁 Chọn folder Unity", self.load_existing_project),
                (
                    "📂 Mở thư mục dự án",
                    self.open_project_folder if self.has_project() else None,
                ),
                (
                    "🔄 Refresh dự án",
                    self.refresh_project if self.has_project() else None,
                ),
                ("🗑️ Xóa dự án đã lưu", self.clear_last_project),
            ],
        )

    def show_project_menu(self):
        """Show Project menu dropdown"""
        self.create_dropdown_menu(
            "Project",
            [
                ("🔄 Load XAPK to Unity", self.go_to_xapk_converter),
                (
                    "🎮 Mở Unity Editor",
                    self.open_in_unity if self.has_project() else None,
                ),
                (
                    "🔍 Phân tích dự án",
                    self.analyze_project if self.has_project() else None,
                ),
            ],
        )

    def show_tools_menu(self):
        """Show Tools menu dropdown"""
        self.create_dropdown_menu(
            "Tools",
            [
                ("📦 Tải game (XAPK)", self.download_xapk_game),
                ("🛠️ AssetRipper", self.show_tools_info),
                ("📱 APK Tools", self.show_tools_info),
            ],
        )

    def show_help_menu(self):
        """Show Help menu dropdown"""
        self.create_dropdown_menu(
            "Help",
            [
                ("❓ Trợ giúp", self.show_help),
                ("⚙️ Cài đặt", self.open_settings),
                ("📋 Thông tin", self.show_about),
            ],
        )

    def create_dropdown_menu(self, menu_name, items):
        """Create a dropdown menu window"""
        # Create dropdown window
        dropdown = ctk.CTkToplevel(self)
        dropdown.title(f"{menu_name} Menu")
        dropdown.geometry("250x300")
        dropdown.transient(self.winfo_toplevel())

        # Position dropdown near the menu button
        dropdown.update_idletasks()
        x = self.winfo_rootx() + 50
        y = self.winfo_rooty() + 80
        dropdown.geometry(f"250x300+{x}+{y}")

        # Make sure window is visible before grab
        dropdown.deiconify()
        dropdown.update()

        # Now safe to grab
        try:
            dropdown.grab_set()
        except Exception as e:
            print(f"Warning: Could not grab window: {e}")

        # Dropdown content frame
        content_frame = ctk.CTkFrame(dropdown)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Menu title
        title_label = ctk.CTkLabel(
            content_frame,
            text=f"{menu_name} Menu",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        title_label.pack(pady=(10, 15))

        # Menu items
        for text, command in items:
            if command is None:
                # Disabled item
                btn = ctk.CTkButton(
                    content_frame,
                    text=text,
                    height=35,
                    font=ctk.CTkFont(size=11),
                    fg_color="#555555",
                    state="disabled",
                )
            else:
                btn = ctk.CTkButton(
                    content_frame,
                    text=text,
                    height=35,
                    font=ctk.CTkFont(size=11),
                    command=lambda cmd=command, win=dropdown: self.execute_menu_command(
                        cmd, win
                    ),
                )
            btn.pack(fill="x", padx=10, pady=3)

        # Close button
        close_btn = ctk.CTkButton(
            content_frame,
            text="Đóng",
            command=dropdown.destroy,
            height=30,
            fg_color="#666666",
        )
        close_btn.pack(fill="x", padx=10, pady=(15, 10))

        # Ensure window is properly focused and on top
        dropdown.focus_force()
        dropdown.lift()
        dropdown.attributes("-topmost", True)
        dropdown.after(100, lambda: dropdown.attributes("-topmost", False))

    def execute_menu_command(self, command, dropdown_window):
        """Execute menu command and close dropdown"""
        dropdown_window.destroy()
        if command:
            command()

    def show_tools_info(self):
        """Show tools information"""
        self.add_output_message("🛠️ Tools sẽ được thêm trong phiên bản tương lai")

    def show_about(self):
        """Show about information"""
        self.add_output_message("📋 KingGodCastle AIO - Unity Project Editor v1.0")

    def open_settings(self):
        """Open settings screen"""
        self.add_output_message("⚙️ Mở cài đặt...")
        if self.main_window:
            self.main_window.show_screen("settings")
        else:
            self.add_output_message("❌ Không thể mở cài đặt")

    def toggle_file_browser(self):
        """Toggle file browser view"""
        if self.has_project():
            self.add_output_message(
                "📄 File browser được hiển thị trong Project Overview"
            )
            # File browser is already shown in project overview
        else:
            self.add_output_message("⚠️ Chưa có dự án để hiển thị files")

    def setup_editor_area(self, parent):
        """Create main editor area like VSCode"""
        # Use appropriate column based on sidebar presence
        column = 1 if self.has_project() else 0

        editor_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        editor_frame.grid(row=1, column=column, sticky="nsew", padx=0, pady=0)
        editor_frame.grid_rowconfigure(1, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        # Main content area
        content_area = ctk.CTkFrame(editor_frame, fg_color="#1e1e1e")
        content_area.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        content_area.grid_rowconfigure(0, weight=1)
        content_area.grid_columnconfigure(0, weight=1)

        if self.has_project():
            self.setup_project_editor(content_area)
        else:
            self.setup_welcome_screen(content_area)

    def setup_project_editor(self, parent):
        """Create simple project editor area"""
        editor_area = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        editor_area.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        editor_area.grid_rowconfigure(0, weight=1)
        editor_area.grid_columnconfigure(0, weight=1)

        # Simple project editor content
        project_name = self.get_project_name()

        # Main editor label
        editor_label = ctk.CTkLabel(
            editor_area,
            text=f"📝 Editor Area - {project_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        editor_label.grid(row=0, column=0)

    def setup_welcome_screen(self, parent):
        """Create simple welcome screen without dialogs"""
        welcome_frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        welcome_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        welcome_frame.grid_rowconfigure(0, weight=1)
        welcome_frame.grid_columnconfigure(0, weight=1)

        # Center content
        center_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        center_frame.grid(row=0, column=0)
        center_frame.grid_rowconfigure(2, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        # Welcome title
        welcome_title = ctk.CTkLabel(
            center_frame,
            text="KingGodCastle AIO",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#ffffff",
        )
        welcome_title.grid(row=0, column=0, pady=(0, 10))

        # Subtitle
        subtitle = ctk.CTkLabel(
            center_frame,
            text="'Tôi chả hiểu sao tôi làm app này' - NOwL không nói zị",
            font=ctk.CTkFont(size=16),
            text_color="#cccccc",
        )
        subtitle.grid(row=1, column=0, pady=(0, 30))

    def setup_bottom_panel(self, parent):
        """Create VSCode-like bottom panel with resize and collapse functionality"""
        # Container for bottom panel + resize handle
        self.bottom_container = ctk.CTkFrame(parent, fg_color="transparent")
        columnspan = 2 if self.has_project() else 1
        self.bottom_container.grid(
            row=2, column=0, columnspan=columnspan, sticky="ew", padx=0, pady=0
        )
        self.bottom_container.grid_columnconfigure(0, weight=1)
        self.bottom_container.grid_rowconfigure(0, weight=0)  # Resize handle
        self.bottom_container.grid_rowconfigure(1, weight=1)  # Bottom panel

        # Resize handle
        resize_handle = ctk.CTkFrame(
            self.bottom_container,
            height=4,
            fg_color="#555555",
            corner_radius=0,
            cursor="sb_v_double_arrow",
        )
        resize_handle.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        resize_handle.grid_propagate(False)

        # Bind resize events
        resize_handle.bind("<Button-1>", self.start_bottom_resize)
        resize_handle.bind("<B1-Motion>", self.on_bottom_resize)
        resize_handle.bind("<ButtonRelease-1>", self.stop_bottom_resize)

        # Bottom panel frame
        self.bottom_frame = ctk.CTkFrame(
            self.bottom_container, height=self.bottom_height, fg_color="#181818"
        )
        self.bottom_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)
        self.bottom_frame.grid_propagate(False)

        # Bottom panel header
        bottom_header = ctk.CTkFrame(
            self.bottom_frame, height=30, fg_color="#252526", corner_radius=0
        )
        bottom_header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        bottom_header.grid_columnconfigure(0, weight=1)
        bottom_header.grid_columnconfigure(1, weight=0)
        bottom_header.grid_propagate(False)

        # Tab-like headers
        tabs_frame = ctk.CTkFrame(bottom_header, fg_color="transparent")
        tabs_frame.grid(row=0, column=0, sticky="w", padx=10, pady=3)

        output_tab = ctk.CTkLabel(
            tabs_frame,
            text="LOG",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#cccccc",
        )
        output_tab.grid(row=0, column=0, padx=10)

        # Collapse button
        self.bottom_collapse_btn = ctk.CTkButton(
            bottom_header,
            text="▼",
            width=20,
            height=20,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color="#cccccc",
            hover_color="#404040",
            command=self.toggle_bottom_panel,
        )
        self.bottom_collapse_btn.grid(row=0, column=1, sticky="e", padx=5, pady=3)

        # Output text area
        self.output_text = ctk.CTkTextbox(
            self.bottom_frame,
            fg_color="#1e1e1e",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Consolas", size=11),
            scrollbar_button_color="#424242",
            scrollbar_button_hover_color="#4a4a4a",
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Initialize messages
        self.add_output_message("Editor khởi tạo thành công")
        self.add_output_message(
            "Sử dụng toolbar để bắt đầu làm việc với Unity projects"
        )

    def start_bottom_resize(self, event):
        """Start resizing bottom panel"""
        self.resize_start_y = event.y_root
        self.resize_start_height = self.bottom_frame.winfo_height()

    def on_bottom_resize(self, event):
        """Handle bottom panel resize"""
        delta = (
            self.resize_start_y - event.y_root
        )  # Inverted because we want to drag up to increase height
        new_height = max(
            self.min_bottom_height,
            min(self.max_bottom_height, self.resize_start_height + delta),
        )
        self.bottom_frame.configure(height=new_height)
        self.bottom_height = new_height

    def stop_bottom_resize(self, event):
        """Stop resizing bottom panel"""
        pass

    def add_output_message(self, message):
        """Add message to output panel"""
        if hasattr(self, "output_text"):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.output_text.insert("end", formatted_message)
            self.output_text.see("end")  # Auto-scroll to bottom

    def get_hover_color(self, color):
        """Get hover color for button"""
        hover_colors = {
            "#0e639c": "#1177bb",
            "#4CAF50": "#45a049",
            "#FF9800": "#F57C00",
            "#6c757d": "#5a6268",
            "#2196F3": "#1976D2",
            "#9C27B0": "#7B1FA2",
        }
        return hover_colors.get(color, "#37373d")

    def get_directory_size(self, path):
        """Calculate directory size in MB"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    try:
                        file_path = os.path.join(dirpath, file)
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
        except:
            pass
        return total_size / (1024 * 1024)  # Convert to MB

    # Action methods
    def load_existing_project(self):
        """Load an existing Unity project"""
        project_folder = filedialog.askdirectory(
            title="Chọn thư mục dự án Unity", initialdir=os.path.expanduser("~")
        )

        if project_folder:
            # Check if it's a valid Unity project
            if self.is_unity_project(project_folder):
                self.unity_project_path = project_folder

                # Save this project as the last opened project
                self.save_last_project(project_folder)

                self.add_output_message(
                    f"✅ Đã tải dự án Unity: {os.path.basename(project_folder)}"
                )
                self.add_output_message(f"📂 Đường dẫn: {project_folder}")

                # Refresh UI to show project and sidebar
                self.refresh_layout()

                # Update main window if available
                if self.main_window:
                    self.main_window.unity_project_path = project_folder
            else:
                self.add_output_message(
                    "❌ Thư mục đã chọn không phải là dự án Unity hợp lệ"
                )
                self.add_output_message(
                    "💡 Hãy chọn thư mục chứa file ProjectSettings/ProjectVersion.txt"
                )
        else:
            self.add_output_message("⚠️ Đã hủy chọn dự án")

    def is_unity_project(self, path):
        """Check if path is a valid Unity project"""
        # Check for ProjectSettings folder and ProjectVersion.txt
        project_settings = os.path.join(path, "ProjectSettings", "ProjectVersion.txt")
        return os.path.exists(project_settings)

    def load_project(self, project_path):
        """Load a specific project path"""
        self.unity_project_path = project_path
        self.add_output_message(f"✅ Đã tải dự án: {os.path.basename(project_path)}")
        self.setup_ui()  # Refresh UI

    def go_to_xapk_converter(self):
        """Navigate to XAPK converter screen"""
        self.add_output_message("📦 Chuyển sang XAPK Converter...")
        if self.main_window:
            self.main_window.show_screen("xapk_install")
        else:
            self.add_output_message(
                "❌ Không thể điều hướng - main window không khả dụng"
            )

    def download_xapk_game(self):
        """Navigate to XAPK download screen"""
        self.add_output_message("🎮 Chuyển sang tải game XAPK...")
        if self.main_window:
            # Navigate to download screen or show download functionality
            self.main_window.show_screen("xapk_install")
            self.add_output_message("✅ Sử dụng XAPK Install để tải game")
        else:
            self.add_output_message(
                "❌ Không thể điều hướng - main window không khả dụng"
            )

    def open_project_folder(self):
        """Open project folder in file manager"""
        if not self.has_project():
            self.add_output_message("❌ Chưa chọn dự án nào để mở")
            return

        try:
            project_path = str(self.unity_project_path)
            system = platform.system()

            if system == "Windows":
                subprocess.run(["explorer", project_path])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", project_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", project_path])

            self.add_output_message(f"📂 Đã mở thư mục: {project_path}")
        except Exception as e:
            self.add_output_message(f"❌ Lỗi khi mở thư mục: {str(e)}")

    def open_in_unity(self):
        """Open project in Unity Editor"""
        if not self.has_project():
            self.add_output_message("❌ Chưa chọn dự án nào để mở trong Unity")
            return

        try:
            project_path = str(self.unity_project_path)

            # Find Unity installation
            unity_path = self.find_unity_installation()
            if not unity_path:
                self.add_output_message("❌ Không tìm thấy Unity Editor trên hệ thống")
                return

            self.add_output_message(
                f"🎮 Đang mở dự án trong Unity: {os.path.basename(project_path)}"
            )

            # Launch Unity with project
            if platform.system() == "Windows":
                cmd = [unity_path, "-projectPath", project_path]
            else:
                cmd = [unity_path, "-projectPath", project_path]

            subprocess.Popen(cmd)
            self.add_output_message("✅ Đã khởi động Unity Editor")

        except Exception as e:
            self.add_output_message(f"❌ Lỗi khi mở Unity: {str(e)}")

    def find_unity_installation(self):
        """Find Unity installation path"""
        system = platform.system()

        # Common Unity installation paths
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe",
                r"C:\Program Files\Unity\Editor\Unity.exe",
                r"C:\Program Files (x86)\Unity\Editor\Unity.exe",
            ]
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity",
                "/Applications/Unity/Unity.app/Contents/MacOS/Unity",
            ]
        else:  # Linux
            possible_paths = [
                "/opt/Unity/Editor/Unity",
                "/usr/bin/unity-editor",
                "/home/*/Unity/Hub/Editor/*/Editor/Unity",
            ]

        for pattern in possible_paths:
            matches = glob.glob(pattern)
            if matches:
                # Return the first (usually latest) match
                return matches[0]

        return None

    def analyze_project(self):
        """Analyze Unity project structure and show statistics"""
        if not self.has_project():
            self.add_output_message("❌ Chưa chọn dự án nào để phân tích")
            return

        try:
            project_path = str(self.unity_project_path)
            self.add_output_message("🔍 Đang phân tích dự án...")

            # Analyze project structure
            assets_path = os.path.join(project_path, "Assets")
            scripts_count = 0
            prefabs_count = 0
            scenes_count = 0

            if os.path.exists(assets_path):
                for root, dirs, files in os.walk(assets_path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext == ".cs":
                            scripts_count += 1
                        elif ext == ".prefab":
                            prefabs_count += 1
                        elif ext == ".unity":
                            scenes_count += 1

            # Project size
            size_mb = self.get_directory_size(project_path)

            # Unity version
            unity_version = self.get_unity_version()

            # Output analysis
            self.add_output_message("📊 Kết quả phân tích dự án:")
            self.add_output_message(f"   📂 Scripts (C#): {scripts_count}")
            self.add_output_message(f"   🧩 Prefabs: {prefabs_count}")
            self.add_output_message(f"   🎬 Scenes: {scenes_count}")
            self.add_output_message(f"   💾 Kích thước: {size_mb:.1f} MB")
            self.add_output_message(f"   🎮 Unity Version: {unity_version}")

        except Exception as e:
            self.add_output_message(f"❌ Lỗi khi phân tích dự án: {str(e)}")

    def get_unity_version(self):
        """Get Unity version from ProjectVersion.txt"""
        try:
            project_path = str(self.unity_project_path)
            version_file = os.path.join(
                project_path, "ProjectSettings", "ProjectVersion.txt"
            )

            if os.path.exists(version_file):
                with open(version_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract version from "m_EditorVersion: 2022.3.0f1"
                    for line in content.split("\n"):
                        if line.startswith("m_EditorVersion:"):
                            return line.split(":", 1)[1].strip()
        except:
            pass
        return "Không xác định"

    def get_project_size_text(self):
        """Get project size as formatted text"""
        if not self.has_project():
            return "N/A"

        try:
            size_mb = self.get_directory_size(str(self.unity_project_path))
            if size_mb < 1000:
                return f"{size_mb:.1f} MB"
            else:
                return f"{size_mb/1024:.1f} GB"
        except:
            return "Không xác định"

    def get_files_count_text(self):
        """Get total files count as text"""
        if not self.has_project():
            return "N/A"

        try:
            project_path = str(self.unity_project_path)
            total_files = sum([len(files) for r, d, files in os.walk(project_path)])
            return f"{total_files:,}"
        except:
            return "Không xác định"

    def get_unity_version_text(self):
        """Get Unity version text"""
        if not self.has_project():
            return "N/A"

        return self.get_unity_version()

    def open_tools(self):
        """Open Unity tools or show tools menu"""
        self.add_output_message("🔧 Hiển thị công cụ Unity...")
        # This could open a submenu or navigate to tools screen
        if self.main_window:
            # Could add tools screen later
            self.add_output_message(
                "💡 Tính năng này sẽ được thêm trong phiên bản tương lai"
            )
        else:
            self.add_output_message("❌ Không thể truy cập công cụ")

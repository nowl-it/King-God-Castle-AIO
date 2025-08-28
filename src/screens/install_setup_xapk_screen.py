"""
XAPK Install Screen
Screen for installing and selecting XAPK files
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import subprocess
import threading
import platform
from pathlib import Path
from PIL import Image, ImageDraw
from .base_screen import BaseScreen
from src.utils import *


class XAPKInstallScreen(BaseScreen):
    """King God Castle Download Screen with integrated tools"""

    def __init__(self, parent, **kwargs):
        # Initialize attributes first
        self.download_folder = None
        self.selected_file = None
        self.processing = False

        # Version caching
        self.cached_versions = {}
        self.package_info_cache = {}
        self.versions_loading = False

        self.tools = ToolsManager()
        self.cfg: ConfigManager = ConfigManager()

        self.apk_processor = APKProcessor(self.add_log_message)

        self.tools_status = self.tools.check_tools()

        # Then call parent init which calls setup_ui
        super().__init__(parent, **kwargs)

    def setup_ui(self):
        """Setup modern King God Castle-focused UI"""
        # Configure main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create main scrollable container
        self.main_container = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color=("#ffffff", "#0a0a0a")
        )
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)

        # Enable mouse wheel scrolling for main_container
        def _on_mousewheel(event):
            # For Windows and MacOS, event.delta is in units of 120, for Linux it's 1/-1
            if event.num == 4 or event.delta > 0:
                self.main_container._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                self.main_container._parent_canvas.yview_scroll(1, "units")

        # Windows/MacOS
        self.main_container.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux (button 4/5)
        self.main_container.bind_all("<Button-4>", _on_mousewheel)
        self.main_container.bind_all("<Button-5>", _on_mousewheel)

        # Create sections
        self.create_hero_section()
        self.create_action_section()
        self.create_status_section()
        self.create_logs_section()

        # Initialize data
        self.tools_status = self.tools.check_tools()
        self.processing = False
        self.versions_loading = False

        # Create dummy attributes for backward compatibility
        class MockLabel:
            def configure(self, **kwargs):
                pass

        self.file_status_label = MockLabel()
        self.process_status_label = MockLabel()

        # Initialize logging and load versions
        self.initialize_logging()
        self.after(100, self.auto_refresh_versions)
        self.after(200, self.quick_setup_check)

    def create_hero_section(self):
        """Create hero section with King God Castle branding"""
        hero_frame = ctk.CTkFrame(
            self.main_container,
            height=200,
            corner_radius=20,
            fg_color=("#1a1a2e", "#0f1419"),
            border_width=2,
            border_color=("#3d5afe", "#58a6ff"),
        )
        hero_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 15))
        hero_frame.grid_columnconfigure(1, weight=1)
        hero_frame.grid_propagate(False)

        # Castle icon with glow effect (using favicon.ico)
        icon_frame = ctk.CTkFrame(
            hero_frame,
            width=120,
            height=120,
            corner_radius=60,
            fg_color=("#2d3748", "#1a202c"),
            border_width=3,
            border_color=("#3d5afe", "#58a6ff"),
        )
        icon_frame.grid(row=0, column=0, padx=40, pady=40, sticky="ns")
        icon_frame.grid_propagate(False)

        # Load favicon.ico as icon
        try:
            favicon_path = os.path.join(os.getcwd(), "assets", "favicon.ico")
            favicon_image = Image.open(favicon_path)

            # Create circular mask to prevent overflow
            icon_size = 90  # Safe size for 120px frame with 3px border
            favicon_image = favicon_image.resize(
                (icon_size, icon_size), Image.Resampling.LANCZOS
            )

            # Create circular mask
            mask = Image.new("L", (icon_size, icon_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, icon_size, icon_size), fill=255)

            # Apply mask to make image circular
            output = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            output.paste(favicon_image, (0, 0))
            output.putalpha(mask)

            favicon_ctk = ctk.CTkImage(output, size=(icon_size, icon_size))

            castle_icon = ctk.CTkLabel(
                icon_frame,
                image=favicon_ctk,
                text="",  # No text when using image
                fg_color="transparent",  # Transparent background
            )
        except Exception as e:
            # Fallback to emoji if favicon can't be loaded
            print(f"Could not load favicon.ico: {e}")
            castle_icon = ctk.CTkLabel(
                icon_frame, text="🏰", font=ctk.CTkFont(size=42), fg_color="transparent"
            )

        castle_icon.place(relx=0.5, rely=0.5, anchor="center")

        # Title and description
        content_frame = ctk.CTkFrame(hero_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=(20, 40), pady=40)
        content_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            content_frame,
            text="King God Castle",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("#3d5afe", "#58a6ff"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="ew")

        subtitle_label = ctk.CTkLabel(
            content_frame,
            text="APK Processor & Asset Extractor",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#ffffff", "#e6edf3"),
            anchor="w",
        )
        subtitle_label.grid(row=1, column=0, sticky="ew", pady=(5, 10))

        # Status indicator
        status_text = (
            "All Systems Ready"
            if all(self.tools_status.values())
            else "Setting up tools..."
        )
        status_color = (
            ("#00d084", "#2ea043")
            if all(self.tools_status.values())
            else ("#ffa500", "#d1242f")
        )

        status_label = ctk.CTkLabel(
            content_frame,
            text=f"Status: {status_text}",
            font=ctk.CTkFont(size=14),
            text_color=status_color,
            anchor="w",
        )
        status_label.grid(row=2, column=0, sticky="ew")

    def create_action_section(self):
        """Create main action section for downloading"""
        action_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=16,
            fg_color=("#f8fafc", "#161b22"),
            border_width=1,
            border_color=("#e2e8f0", "#30363d"),
        )
        action_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=15)
        action_frame.grid_columnconfigure(0, weight=1)

        # Section header
        header_frame = ctk.CTkFrame(action_frame, fg_color="transparent", height=70)
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 0))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)

        download_icon = ctk.CTkLabel(header_frame, text="📥", font=ctk.CTkFont(size=28))
        download_icon.grid(row=0, column=0, padx=(0, 20))

        header_text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_text_frame.grid(row=0, column=1, sticky="ew")

        action_title = ctk.CTkLabel(
            header_text_frame,
            text="Download Game",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        )
        action_title.pack(anchor="w")

        action_subtitle = ctk.CTkLabel(
            header_text_frame,
            text="Select version and download King God Castle APK",
            font=ctk.CTkFont(size=14),
            text_color=("#64748b", "#7d8590"),
            anchor="w",
        )
        action_subtitle.pack(anchor="w", pady=(2, 0))

        # Download controls
        controls_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(20, 30))
        controls_frame.grid_columnconfigure(1, weight=1)

        # Version selection
        version_label = ctk.CTkLabel(
            controls_frame,
            text="Game Version:",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=120,
        )
        version_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Modern dropdown with better styling
        self.version_dropdown = ctk.CTkComboBox(
            controls_frame,
            values=["🔄 Loading latest versions..."],
            height=50,
            width=300,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=13),
            state="readonly",
            corner_radius=12,
            border_width=2,
            border_color=("#cbd5e1", "#30363d"),
            button_color=("#3d5afe", "#58a6ff"),
            button_hover_color=("#3949ab", "#4493f8"),
            dropdown_fg_color=("#ffffff", "#21262d"),
            dropdown_hover_color=("#f1f5f9", "#30363d"),
        )
        self.version_dropdown.grid(
            row=0, column=1, sticky="w", padx=(20, 20), pady=(0, 20)
        )
        self.version_dropdown.set("🔄 Loading latest versions...")

        # Download button with modern design
        download_btn = ctk.CTkButton(
            controls_frame,
            text="� Choose & Download",
            command=self.download_apk_by_package,
            height=50,
            width=160,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#00d084", "#2ea043"),
            hover_color=("#00b370", "#2d9f39"),
            corner_radius=12,
            border_width=2,
            border_color=("#00b370", "#2d9f39"),
        )
        download_btn.grid(row=0, column=2, pady=(0, 20))

        # Store reference for state management
        self.download_btn = download_btn

        # Progress bar for downloads (initially hidden)
        self.download_progress = ctk.CTkProgressBar(
            controls_frame,
            height=8,
            corner_radius=4,
            fg_color=("#e2e8f0", "#30363d"),
            progress_color=("#00d084", "#2ea043"),
        )
        self.download_progress.grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(5, 15)
        )
        self.download_progress.set(0)
        self.download_progress.grid_remove()  # Hide initially

    def create_status_section(self):
        """Create tools and system status section"""
        status_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=16,
            fg_color=("#f8fafc", "#161b22"),
            border_width=1,
            border_color=("#e2e8f0", "#30363d"),
        )
        status_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=15)
        status_frame.grid_columnconfigure((0, 1), weight=1)

        # Tools status
        tools_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        tools_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=25)

        tools_title = ctk.CTkLabel(
            tools_frame,
            text="🔧 Tools Status",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        tools_title.pack(anchor="w", pady=(0, 15))

        # Tool status items
        tools_status = getattr(self, "tools_status", {})
        tools_info = [
            ("APKeep", "APK Download Tool", tools_status.get("apkeep", False)),
            (
                "AssetRipper",
                "Game Asset Extractor",
                tools_status.get("asset-ripper", False),
            ),
        ]

        for tool_name, tool_desc, is_ready in tools_info:
            tool_item = ctk.CTkFrame(
                tools_frame,
                corner_radius=8,
                fg_color=("#ffffff", "#21262d"),
                border_width=1,
                border_color=("#e2e8f0", "#30363d"),
            )
            tool_item.pack(fill="x", pady=5)

            tool_content = ctk.CTkFrame(tool_item, fg_color="transparent")
            tool_content.pack(fill="x", padx=15, pady=12)

            status_icon = "✅" if is_ready else "❌"
            status_text = "Ready" if is_ready else "Missing"
            status_color = (
                ("#00d084", "#2ea043") if is_ready else ("#dc2626", "#d1242f")
            )

            tool_header = ctk.CTkLabel(
                tool_content,
                text=f"{status_icon} {tool_name} - {status_text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=status_color,
                anchor="w",
            )
            tool_header.pack(anchor="w")

            tool_description = ctk.CTkLabel(
                tool_content,
                text=tool_desc,
                font=ctk.CTkFont(size=12),
                text_color=("#64748b", "#7d8590"),
                anchor="w",
            )
            tool_description.pack(anchor="w", pady=(2, 0))

        # File operations
        files_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        files_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=25)

        files_title = ctk.CTkLabel(
            files_frame,
            text="📁 File Operations",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        files_title.pack(anchor="w", pady=(0, 15))

        # File action buttons
        buttons_container = ctk.CTkFrame(files_frame, fg_color="transparent")
        buttons_container.pack(fill="x")

        select_btn = ctk.CTkButton(
            buttons_container,
            text="📂 Select XAPK File",
            command=self.select_file,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#6366f1", "#8b5cf6"),
            hover_color=("#5b21b6", "#7c3aed"),
            corner_radius=10,
        )
        select_btn.pack(fill="x", pady=(0, 10))

        process_btn = ctk.CTkButton(
            buttons_container,
            text="🔄 Process XAPK",
            command=self.process_files,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#f59e0b", "#f97316"),
            hover_color=("#d97706", "#ea580c"),
            corner_radius=10,
        )
        process_btn.pack(fill="x")

        # Store reference
        self.process_btn = process_btn

        # Files display
        files_display_frame = ctk.CTkFrame(
            files_frame,
            corner_radius=8,
            fg_color=("#ffffff", "#0d1117"),
            border_width=1,
            border_color=("#e2e8f0", "#30363d"),
        )
        files_display_frame.pack(fill="x", pady=(15, 0))

        self.files_display = ctk.CTkTextbox(
            files_display_frame,
            height=100,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
        )
        self.files_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.files_display.insert(
            "1.0",
            "No XAPK file selected...\n\n📝 Click 'Select XAPK File' to choose a file",
        )
        self.files_display.configure(state="disabled")

    def create_logs_section(self):
        """Create activity logs section"""
        logs_frame = ctk.CTkFrame(
            self.main_container,
            corner_radius=16,
            fg_color=("#f8fafc", "#161b22"),
            border_width=1,
            border_color=("#e2e8f0", "#30363d"),
        )
        logs_frame.grid(row=3, column=0, sticky="ew", padx=25, pady=(15, 25))
        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(1, weight=1)

        # Header
        logs_header = ctk.CTkFrame(logs_frame, fg_color="transparent", height=60)
        logs_header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 15))
        logs_header.grid_columnconfigure(1, weight=1)
        logs_header.grid_propagate(False)

        logs_icon = ctk.CTkLabel(logs_header, text="📝", font=ctk.CTkFont(size=24))
        logs_icon.grid(row=0, column=0, padx=(0, 15))

        logs_title = ctk.CTkLabel(
            logs_header,
            text="Activity Log",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        logs_title.grid(row=0, column=1, sticky="ew")

        # Clear logs button
        clear_btn = ctk.CTkButton(
            logs_header,
            text="🗑️ Clear",
            command=self.clear_logs,
            height=32,
            width=80,
            font=ctk.CTkFont(size=12),
            fg_color=("#64748b", "#6e7681"),
            hover_color=("#475569", "#545d68"),
            corner_radius=8,
        )
        clear_btn.grid(row=0, column=2)

        # Log display with terminal-like styling
        log_container = ctk.CTkFrame(
            logs_frame,
            corner_radius=12,
            fg_color=("#1e293b", "#0d1117"),
            border_width=2,
            border_color=("#334155", "#21262d"),
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))

        self.log_display = ctk.CTkTextbox(
            log_container,
            height=200,
            font=ctk.CTkFont(size=12, family="monospace"),
            fg_color="transparent",
        )
        self.log_display.pack(fill="both", expand=True, padx=15, pady=15)

    def clear_logs(self):
        """Clear the activity log"""
        if hasattr(self, "log_display"):
            self.log_display.configure(state="normal")
            self.log_display.delete("1.0", "end")
            self.log_display.configure(state="disabled")
            self.add_log_message("🧹 Activity log cleared")

    def initialize_logging(self):
        """Initialize logging system"""
        self.add_log_message("🏰 King God Castle Processor started")
        self.add_log_message("🔄 Initializing tools...")

        # Check tools status
        if all(self.tools_status.values()):
            self.add_log_message("✅ All tools ready")
        else:
            missing_tools = [
                tool for tool, status in self.tools_status.items() if not status
            ]
            self.add_log_message(f"⚠️ Missing tools: {', '.join(missing_tools)}")

    def add_log_message(self, message):
        """Add message to activity log"""
        if not hasattr(self, "log_display"):
            return

        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_display.configure(state="normal")
        self.log_display.insert("end", log_entry)
        self.log_display.configure(state="disabled")
        self.log_display.see("end")

    def auto_refresh_versions(self):
        """Auto refresh versions on startup"""
        self.add_log_message("🔄 Loading King God Castle versions...")
        self.refresh_versions()

    def create_status_indicators(self, parent):
        """Create modern status indicators"""
        parent.grid_columnconfigure((0, 1), weight=1)

        # apkeep status
        apkeep_color = "#4CAF50" if self.tools_status.get("apkeep") else "#F44336"
        apkeep_indicator = ctk.CTkFrame(
            parent, fg_color=apkeep_color, height=8, width=80
        )
        apkeep_indicator.grid(row=0, column=0, padx=2, pady=(5, 2), sticky="ew")

        apkeep_label = ctk.CTkLabel(
            parent, text="APKeep", font=ctk.CTkFont(size=9), text_color="#B0B0B0"
        )
        apkeep_label.grid(row=1, column=0, padx=2)

        # assetripper status
        ripper_color = "#4CAF50" if self.tools_status.get("asset-ripper") else "#F44336"
        ripper_indicator = ctk.CTkFrame(
            parent, fg_color=ripper_color, height=8, width=80
        )
        ripper_indicator.grid(row=0, column=1, padx=2, pady=(5, 2), sticky="ew")

        ripper_label = ctk.CTkLabel(
            parent, text="AssetRipper", font=ctk.CTkFont(size=9), text_color="#B0B0B0"
        )
        ripper_label.grid(row=1, column=1, padx=2)

    def on_version_selected(self, choice):
        """Handle version selection from dropdown with enhanced feedback"""
        if choice and choice not in ["Loading versions...", "Loading..."]:
            # Enhanced log message with version info
            if choice == "latest":
                self.add_log_message("📋 Selected: Latest version (recommended)")
            elif choice.replace(".", "").isdigit():
                self.add_log_message(f"📋 Selected specific version: {choice}")
            else:
                self.add_log_message(f"📋 Selected version: {choice}")

            # Visual feedback - briefly highlight dropdown
            original_color = self.version_dropdown.cget("border_color")
            self.version_dropdown.configure(border_color="#FF6B35")
            self.after(
                200,
                lambda: self.version_dropdown.configure(border_color=original_color),
            )

    def load_dropdown_versions(self):
        """Load versions into dropdown using apkeep command"""
        package_name = "com.awesomepiece.castle"

        try:
            # Set dropdown to loading state
            self.version_dropdown.configure(values=["latest", "🔄 Loading..."])
            self.version_dropdown.set("🔄 Loading...")

            # Run apkeep command to get versions
            result = subprocess.run(
                ["apkeep", "-a", package_name, "-l", "."],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            if result.returncode == 0:
                # Parse version list from output
                version_lines = result.stdout.strip().split("\n")
                versions = []  # No "latest" - only real versions

                # Look for the line with versions (contains |)
                for line in version_lines:
                    line = line.strip()
                    if "|" in line and any(c.isdigit() for c in line):
                        # Extract versions from table format "| version1, version2, ... |"
                        version_part = line.replace("|", "").strip()
                        if version_part:
                            # Split by comma and clean each version
                            for v in version_part.split(","):
                                v = v.strip()
                                # Validate version format (contains digits and dots)
                                if v and any(c.isdigit() for c in v) and "." in v:
                                    if v not in versions:
                                        versions.append(v)

                # Limit to reasonable number (15 real versions only)
                if len(versions) > 15:
                    versions = versions[:15]

                # Update dropdown with versions
                self.version_dropdown.configure(values=versions)
                # Set to newest version (first in list) instead of "latest"
                if versions:
                    self.version_dropdown.set(versions[0])
                self.add_log_message(f"✅ Loaded {len(versions)} versions from apkeep")

            else:
                # Error case - use some default versions (no "latest")
                default_versions = ["159.0.02", "158.1.03", "157.1.00"]
                self.version_dropdown.configure(values=default_versions)
                self.version_dropdown.set(default_versions[0])
                self.add_log_message(f"⚠️ apkeep error: {result.stderr.strip()[:100]}")

        except subprocess.TimeoutExpired:
            default_versions = ["159.0.02", "158.1.03", "157.1.00"]
            self.version_dropdown.configure(values=default_versions)
            self.version_dropdown.set(default_versions[0])
            self.add_log_message("⚠️ apkeep timeout - using default versions")

        except Exception as e:
            default_versions = ["159.0.02", "158.1.03", "157.1.00"]
            self.version_dropdown.configure(values=default_versions)
            self.version_dropdown.set(default_versions[0])
            self.add_log_message(f"⚠️ Version loading error: {str(e)[:100]}")

    def create_file_operations_card(self, parent):
        """Create file operations card"""
        card = ctk.CTkFrame(parent, corner_radius=16)
        card.grid(
            row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 20)
        )  # Changed row to 1
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        # Card header
        header = ctk.CTkLabel(
            card,
            text="📁 File Operations",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))

        # File selection buttons
        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        select_file_btn = ctk.CTkButton(
            buttons_frame,
            text="📂 Select Files",
            command=self.select_file,
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            corner_radius=10,
        )
        select_file_btn.grid(row=0, column=0, columnspan=2, sticky="ew")

        # REMOVED: Folder selection button - single file mode only
        # select_folder_btn = ctk.CTkButton(
        #     buttons_frame,
        #     text="📁 Select Folder",
        #     command=self.select_folder,
        #     height=45,
        #     font=ctk.CTkFont(size=12, weight="bold"),
        #     fg_color="#673AB7",
        #     hover_color="#512DA8",
        #     corner_radius=10,
        # )
        # select_folder_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Selected files display
        self.files_display = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=10,
        )
        self.files_display.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))

        # Process button
        self.process_btn = ctk.CTkButton(
            card,
            text="🔧 Process Selected Files",
            command=self.process_files,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#FF5722",
            hover_color="#E64A19",
            corner_radius=12,
            state="disabled",
        )
        self.process_btn.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

    def create_tools_status_card(self, parent):
        """Create tools status card"""
        card = ctk.CTkFrame(parent, corner_radius=16)
        card.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 20))

        # Card header
        header = ctk.CTkLabel(
            card,
            text="🔧 Tools Status",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))

        # Status items
        status_frame = ctk.CTkFrame(card, fg_color="transparent")
        status_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        status_frame.grid_columnconfigure(1, weight=1)

        # APKeep status
        apkeep_status = "✅ Ready" if self.tools_status.get("apkeep") else "❌ Missing"
        apkeep_color = "#4CAF50" if self.tools_status.get("apkeep") else "#F44336"

        apkeep_icon = ctk.CTkLabel(status_frame, text="📦", font=ctk.CTkFont(size=20))
        apkeep_icon.grid(row=0, column=0, padx=(0, 10), pady=5)

        apkeep_info = ctk.CTkLabel(
            status_frame,
            text=f"APKeep\n{apkeep_status}",
            font=ctk.CTkFont(size=12),
            text_color=apkeep_color,
            anchor="w",
        )
        apkeep_info.grid(row=0, column=1, sticky="ew", pady=5)

        # AssetRipper status
        ripper_status = (
            "✅ Ready" if self.tools_status.get("asset-ripper") else "❌ Missing"
        )
        ripper_color = "#4CAF50" if self.tools_status.get("asset-ripper") else "#F44336"

        ripper_icon = ctk.CTkLabel(status_frame, text="🔧", font=ctk.CTkFont(size=20))
        ripper_icon.grid(row=1, column=0, padx=(0, 10), pady=5)

        ripper_info = ctk.CTkLabel(
            status_frame,
            text=f"AssetRipper\n{ripper_status}",
            font=ctk.CTkFont(size=12),
            text_color=ripper_color,
            anchor="w",
        )
        ripper_info.grid(row=1, column=1, sticky="ew", pady=5)

    def create_activity_log_card(self, parent):
        """Create activity log card"""
        card = ctk.CTkFrame(parent, corner_radius=16)
        card.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(10, 0), pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        # Card header with clear button
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        header_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            header_frame,
            text="📝 Activity Log",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        header.grid(row=0, column=0, sticky="ew")

        clear_btn = ctk.CTkButton(
            header_frame,
            text="🗑️",
            command=self.clear_log,
            width=40,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#666666",
            hover_color="#777777",
            corner_radius=6,
        )
        clear_btn.grid(row=0, column=1, padx=(10, 0))

        # Log display
        self.log_textbox = ctk.CTkTextbox(
            card,
            font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled",
            corner_radius=10,
        )
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Initialize log
        self.initialize_log()

    # File operation methods for the new UI
    def select_file(self):
        """Select single XAPK file for processing"""
        file_types = [
            ("XAPK files", "*.xapk"),
            ("All files", "*.*"),
        ]

        selected_file = filedialog.askopenfilename(
            title="Select XAPK file to process",
            filetypes=file_types,
        )

        if selected_file:
            # Only allow XAPK files
            if not selected_file.lower().endswith(".xapk"):
                messagebox.showwarning(
                    "Invalid File",
                    "Please select a XAPK file only.\nOther file types are not supported.",
                )
                return

            self.selected_file = selected_file
            self.update_files_display()
            self.process_btn.configure(state="normal")
            self.add_log_message(
                f"📂 Selected XAPK file: {os.path.basename(selected_file)}"
            )

    def update_files_display(self):
        """Update the files display textbox for single XAPK file"""
        self.files_display.configure(state="normal")
        self.files_display.delete("1.0", "end")

        if hasattr(self, "selected_file") and self.selected_file:
            file_path = self.selected_file  # Only one file
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB

            # Show detailed file information
            self.files_display.insert("end", f"📁 Selected XAPK File:\n")
            self.files_display.insert("end", f"   Name: {filename}\n")
            self.files_display.insert("end", f"   Size: {file_size:.1f} MB\n")
            self.files_display.insert("end", f"   Path: {file_path}\n")
            self.files_display.insert("end", f"\n✅ Ready for processing!")
        else:
            self.files_display.insert("end", "No XAPK file selected...\n\n")
            self.files_display.insert(
                "end", "📝 Click 'Select XAPK File' to choose a file"
            )

        self.files_display.configure(state="disabled")

    def process_files(self):
        """Process selected XAPK file"""
        if not hasattr(self, "selected_file") or not self.selected_file:
            messagebox.showwarning("Warning", "No XAPK file selected!")
            return

        if self.processing:
            messagebox.showinfo("Info", "Already processing, please wait!")
            return

        # Start processing single XAPK file
        self.processing = True
        self.process_btn.configure(state="disabled", text="🔄 Processing XAPK...")

        file_path = self.selected_file  # Only one file
        filename = os.path.basename(file_path)

        self.add_log_message(f"🚀 Started processing XAPK: {filename}")

        # Process file in background thread
        def process_worker():
            try:
                if file_path.lower().endswith(".xapk"):
                    self.add_log_message(f"📂 Processing XAPK file: {filename}")
                    self.process_xapk_file(file_path, filename)
                else:
                    self.add_log_message(
                        f"❌ Invalid file type. Only XAPK files are supported."
                    )
                    self.after(100, self.files_processing_failed)
                    return

                self.after(100, self.files_processing_completed)

            except Exception as e:
                self.add_log_message(f"❌ Error: {str(e)}")
                self.after(100, self.files_processing_failed)

        threading.Thread(target=process_worker, daemon=True).start()

    def files_processing_completed(self):
        """Handle completion of XAPK processing"""
        self.processing = False
        self.process_btn.configure(state="normal", text="✅ XAPK Processed")
        self.add_log_message("🎉 XAPK file processed successfully!")

    def files_processing_failed(self):
        """Handle XAPK processing failure"""
        self.processing = False
        self.process_btn.configure(state="normal", text="� Process XAPK")
        self.add_log_message("❌ XAPK processing failed")

    def create_apk_download_section(self, parent):
        """Create APK download section with package name input"""
        download_frame = ctk.CTkFrame(parent)
        download_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        download_frame.grid_columnconfigure(1, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            download_frame,
            text="🏰 Tải King God Castle",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        title_label.grid(
            row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=(15, 10)
        )

        # Version selection row (removed package input)
        version_label = ctk.CTkLabel(
            download_frame,
            text="Version:",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80,
        )
        version_label.grid(row=1, column=0, padx=(15, 5), pady=5, sticky="w")

        # Package info and restrictions (moved up)
        info_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        info_frame.grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=15, pady=(5, 15)
        )

        info_label = ctk.CTkLabel(
            info_frame,
            text="🏰 Chỉ hỗ trợ King God Castle (com.awesomepiece.castle)",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        info_label.pack(pady=5)

    def set_version(self, version):
        """Set version in dropdown"""
        if hasattr(self, "version_dropdown"):
            # Check if version is in dropdown values
            current_values = self.version_dropdown.cget("values")
            if version in current_values:
                self.version_dropdown.set(version)
            else:
                # If not found, add it and set
                if current_values:
                    updated_values = list(current_values) + [version]
                    self.version_dropdown.configure(values=updated_values)
                else:
                    self.version_dropdown.configure(values=[version])
                self.version_dropdown.set(version)

    def show_version_help(self):
        """Show help about version options"""
        help_text = """📋 Version Options Help

🔸 latest: Tải phiên bản mới nhất
🔸 stable: Tải phiên bản ổn định  
🔸 beta: Tải phiên bản beta/testing
🔸 Version code: Tải version cụ thể (ví dụ: 1.2.3)

� Real-time Version Loading:
• Nhấn "Refresh" để load versions thực từ apkeep
• Versions được cache để load nhanh hơn
• Hiển thị tối đa 5 versions gần nhất

📝 Lưu ý:
• Versions được lấy trực tiếp từ apkeep
• Không phải tất cả versions đều có sẵn
• Auto fallback về "latest" nếu version không tồn tại
• Custom: Cho phép nhập version cụ thể

💡 Mẹo: 
• Dùng "Refresh" để cập nhật versions mới nhất
• "latest" luôn an toàn nhất để sử dụng"""

        messagebox.showinfo("Version Help", help_text)
        self.add_log_message("❓ Đã hiển thị help về version options")

    def refresh_versions(self):
        """Refresh available versions from apkeep with enhanced UI feedback"""
        if self.versions_loading:
            self.add_log_message("⏳ Still loading versions, please wait...")
            return

        self.add_log_message("🔄 Refreshing version list from apkeep...")
        self.versions_loading = True

        # Update UI to show loading state
        if hasattr(self, "version_dropdown"):
            self.version_dropdown.configure(values=["🔄 Loading versions..."])
            self.version_dropdown.set("🔄 Loading versions...")

        # Start background thread to fetch versions
        def fetch_worker():
            try:
                package_name = "com.awesomepiece.castle"

                # Run apkeep command to get versions
                result = subprocess.run(
                    ["apkeep", "-a", package_name, "-l", "."],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    # Parse version list from output
                    version_lines = result.stdout.strip().split("\n")
                    versions = []  # No "latest" - only real versions

                    # Look for the line with versions (contains |)
                    for line in version_lines:
                        line = line.strip()
                        if "|" in line and any(c.isdigit() for c in line):
                            # Extract versions from table format "| version1, version2, ... |"
                            version_part = line.replace("|", "").strip()
                            if version_part:
                                # Split by comma and clean each version
                                for v in version_part.split(","):
                                    v = v.strip()
                                    # Validate version format (contains digits and dots)
                                    if v and any(c.isdigit() for c in v) and "." in v:
                                        if v not in versions:
                                            versions.append(v)

                    versions = sorted(versions, reverse=True)  # Sort newest first

                    # Update UI on main thread
                    self.after(100, lambda: self.versions_fetch_completed(versions))

                else:
                    # Error - use default versions (no "latest")
                    self.after(
                        100,
                        lambda: self.versions_fetch_completed([]),
                    )

            except Exception as e:
                self.add_log_message(f"❌ Error refreshing versions: {str(e)[:100]}")
                self.after(
                    100,
                    lambda: self.versions_fetch_completed([]),
                )

        threading.Thread(target=fetch_worker, daemon=True).start()

    def versions_fetch_completed(self, versions):
        """Handle completion of version fetching with UI state restoration"""
        self.versions_loading = False
        self.add_log_message(f"✅ Loaded {len(versions)} versions from apkeep")

        # Update version dropdown
        if hasattr(self, "version_dropdown"):
            self.version_dropdown.configure(values=versions)
            # Keep current selection if still available, otherwise set to newest version
            current = self.version_dropdown.get()
            if current in versions:
                self.version_dropdown.set(current)
            else:
                # Set to newest version (first in list) instead of "latest"
                if versions:
                    self.version_dropdown.set(versions[0])

        # Show newest version info if available
        if len(versions) > 0:
            newest_version = versions[0]
            self.add_log_message(f"📱 King God Castle - Newest: {newest_version}")

        # Success feedback
        if len(versions) > 3:
            self.add_log_message(
                f"🎯 Ready to download from {len(versions)} available versions"
            )

    def download_apk_by_package(self):
        """Download APK using package name and version - restricted to King God Castle only"""
        # Hard-coded package name for King God Castle only
        package_name = "com.awesomepiece.castle"
        version = (
            self.version_dropdown.get()
            if hasattr(self, "version_dropdown")
            else "159.0.02"
        )

        if not version or version in [
            "Loading...",
            "Loading versions...",
            "🔄 Loading...",
        ]:
            # Use newest known version instead of "latest"
            version = "159.0.02"
            if hasattr(self, "version_dropdown"):
                current_values = self.version_dropdown.cget("values")
                if current_values and len(current_values) > 0:
                    version = current_values[0]
                    self.version_dropdown.set(version)

        if self.processing:
            messagebox.showinfo("Thông báo", "Đang xử lý, vui lòng đợi!")
            return

        # Ask user to choose download directory
        output_dir = filedialog.askdirectory(
            title="Chọn thư mục lưu file APK",
        )

        if not output_dir:
            # User cancelled the dialog
            self.add_log_message("❌ Download cancelled - No directory selected")
            return

        # Ensure the selected directory exists
        try:
            pass  # Không tạo thư mục
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo thư mục: {str(e)}")
            return

        self.add_log_message(f"🚀 Bắt đầu tải APK cho: {package_name}")
        self.add_log_message(f"📋 Version: {version}")
        self.add_log_message(f"📁 Lưu vào: {output_dir}")

        # Show progress UI
        self.processing = True
        self.download_btn.configure(
            state="disabled", text="⏳ Downloading...", fg_color=("#6b7280", "#4b5563")
        )
        self.download_progress.grid()  # Show progress bar
        self.download_progress.set(0.1)  # Initial progress

        self.update_processing_state(True)

        # Start download in background thread
        def download_worker():
            try:
                success = self.apk_processor.download_apk(
                    package_name, version, output_dir, self.update_download_progress
                )

                self.after(100, lambda: self.download_completed(success, output_dir))
            except Exception as e:
                self.add_log_message(f"❌ Lỗi: {str(e)}")
                self.after(100, lambda: self.download_completed(False, None))

        threading.Thread(target=download_worker, daemon=True).start()

    def update_download_progress(self, message, progress=None):
        """Update download progress with optional progress value"""
        # This will be called from worker thread, so we need to schedule UI update
        self.after(10, lambda: self.add_log_message(f"📥 {message}"))

        if progress is not None:
            # Update progress bar with real apkeep progress
            def update_progress_bar():
                self.download_progress.set(
                    min(progress, 0.95)
                )  # Cap at 95% until completion

                # Update button text based on progress
                if progress < 0.2:
                    self.download_btn.configure(text="🔍 Fetching...")
                elif progress < 0.4:
                    self.download_btn.configure(text="🔗 Connecting...")
                elif progress < 0.7:
                    self.download_btn.configure(text="⬇️ Downloading...")
                elif progress < 0.9:
                    self.download_btn.configure(text="💾 Saving...")
                else:
                    self.download_btn.configure(text="✅ Completing...")

            self.after(10, update_progress_bar)

    def download_completed(self, success, output_dir):
        """Handle download completion"""
        self.processing = False
        self.download_progress.set(1.0 if success else 0)

        if success:
            self.download_btn.configure(
                state="normal",
                text="✅ Download Complete",
                fg_color=("#00d084", "#2ea043"),
            )
            self.add_log_message(f"🎉 Tải APK thành công vào: {output_dir}")

            # Find the downloaded APK and add to selected files
            apk_file = list(Path(output_dir).glob("*.xapk"))[0]
            if apk_file:
                self.selected_file = str(apk_file)
                self.update_files_display()
                self.process_btn.configure(state="normal")
                self.add_log_message("📂 Added downloaded APK to processing queue")
        else:
            self.download_btn.configure(
                state="normal",
                text="❌ Download Failed",
                fg_color=("#dc2626", "#d1242f"),
            )
            self.add_log_message("❌ Tải APK thất bại")

        # Hide progress bar after delay
        self.after(3000, lambda: self.download_progress.grid_remove())

        # Reset button text after delay
        if success:
            self.after(
                5000, lambda: self.download_btn.configure(text="� Choose & Download")
            )
        else:
            self.after(
                3000,
                lambda: self.download_btn.configure(
                    text="� Choose & Download", fg_color=("#00d084", "#2ea043")
                ),
            )

        self.update_processing_state(False)

        # COMMENTED OUT: Old download_completed method - replaced with enhanced version
        # def download_completed(self, success, output_dir):
        """Handle download completion"""
        self.processing = False
        self.update_processing_state(False)

        if success and output_dir:
            # Look for downloaded APK files
            apk_file = None
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    if file.lower().endswith(".xapk"):
                        apk_file = os.path.join(output_dir, file)

            if apk_file:
                # Select the first APK file
                self.selected_file = apk_file
                self.add_log_message(f"✅ Đã tải và chọn: {os.path.basename(apk_file)}")

            else:
                self.add_log_message("⚠️ Không tìm thấy file APK đã tải")

    def update_processing_state(self, processing):
        """Update UI state when processing"""
        if hasattr(self, "process_btn"):
            if processing:
                self.process_btn.configure(
                    text="⏳ Đang Xử Lý...", state="disabled", fg_color="#666666"
                )
                if hasattr(self, "cancel_btn"):
                    self.cancel_btn.configure(state="normal")
                if hasattr(self, "progress_bar"):
                    self.progress_bar.grid()
                    self.progress_bar.set(0.1)
            else:
                self.process_btn.configure(
                    text="🚀 Trích Xuất Assets",
                    state="normal" if self.selected_file else "disabled",
                    fg_color="#9C27B0",
                )
                if hasattr(self, "cancel_btn"):
                    self.cancel_btn.configure(state="disabled")
                if hasattr(self, "progress_bar"):
                    self.progress_bar.grid_remove()

        # Update process status
        if hasattr(self, "process_status_label"):
            if processing:
                self.process_status_label.configure(
                    text="Đang xử lý...", text_color="#FF9800"
                )
            else:
                self.process_status_label.configure(
                    text="Sẵn sàng", text_color="#4CAF50"
                )

    def start_asset_extraction(self):
        """Start asset extraction from selected APK/XAPK"""
        if not self.selected_file:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file APK/XAPK trước!")
            return

        if self.processing:
            messagebox.showinfo("Thông báo", "Đang xử lý, vui lòng đợi!")
            return

        if not os.path.exists(self.selected_file):
            messagebox.showerror("Lỗi", "File đã chọn không tồn tại!")
            return

        # Sử dụng thư mục chứa file XAPK làm nơi giải nén và chuyển đổi
        output_dir = os.path.dirname(self.selected_file)

        self.add_log_message(
            f"🔧 Bắt đầu trích xuất assets từ: {os.path.basename(self.selected_file)}"
        )
        self.processing = True
        self.update_processing_state(True)

        # Start extraction in background thread
        def extraction_worker():
            try:
                success = self.apk_processor.extract_assets(
                    self.selected_file, output_dir, self.update_extraction_progress
                )
                self.after(100, lambda: self.extraction_completed(success, output_dir))
            except Exception as e:
                self.add_log_message(f"❌ Lỗi: {str(e)}")
                self.after(100, lambda: self.extraction_completed(False, None))

        threading.Thread(target=extraction_worker, daemon=True).start()

    def update_extraction_progress(self, message):
        """Update extraction progress"""
        self.after(10, lambda: self.add_log_message(f"🔧 {message}"))

    def extraction_completed(self, success, output_dir):
        """Handle extraction completion"""
        self.processing = False
        self.update_processing_state(False)

        if success and output_dir:
            self.add_log_message("✅ Trích xuất assets hoàn thành!")

            # Open output folder if option is enabled
            if hasattr(self, "open_output") and self.open_output.get():
                self.open_folder(output_dir)

            messagebox.showinfo(
                "Thành công",
                f"Trích xuất assets thành công!\nKết quả lưu tại: {output_dir}",
            )
        else:
            messagebox.showerror("Lỗi", "Trích xuất assets thất bại!")

    def open_folder(self, folder_path):
        """Open folder in system file manager"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            self.add_log_message(f"❌ Không thể mở thư mục: {str(e)}")

    def create_file_selection_section(self, parent):
        """Create file selection interface"""
        selection_frame = ctk.CTkFrame(parent)
        selection_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        selection_frame.grid_columnconfigure(0, weight=1)

        # Section title
        title_label = ctk.CTkLabel(
            selection_frame,
            text="📁 Chọn File APK/XAPK",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        # Selection buttons
        buttons_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Select single file
        self.select_file_btn = ctk.CTkButton(
            buttons_frame,
            text="📦 Chọn File",
            command=self.select_xapk_files,
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            corner_radius=8,
        )
        self.select_file_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Select folder
        select_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="📂 Chọn Thư Mục",
            command=self.select_xapk_folder,
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FF9800",
            hover_color="#F57C00",
            corner_radius=8,
        )
        select_folder_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Clear selection
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Xóa",
            command=self.clear_selection,
            height=45,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#F44336",
            hover_color="#D32F2F",
            corner_radius=8,
        )
        clear_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")

    def create_selected_file_section(self, parent):
        """Create selected files display"""
        files_frame = ctk.CTkFrame(parent)
        files_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 15))
        files_frame.grid_columnconfigure(0, weight=1)
        files_frame.grid_rowconfigure(1, weight=1)

        # Section title
        title_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        title_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            title_frame,
            text="📋 File Đã Chọn",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")

        self.file_count_label = ctk.CTkLabel(
            title_frame,
            text="0 file",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            anchor="e",
        )
        self.file_count_label.grid(row=0, column=1, sticky="e")

        # Files list
        self.file_listbox = ctk.CTkScrollableFrame(
            files_frame, fg_color="#1a1a1a", corner_radius=8, height=200
        )
        self.file_listbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.file_listbox.grid_columnconfigure(0, weight=1)

    def create_process_section(self, parent):
        """Create processing section"""
        process_frame = ctk.CTkFrame(parent, fg_color="transparent")
        process_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        process_frame.grid_columnconfigure((0, 1), weight=1)

        # Process button
        self.process_btn = ctk.CTkButton(
            process_frame,
            text="🚀 Trích Xuất Assets",
            command=self.start_asset_extraction,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            corner_radius=10,
            state="disabled",
        )
        self.process_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            process_frame,
            text="⏹️ Hủy",
            command=self.cancel_operation,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#F44336",
            hover_color="#D32F2F",
            corner_radius=10,
            state="disabled",
        )
        self.cancel_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(process_frame, height=8)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()

    def cancel_operation(self):
        """Cancel current operation"""
        if self.processing:
            self.processing = False
            self.update_processing_state(False)
            self.add_log_message("⚠️ Đã hủy thao tác")

    def create_options_section(self, parent):
        """Create options section"""
        options_frame = ctk.CTkFrame(parent)
        options_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        options_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            options_frame,
            text="⚙️ Tùy Chọn",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        # Options container
        options_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_container.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Auto process option
        self.auto_process = ctk.CTkCheckBox(
            options_container,
            text="Tự động xử lý sau khi chọn file",
            font=ctk.CTkFont(size=12),
        )
        self.auto_process.pack(anchor="w", pady=3)

        # Backup option
        self.backup_original = ctk.CTkCheckBox(
            options_container,
            text="Sao lưu file gốc",
            font=ctk.CTkFont(size=12),
        )
        self.backup_original.pack(anchor="w", pady=3)
        self.backup_original.select()

        # Clean temp option
        self.clean_temp = ctk.CTkCheckBox(
            options_container,
            text="Xóa file tạm sau khi hoàn thành",
            font=ctk.CTkFont(size=12),
        )
        self.clean_temp.pack(anchor="w", pady=3)
        self.clean_temp.select()

        # Open output option
        self.open_output = ctk.CTkCheckBox(
            options_container,
            text="Mở thư mục kết quả sau khi hoàn thành",
            font=ctk.CTkFont(size=12),
        )
        self.open_output.pack(anchor="w", pady=3)

        # Extract format option
        self.extract_format = ctk.CTkCheckBox(
            options_container,
            text="Trích xuất định dạng Unity native",
            font=ctk.CTkFont(size=12),
        )
        self.extract_format.pack(anchor="w", pady=3)
        self.extract_format.select()

        # Extract audio option
        self.extract_audio = ctk.CTkCheckBox(
            options_container,
            text="Trích xuất audio files",
            font=ctk.CTkFont(size=12),
        )
        self.extract_audio.pack(anchor="w", pady=3)
        self.extract_audio.select()

        # Extract textures option
        self.extract_textures = ctk.CTkCheckBox(
            options_container,
            text="Trích xuất texture files",
            font=ctk.CTkFont(size=12),
        )
        self.extract_textures.pack(anchor="w", pady=3)
        self.extract_textures.select()

    def create_log_section(self, parent):
        """Create log display section"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        # Log header
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        log_header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            log_header,
            text="📝 Nhật Ký Hoạt Động",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")

        clear_log_btn = ctk.CTkButton(
            log_header,
            text="🗑️ Xóa",
            command=self.clear_log,
            width=60,
            height=25,
            font=ctk.CTkFont(size=10),
            fg_color="#666666",
            hover_color="#777777",
        )
        clear_log_btn.grid(row=0, column=1, sticky="e")

        # Log text area
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=10),
            state="disabled",
            corner_radius=8,
        )
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # Initialize log
        self.initialize_log()

        # Auto-refresh versions after UI is ready
        if self.tools_status.get("apkeep", False):
            self.after(3000, self.auto_refresh_versions)  # Delay 3 seconds

    def initialize_log(self):
        """Initialize the log with welcome messages"""
        self.add_log_message("� King God Castle Processor")
        self.add_log_message("====================================")
        self.add_log_message("🔧 Tích hợp apkeep và AssetRipper")
        self.add_log_message("📱 Chỉ hỗ trợ King God Castle (com.awesomepiece.castle)")
        self.add_log_message("🎯 Trích xuất assets từ APK/XAPK")
        self.add_log_message("⚡ Tải và xử lý King God Castle chuyên biệt")

        # Display tools status
        if self.tools_status["apkeep"]:
            self.add_log_message("✅ apkeep - Ready")
        else:
            self.add_log_message("❌ apkeep - Not Available")

        if self.tools_status["asset-ripper"]:
            self.add_log_message("✅ AssetRipper - Ready")
        else:
            self.add_log_message("❌ AssetRipper - Not Available")

        self.add_log_message("🏰 Chỉ cho phép tải King God Castle")
        self.add_log_message("� Sử dụng version selector để chọn phiên bản")
        self.add_log_message("🔄 Auto fallback nếu version không tồn tại")
        self.add_log_message("�🚀 Sẵn sàng để bắt đầu...")
        self.add_log_message("")

    def clear_log(self):
        """Clear the log display"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.initialize_log()

    def conversion_completed(self):
        """Handle successful conversion completion"""
        self.process_status_label.configure(text="Hoàn thành", text_color="#4CAF50")
        self.process_btn.configure(state="normal", text="🎉 Chuyển Đổi Thành Công")
        # ĐÃ LOẠI BỎ tự động mở app/folder sau khi chuyển đổi thành công

    def conversion_failed(self):
        """Handle conversion failure"""
        self.process_status_label.configure(text="Thất bại", text_color="#F44336")
        self.process_btn.configure(state="normal", text="🚀 Thử Lại")
        self.progress_bar.grid_remove()

    def create_action_buttons(self, parent):
        """Create action buttons for file selection and download"""
        action_frame = ctk.CTkFrame(parent)
        action_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)

        # Select single XAPK file button
        self.select_btn = ctk.CTkButton(
            action_frame,
            text="� Chọn 1 file XAPK",
            command=self.select_xapk_files,
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.cfg.get_theme_setting("colors.primary", "#1f538d"),
            hover_color=self.cfg.get_theme_setting("colors.secondary", "#14375e"),
        )
        self.select_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        # Download King God Castle button (combined folder selection + download)
        self.download_btn = ctk.CTkButton(
            action_frame,
            text="⬇️ Tải King God Castle",
            command=self.download_king_god_castle,
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#00BCD4",  # Bright cyan
            hover_color="#00ACC1",  # Darker cyan on hover
            text_color="white",
        )
        self.download_btn.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

    def create_file_list_section(self, parent):
        """Create file list section for selected XAPK files"""
        file_list_frame = ctk.CTkFrame(parent)
        file_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        file_list_frame.grid_columnconfigure(0, weight=1)
        file_list_frame.grid_rowconfigure(1, weight=1)

        # File list title
        list_title = ctk.CTkLabel(
            file_list_frame,
            text="📁 Selected Files",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        list_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Scrollable frame for file list
        self.file_listbox = ctk.CTkScrollableFrame(
            file_list_frame, height=200, fg_color="#1a1a1a", corner_radius=8
        )
        self.file_listbox.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="nsew")
        self.file_listbox.grid_columnconfigure(0, weight=1)

        # Initialize with placeholder

    def create_download_log(self, parent):
        """Create download log display"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        # Log title with download info
        title_frame = ctk.CTkFrame(log_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        title_frame.grid_columnconfigure(1, weight=1)

        log_title = ctk.CTkLabel(
            title_frame, text="� Log Tải Về", font=ctk.CTkFont(size=16, weight="bold")
        )
        log_title.grid(row=0, column=0, sticky="w")

        # Download path display
        self.path_label = ctk.CTkLabel(
            title_frame,
            text="📁 Chưa chọn thư mục lưu",
            font=ctk.CTkFont(size=12),
            text_color=self.cfg.get_theme_setting("colors.text_secondary", "#b0b0b0"),
        )
        self.path_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Scrollable frame for download log
        self.log_textbox = ctk.CTkTextbox(
            log_frame, font=ctk.CTkFont(family="Consolas", size=11), state="disabled"
        )
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="nsew")

        # Initial log message
        self.add_log_message("🎮 XAPK to Unity Converter & King God Castle Downloader")
        self.add_log_message("� Chọn 1 file XAPK để chuyển đổi thành Unity project")
        self.add_log_message("⚡ Tự động xử lý: XAPK → APK merge → Unity conversion")
        self.add_log_message(
            "ℹ️  Sử dụng 2 chức năng: XAPK→Unity hoặc Tải King God Castle"
        )

        # Initialize download folder
        self.download_folder = None

    def select_download_folder(self):
        """Allow user to select download folder"""
        folder = filedialog.askdirectory(
            title="Chọn thư mục lưu file APK",
            initialdir=os.path.expanduser("~/Downloads"),
        )

        if folder:
            self.download_folder = folder
            # Update path display
            folder_name = os.path.basename(folder) or folder
            self.path_label.configure(text=f"📁 {folder_name}")
            self.add_log_message(f"📂 Đã chọn thư mục: {folder}")
        else:
            self.add_log_message("❌ Chưa chọn thư mục lưu")

    def create_install_section(self, parent):
        """Create installation options and status section"""
        install_frame = ctk.CTkFrame(parent)
        install_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        install_frame.grid_columnconfigure(0, weight=1)

        # Install options
        options_frame = ctk.CTkFrame(install_frame, fg_color="transparent")
        options_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")

        # Checkbox options
        self.auto_install = ctk.CTkCheckBox(
            options_frame,
            text="Tự động cài đặt sau khi chọn file",
            font=ctk.CTkFont(size=12),
        )
        self.auto_install.pack(anchor="w", pady=2)

        self.backup_apk = ctk.CTkCheckBox(
            options_frame,
            text="Sao lưu APK trước khi cài đặt",
            font=ctk.CTkFont(size=12),
        )
        self.backup_apk.pack(anchor="w", pady=2)
        self.backup_apk.select()  # Default selected

        self.keep_data = ctk.CTkCheckBox(
            options_frame, text="Giữ lại dữ liệu ứng dụng cũ", font=ctk.CTkFont(size=12)
        )
        self.keep_data.pack(anchor="w", pady=2)
        self.keep_data.select()  # Default selected

        # Progress bar (hidden initially)
        self.progress_bar = ctk.CTkProgressBar(install_frame)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(10, 15), sticky="ew")
        self.progress_bar.grid_remove()

        # Status label
        self.status_label = ctk.CTkLabel(
            install_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.cfg.get_theme_setting("colors.info", "#2196f3"),
        )
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 15))

    def select_and_close(self, menu_window, action):
        """Handle selection action and close menu"""
        menu_window.destroy()
        if action == "files":
            self.select_xapk_files()
        elif action == "folder":
            self.select_xapk_folder()
        elif action == "clear":
            self.clear_selection()

        """Open file dialog to select XAPK files"""
        file_types = [
            ("XAPK files", "*.xapk"),
            ("APK files", "*.xapk"),
            ("All files", "*.*"),
        ]

        file = filedialog.askopenfilename(
            title="Chọn file XAPK/APK",
            filetypes=file_types,
        )

        if file:
            self.selected_file = file

    def create_modern_file_item(self, file_path):
        """Create a modern file item display"""
        item_frame = ctk.CTkFrame(
            self.file_listbox, corner_radius=8, fg_color="#2b2b2b"
        )
        item_frame.pack(fill="x", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)

        # File icon
        file_extension = os.path.splitext(file_path)[1].lower()
        icon_text = (
            "📦"
            if file_extension == ".xapk"
            else "📱" if file_extension == ".apk" else "📄"
        )

        icon_label = ctk.CTkLabel(
            item_frame,
            text=icon_text,
            font=ctk.CTkFont(size=20),
        )
        icon_label.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="w")

        # File info container
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)

        # File name
        file_name = os.path.basename(file_path)
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        name_label.grid(row=0, column=0, sticky="ew", pady=(0, 2))

        # File details
        file_size = "N/A"
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes >= 1024 * 1024 * 1024:  # GB
                file_size = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            elif size_bytes >= 1024 * 1024:  # MB
                file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            elif size_bytes >= 1024:  # KB
                file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                file_size = f"{size_bytes} bytes"
        except:
            pass

        details_text = f"📏 {file_size} • 📁 {os.path.dirname(file_path)}"
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            anchor="w",
        )
        details_label.grid(row=1, column=0, sticky="ew")

        # Remove button
        remove_btn = ctk.CTkButton(
            item_frame,
            text="🗑️",
            command=self.clear_selection,
            width=40,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#F44336",
            hover_color="#D32F2F",
            corner_radius=6,
        )
        remove_btn.grid(row=0, column=2, padx=(5, 15), pady=15)

    def create_file_item(self, file_path, index):
        """Create a file item in the list"""
        item_frame = ctk.CTkFrame(self.file_listbox)
        item_frame.pack(fill="x", padx=5, pady=2)
        item_frame.grid_columnconfigure(1, weight=1)

        # File icon
        icon_label = ctk.CTkLabel(
            item_frame,
            text="📦" if file_path.lower().endswith(".xapk") else "📱",
            font=ctk.CTkFont(size=16),
        )
        icon_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        # File info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)

        # File name
        file_name = os.path.basename(file_path)
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        name_label.grid(row=0, column=0, sticky="ew")

        # File path
        path_label = ctk.CTkLabel(
            info_frame,
            text=file_path,
            font=ctk.CTkFont(size=10),
            text_color=self.cfg.get_theme_setting("colors.text_secondary", "#b0b0b0"),
            anchor="w",
        )
        path_label.grid(row=1, column=0, sticky="ew")

        # Remove button
        remove_btn = ctk.CTkButton(
            item_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda idx=index: self.remove_file(idx),
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=12),
        )
        remove_btn.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")

    def remove_file(self, index):
        """Remove a file from the selection"""
        if self.selected_file:
            self.selected_file = None

    def install_xapk(self):
        """Download King God Castle using apkeep"""
        # Check if download folder is selected
        if not self.download_folder:
            self.add_log_message("❌ Vui lòng chọn thư mục lưu file trước!")
            messagebox.showwarning(
                "Chưa chọn thư mục", "Vui lòng chọn thư mục lưu file APK trước khi tải!"
            )
            return

        # Show progress bar and disable button
        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.download_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")

        try:
            self.add_log_message("🚀 Bắt đầu tải King God Castle...")
            self.progress_bar.set(0.1)
            self.update()

            # Use selected download directory
            downloads_dir = self.download_folder
            self.add_log_message(f"📁 Thư mục lưu: {downloads_dir}")

            # Path to apkeep executable
            apkeep_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "tools",
                "apkeep",
                "target",
                "release",
                "apkeep",
            )
            apkeep_path = os.path.abspath(apkeep_path)

            if not os.path.exists(apkeep_path):
                self.add_log_message("❌ Lỗi: Không tìm thấy apkeep tool!")
                self.download_error("Không tìm thấy apkeep tool!")
                return

            self.add_log_message("🔧 Sử dụng apkeep tool để tải APK...")
            self.add_log_message("📦 Đang kết nối với APKPure...")
            self.progress_bar.set(0.3)
            self.update()

            # Command to download King God Castle
            cmd = [
                apkeep_path,
                "-a",
                "com.awesomepiece.castle",
                "-d",
                "apk-pure",
                downloads_dir,
            ]

            # Run apkeep command
            def run_download():
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=downloads_dir,
                    )

                    self.add_log_message("⏳ Đang tải APK file...")
                    # Monitor progress
                    self.after(
                        100,
                        lambda: self.monitor_download_progress_with_dir(
                            process, downloads_dir
                        ),
                    )

                except Exception as e:
                    self.after(0, lambda: self.download_error(str(e)))

            # Start download in separate thread
            download_thread = threading.Thread(target=run_download)
            download_thread.daemon = True
            download_thread.start()

        except Exception as e:
            self.download_error(str(e))

    def monitor_download_progress_with_dir(self, process, downloads_dir):
        """Monitor download progress with logging"""
        if process.poll() is None:  # Process still running
            # Update progress bar
            current_progress = self.progress_bar.get()
            if current_progress < 0.8:
                self.progress_bar.set(current_progress + 0.05)

                # Add progress log every 10%
                if current_progress >= 0.4 and current_progress < 0.45:
                    self.add_log_message("📥 Đang tải... 40%")
                elif current_progress >= 0.6 and current_progress < 0.65:
                    self.add_log_message("📥 Đang tải... 60%")
                elif current_progress >= 0.7 and current_progress < 0.75:
                    self.add_log_message("📥 Đang tải... 70%")

            # Continue monitoring
            self.after(
                500,
                lambda: self.monitor_download_progress_with_dir(process, downloads_dir),
            )
        else:
            # Process finished
            if process.returncode == 0:
                self.download_success_with_dir(downloads_dir)
            else:
                stderr = process.stderr.read() if process.stderr else "Unknown error"
                self.download_error_with_msg(f"Download failed: {stderr}")

    def download_success_with_dir(self, downloads_dir):
        """Handle successful download with logging"""
        self.progress_bar.set(1.0)
        self.add_log_message("✅ Tải hoàn tất!")

        # Find downloaded APK file
        apk_files = [f for f in os.listdir(downloads_dir) if f.endswith(".apk")]

        if apk_files:
            apk_path = os.path.join(downloads_dir, apk_files[0])
            apk_size = os.path.getsize(apk_path) / (1024 * 1024)  # Size in MB
            self.add_log_message(f"📁 File: {apk_files[0]} ({apk_size:.1f} MB)")
            self.add_log_message(f"💾 Đường dẫn: {apk_path}")
            self.update_status(f"✅ Tải thành công King God Castle!")

            # Show success dialog
            messagebox.showinfo(
                "Tải Thành Công!",
                f"✅ King God Castle đã được tải thành công!\n\n"
                f"📁 Vị trí file: {apk_path}\n\n"
                f"🎮 Bạn có thể cài đặt file APK này để chơi game.",
            )

            self.add_log_message("🚀 Mở thư mục chứa file APK...")
            # Open download folder
            try:
                if os.name == "nt":  # Windows
                    os.startfile(downloads_dir)
                elif os.name == "posix":  # macOS and Linux
                    subprocess.run(["xdg-open", downloads_dir])
                self.add_log_message("📂 Đã mở thư mục chứa file APK")
            except:
                self.add_log_message("⚠️  Không thể mở thư mục tự động")
        else:
            self.download_error("Không tìm thấy file APK sau khi tải")

        # Reset UI
        self.progress_bar.grid_remove()
        self.download_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.add_log_message("🎉 Hoàn tất! Sẵn sàng cho lần tải tiếp theo.")

    def download_error_with_msg(self, error_msg):
        """Handle download error with logging"""
        self.add_log_message(f"❌ Lỗi: {error_msg}")
        self.progress_bar.grid_remove()
        self.download_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.update_status(f"❌ Lỗi: {error_msg}")

        messagebox.showerror(
            "Lỗi Tải File",
            f"❌ Không thể tải King God Castle!\n\n"
            f"Chi tiết lỗi: {error_msg}\n\n"
            f"Vui lòng thử lại sau hoặc kiểm tra kết nối mạng.",
        )

        self.add_log_message(
            "🔄 Sẵn sàng thử lại. Hãy nhấn 'Tải King God Castle' một lần nữa."
        )

    def update_status(self, message):
        """Update status message"""
        self.status_label.configure(text=message)
        # Clear status after 3 seconds
        self.after(3000, lambda: self.status_label.configure(text=""))

    def download_king_god_castle(self):
        """Download King God Castle with folder selection"""
        # First, ask user to select download folder
        folder = filedialog.askdirectory(
            title="Chọn thư mục lưu King God Castle APK",
        )

        if not folder:
            self.add_log_message("❌ Không chọn thư mục tải file")
            return

        self.download_folder = folder
        self.add_log_message(f"📂 Đã chọn thư mục: {os.path.basename(folder)}")
        self.start_download()

    def start_download(self):
        """Start downloading King God Castle"""
        # Show progress bar and update status
        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.download_btn.configure(state="disabled")
        self.select_btn.configure(state="disabled")

        try:
            self.add_log_message("🚀 Bắt đầu tải King God Castle...")
            self.progress_bar.set(0.1)
            self.update()

            # Path to apkeep executable
            apkeep_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "scripts",
            )

            if not os.path.exists(apkeep_path):
                self.download_error("apkeep tool không tìm thấy")
                return

            self.add_log_message("🔧 Sử dụng apkeep tool để tải APK...")
            self.progress_bar.set(0.2)
            self.update()

            # Command to download King God Castle
            cmd = [
                apkeep_path,
                "-a",
                "com.awesomepiece.castle",
                "-d",
                "apk-pure",
                self.download_folder,
            ]

            # Run apkeep command
            def run_download():
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,  # Line buffered
                        universal_newlines=True,
                        cwd=self.download_folder,
                    )

                    self.add_log_message("⏳ Kết nối với apkeep...")
                    # Monitor progress
                    self.after(100, lambda: self.monitor_download_progress(process))

                except Exception as e:
                    self.after(0, lambda: self.download_error(str(e)))

            # Start download in separate thread
            download_thread = threading.Thread(target=run_download)
            download_thread.daemon = True
            download_thread.start()

        except Exception as e:
            self.download_error(str(e))

    def monitor_download_progress(self, process):
        """Monitor download progress by reading apkeep output"""
        if process.poll() is None:  # Process still running
            # Read any available output from stdout
            try:
                # Check if there's output to read (non-blocking)
                if process.stdout and process.stdout.readable():
                    import select

                    # For Unix systems, use select to check if data is available
                    if hasattr(select, "select"):
                        ready, _, _ = select.select([process.stdout], [], [], 0)
                        if ready:
                            line = process.stdout.readline()
                            if line:
                                # Display raw apkeep output
                                self.add_log_message(f"🔧 {line.strip()}")

                                # Try to extract progress from apkeep progress bar
                                self.parse_apkeep_progress(line.strip())
                    else:
                        # For Windows or when select is not available
                        try:
                            line = process.stdout.readline()
                            if line:
                                # Display raw apkeep output
                                self.add_log_message(f"🔧 {line.strip()}")

                                # Try to extract progress from apkeep progress bar
                                self.parse_apkeep_progress(line.strip())
                        except:
                            pass
            except Exception:
                # If reading fails, continue monitoring
                pass

            # Continue monitoring
            self.after(200, lambda: self.monitor_download_progress(process))
        else:
            # Process finished - read any remaining output
            try:
                if process.stdout:
                    remaining_output = process.stdout.read()
                    if remaining_output:
                        for line in remaining_output.split("\n"):
                            if line.strip():
                                self.add_log_message(f"🔧 {line.strip()}")
            except:
                pass

            # Handle completion
            if process.returncode == 0:
                self.download_success()
            else:
                stderr_output = ""
                try:
                    if process.stderr:
                        stderr_output = process.stderr.read()
                except:
                    pass
                self.download_error(
                    f"Download failed: {stderr_output or 'Unknown error'}"
                )

    def parse_apkeep_progress(self, line):
        """Extract progress from apkeep output"""
        # Look for apkeep progress pattern: [MM:SS:SS] ░░░░░░░░░░░░░░░░░░░░░░░░ SIZE/TOTAL | filename
        import re

        progress_pattern = (
            r"\[(\d{2}:\d{2}:\d{2})\]\s*(░+)\s*([\d.]+\s*\w+)/([\d.]+\s*\w+)"
        )
        progress_match = re.search(progress_pattern, line)

        if progress_match:
            try:
                downloaded_str = progress_match.group(3).strip()
                total_str = progress_match.group(4).strip()

                # Parse sizes (convert to MB for calculation)
                def parse_size(size_str):
                    parts = size_str.split()
                    if len(parts) >= 2:
                        value = float(parts[0])
                        unit = parts[1].lower()
                        if "kb" in unit or "kib" in unit:
                            return value / 1024
                        elif "gb" in unit or "gib" in unit:
                            return value * 1024
                        else:  # MB/MiB
                            return value
                    return 0

                downloaded_mb = parse_size(downloaded_str)
                total_mb = parse_size(total_str)

                if total_mb > 0:
                    percentage = (downloaded_mb / total_mb) * 100
                    # Update progress bar (0.3 to 0.95 range)
                    progress = 0.3 + (percentage / 100) * 0.65
                    self.progress_bar.set(min(progress, 0.95))

            except Exception:
                # If parsing fails, keep default progress updates
                pass

    def download_success(self):
        """Handle successful download with logging"""
        self.progress_bar.set(1.0)
        self.add_log_message("✅ Tải hoàn tất!")

        # Find downloaded APK file
        if self.download_folder:
            apk_files = [
                f
                for f in os.listdir(self.download_folder)
                if f.endswith(".apk") or f.endswith(".xapk")
            ]

            if apk_files:
                apk_path = os.path.join(self.download_folder, apk_files[0])
                apk_size = os.path.getsize(apk_path) / (1024 * 1024)  # Size in MB
                self.add_log_message(f"📁 File: {apk_files[0]} ({apk_size:.1f} MB)")
                self.add_log_message(f"💾 Đường dẫn: {apk_path}")
                self.update_status(f"✅ Tải thành công King God Castle!")

                # Show success dialog
                messagebox.showinfo(
                    "Tải Thành Công!",
                    f"✅ King God Castle đã được tải thành công!\n\n"
                    f"📁 Vị trí file: {apk_path}\n\n"
                    f"🎮 Bạn có thể cài đặt file APK này để chơi game.",
                )

                self.add_log_message("🚀 Mở thư mục chứa file APK...")
                # Open download folder
                try:
                    if os.name == "nt":  # Windows
                        os.startfile(self.download_folder)
                    elif os.name == "posix":  # macOS and Linux
                        subprocess.run(["xdg-open", self.download_folder])
                    self.add_log_message("📂 Đã mở thư mục chứa file APK")
                except Exception as e:
                    self.add_log_message(f"❌ Không thể mở thư mục: {str(e)}")

        # Re-enable buttons
        self.progress_bar.grid_remove()
        self.download_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.add_log_message("🎉 Hoàn tất! Sẵn sàng cho hoạt động tiếp theo.")

    def download_error(self, error_msg):
        """Handle download error with logging"""
        self.add_log_message(f"❌ Lỗi: {error_msg}")
        self.progress_bar.grid_remove()
        self.download_btn.configure(state="normal")
        self.select_btn.configure(state="normal")
        self.update_status(f"❌ Lỗi: {error_msg}")

        messagebox.showerror(
            "Lỗi Tải File",
            f"❌ Không thể tải King God Castle!\n\n"
            f"Chi tiết lỗi: {error_msg}\n\n"
            f"Vui lòng thử lại sau hoặc kiểm tra kết nối mạng.",
        )

        self.add_log_message(
            "🔄 Sẵn sàng thử lại. Hãy nhấn 'Tải King God Castle' một lần nữa."
        )

    def show_select_menu(self):
        """Show menu to choose between file or folder selection"""
        menu = ctk.CTkToplevel(self)
        menu.title("Select XAPK")
        menu.geometry("300x200")
        menu.resizable(False, False)
        menu.transient(self.winfo_toplevel())

        # Center the menu first
        menu.update_idletasks()
        x = (menu.winfo_screenwidth() // 2) - (300 // 2)
        y = (menu.winfo_screenheight() // 2) - (200 // 2)
        menu.geometry(f"300x200+{x}+{y}")

        # Wait for window to be fully created before grabbing
        menu.after(10, lambda: menu.grab_set())

        # Menu content
        title_label = ctk.CTkLabel(
            menu,
            text="📁 Chọn cách thức chọn file",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title_label.pack(pady=20)

        # Select individual files button
        files_btn = ctk.CTkButton(
            menu,
            text="📄 Chọn file riêng lẻ",
            command=lambda: (menu.destroy(), self.select_xapk_files()),
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#4CAF50",
            hover_color="#66BB6A",
        )
        files_btn.pack(pady=5, padx=40, fill="x")

        # Select folder button
        folder_btn = ctk.CTkButton(
            menu,
            text="📂 Chọn từ thư mục",
            command=lambda: (menu.destroy(), self.select_xapk_folder()),
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2196F3",
            hover_color="#42A5F5",
        )
        folder_btn.pack(pady=5, padx=40, fill="x")

        # Clear selection button
        clear_btn = ctk.CTkButton(
            menu,
            text="🗑️ Xóa lựa chọn",
            command=lambda: (menu.destroy(), self.clear_selection()),
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#F44336",
            hover_color="#EF5350",
        )
        clear_btn.pack(pady=5, padx=40, fill="x")

    def select_xapk_files(self):
        """Open file dialog to select single XAPK file and process immediately"""
        file_types = [
            ("XAPK files", "*.xapk"),
            ("APK files", "*.xapk"),
            ("All files", "*.*"),
        ]

        # Use askopenfilename (single file) instead of askopenfilenames (multiple)
        selected_file = filedialog.askopenfilename(
            title="Chọn 1 file XAPK để xử lý",
            filetypes=file_types,
        )

        if selected_file:
            # Add to selected files list
            self.selected_file = selected_file

            filename = os.path.basename(selected_file)

            # Check if it's XAPK file and process immediately
            if selected_file.lower().endswith(".xapk"):
                self.add_log_message(f"📦 Đã chọn file XAPK: {filename}")

                # Show loading screen and start XAPK processing immediately
                self.show_loading_screen("Đang xử lý XAPK...")

                # Start XAPK processing in separate thread
                import threading

                def start_xapk_processing():
                    try:
                        self.process_xapk_file(selected_file, filename)
                        # Complete processing
                        self.after(500, self.hide_loading_screen)
                    except Exception as e:
                        self.add_log_message(f"❌ Lỗi xử lý XAPK: {str(e)}")
                        self.after(0, self.hide_loading_screen)

                process_thread = threading.Thread(target=start_xapk_processing)
                process_thread.daemon = True
                process_thread.start()

            else:
                # For APK files, just show info
                self.add_log_message(f"📱 Đã chọn file APK: {filename}")
                file_size = os.path.getsize(selected_file) / (1024 * 1024)  # Size in MB
                self.add_log_message(f"💾 Kích thước: {file_size:.1f} MB")
                self.add_log_message(
                    "ℹ️  File APK thông thường - không cần xử lý đặc biệt"
                )

                # Update file count
                self.update_file_count()
        else:
            self.add_log_message("❌ Không có file nào được chọn")

    def show_loading_screen(self, message):
        """Show loading screen with progress"""
        # Show progress bar
        self.progress_bar.grid()
        self.progress_bar.set(0)

        # Disable buttons during processing
        self.select_btn.configure(state="disabled")
        self.download_btn.configure(state="disabled")

        # Log loading message
        self.add_log_message(f"⏳ {message}")
        self.update()

    def process_selected_file(self, files):
        """Process selected files with loading animation"""

        def process_files():
            try:
                total_files = len(files)
                processed_files = []

                for i, file in enumerate(files):
                    # Update progress
                    progress = (i + 1) / total_files
                    self.progress_bar.set(progress)

                    # Avoid duplicates
                    if file != self.selected_file:
                        self.selected_file = file
                        processed_files.append(file)

                    # Log current file being processed
                    filename = os.path.basename(file)
                    self.add_log_message(f"📦 Đang phân tích: {filename}")

                    # Update UI
                    self.update()

                    # Simulate processing time (reading file info)
                    import time

                    time.sleep(0.3)  # Small delay for better UX

                # Complete processing
                self.complete_file_processing(processed_files)

            except Exception as e:
                self.add_log_message(f"❌ Lỗi khi phân tích file: {str(e)}")
                self.hide_loading_screen()

        # Start processing in separate thread to avoid UI blocking
        import threading

        process_thread = threading.Thread(target=process_files)
        process_thread.daemon = True
        process_thread.start()

    def complete_file_processing(self, processed_files):
        """Complete file processing and show results"""
        # Final progress
        self.progress_bar.set(1.0)

        # Show summary
        if processed_files:
            self.add_log_message(
                f"✅ Đã phân tích thành công {len(processed_files)} file mới"
            )
            self.add_log_message("📋 Thông tin chi tiết:")

            for file in processed_files:
                filename = os.path.basename(file)
                try:
                    file_size = os.path.getsize(file) / (1024 * 1024)  # Size in MB
                    file_ext = os.path.splitext(file)[1].upper()

                    # Get file creation/modification time
                    import datetime

                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file))
                    mod_time_str = mod_time.strftime("%Y-%m-%d %H:%M")

                    self.add_log_message(f"  📦 {filename}")
                    self.add_log_message(f"     💾 Kích thước: {file_size:.1f} MB")
                    self.add_log_message(f"     📅 Cập nhật: {mod_time_str}")
                    self.add_log_message(f"     🏷️  Loại: {file_ext[1:]} file")

                except Exception as e:
                    self.add_log_message(f"  📦 {filename} (Không thể đọc thông tin)")
        else:
            self.add_log_message("ℹ️  Không có file mới nào được thêm (file đã tồn tại)")

        # Update file count and hide loading
        self.update_file_count()

        # Hide loading screen after short delay
        self.after(500, self.hide_loading_screen)

    def hide_loading_screen(self):
        """Hide loading screen and re-enable interface"""
        # Hide progress bar
        self.progress_bar.grid_remove()

        # Re-enable buttons
        self.select_btn.configure(state="normal")
        self.download_btn.configure(state="normal")

        # Final completion message
        self.add_log_message("🎉 Sẵn sàng cho thao tác tiếp theo!")

    def process_xapk_file(self, file_path, filename):
        """Process XAPK file: extract, merge APKs, convert to Unity"""
        import zipfile, shutil, os

        try:
            self.add_log_message("📂 Bước 1: Giải nén file XAPK...")
            if hasattr(self, "progress_bar"):
                self.progress_bar.set(0.1)
            output_dir = os.path.dirname(file_path)

            extract_dir = os.path.join(
                output_dir, f"{os.path.splitext(filename)[0]}_extracted"
            )
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            self.add_log_message(f"✅ Đã giải nén XAPK vào: {extract_dir}")

            # 2. Giải nén base_assets và config
            self.add_log_message("🔍 Bước 2: Tìm và giải nén base_assets/config...")
            if hasattr(self, "progress_bar"):
                self.progress_bar.set(0.2)
            base_apk, config_apk = None, None
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith(".apk"):
                        file_path_apk = os.path.join(root, file)
                        if "base" in file.lower() or "assets" in file.lower():
                            base_apk = file_path_apk
                        elif "config" in file.lower():
                            config_apk = file_path_apk
            if not base_apk:
                self.add_log_message("❌ Không tìm thấy base_assets APK!")
                return
            base_extract = os.path.join(extract_dir, "base_assets_extracted")
            with zipfile.ZipFile(base_apk, "r") as zip_ref:
                zip_ref.extractall(base_extract)
            if config_apk:
                config_extract = os.path.join(extract_dir, "config_extracted")
                with zipfile.ZipFile(config_apk, "r") as zip_ref:
                    zip_ref.extractall(config_extract)
                self.add_log_message("✅ Đã giải nén config APK")
            else:
                config_extract = None
                self.add_log_message("ℹ️ Không có config APK, chỉ dùng base_assets")

            # 3. Di chuyển config/lib vào base_assets
            if config_extract:
                self.add_log_message(
                    "🔄 Bước 3: Di chuyển config/lib vào base_assets..."
                )
                if hasattr(self, "progress_bar"):
                    self.progress_bar.set(0.4)

                config_lib = os.path.join(config_extract, "lib")
                if os.path.exists(config_lib):
                    # Moving config/lib folder into base_assets
                    shutil.move(config_lib, base_extract)

                    self.add_log_message(
                        "✅ Đã hợp nhất config/lib vào base_assets/lib"
                    )
            else:
                self.add_log_message("ℹ️ Không tìm thấy config/lib để hợp nhất")

            # 4. Xóa toàn bộ trừ base_assets_extracted
            self.add_log_message("🧹 Bước 4: Xóa toàn bộ trừ base_assets...")
            if hasattr(self, "progress_bar"):
                self.progress_bar.set(0.55)
            for item in os.listdir(extract_dir):
                item_path = os.path.join(extract_dir, item)
                if item != "base_assets_extracted":
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)

            # 6. Dùng AssetRipper để chuyển thành Unity project
            self.add_log_message("🎮 Bước 6: Chuyển APK thành dự án Unity...")
            if hasattr(self, "progress_bar"):
                self.progress_bar.set(0.85)

            # Gọi AssetRipper thực sự
            self.convert_to_unity(base_extract)

            # Sau khi convert thành công, xóa toàn bộ file/folder tạm, chỉ giữ lại Unity project
            try:
                # Xóa file XAPK gốc
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.add_log_message(
                        f"🗑️ Đã xóa file XAPK: {os.path.basename(file_path)}"
                    )
                # Xóa folder giải nén
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                    self.add_log_message(
                        f"🗑️ Đã xóa folder giải nén: {os.path.basename(extract_dir)}"
                    )
            except Exception as e:
                self.add_log_message(f"⚠️ Không thể dọn dẹp file/folder tạm: {e}")

            if hasattr(self, "progress_bar"):
                self.progress_bar.set(1.0)
            self.add_log_message("🎉 Hoàn tất xử lý XAPK!")

            # Chuyển sang màn hình editor và truyền path project
            if hasattr(self, "main_window") and self.main_window:
                # Nếu EditorWindow nhận unity_project_path qua thuộc tính
                if (
                    hasattr(self.main_window, "screens")
                    and "unity_editor" in self.main_window.screens
                ):
                    editor = self.main_window.screens["unity_editor"]
                    if hasattr(editor, "load_project"):
                        unity_project_path = os.path.join(
                            os.path.dirname(base_extract),
                            f"{file_path.split('/')[-1].split('@')[1].replace('.xapk', '')}",
                        )

                        print(f"🔄 Đang tải dự án Unity từ: {unity_project_path}...")

                        editor.load_project(unity_project_path)
                self.main_window.show_screen("unity_editor")
        except Exception as e:
            self.add_log_message(f"❌ Lỗi xử lý XAPK: {str(e)}")
            import traceback

            traceback.print_exc()

    def merge_apk_files(self, base_apk, config_apk, work_dir):
        """Merge config APK content into base APK"""
        try:
            import zipfile
            import shutil

            # Extract base APK
            base_extract = os.path.join(work_dir, "base_extracted")

            with zipfile.ZipFile(base_apk, "r") as zip_ref:
                zip_ref.extractall(base_extract)
            self.add_log_message("📂 Đã giải nén base APK")

            # Extract config APK
            config_extract = os.path.join(work_dir, "config_extracted")

            with zipfile.ZipFile(config_apk, "r") as zip_ref:
                zip_ref.extractall(config_extract)
            self.add_log_message("📂 Đã giải nén config APK")

            # Copy config content to base
            self.add_log_message("🔄 Đang hợp nhất nội dung...")
            for root, dirs, files in os.walk(config_extract):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, config_extract)
                    dst_file = os.path.join(base_extract, rel_path)

                    # Create directories if needed
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)

                    # Copy file
                    shutil.copy2(src_file, dst_file)

            # Create merged APK
            merged_apk = os.path.join(work_dir, "merged_base.apk")
            with zipfile.ZipFile(merged_apk, "w", zipfile.ZIP_DEFLATED) as zip_ref:
                for root, dirs, files in os.walk(base_extract):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, base_extract)
                        zip_ref.write(file_path, arc_name)

            # Replace original base APK
            shutil.move(merged_apk, base_apk)
            self.add_log_message("✅ Đã tạo APK hợp nhất")

            # Cleanup
            shutil.rmtree(base_extract)
            shutil.rmtree(config_extract)

        except Exception as e:
            self.add_log_message(f"❌ Lỗi hợp nhất APK: {str(e)}")

    def convert_to_unity(self, merged_folder):
        """Convert APK to Unity project using AssetRipper"""
        try:
            import subprocess

            selected_file = self.selected_file or ""
            unity_dir = os.path.join(
                os.path.dirname(selected_file),
                f"{os.path.splitext(os.path.basename(selected_file))[0].split('@')[1]}",
            )
            os.makedirs(unity_dir, exist_ok=True)
            self.add_log_message(
                f"🎮 Đang chuyển đổi {os.path.basename(merged_folder)}..."
            )
            self.add_log_message(f"📁 Dự án Unity: {unity_dir}")

            cmd = self.tools.asset_ripper(
                ["--InputPath", merged_folder, "--OutputPath", unity_dir]
            )

            self.add_log_message("🔧 Khởi động AssetRipper CLI...")
            self.add_log_message(f"📝 Command: {' '.join(cmd)}")

            if platform.system() != "windows":
                try:
                    import resource

                    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
                    resource.setrlimit(resource.RLIMIT_NOFILE, (min(8192, hard), hard))
                    self.add_log_message(
                        f"🔧 Đã tăng giới hạn file descriptor: {min(8192, hard)}"
                    )

                except Exception as e:
                    self.add_log_message(
                        f"⚠️ Không thể tăng giới hạn file descriptor: {e}"
                    )

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            self.add_log_message("📊 AssetRipper đang chạy...")
            try:
                if process.stdout:
                    while True:
                        output = process.stdout.readline()
                        if output == "" and process.poll() is not None:
                            break
                        if output:
                            line = output.strip()
                            if line:
                                if any(
                                    keyword in line.lower()
                                    for keyword in ["error", "exception", "fail"]
                                ):
                                    self.add_log_message(f"❌ AssetRipper: {line}")
                                elif any(
                                    keyword in line.lower()
                                    for keyword in ["warning", "warn"]
                                ):
                                    self.add_log_message(f"⚠️  AssetRipper: {line}")
                                elif any(
                                    keyword in line.lower()
                                    for keyword in [
                                        "loading",
                                        "processing",
                                        "extracting",
                                        "converting",
                                    ]
                                ):
                                    self.add_log_message(f"🔄 AssetRipper: {line}")
                                elif any(
                                    keyword in line.lower()
                                    for keyword in [
                                        "complete",
                                        "finished",
                                        "done",
                                        "success",
                                    ]
                                ):
                                    self.add_log_message(f"✅ AssetRipper: {line}")
                                elif "export" in line.lower():
                                    self.add_log_message(f"📤 AssetRipper: {line}")
                                else:
                                    self.add_log_message(f"🔧 AssetRipper: {line}")
                        self.update()
                else:
                    self.add_log_message("⚠️  Không thể đọc output từ AssetRipper")
            except Exception as e:
                self.add_log_message(f"❌ Lỗi khi đọc output AssetRipper: {e}")

            return_code = process.poll()

            if return_code == 0:
                self.add_log_message("✅ Chuyển đổi Unity thành công!")
                self.add_log_message(f"📂 Kết quả: {unity_dir}")
            else:
                return_output = process.stderr
                self.add_log_message(
                    f"❌ AssetRipper thất bại với exit code: {return_code}"
                )

                with open(
                    os.path.join(unity_dir, "assetripper_error.log"), "w"
                ) as log_file:
                    log_file.write(
                        f"AssetRipper failed with exit code: {return_code}\n"
                    )
                    if return_output:
                        log_file.write(return_output.read())

        except Exception as e:
            self.add_log_message(f"❌ Lỗi chuyển đổi Unity: {str(e)}")
            import traceback

            self.add_log_message(traceback.format_exc())

    def select_xapk_folder(self):
        """Open folder dialog to select XAPK folder"""
        folder = filedialog.askdirectory(
            title="Chọn thư mục chứa file XAPK/APK",
        )

        if folder:
            self.add_log_message(f"📂 Đã chọn thư mục: {os.path.basename(folder)}")
            self.xapk_folder = folder
            self.update_file_count()

    def clear_selection(self):
        """Clear all selected files"""
        self.selected_file = None
        self.add_log_message("🗑️ Đã xóa file đã chọn")
        self.update_file_count()

    def update_file_count(self):
        """Update file count display via log message"""
        if not self.selected_file:
            self.add_log_message("📁 Danh sách file trống")
        else:
            self.add_log_message(f"📁 Tổng cộng: 1 file đã chọn")

    def minimize_window(self):
        """Minimize the application window"""
        self.winfo_toplevel().iconify()

    def go_back(self):
        """Navigate back to previous screen"""
        if self.main_window:
            self.main_window.go_back()

    def close_app(self):
        """Close the application"""
        self.winfo_toplevel().quit()
        self.winfo_toplevel().destroy()

    def quick_setup_check(self):
        """Quick check to ensure all components are ready"""
        issues = []
        if not all(self.tools_status.values()):
            issues.append("Some tools are not available")
        if issues:
            self.add_log_message("⚠️ Setup issues detected:")
            for issue in issues:
                self.add_log_message(f"  • {issue}")
        else:
            self.add_log_message("✅ All systems ready for King God Castle processing!")
        return len(issues) == 0

    def get_title(self) -> str:
        return "XAPK Installer"

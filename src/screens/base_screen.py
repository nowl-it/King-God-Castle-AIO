"""
Base Screen Class
Abstract base class for all application screens
"""

import customtkinter as ctk
from abc import ABC, abstractmethod


class BaseScreen(ctk.CTkFrame, ABC):
    """Abstract base class for all application screens"""

    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        """Setup the user interface for this screen"""
        pass

    def on_show(self):
        """Called when the screen is shown"""
        pass

    def on_hide(self):
        """Called when the screen is hidden"""
        pass

    def get_title(self) -> str:
        """Get the title for this screen"""
        return "Screen"

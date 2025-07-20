import tkinter as tk
from base import BaseOverlayWindow

class SettingsManager:
    """Manager class for overlay settings window"""
    
    def __init__(self, parent_overlay):
        """Initialize settings manager with reference to parent overlay"""
        self.parent_overlay = parent_overlay
        self.settings_window = None
        
    def open_settings(self):
        """Open the settings window"""
        if self.settings_window and self.settings_window.winfo_exists():
            # If settings window already exists, bring it to front
            self.settings_window.lift()
            self.settings_window.focus()
            return
            
        self._create_settings_window()
        
    def _create_settings_window(self):
        """Create the settings window"""
        self.settings_window = tk.Toplevel(self.parent_overlay.root)
        self.settings_window.title("Overlay Settings")
        self.settings_window.geometry("300x250")
        self.settings_window.configure(bg=self.parent_overlay.COLORS['bg_primary'])
        self.settings_window.resizable(False, False)
        
        # Make settings window stay on top
        self.settings_window.attributes('-topmost', True)
        
        # Position relative to main window
        settings_width = 300
        settings_height = 250
        
        preferred_x, preferred_y = self.parent_overlay.get_safe_position_relative_to(
            self.parent_overlay.root, 
            settings_width, 
            settings_height
        )
        
        self.settings_window.geometry(f"+{preferred_x}+{preferred_y}")
        
        self._create_settings_content()
        
        # Handle window close event
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings)
        
    def _create_settings_content(self):
        """Create the content of the settings window"""
        # Settings content frame
        content_frame = self.parent_overlay.create_styled_frame(
            self.settings_window, 
            style='default'
        )
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        title_label = self.parent_overlay.create_styled_label(
            content_frame,
            "Overlay Settings",
            style='title'
        )
        title_label.pack(pady=(0, 15))
        
        # Transparency section
        self._create_transparency_section(content_frame)
        
        # Window options section
        self._create_window_options_section(content_frame)
        
        # Close settings button
        close_settings_button = self.parent_overlay.create_styled_button(
            content_frame,
            "Close Settings",
            self.close_settings,
            style='danger'
        )
        close_settings_button.pack(pady=(10, 0))
        
    def _create_transparency_section(self, parent):
        """Create transparency control section"""
        transparency_section = self.parent_overlay.create_styled_frame(parent)
        transparency_section.pack(fill='x', pady=(0, 10))
        
        transparency_label = self.parent_overlay.create_styled_label(
            transparency_section,
            "Transparency:",
            font=self.parent_overlay.FONTS['button']
        )
        transparency_label.pack(anchor='w')
        
        transparency_scale = tk.Scale(
            transparency_section,
            from_=0.5,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.parent_overlay.transparency_var,
            command=self.parent_overlay.update_transparency,
            bg=self.parent_overlay.COLORS['bg_primary'],
            fg=self.parent_overlay.COLORS['fg_primary'],
            highlightbackground=self.parent_overlay.COLORS['bg_primary'],
            troughcolor=self.parent_overlay.COLORS['trough_color'],
            length=250
        )
        transparency_scale.pack(fill='x', pady=(5, 0))
        
    def _create_window_options_section(self, parent):
        """Create window options section"""
        options_section = self.parent_overlay.create_styled_frame(parent)
        options_section.pack(fill='x', pady=(0, 10))
        
        options_label = self.parent_overlay.create_styled_label(
            options_section,
            "Window Options:",
            font=self.parent_overlay.FONTS['button']
        )
        options_label.pack(anchor='w', pady=(0, 5))
        
        # Toggle decorations button
        toggle_button = self.parent_overlay.create_styled_button(
            options_section,
            "Toggle Window Frame",
            self._toggle_decorations_with_settings,
            width=20
        )
        toggle_button.pack(pady=2)
        
        # Toggle fullscreen button
        fullscreen_button = self.parent_overlay.create_styled_button(
            options_section,
            "Toggle Fullscreen",
            self.parent_overlay.toggle_fullscreen,
            width=20
        )
        fullscreen_button.pack(pady=2)
        
        # Always on top toggle
        topmost_button = self.parent_overlay.create_styled_button(
            options_section,
            "Toggle Always On Top",
            self._toggle_always_on_top_with_settings,
            width=20
        )
        topmost_button.pack(pady=2)
        
    def _toggle_always_on_top_with_settings(self):
        """Toggle always on top and update settings window accordingly"""
        new_state = self.parent_overlay.toggle_always_on_top()
        if self.settings_window:
            self.settings_window.attributes('-topmost', new_state)
            
    def _toggle_decorations_with_settings(self):
        """Toggle window decorations and handle settings window appropriately"""
        # Store current settings window position before toggling
        if self.settings_window:
            settings_x = self.settings_window.winfo_x()
            settings_y = self.settings_window.winfo_y()
        
        # Toggle the main window decorations
        self.parent_overlay.toggle_decorations()
        
        # If settings window exists, ensure it stays accessible
        if self.settings_window:
            try:
                # Bring settings window to front to ensure it's still accessible
                self.settings_window.lift()
                self.settings_window.focus_set()
                # Reposition it slightly to ensure it's visible
                self.settings_window.geometry(f"+{settings_x}+{settings_y}")
            except tk.TclError:
                # If there's an issue with the settings window, recreate it
                self.close_settings()
                self.open_settings()
            
    def close_settings(self):
        """Close the settings window"""
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
            
    def is_open(self):
        """Check if settings window is currently open"""
        return self.settings_window is not None and self.settings_window.winfo_exists()

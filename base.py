import tkinter as tk
from abc import ABC, abstractmethod

class BaseOverlayWindow(ABC):
    """Base class for overlay windows with shared functionality"""
    
    # Shared styling constants
    COLORS = {
        'bg_primary': '#2c2c2c',
        'bg_secondary': '#404040',
        'bg_button': '#4a4a4a',
        'bg_button_hover': '#5a5a5a',
        'bg_button_danger': '#d32f2f',
        'bg_button_danger_hover': '#f44336',
        'fg_primary': 'white',
        'trough_color': '#404040'
    }
    
    FONTS = {
        'default': ("Arial", 10),
        'button': ("Arial", 10),
        'title': ("Arial", 14, "bold"),
        'icon': ("Arial", 12, "bold"),
        'large': ("Arial", 14)
    }
    
    def __init__(self, title="Overlay Window"):
        """Initialize base window with common settings"""
        self.root = tk.Tk()
        # Initialize drag tracking
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.transparency_var = tk.DoubleVar(value=0.8)
        self._post_drag_callback = None  # Optional callback after dragging ends
        self._setup_base_window(title)
        
    def _setup_base_window(self, title):
        """Configure base window properties"""
        self.root.title(title)
        self.root.configure(bg=self.COLORS['bg_primary'])
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        self.root.resizable(True, True)
        
    def center_window(self, width=400, height=300):
        """Center the window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.position_window_safely(self.root, width, height, x, y)
        
    def position_relative_to(self, parent_window, offset_x=10, offset_y=0):
        """Position window relative to another window"""
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        self.root.geometry(f"+{parent_x + parent_width + offset_x}+{parent_y + offset_y}")
        
    def create_styled_button(self, parent, text, command, style='default', **kwargs):
        """Create a styled button with consistent appearance"""
        button_styles = {
            'default': {
                'bg': self.COLORS['bg_button'],
                'fg': self.COLORS['fg_primary'],
                'activebackground': self.COLORS['bg_button_hover'],
                'activeforeground': self.COLORS['fg_primary'],
                'font': self.FONTS['button']
            },
            'danger': {
                'bg': self.COLORS['bg_button_danger'],
                'fg': self.COLORS['fg_primary'],
                'activebackground': self.COLORS['bg_button_danger_hover'],
                'activeforeground': self.COLORS['fg_primary'],
                'font': self.FONTS['button']
            },
            'icon': {
                'bg': self.COLORS['bg_button'],
                'fg': self.COLORS['fg_primary'],
                'activebackground': self.COLORS['bg_button_hover'],
                'activeforeground': self.COLORS['fg_primary'],
                'width': 3,
                'height': 1,
                'relief': 'flat',
                'bd': 1,
                'font': self.FONTS['icon']
            }
        }
        
        button_config = button_styles.get(style, button_styles['default'])
        button_config.update(kwargs)
        
        return tk.Button(
            parent,
            text=text,
            command=command,
            **button_config
        )
        
    def create_styled_label(self, parent, text="", style='default', **kwargs):
        """Create a styled label with consistent appearance"""
        label_styles = {
            'default': {
                'fg': self.COLORS['fg_primary'],
                'bg': self.COLORS['bg_primary'],
                'font': self.FONTS['default']
            },
            'title': {
                'fg': self.COLORS['fg_primary'],
                'bg': self.COLORS['bg_primary'],
                'font': self.FONTS['title']
            },
            'large': {
                'fg': self.COLORS['fg_primary'],
                'bg': self.COLORS['bg_secondary'],
                'font': self.FONTS['large']
            }
        }
        
        label_config = label_styles.get(style, label_styles['default'])
        label_config.update(kwargs)
        
        return tk.Label(parent, text=text, **label_config)
        
    def create_styled_frame(self, parent, style='default', **kwargs):
        """Create a styled frame with consistent appearance"""
        frame_styles = {
            'default': {'bg': self.COLORS['bg_primary']},
            'secondary': {'bg': self.COLORS['bg_secondary']},
            'sunken': {
                'bg': self.COLORS['bg_secondary'],
                'relief': 'flat',
                'bd': 0
            }
        }
        
        frame_config = frame_styles.get(style, frame_styles['default'])
        frame_config.update(kwargs)
        
        return tk.Frame(parent, **frame_config)
        
    def setup_drag_functionality(self, *widgets):
        """Enable dragging for specified widgets"""
        for widget in widgets:
            widget.bind('<Button-1>', self.start_drag)
            widget.bind('<B1-Motion>', self.on_drag)
            widget.bind('<ButtonRelease-1>', self.end_drag)
            
    def start_drag(self, event):
        """Start window dragging"""
        # Store the initial mouse position relative to the window
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()
        self.drag_data["dragging"] = False
        
    def on_drag(self, event):
        """Handle window dragging"""
        # Mark as dragging to distinguish from clicks
        self.drag_data["dragging"] = True
        
        # Calculate new window position based on mouse position
        new_x = event.x_root - self.drag_data["x"]
        new_y = event.y_root - self.drag_data["y"]
        
        # Move the window immediately for smooth dragging (position only)
        self.root.wm_geometry(f"+{new_x}+{new_y}")
        
    def end_drag(self, event):
        """End window dragging and ensure safe position"""
        # Only apply safe positioning if we actually dragged
        if self.drag_data["dragging"]:
            # Get current window position and size
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # Ensure the final position is safe (only at the end of drag)
            safe_x, safe_y = self.ensure_on_screen(self.root, window_width, window_height, current_x, current_y)
            
            # If the position needed adjustment, move to safe position
            if safe_x != current_x or safe_y != current_y:
                self.root.geometry(f"+{safe_x}+{safe_y}")
        
        # Reset dragging state
        was_dragging = self.drag_data["dragging"]
        self.drag_data["dragging"] = False
        
        # Call post-drag callback if one was dragging and callback exists
        if was_dragging and self._post_drag_callback is not None:
            self.root.after_idle(self._post_drag_callback)
        
    def update_transparency(self, value):
        """Update window transparency"""
        self.root.attributes('-alpha', float(value))
        
    def smart_position_window(self, window, snap_threshold=25, force_on_screen=False, allow_multi_monitor=True):
        """Master function to position window - snaps to edges if close, ensures on screen if needed"""
        # Always get fresh coordinates from the window
        current_x = window.winfo_x()
        current_y = window.winfo_y()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        # Determine appropriate margin based on decoration state
        is_borderless = window.overrideredirect()
        margin = 1 if is_borderless else 10
        
        new_x = current_x
        new_y = current_y
        
        if allow_multi_monitor:
            # Multi-monitor friendly mode - only snap to visible screen edges
            # Get all monitor bounds using tkinter's virtual screen info
            try:
                # Get virtual screen dimensions (all monitors combined)
                virtual_width = window.winfo_vrootwidth()
                virtual_height = window.winfo_vrootheight()
                virtual_x = window.winfo_vrootx()
                virtual_y = window.winfo_vrooty()
                
                # Calculate actual desktop bounds
                desktop_left = virtual_x
                desktop_right = virtual_x + virtual_width
                desktop_top = virtual_y  
                desktop_bottom = virtual_y + virtual_height
                
                # Check if window is larger than virtual screen - fall back to single monitor
                if window_width > virtual_width or window_height > virtual_height:
                    allow_multi_monitor = False
                else:
                    # Only snap/constrain to the outer edges of the entire desktop
                    # LEFT EDGE (leftmost edge of all monitors)
                    if force_on_screen and current_x < desktop_left + margin:
                        new_x = desktop_left + margin
                    elif abs(current_x - desktop_left) <= snap_threshold:
                        new_x = desktop_left + margin
                    
                    # RIGHT EDGE (rightmost edge of all monitors)
                    if force_on_screen and current_x + window_width > desktop_right - margin:
                        new_x = desktop_right - window_width - margin
                    elif abs(current_x + window_width - desktop_right) <= snap_threshold:
                        new_x = desktop_right - window_width - margin
                        
                    # TOP EDGE (topmost edge of all monitors)
                    if force_on_screen and current_y < desktop_top + margin:
                        new_y = desktop_top + margin
                    elif abs(current_y - desktop_top) <= snap_threshold:
                        new_y = desktop_top + margin
                        
                    # BOTTOM EDGE (bottommost edge of all monitors)
                    if force_on_screen and current_y + window_height > desktop_bottom - margin:
                        new_y = desktop_bottom - window_height - margin
                    elif abs(current_y + window_height - desktop_bottom) <= snap_threshold:
                        new_y = desktop_bottom - window_height - margin
                    
            except:
                # Fallback to single monitor mode if virtual screen info fails
                allow_multi_monitor = False
        
        if not allow_multi_monitor:
            # Single monitor mode (original behavior)
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            
            # LEFT EDGE
            if force_on_screen and current_x < margin:
                new_x = margin
            elif current_x <= snap_threshold:
                new_x = margin
            
            # RIGHT EDGE
            right_edge_distance = screen_width - (current_x + window_width)
            if force_on_screen and current_x + window_width > screen_width - margin:
                # For oversized windows, position at margin
                if window_width > screen_width - 2 * margin:
                    new_x = margin
                else:
                    new_x = screen_width - window_width - margin
            elif right_edge_distance <= snap_threshold:
                new_x = screen_width - window_width - margin
                
            # TOP EDGE
            if force_on_screen and current_y < margin:
                new_y = margin
            elif current_y <= snap_threshold:
                new_y = margin
                
            # BOTTOM EDGE
            bottom_edge_distance = screen_height - (current_y + window_height)
            if force_on_screen and current_y + window_height > screen_height - margin:
                # For oversized windows, position at margin
                if window_height > screen_height - 2 * margin:
                    new_y = margin
                else:
                    new_y = screen_height - window_height - margin
            elif bottom_edge_distance <= snap_threshold:
                new_y = screen_height - window_height - margin
            
        # Apply new position if it changed
        if new_x != current_x or new_y != current_y:
            window.geometry(f"+{new_x}+{new_y}")
            return True
        return False

    def toggle_decorations(self):
        """Toggle window decorations (title bar, borders)"""
        # Toggle decorations
        current_borderless = self.root.overrideredirect()
        self.root.overrideredirect(not current_borderless)
        
        # Ensure window fully updates after decoration change
        self.root.update_idletasks()
        self.root.update()
        
        # Snap to edges after window has completed all updates
        self.root.after_idle(lambda: self.snap_to_edges_if_close(self.root))
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def toggle_always_on_top(self):
        """Toggle always on top setting"""
        current_state = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current_state)
        return not current_state
        
    def minimize_window(self):
        """Minimize the window"""
        # Can't minimize borderless windows - temporarily enable decorations
        if self.root.overrideredirect():
            self.root.overrideredirect(False)
            self.root.update_idletasks()
            self.root.iconify()
            # Note: Window will have decorations when restored
        else:
            self.root.iconify()
        
    def close_window(self):
        """Close the window"""
        self.root.quit()
        self.root.destroy()
        
    @abstractmethod
    def create_widgets(self):
        """Abstract method to create specific widgets for the window"""
        pass
        
    def run(self):
        """Start the window mainloop"""
        self.root.mainloop()
        
    def snap_to_edges_if_close(self, window, snap_threshold=25):
        """Snap window to screen edges if close enough (convenience wrapper)"""
        return self.smart_position_window(window, snap_threshold=snap_threshold, force_on_screen=False)
        
    def ensure_on_screen(self, window, width=None, height=None, x=None, y=None):
        """Ensure a window stays on screen by adjusting position if needed
        Legacy wrapper for smart_position_window with force_on_screen=True"""
        # Use smart_position_window with force_on_screen enabled
        self.smart_position_window(window, snap_threshold=0, force_on_screen=True)
        
        # For backwards compatibility, return the final position
        return window.winfo_x(), window.winfo_y()
        
    def position_window_safely(self, window, width, height, x, y):
        """Position a window safely on screen"""
        safe_x, safe_y = self.ensure_on_screen(window, width, height, x, y)
        window.geometry(f"{width}x{height}+{safe_x}+{safe_y}")
        
    def get_safe_position_relative_to(self, target_window, window_width, window_height, offset_x=10, offset_y=0):
        """Get safe position for a window relative to another window"""
        main_x = target_window.winfo_x()
        main_y = target_window.winfo_y()
        main_width = target_window.winfo_width()
        
        # Get screen dimensions
        screen_width = target_window.winfo_screenwidth()
        screen_height = target_window.winfo_screenheight()
        
        # Calculate preferred position (to the right of main window)
        preferred_x = main_x + main_width + offset_x
        preferred_y = main_y + offset_y
        
        # Check if window would go off-screen horizontally
        if preferred_x + window_width > screen_width:
            # Position to the left of main window instead
            preferred_x = main_x - window_width - offset_x
            # If still off-screen, center it
            if preferred_x < 0:
                preferred_x = (screen_width - window_width) // 2
        
        # Check if window would go off-screen vertically
        if preferred_y + window_height > screen_height:
            preferred_y = screen_height - window_height - 10
        if preferred_y < 0:
            preferred_y = 10
            
        return preferred_x, preferred_y

    def setup_clickable_drag_functionality(self, widget, click_callback):
        """Enable both dragging and clicking for a widget"""
        widget.bind('<Button-1>', self.start_drag)
        widget.bind('<B1-Motion>', self.on_drag)
        widget.bind('<ButtonRelease-1>', lambda e: self.end_drag_with_click(e, click_callback))
        
    def end_drag_with_click(self, event, click_callback):
        """End drag and handle click if no dragging occurred"""
        # Call the regular end_drag first
        was_dragging = self.drag_data["dragging"]
        self.end_drag(event)
        
        # If we weren't dragging, treat it as a click
        if not was_dragging:
            click_callback()

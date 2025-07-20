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
                'relief': 'sunken',
                'bd': 2
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
        
        # Move the window immediately for smooth dragging
        self.root.geometry(f"+{new_x}+{new_y}")
        
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
        self.drag_data["dragging"] = False
        
    def update_transparency(self, value):
        """Update window transparency"""
        self.root.attributes('-alpha', float(value))
        
    def toggle_decorations(self):
        """Toggle window decorations (title bar, borders)"""
        current_state = self.root.overrideredirect()
        self.root.overrideredirect(not current_state)
        
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
        
    def ensure_on_screen(self, window, width, height, x, y):
        """Ensure a window stays on screen by adjusting position if needed"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Ensure minimum margins from screen edges
        min_margin = 10
        
        # Adjust horizontal position
        # Check if left edge is off-screen
        if x < min_margin:
            x = min_margin
        # Check if right edge is off-screen
        elif x + width > screen_width - min_margin:
            x = screen_width - width - min_margin
            
        # Adjust vertical position
        # Check if top edge is off-screen
        if y < min_margin:
            y = min_margin
        # Check if bottom edge is off-screen
        elif y + height > screen_height - min_margin:
            y = screen_height - height - min_margin
            
        # Final safety check - if window is larger than screen, position at margin
        if x < 0:
            x = min_margin
        if y < 0:
            y = min_margin
            
        return x, y
        
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

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sys
import os
from base import BaseOverlayWindow
from settings import SettingsManager

class ImageOverlay(BaseOverlayWindow):
    def __init__(self):
        super().__init__("Image Overlay")
        self.image_path = None
        self.image_label = None
        self.original_image = None
        self.current_image = None
        self.aspect_ratio = None
        self.settings_manager = SettingsManager(self)
        
        # Track window state for smart clearing
        self.pre_image_state = None  # (x, y, width, height) before loading image
        self.post_image_state = None  # (x, y, width, height) after loading image
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the overlay-specific window properties"""
        # Set initial window size and position using base class method
        self.center_window(400, 300)
        
    def create_widgets(self):
        """Create overlay content"""
        # Main container
        main_frame = self.create_styled_frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Top bar with settings gear icon
        top_bar = self.create_styled_frame(main_frame, height=30)
        top_bar.pack(fill='x', pady=(0, 5))
        top_bar.pack_propagate(False)
        
        # Settings gear button
        settings_button = self.create_styled_button(
            top_bar,
            "⚙",  # Gear Unicode character
            self.settings_manager.open_settings,
            style='icon'
        )
        settings_button.pack(side='right', padx=(5, 0))
        
        # Load image button (compact)
        load_button = self.create_styled_button(
            top_bar,
            "📁",  # Folder Unicode character
            self.load_image,
            style='icon'
        )
        load_button.pack(side='left', padx=(0, 5))
        
        # Clear button (compact)
        clear_button = self.create_styled_button(
            top_bar,
            "🗑",  # Trash Unicode character
            self.clear_image,
            style='icon'
        )
        clear_button.pack(side='left')
        
        # Image display area
        self.image_frame = self.create_styled_frame(main_frame, style='sunken')
        self.image_frame.pack(fill='both', expand=True)
        
        # Placeholder label for when no image is loaded
        self.placeholder_label = self.create_styled_label(
            self.image_frame,
            "📁 Load Image",
            style='large'
        )
        self.placeholder_label.pack(expand=True)
        
        # Bind events
        self.root.bind('<Escape>', lambda e: self.close_overlay())
        self.root.bind('<Button-3>', self.show_context_menu)
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Enable dragging for the main frame and image frame
        self.setup_drag_functionality(main_frame, self.image_frame)
        
    def load_image(self):
        """Load an image file"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        self.image_path = filedialog.askopenfilename(
            title="Select Image for Overlay",
            filetypes=file_types
        )
        
        if self.image_path:
            try:
                self.display_image()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {str(e)}")
                
    def display_image(self):
        """Display the loaded image"""
        if not self.image_path or not os.path.exists(self.image_path):
            return
            
        try:
            # Store window state before loading image
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            self.pre_image_state = (current_x, current_y, current_width, current_height)
            
            # Load the original image
            self.original_image = Image.open(self.image_path)
            img_width, img_height = self.original_image.size
            
            # Store aspect ratio for window resizing
            self.aspect_ratio = img_width / img_height
            
            # Calculate target window size (with some padding for controls)
            max_width = self.root.winfo_screenwidth() - 100
            max_height = self.root.winfo_screenheight() - 100
            
            # Scale image to fit screen if necessary
            if img_width > max_width or img_height > max_height:
                scale_x = max_width / img_width
                scale_y = max_height / img_height
                scale = min(scale_x, scale_y)
                target_width = int(img_width * scale)
                target_height = int(img_height * scale)
            else:
                target_width = img_width
                target_height = img_height
            
            # Resize window to match image (plus padding for controls)
            window_width = target_width + 20  # Padding for frame
            window_height = target_height + 50  # Padding for top bar and frame
            
            # Resize and reposition window
            self.root.geometry(f"{window_width}x{window_height}+{current_x}+{current_y}")
            
            # Wait for window to resize
            self.root.update_idletasks()
            
            # Ensure the resized window stays on screen (especially important when borderless)
            # This prevents the settings button and controls from becoming inaccessible
            # when loading images near screen edges with window frame toggled off
            safe_x, safe_y = self.ensure_on_screen(
                self.root, 
                window_width, 
                window_height, 
                current_x, 
                current_y
            )
            
            # Apply safe positioning if needed
            if safe_x != current_x or safe_y != current_y:
                self.root.geometry(f"{window_width}x{window_height}+{safe_x}+{safe_y}")
                self.root.update_idletasks()
            
            # Store final window state after loading and positioning
            final_x = self.root.winfo_x()
            final_y = self.root.winfo_y()
            final_width = self.root.winfo_width()
            final_height = self.root.winfo_height()
            self.post_image_state = (final_x, final_y, final_width, final_height)
            
            # Now display the image at the calculated size
            self._update_image_display()
            
        except ImportError:
            # Fallback if PIL is not available
            messagebox.showerror(
                "Missing Dependency", 
                "PIL (Pillow) is required for image support.\n"
                "Install it with: pip install Pillow"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {str(e)}")
            
    def _update_image_display(self):
        """Update the image display based on current window size"""
        if not self.original_image:
            return
            
        try:
            # Get the current size of the image frame
            self.image_frame.update_idletasks()
            frame_width = self.image_frame.winfo_width() - 10
            frame_height = self.image_frame.winfo_height() - 10
            
            if frame_width <= 1 or frame_height <= 1:
                return
            
            # Calculate the scaling to fit the image in the frame while maintaining aspect ratio
            img_width, img_height = self.original_image.size
            scale_x = frame_width / img_width
            scale_y = frame_height / img_height
            scale = min(scale_x, scale_y)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize the image
            resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.current_image = ImageTk.PhotoImage(resized_image)
            
            # Remove placeholder and add image
            if self.placeholder_label:
                self.placeholder_label.destroy()
                self.placeholder_label = None
                
            if self.image_label:
                self.image_label.destroy()
                
            self.image_label = self.create_styled_label(
                self.image_frame,
                "",
                style='large',
                image=self.current_image
            )
            self.image_label.pack(expand=True)
            
            # Enable dragging for the image
            self.setup_drag_functionality(self.image_label)
            
        except Exception as e:
            print(f"Error updating image display: {e}")
            
    def on_window_resize(self, event):
        """Handle window resize events to maintain aspect ratio"""
        # Only handle resize events for the root window
        if event.widget != self.root:
            return
            
        # If we have an image loaded and aspect ratio stored
        if self.original_image and self.aspect_ratio:
            # Update the image display
            self.root.after_idle(self._update_image_display)
            
    def clear_image(self):
        """Clear the current image with smart window positioning"""
        if self.image_label:
            self.image_label.destroy()
            self.image_label = None
            
        if not self.placeholder_label:
            self.placeholder_label = self.create_styled_label(
                self.image_frame,
                "📁 Load Image",
                style='large'
            )
            self.placeholder_label.pack(expand=True)
            # Enable dragging for placeholder
            self.setup_drag_functionality(self.placeholder_label)
            
        self.image_path = None
        self.original_image = None
        self.current_image = None
        self.aspect_ratio = None
        
        # Smart window positioning: maintain current position but resize appropriately
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        
        # Target size for cleared state
        target_width = 400
        target_height = 300
        
        # If we have tracking data about how the window expanded, try to contract intelligently
        if self.pre_image_state and self.post_image_state:
            pre_x, pre_y, pre_width, pre_height = self.pre_image_state
            post_x, post_y, post_width, post_height = self.post_image_state
            
            # Calculate how the window was adjusted when the image was loaded
            x_offset = post_x - pre_x
            y_offset = post_y - pre_y
            width_change = post_width - pre_width
            height_change = post_height - pre_height
            
            # Try to reverse the expansion logic
            # If window moved left (x_offset < 0), it was because it expanded right and hit screen edge
            # So when contracting, we should move it back right
            if x_offset < 0 and width_change > 0:
                # Window was pushed left due to right expansion, contract by moving right
                clear_x = current_x + (post_width - target_width)
            # If window moved right (x_offset > 0), it expanded left, so stay put when contracting
            elif x_offset > 0 and width_change > 0:
                # Window was moved right due to left expansion, keep current position
                clear_x = current_x
            else:
                # No horizontal adjustment needed or unclear case, keep current position
                clear_x = current_x
            
            # Similar logic for vertical positioning
            if y_offset < 0 and height_change > 0:
                # Window was pushed up due to bottom expansion, contract by moving down
                clear_y = current_y + (post_height - target_height)
            elif y_offset > 0 and height_change > 0:
                # Window was moved down due to top expansion, keep current position
                clear_y = current_y
            else:
                # No vertical adjustment needed or unclear case, keep current position
                clear_y = current_y
        else:
            # No tracking data, just maintain current position
            clear_x = current_x
            clear_y = current_y
        
        # Ensure the cleared window position is safe
        safe_x, safe_y = self.ensure_on_screen(
            self.root, 
            target_width, 
            target_height, 
            clear_x, 
            clear_y
        )
        
        # Apply the new size and position
        self.root.geometry(f"{target_width}x{target_height}+{safe_x}+{safe_y}")
        
        # Clear the tracking data
        self.pre_image_state = None
        self.post_image_state = None
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Load Image", command=self.load_image)
        context_menu.add_command(label="Clear Image", command=self.clear_image)
        context_menu.add_separator()
        context_menu.add_command(label="Settings", command=self.settings_manager.open_settings)
        context_menu.add_separator()
        context_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen)
        context_menu.add_command(label="Toggle Frame", command=self.toggle_decorations)
        context_menu.add_command(label="Minimize", command=self.minimize_window)
        context_menu.add_separator()
        context_menu.add_command(label="Close", command=self.close_overlay)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def close_overlay(self):
        """Close the overlay"""
        if self.settings_manager.is_open():
            self.settings_manager.close_settings()
        self.close_window()
        
    def run(self):
        """Start the overlay"""
        print("Starting image overlay...")
        print("Controls:")
        print("- ESC key: Close overlay")
        print("- Right-click: Context menu")
        print("- Drag window: Click and drag")
        print("- Load Image: Use button or context menu")
        print("- Window resizes to image size automatically")
        print("- Image scales with window while maintaining aspect ratio")
        
        super().run()

def main():
    """Main function to run the overlay"""
    try:
        overlay = ImageOverlay()
        overlay.run()
    except KeyboardInterrupt:
        print("\nOverlay closed by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
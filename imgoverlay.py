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
        self.settings_manager = SettingsManager(self)
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
            # Load and resize image to fit the frame
            self.original_image = Image.open(self.image_path)
            
            # Get the current size of the image frame
            self.image_frame.update_idletasks()
            frame_width = self.image_frame.winfo_width() - 10
            frame_height = self.image_frame.winfo_height() - 10
            
            if frame_width <= 1 or frame_height <= 1:
                frame_width, frame_height = 300, 200
            
            # Calculate the scaling to fit the image in the frame
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
            
        except ImportError:
            # Fallback if PIL is not available
            messagebox.showerror(
                "Missing Dependency", 
                "PIL (Pillow) is required for image support.\n"
                "Install it with: pip install Pillow"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image: {str(e)}")
            
    def clear_image(self):
        """Clear the current image"""
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
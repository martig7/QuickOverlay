# Image Overlay Application

A tkinter-based image overlay application with modular architecture.

## Project Structure

### 1. `base.py` - BaseOverlayWindow Class
Contains shared functionality for all overlay windows:
- **Styling constants**: Colors, fonts, and common UI elements
- **Window management**: Transparency, always-on-top, fullscreen, decorations
- **Drag functionality**: Unified dragging behavior with off-screen prevention
- **UI helpers**: Styled button, label, and frame creation methods
- **Common window operations**: Centering, positioning, minimizing, closing
- **Off-screen prevention**: Ensures windows stay visible on screen during positioning and dragging

### 2. `settings.py` - SettingsManager Class
Handles all settings-related functionality:
- **Settings window creation**: Dedicated settings UI management
- **Settings controls**: Transparency slider, window options buttons
- **Settings persistence**: Manages settings window lifecycle
- **Parent communication**: Interacts with main overlay through callbacks

### 3. `imgoverlay.py` - ImageOverlay Class
Main overlay functionality focused on image display:
- **Image handling**: Loading, displaying, and clearing images
- **Context menu**: Right-click menu with overlay operations
- **Event handling**: Keyboard shortcuts and window events
- **Integration**: Uses base class and settings manager

## Usage

Run the application:
```bash
python imgoverlay.py
```

## Testing

The project includes comprehensive unit tests:

```bash
# Run basic unit tests
python test_overlay_simple.py

# Run comprehensive test suite
python run_tests.py
```

**Test Coverage:**
- **Basic Functionality**: Core window operations, styling, positioning
- **Manual Integration**: Component interaction and edge cases  
- **File Structure**: Required files and module imports
- **Performance**: Window creation and calculation speed

## Dependencies

- `tkinter` (built-in with Python)
- `PIL` (Pillow) for image handling

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **For development (optional):**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Features

- **Image overlay display** with drag and drop positioning
- **Off-screen prevention** - windows stay visible during dragging and positioning
- **Transparency control** via settings
- **Always on top** functionality
- **Fullscreen mode** toggle
- **Window frame** toggle (borderless mode)
- **Context menu** with quick actions
- **Keyboard shortcuts** (ESC to close)
- **Modern dark theme** UI

## Architecture Notes

- `BaseOverlayWindow` is an abstract base class that enforces the `create_widgets()` method
- `SettingsManager` is a composition-based component that manages settings UI
- All styling is centralized through constants in the base class
- Drag functionality is unified and reusable across all components with off-screen prevention
- Settings window lifecycle is properly managed to prevent multiple instances
- Off-screen prevention ensures all windows remain visible and accessible regardless of screen size or position

## Project Files

### Core Application:
- **`base.py`** - Abstract base class with shared functionality
- **`settings.py`** - Settings window manager
- **`imgoverlay.py`** - Main image overlay application

### Dependencies:
- **`requirements.txt`** - Required packages for running the application
- **`requirements-dev.txt`** - Additional packages for development

### Testing:
- **`test_overlay_simple.py`** - Unit tests for core functionality
- **`run_tests.py`** - Comprehensive test runner with reporting

### Documentation:
- **`README.md`** - This documentation file

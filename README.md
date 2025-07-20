# Image Overlay Application

A tkinter-based image overlay application with modular architecture and automated build system.

## Quick Start

1. **Download** or build `ImageOverlay.exe`
2. **Double-click** to run - No installation required!
3. **Load an image** using the button or right-click menu
4. **Drag to position**, adjust transparency in settings

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

## Usage

### Standalone Executable (Recommended)

Simply run the standalone executable:
```bash
# Windows
ImageOverlay.exe

# Or double-click ImageOverlay.exe in your file explorer
```

### From Source (Development)

If you need to run from source code:
```bash
python imgoverlay.py
```

## Testing

### Automated Testing (Recommended)

The build script includes comprehensive testing:
```bash
# Run all tests as part of build process
python build.py --no-exe

# Fast test run
python build.py --no-exe --fast
```

### Manual Testing

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

### For End Users

1. **Download the executable** from the build artifacts or releases
2. **Run ImageOverlay.exe** - No installation required!

### For Developers

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **For development and building:**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Building

The project includes a comprehensive build script that tests, lints, and packages the application.

### Quick Build (Recommended)

Create a standalone executable for distribution:
```bash
python build.py --clean
```

This creates `build/executable/ImageOverlay.exe` - a single-file executable that requires no Python installation.

### Build Options

```bash
# Default: Create standalone executable only
python build.py

# Fast build (skip slow tests)
python build.py --fast

# Clean build (remove previous build artifacts)
python build.py --clean

# Build without executable (tests/lint only)
python build.py --no-exe

# Include Python distribution package
python build.py --include-python-dist

# Skip specific steps
python build.py --no-tests --no-lint

# Quick development build
python build.py --fast --no-lint
```

### Build Process

The build script automatically:

1. **Validates** project structure and dependencies
2. **Runs tests** - Unit tests and integration tests
3. **Checks code quality** - Syntax validation and linting (if available)
4. **Creates executable** - Single-file standalone application using PyInstaller
5. **Generates reports** - Detailed build reports and logs

### Build Output

```
build/
├── executable/              # Main distribution
│   ├── ImageOverlay.exe     # Standalone executable (29MB)
│   └── README.md           # Usage instructions
├── dist/                   # Python distribution (optional)
├── reports/                # Build reports and logs
│   ├── build_report.md     # Comprehensive build summary
│   ├── test_results.txt    # Test execution details
│   └── pyinstaller_log.txt # Executable build log
└── pyinstaller_temp/       # Temporary build files
```

### Distribution

For internal distribution, simply copy the `build/executable/` folder to the target system. The executable requires no Python installation or dependencies.

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

## Architecture Notes

- `BaseOverlayWindow` is an abstract base class that enforces the `create_widgets()` method
- `SettingsManager` is a composition-based component that manages settings UI
- All styling is centralized through constants in the base class
- Drag functionality is unified and reusable across all components with off-screen prevention
- Settings window lifecycle is properly managed to prevent multiple instances
- Off-screen prevention ensures all windows remain visible and accessible regardless of screen size or position

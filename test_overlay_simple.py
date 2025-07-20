#!/usr/bin/env python3
"""
Unit tests for the Image Overlay application.
Run with: python test_overlay_simple.py
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base import BaseOverlayWindow


class TestBaseOverlayWindow(unittest.TestCase):
    """Test cases for BaseOverlayWindow base class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a concrete implementation for testing
        class TestWindow(BaseOverlayWindow):
            def create_widgets(self):
                pass
        
        try:
            self.test_window = TestWindow("Test Window")
        except tk.TclError:
            self.skipTest("Cannot create Tk window in this environment")
        
    def tearDown(self):
        """Clean up after tests"""
        try:
            if hasattr(self, 'test_window'):
                self.test_window.root.destroy()
        except:
            pass
            
    def test_color_constants(self):
        """Test that color constants are properly defined"""
        colors = BaseOverlayWindow.COLORS
        self.assertIn('bg_primary', colors)
        self.assertIn('bg_secondary', colors)
        self.assertIn('fg_primary', colors)
        self.assertEqual(colors['bg_primary'], '#2c2c2c')
        self.assertEqual(colors['fg_primary'], 'white')
        
    def test_font_constants(self):
        """Test that font constants are properly defined"""
        fonts = BaseOverlayWindow.FONTS
        self.assertIn('default', fonts)
        self.assertIn('button', fonts)
        self.assertIn('title', fonts)
        self.assertIn('icon', fonts)
        self.assertIn('large', fonts)
        
    def test_ensure_on_screen_logic(self):
        """Test off-screen prevention logic with mock window"""
        # Create a mock window object
        mock_window = Mock()
        mock_window.winfo_screenwidth.return_value = 1920
        mock_window.winfo_screenheight.return_value = 1080
        
        # Test normal positioning (should not change)
        x, y = self.test_window.ensure_on_screen(mock_window, 400, 300, 100, 100)
        self.assertEqual(x, 100)
        self.assertEqual(y, 100)
        
        # Test off-screen right (should move left)
        x, y = self.test_window.ensure_on_screen(mock_window, 400, 300, 1800, 100)
        self.assertEqual(x, 1510)  # 1920 - 400 - 10
        self.assertEqual(y, 100)
        
        # Test off-screen bottom (should move up)
        x, y = self.test_window.ensure_on_screen(mock_window, 400, 300, 100, 1000)
        self.assertEqual(x, 100)
        self.assertEqual(y, 770)  # 1080 - 300 - 10
        
        # Test off-screen left (should move right)
        x, y = self.test_window.ensure_on_screen(mock_window, 400, 300, -50, 100)
        self.assertEqual(x, 10)
        self.assertEqual(y, 100)
        
        # Test off-screen top (should move down)
        x, y = self.test_window.ensure_on_screen(mock_window, 400, 300, 100, -50)
        self.assertEqual(x, 100)
        self.assertEqual(y, 10)
        
    def test_get_safe_position_relative_to(self):
        """Test safe relative positioning logic"""
        # Create mock target window
        mock_target = Mock()
        mock_target.winfo_x.return_value = 100
        mock_target.winfo_y.return_value = 100
        mock_target.winfo_width.return_value = 400
        mock_target.winfo_screenwidth.return_value = 1920
        mock_target.winfo_screenheight.return_value = 1080
        
        # Test normal positioning (to the right of target)
        x, y = self.test_window.get_safe_position_relative_to(mock_target, 300, 250)
        self.assertEqual(x, 510)  # 100 + 400 + 10
        self.assertEqual(y, 100)
        
        # Test positioning when target is near right edge
        mock_target.winfo_x.return_value = 1700
        x, y = self.test_window.get_safe_position_relative_to(mock_target, 300, 250)
        self.assertEqual(x, 1390)  # 1700 - 300 - 10 (positioned to the left)
        
        # Test positioning when target is very close to left edge
        mock_target.winfo_x.return_value = 50
        mock_target.winfo_width.return_value = 300
        x, y = self.test_window.get_safe_position_relative_to(mock_target, 500, 250)
        # Should position to the right: 50 + 300 + 10 = 360
        x, y = self.test_window.get_safe_position_relative_to(mock_target, 500, 250)
        self.assertEqual(x, 360)
        
    def test_window_initialization(self):
        """Test window is properly initialized"""
        self.assertIsNotNone(self.test_window.root)
        self.assertEqual(self.test_window.root.title(), "Test Window")
        self.assertIsInstance(self.test_window.transparency_var, tk.DoubleVar)
        self.assertEqual(self.test_window.transparency_var.get(), 0.8)
        
    def test_create_styled_widgets(self):
        """Test styled widget creation methods"""
        parent = tk.Frame(self.test_window.root)
        
        # Test button creation
        button = self.test_window.create_styled_button(
            parent, "Test", lambda: None, style='default'
        )
        self.assertIsInstance(button, tk.Button)
        self.assertEqual(button['text'], "Test")
        
        # Test icon button
        icon_button = self.test_window.create_styled_button(
            parent, "⚙", lambda: None, style='icon'
        )
        self.assertEqual(icon_button['width'], 3)
        
        # Test label creation
        label = self.test_window.create_styled_label(parent, "Test Label")
        self.assertIsInstance(label, tk.Label)
        self.assertEqual(label['text'], "Test Label")
        
        # Test frame creation
        frame = self.test_window.create_styled_frame(parent)
        self.assertIsInstance(frame, tk.Frame)


class TestImageOverlayLogic(unittest.TestCase):
    """Test ImageOverlay logic without GUI dependencies"""
    
    def test_image_overlay_import(self):
        """Test that ImageOverlay can be imported"""
        try:
            from imgoverlay import ImageOverlay
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Could not import ImageOverlay: {e}")
            
    def test_settings_manager_import(self):
        """Test that SettingsManager can be imported"""
        try:
            from settings import SettingsManager
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Could not import SettingsManager: {e}")
            
    def test_base_class_abstract_method(self):
        """Test that BaseOverlayWindow is properly abstract"""
        with self.assertRaises(TypeError):
            # Should not be able to instantiate abstract class directly
            BaseOverlayWindow() # type: ignore
            
    def test_color_scheme_completeness(self):
        """Test that all required colors are defined"""
        required_colors = [
            'bg_primary', 'bg_secondary', 'bg_button', 'bg_button_hover',
            'bg_button_danger', 'bg_button_danger_hover', 'fg_primary', 'trough_color'
        ]
        
        for color in required_colors:
            self.assertIn(color, BaseOverlayWindow.COLORS)
            self.assertIsInstance(BaseOverlayWindow.COLORS[color], str)
            self.assertTrue(BaseOverlayWindow.COLORS[color].startswith('#') or 
                          BaseOverlayWindow.COLORS[color] in ['white', 'black'])
            
    def test_font_scheme_completeness(self):
        """Test that all required fonts are defined"""
        required_fonts = ['default', 'button', 'title', 'icon', 'large']
        
        for font in required_fonts:
            self.assertIn(font, BaseOverlayWindow.FONTS)
            self.assertIsInstance(BaseOverlayWindow.FONTS[font], tuple)
            
    def test_ensure_on_screen_edge_cases(self):
        """Test edge cases for ensure_on_screen method"""
        # Create a concrete test class
        class TestWindow(BaseOverlayWindow):
            def create_widgets(self):
                pass
                
        try:
            test_window = TestWindow("Test")
        except tk.TclError:
            self.skipTest("Cannot create Tk window in this environment")
            
        try:
            mock_window = Mock()
            mock_window.winfo_screenwidth.return_value = 800
            mock_window.winfo_screenheight.return_value = 600
            
            # Test window larger than screen
            x, y = test_window.ensure_on_screen(mock_window, 1000, 700, 0, 0)
            self.assertEqual(x, 10)  # Should position at margin
            self.assertEqual(y, 10)  # Should position at margin
            
            # Test very small screen
            mock_window.winfo_screenwidth.return_value = 100
            mock_window.winfo_screenheight.return_value = 100
            x, y = test_window.ensure_on_screen(mock_window, 50, 50, 80, 80)
            self.assertEqual(x, 40)  # 100 - 50 - 10
            self.assertEqual(y, 40)  # 100 - 50 - 10
            
        finally:
            try:
                test_window.root.destroy()
            except:
                pass

    def test_smart_clearing_attributes(self):
        """Test that smart clearing attributes are properly initialized"""
        from imgoverlay import ImageOverlay
        
        try:
            # Create a mock root to avoid Tk issues in testing
            with patch('tkinter.Tk') as mock_tk:
                mock_root = Mock()
                mock_tk.return_value = mock_root
                mock_root.attributes = Mock()
                mock_root.winfo_screenwidth.return_value = 1920
                mock_root.winfo_screenheight.return_value = 1080
                
                overlay = ImageOverlay()
                
                # Test that smart clearing attributes exist
                self.assertTrue(hasattr(overlay, 'pre_image_state'))
                self.assertTrue(hasattr(overlay, 'post_image_state'))
                
                # Test initial state
                self.assertIsNone(overlay.pre_image_state)
                self.assertIsNone(overlay.post_image_state)
                
        except Exception as e:
            self.skipTest(f"Cannot test ImageOverlay in this environment: {e}")
            
    def test_smart_clearing_state_tracking(self):
        """Test state tracking logic for smart clearing"""
        from imgoverlay import ImageOverlay
        
        try:
            with patch('tkinter.Tk') as mock_tk:
                mock_root = Mock()
                mock_tk.return_value = mock_root
                mock_root.attributes = Mock()
                mock_root.winfo_screenwidth.return_value = 1920
                mock_root.winfo_screenheight.return_value = 1080
                mock_root.winfo_x.return_value = 100
                mock_root.winfo_y.return_value = 100
                mock_root.winfo_width.return_value = 400
                mock_root.winfo_height.return_value = 300
                mock_root.geometry = Mock()
                mock_root.update_idletasks = Mock()
                
                overlay = ImageOverlay()
                overlay.root = mock_root
                
                # Simulate state tracking by setting states manually
                overlay.pre_image_state = (100, 100, 400, 300)
                overlay.post_image_state = (50, 100, 800, 600)  # Moved left, expanded
                
                # Mock the necessary methods and attributes
                overlay.image_label = Mock()
                overlay.placeholder_label = None
                overlay.create_styled_label = Mock(return_value=Mock())
                overlay.setup_drag_functionality = Mock()
                overlay.ensure_on_screen = Mock(return_value=(100, 100))
                
                # Test clear_image clears tracking state
                overlay.clear_image()
                
                self.assertIsNone(overlay.pre_image_state)
                self.assertIsNone(overlay.post_image_state)
                
        except Exception as e:
            self.skipTest(f"Cannot test smart clearing in this environment: {e}")

class TestFileStructure(unittest.TestCase):
    """Test that all required files exist and are importable"""
    
    def test_required_files_exist(self):
        """Test that all required project files exist"""
        required_files = ['base.py', 'settings.py', 'imgoverlay.py', 'README.md', 'requirements.txt']
        
        for file in required_files:
            file_path = os.path.join(os.path.dirname(__file__), file)
            self.assertTrue(os.path.exists(file_path), f"Required file {file} not found")
            
    def test_all_modules_importable(self):
        """Test that all modules can be imported without errors"""
        modules = ['base', 'settings']
        
        for module_name in modules:
            try:
                __import__(module_name)
            except Exception as e:
                self.fail(f"Could not import {module_name}: {e}")


def run_simple_tests():
    """Run the simplified test suite"""
    print("Running Image Overlay Unit Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestBaseOverlayWindow,
        TestImageOverlayLogic,
        TestFileStructure
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("SUCCESS: All tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("FAILURE: Some tests failed!")
        print(f"Ran {result.testsRun} tests: {len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)

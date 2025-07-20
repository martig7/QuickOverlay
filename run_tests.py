#!/usr/bin/env python3
"""
Test runner for the Image Overlay application.
Provides multiple testing options and comprehensive coverage reporting.
"""

import unittest
import sys
import os
import time
from typing import Dict, List, Tuple

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_basic_tests() -> bool:
    """Run basic functionality tests"""
    print("🧪 Running Basic Functionality Tests")
    print("-" * 40)
    
    from test_overlay_simple import run_simple_tests
    return run_simple_tests()


def run_manual_tests() -> bool:
    """Run manual integration tests"""
    print("🔧 Running Manual Integration Tests")
    print("-" * 40)
    
    try:
        # Test basic imports
        print("✓ Testing imports...")
        from base import BaseOverlayWindow
        from settings import SettingsManager
        from imgoverlay import ImageOverlay
        
        # Test color scheme
        print("✓ Testing color scheme...")
        colors = BaseOverlayWindow.COLORS
        assert len(colors) >= 8, "Insufficient color definitions"
        
        # Test font scheme
        print("✓ Testing font scheme...")
        fonts = BaseOverlayWindow.FONTS
        assert len(fonts) >= 5, "Insufficient font definitions"
        
        # Test off-screen logic
        print("✓ Testing off-screen prevention...")
        class TestWindow(BaseOverlayWindow):
            def create_widgets(self):
                pass
        
        test_window = TestWindow("Test")
        
        # Mock window for testing with all required methods
        class MockWindow:
            def __init__(self, x=0, y=0, width=400, height=300):
                self.x = x
                self.y = y
                self.width = width
                self.height = height
                self.geometry_calls = []
                
            def winfo_screenwidth(self): return 1920
            def winfo_screenheight(self): return 1080
            def winfo_x(self): return self.x
            def winfo_y(self): return self.y
            def winfo_width(self): return self.width
            def winfo_height(self): return self.height
            def overrideredirect(self): return False  # Decorated window
            def winfo_vrootwidth(self): return 1920
            def winfo_vrootheight(self): return 1080
            def winfo_vrootx(self): return 0
            def winfo_vrooty(self): return 0
            def geometry(self, geom_str):
                self.geometry_calls.append(geom_str)
                # Extract position from geometry string for verification
                if geom_str.startswith('+'):
                    parts = geom_str[1:].split('+')
                    self.x, self.y = int(parts[0]), int(parts[1])
        
        # Test edge cases
        mock_win = MockWindow(-100, -100, 400, 300)
        x, y = test_window.ensure_on_screen(mock_win)
        assert mock_win.x >= 10 and mock_win.y >= 10, "Failed to handle negative coordinates"
        
        mock_win = MockWindow(2000, 2000, 400, 300)
        x, y = test_window.ensure_on_screen(mock_win)
        assert mock_win.x <= 1510 and mock_win.y <= 770, "Failed to handle off-screen coordinates"
        
        test_window.root.destroy()
        
        print("SUCCESS: Manual integration tests passed!")
        return True
        
    except Exception as e:
        print(f"FAILED: Manual test failed: {e}")
        return False


def run_file_structure_tests() -> bool:
    """Test file structure and dependencies"""
    print("📁 Running File Structure Tests")
    print("-" * 40)
    
    try:
        required_files = {
            'base.py': 'Base overlay window class',
            'settings.py': 'Settings manager class',
            'imgoverlay.py': 'Main image overlay application',
            'README.md': 'Project documentation',
            'requirements.txt': 'Project dependencies',
            'requirements-dev.txt': 'Development dependencies'
        }
        
        missing_files = []
        for file, description in required_files.items():
            if os.path.exists(file):
                print(f"✓ {file} - {description}")
            else:
                print(f"MISSING: {file} - {description} (MISSING)")
                missing_files.append(file)
        
        if missing_files:
            print(f"\nMISSING FILES: {', '.join(missing_files)}")
            return False
        
        # Test file sizes (basic sanity check)
        for file in required_files.keys():
            if file.endswith('.py'):
                size = os.path.getsize(file)
                if size < 100:  # Very small files might be incomplete
                    print(f"WARNING: {file} seems unusually small ({size} bytes)")
                else:
                    print(f"✓ {file} size: {size} bytes")
        
        print("SUCCESS: File structure tests passed!")
        return True
        
    except Exception as e:
        print(f"FAILED: File structure test failed: {e}")
        return False


def run_performance_tests() -> bool:
    """Run basic performance tests"""
    print("⚡ Running Performance Tests")
    print("-" * 40)
    
    try:
        from base import BaseOverlayWindow
        
        class TestWindow(BaseOverlayWindow):
            def create_widgets(self):
                pass
        
        # Test window creation time
        start_time = time.time()
        test_window = TestWindow("Performance Test")
        creation_time = time.time() - start_time
        
        print(f"✓ Window creation time: {creation_time:.3f}s")
        
        if creation_time > 2.0:
            print("WARNING: Window creation seems slow")
        
        # Test off-screen calculation performance
        class MockWindow:
            def __init__(self, x=0, y=0, width=400, height=300):
                self.x = x
                self.y = y
                self.width = width
                self.height = height
                self.geometry_calls = []
                
            def winfo_screenwidth(self): return 1920
            def winfo_screenheight(self): return 1080
            def winfo_x(self): return self.x
            def winfo_y(self): return self.y
            def winfo_width(self): return self.width
            def winfo_height(self): return self.height
            def overrideredirect(self): return False  # Decorated window
            def winfo_vrootwidth(self): return 1920
            def winfo_vrootheight(self): return 1080
            def winfo_vrootx(self): return 0
            def winfo_vrooty(self): return 0
            def geometry(self, geom_str):
                self.geometry_calls.append(geom_str)
                if geom_str.startswith('+'):
                    parts = geom_str[1:].split('+')
                    self.x, self.y = int(parts[0]), int(parts[1])
        
        start_time = time.time()
        mock_win = MockWindow(100, 100, 400, 300)
        for _ in range(1000):
            test_window.ensure_on_screen(mock_win)
        calc_time = time.time() - start_time
        
        print(f"✓ 1000 off-screen calculations: {calc_time:.3f}s")
        
        if calc_time > 0.1:
            print("WARNING: Off-screen calculations seem slow")
        
        test_window.root.destroy()
        
        print("SUCCESS: Performance tests completed!")
        return True
        
    except Exception as e:
        print(f"FAILED: Performance test failed: {e}")
        return False


def generate_test_report(results: Dict[str, bool]) -> None:
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 TEST REPORT")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 60)
    
    if all(results.values()):
        print("🎉 ALL TESTS PASSED! The overlay application is ready to use.")
    else:
        print("WARNING: Some tests failed. Please review the issues above.")
        
    print("=" * 60)


def main():
    """Main test runner"""
    print("🚀 Image Overlay Test Suite")
    print("=" * 60)
    print("Testing the refactored image overlay application components")
    print("=" * 60)
    
    test_results = {}
    
    # Run all test suites
    test_suites = [
        ("Basic Functionality", run_basic_tests),
        ("Manual Integration", run_manual_tests),
        ("File Structure", run_file_structure_tests),
        ("Performance", run_performance_tests)
    ]
    
    for suite_name, test_function in test_suites:
        print(f"\n🔍 Running {suite_name} Tests...")
        try:
            result = test_function()
            test_results[suite_name] = result
        except Exception as e:
            print(f"CRASHED: {suite_name} tests crashed: {e}")
            test_results[suite_name] = False
        
        print()  # Add spacing between test suites
    
    # Generate comprehensive report
    generate_test_report(test_results)
    
    # Return overall success
    return all(test_results.values())


if __name__ == "__main__":
    success = main()
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Build script for the Image Overlay application.
Tests, lints, and packages the project for distribution.

Usage:
    python build.py              # Full build with all checks
    python build.py --fast       # Skip slow tests
    python build.py --no-lint    # Skip linting
    python build.py --clean      # Clean build directory first
"""

import os
import sys
import shutil
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class BuildConfig:
    """Build configuration and settings"""
    
    # Project structure
    PROJECT_NAME = "Image Overlay"
    VERSION = "1.0.0"
    
    # Build directories
    BUILD_DIR = Path("build")
    DIST_DIR = BUILD_DIR / "dist"
    REPORTS_DIR = BUILD_DIR / "reports"
    TEMP_DIR = BUILD_DIR / "temp"
    EXE_DIR = BUILD_DIR / "executable"
    PYINSTALLER_DIR = BUILD_DIR / "pyinstaller_temp"
    
    # Core project files to include in distribution
    CORE_FILES = [
        "base.py",
        "settings.py", 
        "imgoverlay.py",
        "requirements.txt",
        "README.md"
    ]
    
    # Additional files to include
    OPTIONAL_FILES = [
        "requirements-dev.txt",
        "test_overlay_simple.py",
        "run_tests.py"
    ]
    
    # Files to exclude from distribution
    EXCLUDE_PATTERNS = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git*",
        "build",
        "dist",
        ".pytest_cache",
        "*.egg-info"
    ]


class BuildLogger:
    """Handles formatted output and logging"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.step_count = 0
        
    def header(self, message: str):
        """Print a header message"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD} {message}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
        
    def step(self, message: str):
        """Print a build step"""
        self.step_count += 1
        print(f"\n{Colors.BLUE}{Colors.BOLD}[{self.step_count}] {message}{Colors.END}")
        
    def success(self, message: str):
        """Print a success message"""
        print(f"{Colors.GREEN}[SUCCESS] {message}{Colors.END}")
        
    def warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.YELLOW}[WARNING] {message}{Colors.END}")
        
    def error(self, message: str):
        """Print an error message"""
        print(f"{Colors.RED}[ERROR] {message}{Colors.END}")
        
    def info(self, message: str):
        """Print an info message"""
        if self.verbose:
            print(f"{Colors.WHITE}   {message}{Colors.END}")


class ProjectBuilder:
    """Main build orchestrator"""
    
    def __init__(self, args):
        self.args = args
        self.logger = BuildLogger(verbose=not args.quiet)
        self.config = BuildConfig()
        self.build_start_time = time.time()
        
    def run(self) -> bool:
        """Execute the full build process"""
        try:
            self.logger.header(f"Building {self.config.PROJECT_NAME} v{self.config.VERSION}")
            
            # Setup build environment
            if not self._setup_build_environment():
                return False
                
            # Run build steps
            build_steps = [
                ("Clean previous builds", self._clean_build_dir),
                ("Validate project structure", self._validate_project_structure),
                ("Run unit tests", self._run_tests),
                ("Check code quality", self._run_linting),
                ("Build executable", self._build_executable),
                ("Generate build report", self._generate_build_report)
            ]
            
            # Add Python distribution step only if requested
            if self.args.include_python_dist:
                build_steps.insert(-1, ("Create Python distribution", self._create_distribution))
                build_steps.insert(-1, ("Validate distribution", self._validate_distribution))
            
            for step_name, step_function in build_steps:
                if not self._execute_step(step_name, step_function):
                    return False
                    
            # Build complete
            build_time = time.time() - self.build_start_time
            self.logger.success(f"Build completed successfully in {build_time:.2f}s")
            self.logger.info(f"Distribution available in: {self.config.DIST_DIR}")
            
            return True
            
        except KeyboardInterrupt:
            self.logger.error("Build interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"Build failed with unexpected error: {e}")
            return False
            
    def _execute_step(self, name: str, function) -> bool:
        """Execute a build step with error handling"""
        self.logger.step(name)
        try:
            if function():
                self.logger.success(f"[OK] {name}")
                return True
            else:
                self.logger.error(f"[FAIL] {name} failed")
                return False
        except Exception as e:
            self.logger.error(f"[FAIL] {name} failed: {e}")
            return False
            
    def _setup_build_environment(self) -> bool:
        """Setup build directories and environment"""
        try:
            # Create build directories
            for directory in [self.config.BUILD_DIR, self.config.DIST_DIR, 
                            self.config.REPORTS_DIR, self.config.TEMP_DIR,
                            self.config.EXE_DIR, self.config.PYINSTALLER_DIR]:
                directory.mkdir(parents=True, exist_ok=True)
                
            self.logger.info("Build directories created")
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup build environment: {e}")
            return False
            
    def _clean_build_dir(self) -> bool:
        """Clean previous build artifacts"""
        try:
            if self.args.clean and self.config.BUILD_DIR.exists():
                shutil.rmtree(self.config.BUILD_DIR)
                self.logger.info("Previous build directory removed")
                
            # Recreate directories
            return self._setup_build_environment()
        except Exception as e:
            self.logger.error(f"Failed to clean build directory: {e}")
            return False
            
    def _validate_project_structure(self) -> bool:
        """Validate that all required files exist"""
        missing_files = []
        
        for file in self.config.CORE_FILES:
            if not Path(file).exists():
                missing_files.append(file)
                
        if missing_files:
            self.logger.error(f"Missing required files: {', '.join(missing_files)}")
            return False
            
        self.logger.info(f"All {len(self.config.CORE_FILES)} core files found")
        return True
        
    def _run_tests(self) -> bool:
        """Run the test suite"""
        if self.args.no_tests:
            self.logger.warning("Tests skipped (--no-tests)")
            return True
            
        try:
            # Run the test suite
            test_command = [sys.executable, "test_overlay_simple.py"]
            result = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                timeout=60 if self.args.fast else 300
            )
            
            # Save test output
            test_report = self.config.REPORTS_DIR / "test_results.txt"
            with open(test_report, 'w') as f:
                f.write(f"Test Command: {' '.join(test_command)}\n")
                f.write(f"Return Code: {result.returncode}\n\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
                
            if result.returncode == 0:
                self.logger.info("All tests passed")
                return True
            else:
                self.logger.error(f"Tests failed (exit code: {result.returncode})")
                self.logger.info(f"Test report saved to: {test_report}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Tests timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to run tests: {e}")
            return False
            
    def _run_linting(self) -> bool:
        """Run code quality checks"""
        if self.args.no_lint:
            self.logger.warning("Linting skipped (--no-lint)")
            return True
            
        lint_results = {}
        
        # Check if linting tools are available
        linting_tools = [
            ("flake8", ["flake8", "--max-line-length=100", "."]),
            ("basic syntax", [sys.executable, "-m", "py_compile"])
        ]
        
        for tool_name, command in linting_tools:
            try:
                if tool_name == "basic syntax":
                    # Check syntax of all Python files
                    for file in self.config.CORE_FILES:
                        if file.endswith('.py'):
                            syntax_result = subprocess.run(
                                command + [file],
                                capture_output=True,
                                text=True
                            )
                            if syntax_result.returncode != 0:
                                lint_results[f"syntax_{file}"] = False
                                self.logger.error(f"Syntax error in {file}")
                            else:
                                lint_results[f"syntax_{file}"] = True
                else:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True
                    )
                    lint_results[tool_name] = result.returncode == 0
                    
                    # Save linting output
                    lint_report = self.config.REPORTS_DIR / f"{tool_name.replace(' ', '_')}_report.txt"
                    with open(lint_report, 'w') as f:
                        f.write(f"Command: {' '.join(command)}\n")
                        f.write(f"Return Code: {result.returncode}\n\n")
                        f.write("STDOUT:\n")
                        f.write(result.stdout)
                        f.write("\nSTDERR:\n")
                        f.write(result.stderr)
                        
            except FileNotFoundError:
                self.logger.warning(f"{tool_name} not available, skipping")
                lint_results[tool_name] = None
            except Exception as e:
                self.logger.error(f"Error running {tool_name}: {e}")
                lint_results[tool_name] = False
                
        # Evaluate results
        failed_checks = [name for name, result in lint_results.items() if result is False]
        passed_checks = [name for name, result in lint_results.items() if result is True]
        skipped_checks = [name for name, result in lint_results.items() if result is None]
        
        if failed_checks:
            self.logger.error(f"Linting failed: {', '.join(failed_checks)}")
            return False
            
        self.logger.info(f"Linting passed: {len(passed_checks)} checks")
        if skipped_checks:
            self.logger.info(f"Skipped: {', '.join(skipped_checks)}")
            
        return True
        
    def _create_distribution(self) -> bool:
        """Create distribution package"""
        try:
            # Copy core files
            for file in self.config.CORE_FILES:
                source = Path(file)
                destination = self.config.DIST_DIR / file
                if source.exists():
                    shutil.copy2(source, destination)
                    self.logger.info(f"Copied {file}")
                    
            # Copy optional files if they exist
            for file in self.config.OPTIONAL_FILES:
                source = Path(file)
                destination = self.config.DIST_DIR / file
                if source.exists():
                    shutil.copy2(source, destination)
                    self.logger.info(f"Copied optional file {file}")
                    
            # Create version info
            version_info = self.config.DIST_DIR / "VERSION"
            with open(version_info, 'w') as f:
                f.write(f"{self.config.VERSION}\n")
                f.write(f"Built: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            # Create startup script
            startup_script = self.config.DIST_DIR / "start.py"
            with open(startup_script, 'w') as f:
                f.write('#!/usr/bin/env python3\n')
                f.write('"""Startup script for Image Overlay application"""\n\n')
                f.write('import sys\n')
                f.write('import os\n\n')
                f.write('# Add current directory to path\n')
                f.write('sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n\n')
                f.write('# Import and run the application\n')
                f.write('from imgoverlay import main\n\n')
                f.write('if __name__ == "__main__":\n')
                f.write('    main()\n')
                
            # Make startup script executable on Unix-like systems
            if os.name != 'nt':
                os.chmod(startup_script, 0o755)
                
            self.logger.info(f"Distribution created with {len(os.listdir(self.config.DIST_DIR))} files")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create distribution: {e}")
            return False
            
    def _validate_distribution(self) -> bool:
        """Validate the created distribution"""
        try:
            # Check that all core files exist in distribution
            missing_files = []
            for file in self.config.CORE_FILES:
                if not (self.config.DIST_DIR / file).exists():
                    missing_files.append(file)
                    
            if missing_files:
                self.logger.error(f"Missing files in distribution: {', '.join(missing_files)}")
                return False
                
            # Try to import the main module from distribution
            old_path = sys.path[:]
            try:
                sys.path.insert(0, str(self.config.DIST_DIR))
                import imgoverlay
                self.logger.info("Distribution import test passed")
            except ImportError as e:
                self.logger.error(f"Distribution import test failed: {e}")
                return False
            finally:
                sys.path = old_path
                
            return True
            
        except Exception as e:
            self.logger.error(f"Distribution validation failed: {e}")
            return False
            
    def _build_executable(self) -> bool:
        """Build standalone executable using PyInstaller"""
        if self.args.no_exe:
            self.logger.warning("Executable build skipped (--no-exe)")
            return True
            
        try:
            # Check if PyInstaller is available
            try:
                import PyInstaller
                self.logger.info(f"Using PyInstaller {PyInstaller.__version__}")
            except ImportError:
                self.logger.warning("PyInstaller not available, skipping executable build")
                return True
                
            # Prepare PyInstaller command
            main_script = "imgoverlay.py"
            app_name = "ImageOverlay"
            
            pyinstaller_cmd = [
                sys.executable, "-m", "PyInstaller",
                "--name", app_name,
                "--onefile",
                "--windowed",
                "--distpath", str(self.config.EXE_DIR),
                "--workpath", str(self.config.PYINSTALLER_DIR),
                "--specpath", str(self.config.PYINSTALLER_DIR),
                "--hidden-import", "PIL._tkinter_finder",
                "--collect-all", "tkinter",
                main_script
            ]
            
            self.logger.info("Building executable with PyInstaller...")
            self.logger.info(f"Command: {' '.join(pyinstaller_cmd)}")
            
            # Run PyInstaller
            result = subprocess.run(
                pyinstaller_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Save PyInstaller output
            pyinstaller_report = self.config.REPORTS_DIR / "pyinstaller_log.txt"
            with open(pyinstaller_report, 'w') as f:
                f.write(f"PyInstaller Command: {' '.join(pyinstaller_cmd)}\n")
                f.write(f"Return Code: {result.returncode}\n\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
            
            if result.returncode == 0:
                # Check if executable was created
                exe_name = f"{app_name}.exe" if os.name == 'nt' else app_name
                exe_path = self.config.EXE_DIR / exe_name
                
                if exe_path.exists():
                    exe_size = exe_path.stat().st_size
                    self.logger.info(f"Executable created: {exe_path} ({exe_size:,} bytes)")
                    
                    # Copy README to executable directory
                    readme_dest = self.config.EXE_DIR / "README.md"
                    if Path("README.md").exists():
                        shutil.copy2("README.md", readme_dest)
                        
                    return True
                else:
                    self.logger.error("Executable was not created")
                    return False
            else:
                self.logger.error(f"PyInstaller failed (exit code: {result.returncode})")
                self.logger.info(f"PyInstaller log saved to: {pyinstaller_report}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("PyInstaller build timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to build executable: {e}")
            return False
            
    def _generate_build_report(self) -> bool:
        """Generate comprehensive build report"""
        try:
            report_file = self.config.REPORTS_DIR / "build_report.md"
            
            with open(report_file, 'w') as f:
                f.write(f"# Build Report - {self.config.PROJECT_NAME}\n\n")
                f.write(f"**Version:** {self.config.VERSION}\n")
                f.write(f"**Build Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Build Duration:** {time.time() - self.build_start_time:.2f}s\n\n")
                
                f.write("## Build Configuration\n\n")
                f.write(f"- Fast Mode: {self.args.fast}\n")
                f.write(f"- Skip Tests: {self.args.no_tests}\n")
                f.write(f"- Skip Linting: {self.args.no_lint}\n")
                f.write(f"- Skip Executable: {self.args.no_exe}\n")
                f.write(f"- Include Python Dist: {self.args.include_python_dist}\n")
                f.write(f"- Clean Build: {self.args.clean}\n\n")
                
                # Add Python distribution information if it exists
                dist_files = list(self.config.DIST_DIR.glob("*")) if self.config.DIST_DIR.exists() else []
                if dist_files:
                    f.write("## Python Distribution Contents\n\n")
                    for file in sorted(dist_files):
                        size = file.stat().st_size if file.is_file() else 0
                        f.write(f"- `{file.name}` ({size} bytes)\n")
                    f.write(f"\n**Total Files:** {len(dist_files)}\n")
                    f.write(f"**Distribution Size:** {sum(f.stat().st_size for f in dist_files if f.is_file())} bytes\n\n")
                
                # Add executable information if it exists
                exe_files = list(self.config.EXE_DIR.glob("*")) if self.config.EXE_DIR.exists() else []
                if exe_files:
                    f.write("## Standalone Executable\n\n")
                    for exe_file in sorted(exe_files):
                        if exe_file.is_file():
                            size = exe_file.stat().st_size
                            f.write(f"- `{exe_file.name}` ({size:,} bytes)\n")
                    f.write(f"\n**Executable Size:** {sum(f.stat().st_size for f in exe_files if f.is_file()):,} bytes\n\n")
                
                f.write("## Usage\n\n")
                
                if exe_files:
                    f.write("To run the standalone executable:\n\n")
                    f.write("```bash\n")
                    f.write("cd build/executable\n")
                    f.write("./ImageOverlay.exe  # Windows\n")
                    f.write("# or\n")
                    f.write("./ImageOverlay      # Linux/Mac\n")
                    f.write("```\n\n")
                
                if dist_files:
                    f.write("To run from the Python distribution:\n\n")
                    f.write("```bash\n")
                    f.write("cd build/dist\n")
                    f.write("python start.py\n")
                    f.write("# or\n")
                    f.write("python imgoverlay.py\n")
                    f.write("```\n\n")
                
                if not exe_files and not dist_files:
                    f.write("No distribution packages were created in this build.\n\n")
                
            self.logger.info(f"Build report generated: {report_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate build report: {e}")
            return False


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Build script for Image Overlay application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build standalone executable only
  python build.py --fast --no-lint  # Quick executable build
  python build.py --clean            # Clean build with executable
  python build.py --no-exe           # Build without executable (tests/lint only)
  python build.py --include-python-dist  # Build both executable and Python distribution
        """
    )
    
    parser.add_argument(
        "--fast", 
        action="store_true",
        help="Skip slow tests and checks"
    )
    
    parser.add_argument(
        "--no-tests",
        action="store_true", 
        help="Skip running tests"
    )
    
    parser.add_argument(
        "--no-lint",
        action="store_true",
        help="Skip code linting"
    )
    
    parser.add_argument(
        "--no-exe",
        action="store_true",
        help="Skip building executable with PyInstaller"
    )
    
    parser.add_argument(
        "--include-python-dist",
        action="store_true",
        help="Also create Python distribution package (in addition to executable)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directory before building"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    builder = ProjectBuilder(args)
    
    success = builder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

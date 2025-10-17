#!/usr/bin/env python3
"""
Setup Verification Script for Property SMS Sender
Tests all dependencies and provides environment setup information
"""

import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("PROPERTY SMS SENDER - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    # Python version
    print(f"Python Version: {sys.version}")
    print()
    
    # Test core dependencies
    print("🔍 Testing Core Dependencies...")
    dependencies = [
        ("pandas", "Data processing"),
        ("selenium", "Web automation"),
        ("gspread", "Google Sheets integration"),
        ("flask", "Web API server"),
        ("schedule", "Task scheduling"),
        ("requests", "HTTP requests"),
        ("psutil", "System monitoring"),
        ("pytesseract", "OCR functionality"),
    ]
    
    success_count = 0
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name:<15} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"  ✗ {module_name:<15} - FAILED: {e}")
    
    print()
    
    # Test GUI dependencies (with virtual display)
    print("🖥️  Testing GUI Dependencies...")
    gui_dependencies = [
        ("PIL", "Image processing"),
        ("pyautogui", "GUI automation (requires virtual display)"),
    ]
    
    for module_name, description in gui_dependencies:
        try:
            if module_name == "pyautogui":
                # Test with minimal functionality
                import pyautogui
                # Disable fail-safe for testing
                pyautogui.FAILSAFE = False
                print(f"  ✓ {module_name:<15} - {description}")
            else:
                __import__(module_name)
                print(f"  ✓ {module_name:<15} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"  ✗ {module_name:<15} - FAILED: {e}")
        except Exception as e:
            print(f"  ⚠ {module_name:<15} - WARNING: {e}")
    
    print()
    
    # Test system tools
    print("🛠️  Testing System Tools...")
    import subprocess
    
    system_tools = [
        ("tesseract", "OCR engine"),
        ("chromium-browser", "Web browser"),
        ("xvfb-run", "Virtual display"),
    ]
    
    for tool, description in system_tools:
        try:
            result = subprocess.run([tool, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"  ✓ {tool:<15} - {description}")
                success_count += 1
            else:
                print(f"  ✗ {tool:<15} - Not working properly")
        except subprocess.TimeoutExpired:
            print(f"  ⚠ {tool:<15} - Timeout (may still work)")
        except FileNotFoundError:
            print(f"  ✗ {tool:<15} - Not installed")
        except Exception as e:
            print(f"  ⚠ {tool:<15} - WARNING: {e}")
    
    print()
    
    # Project structure
    print("📁 Project Structure:")
    project_root = Path(__file__).parent
    key_dirs = [
        "whatsapp-agent",
        "sms-agent", 
        "master-agent",
        "google-sheets-agent",
        "dashboard",
        "venv"
    ]
    
    for dir_name in key_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}")
        else:
            print(f"  ✗ {dir_name} - Missing")
    
    print()
    
    # Configuration
    print("⚙️  Configuration:")
    env_file = project_root / ".env"
    if env_file.exists():
        print("  ✓ .env file exists")
        # Check for required environment variables
        with open(env_file, 'r') as f:
            content = f.read()
            required_vars = ["GEMINI_API_KEY", "WHATSAPP_PHONE_NUMBER"]
            for var in required_vars:
                if var in content:
                    print(f"    ✓ {var} configured")
                else:
                    print(f"    ⚠ {var} not found in .env")
    else:
        print("  ⚠ .env file not found")
        print("    Create .env file with:")
        print("    - GEMINI_API_KEY=your_api_key")
        print("    - WHATSAPP_PHONE_NUMBER=your_number")
    
    print()
    
    # Usage instructions
    print("🚀 Next Steps:")
    print("  1. Create .env file with required API keys")
    print("  2. Run master agent: cd master-agent && python master_agent.py")
    print("  3. Open dashboard: Open dashboard/index.html in browser")
    print("  4. For headless GUI operations, use: DISPLAY=:99 xvfb-run -a python script.py")
    
    print()
    print("=" * 60)
    total_tests = len(dependencies) + len(gui_dependencies) + len(system_tools)
    print(f"Setup Verification Complete: {success_count}/{total_tests} components verified")
    print("=" * 60)

if __name__ == "__main__":
    main()
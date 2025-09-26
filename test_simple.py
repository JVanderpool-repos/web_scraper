"""
Simple Environment Test Script

A simplified test to verify the virtual environment setup without
complex imports that might have circular dependencies.
"""

import sys
import os

def test_environment():
    print("🚀 Web Scraper Environment Verification")
    print("=" * 45)
    print()
    
    # Test 1: Python Environment
    print("🐍 Python Environment:")
    print(f"   Version: {sys.version.split()[0]}")
    print(f"   Executable: {sys.executable}")
    venv_active = 'venv' in sys.executable or 'VIRTUAL_ENV' in os.environ
    print(f"   Virtual Environment: {'✅ Active' if venv_active else '❌ Not Active'}")
    print()
    
    # Test 2: Core Package Imports
    print("📦 Core Package Availability:")
    
    packages = [
        "requests", "bs4", "pandas", "yaml", 
        "dotenv", "fake_useragent", "selenium", 
        "lxml", "aiohttp", "tqdm", "psutil"
    ]
    
    available = []
    missing = []
    
    for package in packages:
        try:
            __import__(package)
            available.append(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package}")
    
    print(f"\n   📊 Available: {len(available)}/{len(packages)} packages")
    
    # Test 3: Project Structure
    print("\n📁 Project Structure:")
    
    required_files = [
        "src/scraper.py", "src/utils.py", "src/storage.py", "src/__init__.py",
        "config/scraper_config.yaml", "config/headers.yaml",
        "examples/basic_scraper.py", "requirements.txt", ".env.example"
    ]
    
    present = []
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            present.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path}")
    
    print(f"\n   📊 Present: {len(present)}/{len(required_files)} files")
    
    # Test 4: Basic HTTP Test
    print("\n🌐 Basic HTTP Test:")
    
    try:
        import requests
        response = requests.get("https://httpbin.org/json", timeout=10)
        if response.status_code == 200:
            print("   ✅ HTTP requests working")
            print(f"   📊 Response: {response.status_code}")
        else:
            print(f"   ⚠️  HTTP request returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ HTTP test failed: {str(e)}")
    
    # Final Summary
    print("\n" + "=" * 45)
    print("📋 Summary:")
    
    if venv_active:
        print("   ✅ Virtual environment is active")
    else:
        print("   ❌ Virtual environment not active")
        print("      Run: .\\venv\\Scripts\\Activate.ps1 (Windows)")
        print("      Run: source venv/bin/activate (Linux/Mac)")
    
    if len(available) == len(packages):
        print("   ✅ All required packages available")
    else:
        print(f"   ⚠️  {len(missing)} packages missing")
        print("      Run: pip install -r requirements.txt")
    
    if len(present) == len(required_files):
        print("   ✅ All project files present")
    else:
        print(f"   ⚠️  {len(missing_files)} files missing")
    
    print("\n🎯 Next Steps:")
    if venv_active and len(available) == len(packages) and len(present) == len(required_files):
        print("   🎉 Environment ready! Try running:")
        print("      python examples/basic_scraper.py")
    else:
        print("   🔧 Fix the issues above and run this test again")
    
    print("\n💡 Quick Commands:")
    print("   Activate venv:  .\\activate.ps1 (Windows) or source activate.sh (Linux/Mac)")
    print("   Install deps:   pip install -r requirements.txt")
    print("   Test example:   python examples/basic_scraper.py")

if __name__ == "__main__":
    test_environment()
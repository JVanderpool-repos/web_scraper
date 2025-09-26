"""
Environment Test Script

This script verifies that the virtual environment is properly set up
and all core dependencies are available.
"""

import sys
import os
from pathlib import Path

def test_python_environment():
    """Test basic Python environment"""
    print("🐍 Python Environment Test")
    print("-" * 30)
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Virtual Environment: {'Yes' if 'venv' in sys.executable else 'No'}")
    print()

def test_core_imports():
    """Test core package imports"""
    print("📦 Testing Core Package Imports")
    print("-" * 35)
    
    packages_to_test = [
        ("requests", "HTTP requests"),
        ("bs4", "BeautifulSoup4 - HTML parsing"),
        ("pandas", "Data manipulation"),
        ("yaml", "YAML configuration"),
        ("dotenv", "Environment variables"),
        ("fake_useragent", "User agent generation"),
    ]
    
    success_count = 0
    
    for package, description in packages_to_test:
        try:
            __import__(package)
            print(f"✅ {package:<15} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package:<15} - {description} (Error: {str(e)})")
    
    print(f"\n📊 Results: {success_count}/{len(packages_to_test)} packages imported successfully")
    return success_count == len(packages_to_test)

def test_project_structure():
    """Test project structure"""
    print("\n📁 Testing Project Structure")
    print("-" * 30)
    
    required_paths = [
        ("src", "Core framework directory"),
        ("src/scraper.py", "Main scraper module"),
        ("src/utils.py", "Utilities module"),
        ("config", "Configuration directory"),
        ("config/scraper_config.yaml", "Main configuration file"),
        ("examples", "Examples directory"),
        ("data", "Data output directory"),
        ("logs", "Logs directory"),
        ("requirements.txt", "Requirements file"),
        (".env.example", "Environment template"),
    ]
    
    success_count = 0
    
    for path, description in required_paths:
        if os.path.exists(path):
            print(f"✅ {path:<25} - {description}")
            success_count += 1
        else:
            print(f"❌ {path:<25} - {description} (Missing)")
    
    print(f"\n📊 Results: {success_count}/{len(required_paths)} required paths found")
    return success_count == len(required_paths)

def test_basic_scraper_functionality():
    """Test basic scraper functionality"""
    print("\n🕷️ Testing Basic Scraper Functionality")
    print("-" * 40)
    
    try:
        # Import our scraper
        import sys
        import os
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        from scraper import WebScraper
        
        print("✅ WebScraper class imported successfully")
        
        # Create scraper instance
        scraper = WebScraper(delay=0.1, timeout=5)
        print("✅ WebScraper instance created successfully")
        
        # Test with a simple, safe URL
        test_url = "https://httpbin.org/html"
        print(f"🌐 Testing scraping with: {test_url}")
        
        try:
            result = scraper.scrape_url(test_url)
            if result.success:
                print("✅ Basic scraping test successful")
                print(f"   - Status Code: {result.status_code}")
                print(f"   - Data extracted: {len(str(result.data))} characters")
                return True
            else:
                print(f"❌ Scraping failed: {result.error_message}")
                return False
        except Exception as e:
            print(f"❌ Scraping error: {str(e)}")
            return False
        
        finally:
            scraper.close()
    
    except ImportError as e:
        print(f"❌ Failed to import WebScraper: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Run all environment tests"""
    print("🚀 Web Scraper Environment Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        ("Python Environment", test_python_environment),
        ("Core Imports", test_core_imports),
        ("Project Structure", test_project_structure),
        ("Basic Functionality", test_basic_scraper_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "Python Environment":
                test_func()  # This one doesn't return a boolean
                results.append(True)
            else:
                result = test_func()
                results.append(result)
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {str(e)}")
            results.append(False)
        
        print()
    
    # Final summary
    print("=" * 50)
    print("🏁 Final Test Results")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your environment is ready for web scraping.")
        print("\nTry running an example:")
        print("   python examples/basic_scraper.py")
    else:
        print("⚠️  Some tests failed. Please check the setup and try again.")
        print("\nTo fix issues:")
        print("1. Make sure you're in the virtual environment")
        print("2. Run: pip install -r requirements.txt")
        print("3. Check that all files were created correctly")

if __name__ == "__main__":
    main()
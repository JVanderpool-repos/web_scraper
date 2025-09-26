# Web Scraper Project - Setup and Usage Guide

## 🚀 Quick Start

### 1. Virtual Environment Setup

**Option A: Automated Setup (Recommended)**

**Windows (PowerShell):**
```powershell
cd web_scraper
.\setup_venv.ps1
```

**Linux/Mac:**
```bash
cd web_scraper
./setup_venv.sh
```

**Option B: Manual Setup**

1. Navigate to the project directory:
```bash
cd web_scraper
```

2. Create virtual environment:
```bash
# Windows
python -m venv venv

# Linux/Mac  
python3 -m venv venv
```

3. Activate virtual environment:
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. Copy the environment configuration:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2. Basic Usage

Run the basic example to test the installation:
```bash
python examples\basic_scraper.py
```

### 3. More Examples

Try different scraping scenarios:
```bash
# E-commerce style scraping
python examples\ecommerce_scraper.py

# News/content scraping  
python examples\news_scraper.py

# Bulk URL scraping
python examples\bulk_scraper.py

# Advanced monitoring features
python examples\monitoring_example.py
```

## 📂 Project Structure

```
web_scraper/
├── venv/                  # Virtual environment (created after setup)
├── src/                   # Core scraping framework
│   ├── scraper.py         # Main WebScraper class
│   ├── storage.py         # Data storage utilities
│   ├── utils.py           # Helper functions
│   ├── monitoring.py      # Logging and monitoring
│   └── __init__.py        # Package initialization
├── config/                # Configuration files
│   ├── scraper_config.yaml # Main configuration
│   └── headers.yaml       # HTTP headers config
├── examples/              # Usage examples
│   ├── basic_scraper.py   # Simple scraping example
│   ├── ecommerce_scraper.py # Product scraping example
│   ├── news_scraper.py    # News/article scraping
│   ├── bulk_scraper.py    # Bulk URL processing
│   └── monitoring_example.py # Advanced monitoring
├── data/                  # Output data directory
├── logs/                  # Log files directory
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── setup_venv.ps1        # Windows venv setup script
├── setup_venv.sh         # Linux/Mac venv setup script
├── USAGE_GUIDE.md        # This guide
└── README.md             # Documentation
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
DEFAULT_DELAY=1
MAX_RETRIES=3
TIMEOUT=30
```

### Main Configuration (config/scraper_config.yaml)
Key settings you can customize:
- `request.delay`: Time between requests
- `request.max_retries`: Retry attempts for failed requests
- `selenium.headless`: Run browser in headless mode
- `logging.level`: Logging verbosity
- `output.default_format`: Default save format

## 🛠️ Features

### Core Scraping
- **Multiple Methods**: requests, Selenium, async support
- **Rate Limiting**: Configurable delays and respectful scraping
- **Error Handling**: Automatic retries with exponential backoff
- **User Agent Rotation**: Avoid detection with rotating headers

### Data Storage
- **Multiple Formats**: JSON, CSV, Excel, SQL, MongoDB
- **Flexible Schema**: Automatic data structure handling
- **Backup Support**: Automatic backup of existing files

### Monitoring & Logging
- **Progress Tracking**: Real-time progress bars and ETA
- **Performance Monitoring**: CPU, memory, and network tracking  
- **Comprehensive Logging**: Multiple log levels and formats
- **Session Reports**: Detailed scraping session analysis

### Advanced Features
- **Custom Extractors**: Define your own data extraction logic
- **Proxy Support**: Built-in proxy rotation capabilities
- **Async Scraping**: High-performance asynchronous operations
- **Database Integration**: Direct SQL and MongoDB support

## 💡 Usage Examples

### Basic Scraping
```python
from src.scraper import WebScraper

scraper = WebScraper(delay=1.0)
result = scraper.scrape_url('https://example.com')
scraper.save_data(result, 'data.json')
```

### Custom Data Extraction
```python
def extract_products(soup):
    products = []
    for item in soup.find_all('div', class_='product'):
        products.append({
            'name': item.find('h3').text,
            'price': item.find('.price').text
        })
    return {'products': products}

scraper = WebScraper()
scraper.set_custom_extractor(extract_products)
result = scraper.scrape_url('https://shop.example.com')
```

### Bulk URL Processing
```python
urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']
results = scraper.scrape_multiple_urls(urls)
scraper.save_data(results, 'bulk_data.csv', format='csv')
```

### Async Scraping
```python
import asyncio
from src.scraper import AsyncWebScraper

async def main():
    scraper = AsyncWebScraper(max_concurrent=5)
    urls = ['https://example1.com', 'https://example2.com']
    results = await scraper.scrape_multiple_async(urls)
    return results

asyncio.run(main())
```

## 🔧 Troubleshooting

### Virtual Environment Management

**Activate virtual environment:**
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Or use the convenience script
.\activate.ps1

# Linux/Mac
source venv/bin/activate

# Or use the convenience script
source activate.sh
```

**Deactivate virtual environment:**
```bash
deactivate
```

**Test your environment:**
```bash
python test_simple.py
```

**Reinstall packages if needed:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Common Issues

**"Module not found" errors:**
- Ensure your virtual environment is activated
- Check you're in the correct directory
- Reinstall requirements: `pip install -r requirements.txt`

**Virtual environment issues:**
- **Windows**: If PowerShell execution policy prevents script execution:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Permission errors**: Run terminal as administrator (Windows) or use `sudo` (Linux/Mac)
- **Path issues**: Ensure Python is in your system PATH
- **Activation fails**: Try using the full path to activation script

**Selenium WebDriver errors:**
- Install Chrome or Firefox browser
- Download appropriate WebDriver executable
- Set WebDriver path in system PATH

**Permission denied errors:**
- Check file permissions in data/ and logs/ directories
- Run with appropriate user permissions

**Memory issues with large scraping:**
- Reduce batch sizes in bulk operations
- Enable data streaming for large datasets
- Monitor memory usage with built-in performance monitoring

### Environment Files

The project includes several convenience scripts:

- **`setup_venv.ps1`** / **`setup_venv.sh`**: Complete environment setup
- **`activate.ps1`** / **`activate.sh`**: Quick environment activation  
- **`test_environment.py`**: Test your installation and environment
- **`.gitignore`**: Excludes venv and other files from version control

### Getting Help

1. Check the logs in the `logs/` directory for detailed error information
2. Review the configuration files for correct settings
3. Try the basic examples first to verify installation
4. Use the monitoring features to identify performance bottlenecks

## 🚨 Best Practices

### Ethical Scraping
- Always check and respect robots.txt
- Use appropriate delays between requests
- Don't overload servers with concurrent requests
- Consider reaching out to website owners for permission

### Performance Optimization
- Use async scraping for multiple URLs
- Implement custom extractors for better performance
- Enable monitoring to identify bottlenecks
- Use appropriate batch sizes for bulk operations

### Data Management  
- Regularly backup your scraped data
- Use appropriate storage formats for your use case
- Implement data validation and cleaning
- Monitor storage space usage

## 📄 License

This project is provided as-is for educational and research purposes. Please ensure you comply with all applicable laws and website terms of service when using this scraper.

---

**Happy Scraping! 🕷️**
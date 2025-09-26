# Web Scraper Project

A comprehensive and flexible web scraping framework built with Python. This project provides a robust foundation for scraping websites with built-in rate limiting, error handling, data storage, and monitoring capabilities.

## Features

- 🚀 **Multiple Scraping Methods**: Support for requests, Selenium, and Scrapy
- 🛡️ **Built-in Protection**: Rate limiting, retry logic, and respectful scraping
- 📊 **Flexible Data Storage**: Save to JSON, CSV, or databases
- 🔧 **Highly Configurable**: Easy configuration through YAML and environment variables
- 📝 **Comprehensive Logging**: Detailed logging and progress monitoring
- 🔄 **Async Support**: Asynchronous scraping for better performance
- 🎭 **Proxy Support**: Built-in proxy rotation capabilities

## Quick Start

1. **Clone and Setup with Virtual Environment**
   
   **Automated Setup (Recommended):**
   ```bash
   cd web_scraper
   
   # Windows
   .\setup_venv.ps1
   
   # Linux/Mac
   ./setup_venv.sh
   ```
   
   **Manual Setup:**
   ```bash
   cd web_scraper
   
   # Create and activate virtual environment
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Basic Usage**
   ```python
   from src.scraper import WebScraper
   
   scraper = WebScraper()
   data = scraper.scrape_url('https://example.com')
   scraper.save_data(data, 'example_data.json')
   ```

3. **Run Examples**
   ```bash
   python examples/basic_scraper.py
   python examples/ecommerce_scraper.py
   ```

## Project Structure

```
web_scraper/
├── src/
│   ├── scraper.py          # Main scraper class
│   ├── storage.py          # Data storage utilities
│   ├── utils.py            # Helper functions
│   └── __init__.py
├── config/
│   ├── scraper_config.yaml # Scraping configuration
│   └── headers.yaml        # HTTP headers
├── examples/
│   ├── basic_scraper.py    # Simple scraping example
│   ├── ecommerce_scraper.py # E-commerce scraping
│   └── news_scraper.py     # News scraping
├── data/                   # Scraped data storage
├── logs/                   # Log files
├── requirements.txt
└── .env.example
```

## Configuration

Edit `config/scraper_config.yaml` to customize:
- Request delays and timeouts
- Retry policies
- User agents and headers
- Output formats
- Logging levels

## Examples

### Basic Web Scraping
```python
from src.scraper import WebScraper

scraper = WebScraper()
data = scraper.scrape_url('https://quotes.toscrape.com/')
print(data)
```

### Bulk URL Scraping
```python
urls = [
    'https://example1.com',
    'https://example2.com',
    'https://example3.com'
]

scraper = WebScraper(delay=2)
results = scraper.scrape_multiple_urls(urls)
scraper.save_to_csv(results, 'bulk_data.csv')
```

### Using Selenium for Dynamic Content
```python
scraper = WebScraper(use_selenium=True)
data = scraper.scrape_url('https://spa-example.com')
```

## Advanced Features

### Custom Data Extraction
```python
def extract_products(soup):
    products = []
    for item in soup.find_all('div', class_='product'):
        products.append({
            'name': item.find('h3').text,
            'price': item.find('.price').text
        })
    return products

scraper = WebScraper()
scraper.set_custom_extractor(extract_products)
data = scraper.scrape_url('https://shop.example.com')
```

### Async Scraping
```python
import asyncio
from src.scraper import AsyncWebScraper

async def main():
    scraper = AsyncWebScraper()
    urls = ['https://example1.com', 'https://example2.com']
    results = await scraper.scrape_multiple_async(urls)
    return results

asyncio.run(main())
```

## Best Practices

1. **Respect robots.txt**: Always check and respect the website's robots.txt file
2. **Use delays**: Implement appropriate delays between requests
3. **Handle errors gracefully**: Implement proper error handling and retries
4. **Monitor your scraping**: Use logging to track your scraping activities
5. **Be respectful**: Don't overload servers with too many concurrent requests

## Legal Considerations

- Always check the website's Terms of Service
- Respect robots.txt files
- Be mindful of copyright and data protection laws
- Consider reaching out to website owners for permission when scraping large amounts of data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue on the GitHub repository.
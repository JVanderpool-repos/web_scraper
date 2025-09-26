"""
Basic Web Scraper Example

This example demonstrates the fundamental usage of the WebScraper class
for scraping basic web content from a single URL.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import WebScraper
from src.utils import setup_logging


def main():
    """Basic scraping example"""
    # Setup logging
    logger = setup_logging('basic_example')
    
    print("🚀 Basic Web Scraper Example")
    print("-" * 40)
    
    # Initialize scraper with basic settings
    scraper = WebScraper(
        delay=1.0,           # 1 second delay between requests
        max_retries=3,       # Retry failed requests up to 3 times
        timeout=30           # 30 second timeout
    )
    
    try:
        # Example URL to scrape (a public test site)
        url = "https://quotes.toscrape.com/"
        
        print(f"📄 Scraping: {url}")
        
        # Scrape the URL
        result = scraper.scrape_url(url)
        
        if result.success:
            print("✅ Scraping successful!")
            print(f"📊 Status Code: {result.status_code}")
            print(f"📝 Title: {result.data.get('title', 'N/A')}")
            print(f"🔗 Links found: {len(result.data.get('links', []))}")
            print(f"🖼️  Images found: {len(result.data.get('images', []))}")
            print(f"📏 Word count: {result.data.get('word_count', 0)}")
            
            # Save data in different formats
            print("\n💾 Saving data...")
            scraper.save_data(result, 'basic_example.json', 'json')
            scraper.save_data(result, 'basic_example.csv', 'csv')
            
            print("✅ Data saved to:")
            print("   - data/basic_example.json")
            print("   - data/basic_example.csv")
            
        else:
            print("❌ Scraping failed!")
            print(f"Error: {result.error_message}")
        
        # Show scraping statistics
        stats = scraper.get_stats()
        print(f"\n📈 Scraping Statistics:")
        print(f"   - Requests made: {stats['requests_made']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        print(f"   - Total delay time: {stats['total_delay_time']:.1f}s")
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
    
    finally:
        # Clean up
        scraper.close()


if __name__ == "__main__":
    main()
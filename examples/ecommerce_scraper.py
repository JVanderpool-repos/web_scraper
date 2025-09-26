"""
E-commerce Scraper Example

This example demonstrates scraping product information from e-commerce sites
with custom data extraction for product details.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import WebScraper
from src.utils import setup_logging, parse_price, clean_text
from bs4 import BeautifulSoup
from typing import Dict, List, Any


def extract_quotes_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Custom extraction function for quotes.toscrape.com
    (Using this as a safe example since it's designed for scraping practice)
    """
    data = {
        'quotes': [],
        'authors': set(),
        'tags': set(),
        'total_quotes': 0
    }
    
    # Extract quotes
    quote_divs = soup.find_all('div', class_='quote')
    
    for quote_div in quote_divs:
        quote_data = {}
        
        # Extract quote text
        text_elem = quote_div.find('span', class_='text')
        if text_elem:
            quote_data['text'] = clean_text(text_elem.text)
        
        # Extract author
        author_elem = quote_div.find('small', class_='author')
        if author_elem:
            quote_data['author'] = clean_text(author_elem.text)
            data['authors'].add(quote_data['author'])
        
        # Extract tags
        tag_elems = quote_div.find_all('a', class_='tag')
        quote_tags = []
        for tag in tag_elems:
            tag_text = clean_text(tag.text)
            quote_tags.append(tag_text)
            data['tags'].add(tag_text)
        quote_data['tags'] = quote_tags
        
        data['quotes'].append(quote_data)
    
    data['total_quotes'] = len(data['quotes'])
    data['authors'] = list(data['authors'])
    data['tags'] = list(data['tags'])
    
    return data


def extract_product_data_example(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Example product extraction function - customize this for specific sites
    """
    data = {
        'products': [],
        'categories': [],
        'total_products': 0,
        'price_range': {'min': None, 'max': None}
    }
    
    # This is a template - customize selectors for your target site
    product_containers = soup.find_all(['div', 'article'], class_=['product', 'item', 'card'])
    
    prices = []
    
    for container in product_containers:
        product = {}
        
        # Extract product name (common selectors)
        name_selectors = [
            'h1', 'h2', 'h3', 'h4',
            '.product-title', '.title', '.name',
            '[data-product-name]', '.product-name'
        ]
        
        for selector in name_selectors:
            name_elem = container.select_one(selector)
            if name_elem:
                product['name'] = clean_text(name_elem.text)
                break
        
        # Extract price (common selectors)
        price_selectors = [
            '.price', '.cost', '.amount',
            '[data-price]', '.product-price',
            '.price-current', '.sale-price'
        ]
        
        for selector in price_selectors:
            price_elem = container.select_one(selector)
            if price_elem:
                price_text = clean_text(price_elem.text)
                price = parse_price(price_text)
                if price:
                    product['price'] = price
                    product['price_text'] = price_text
                    prices.append(price)
                break
        
        # Extract image
        img_elem = container.find('img')
        if img_elem and img_elem.get('src'):
            product['image_url'] = img_elem['src']
        
        # Extract link
        link_elem = container.find('a', href=True)
        if link_elem:
            product['product_url'] = link_elem['href']
        
        if product:  # Only add if we found some data
            data['products'].append(product)
    
    data['total_products'] = len(data['products'])
    
    # Calculate price range
    if prices:
        data['price_range']['min'] = min(prices)
        data['price_range']['max'] = max(prices)
        data['average_price'] = sum(prices) / len(prices)
    
    return data


def main():
    """E-commerce scraping example"""
    logger = setup_logging('ecommerce_example')
    
    print("🛒 E-commerce Web Scraper Example")
    print("-" * 40)
    
    # Initialize scraper with e-commerce friendly settings
    scraper = WebScraper(
        delay=2.0,           # Slower delay to be respectful
        max_retries=3,
        timeout=30,
        use_selenium=False   # Start with requests, can switch to Selenium if needed
    )
    
    # Set custom extraction function
    scraper.set_custom_extractor(extract_quotes_data)
    
    try:
        # Example URLs (using quotes.toscrape.com as safe example)
        urls = [
            "https://quotes.toscrape.com/",
            "https://quotes.toscrape.com/page/2/",
            "https://quotes.toscrape.com/page/3/"
        ]
        
        print(f"📄 Scraping {len(urls)} pages...")
        
        # Scrape multiple URLs
        results = scraper.scrape_multiple_urls(urls)
        
        # Process results
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        print(f"✅ Successful scrapes: {len(successful_results)}")
        print(f"❌ Failed scrapes: {len(failed_results)}")
        
        if successful_results:
            # Aggregate data from all pages
            all_quotes = []
            all_authors = set()
            all_tags = set()
            
            for result in successful_results:
                quotes = result.data.get('quotes', [])
                all_quotes.extend(quotes)
                all_authors.update(result.data.get('authors', []))
                all_tags.update(result.data.get('tags', []))
            
            print(f"\n📊 Aggregated Results:")
            print(f"   - Total quotes scraped: {len(all_quotes)}")
            print(f"   - Unique authors: {len(all_authors)}")
            print(f"   - Unique tags: {len(all_tags)}")
            
            # Display sample data
            if all_quotes:
                print(f"\n📝 Sample Quote:")
                sample_quote = all_quotes[0]
                print(f"   Text: {sample_quote.get('text', 'N/A')[:100]}...")
                print(f"   Author: {sample_quote.get('author', 'N/A')}")
                print(f"   Tags: {', '.join(sample_quote.get('tags', []))}")
            
            # Save aggregated data
            print("\n💾 Saving data...")
            
            # Save individual results
            scraper.save_data(results, 'ecommerce_results.json', 'json')
            scraper.save_data(results, 'ecommerce_results.csv', 'csv')
            
            # Save aggregated data
            aggregated_data = {
                'summary': {
                    'total_quotes': len(all_quotes),
                    'unique_authors': len(all_authors),
                    'unique_tags': len(all_tags),
                    'pages_scraped': len(successful_results)
                },
                'quotes': all_quotes,
                'authors': list(all_authors),
                'tags': list(all_tags)
            }
            
            import json
            with open('data/ecommerce_aggregated.json', 'w', encoding='utf-8') as f:
                json.dump(aggregated_data, f, indent=2, ensure_ascii=False)
            
            print("✅ Data saved to:")
            print("   - data/ecommerce_results.json (individual results)")
            print("   - data/ecommerce_results.csv (flattened data)")
            print("   - data/ecommerce_aggregated.json (aggregated data)")
        
        # Show detailed statistics
        stats = scraper.get_stats()
        print(f"\n📈 Scraping Statistics:")
        print(f"   - Total requests: {stats['requests_made']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        print(f"   - Total delay time: {stats['total_delay_time']:.1f}s")
        print(f"   - Average delay: {stats['average_delay']:.2f}s")
        
        # Show failed URLs if any
        if failed_results:
            print(f"\n❌ Failed URLs:")
            for result in failed_results:
                print(f"   - {result.url}: {result.error_message}")
        
    except Exception as e:
        logger.error(f"E-commerce example failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
    
    finally:
        scraper.close()


def selenium_ecommerce_example():
    """
    Example using Selenium for dynamic content
    (commented out to avoid requiring Selenium setup)
    """
    print("\n🌐 Selenium E-commerce Example")
    print("-" * 40)
    
    scraper = WebScraper(
        delay=3.0,
        use_selenium=True,
        headless=True,
        browser='chrome'
    )
    
    try:
        # This would work for sites with dynamic content
        url = "https://quotes.toscrape.com/js/"  # JavaScript version
        
        print(f"📄 Scraping dynamic content: {url}")
        result = scraper.scrape_url(url)
        
        if result.success:
            print("✅ Dynamic content scraped successfully!")
            # Process and save data...
        
    except Exception as e:
        print(f"❌ Selenium example error: {str(e)}")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
    
    # Uncomment to run Selenium example (requires webdriver setup)
    # selenium_ecommerce_example()
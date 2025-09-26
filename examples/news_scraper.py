"""
News Scraper Example

This example demonstrates scraping news articles with custom extraction
for headlines, content, publication dates, and author information.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import WebScraper, AsyncWebScraper
from src.utils import setup_logging, clean_text, extract_email_addresses
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import asyncio
from datetime import datetime
import re


def extract_news_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Custom extraction function for news websites
    """
    data = {
        'articles': [],
        'headlines': [],
        'publication_info': {},
        'categories': [],
        'total_articles': 0
    }
    
    # Extract main article content
    article_selectors = [
        'article', '.article', '.post', '.entry',
        '.content', '.story', '.news-item'
    ]
    
    articles = []
    for selector in article_selectors:
        articles.extend(soup.select(selector))
    
    # If no articles found, look for headline lists
    if not articles:
        headline_selectors = [
            '.headline', '.title', 'h1', 'h2', 'h3',
            '.post-title', '.entry-title', '.article-title'
        ]
        
        for selector in headline_selectors:
            headlines = soup.select(selector)
            for headline in headlines[:10]:  # Limit to top 10
                if len(clean_text(headline.text)) > 10:  # Filter out short text
                    data['headlines'].append({
                        'title': clean_text(headline.text),
                        'link': headline.find('a')['href'] if headline.find('a') else None
                    })
    
    # Process articles
    for article in articles[:5]:  # Limit to first 5 articles
        article_data = {}
        
        # Extract headline/title
        title_selectors = ['h1', 'h2', 'h3', '.title', '.headline', '.post-title']
        for selector in title_selectors:
            title_elem = article.select_one(selector)
            if title_elem:
                article_data['title'] = clean_text(title_elem.text)
                break
        
        # Extract content/summary
        content_selectors = ['.content', '.entry-content', '.post-content', 'p']
        content_parts = []
        for selector in content_selectors:
            content_elems = article.select(selector)
            for elem in content_elems:
                text = clean_text(elem.text)
                if len(text) > 50:  # Only meaningful content
                    content_parts.append(text)
                if len(content_parts) >= 3:  # Limit content
                    break
            if content_parts:
                break
        
        if content_parts:
            article_data['content'] = ' '.join(content_parts[:3])
            article_data['content_preview'] = content_parts[0][:200] + "..." if len(content_parts[0]) > 200 else content_parts[0]
        
        # Extract author
        author_selectors = ['.author', '.byline', '.post-author', '.writer']
        for selector in author_selectors:
            author_elem = article.select_one(selector)
            if author_elem:
                article_data['author'] = clean_text(author_elem.text)
                break
        
        # Extract date
        date_selectors = ['.date', '.published', '.post-date', 'time']
        for selector in date_selectors:
            date_elem = article.select_one(selector)
            if date_elem:
                article_data['date'] = clean_text(date_elem.text)
                # Try to extract datetime attribute if available
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    article_data['datetime'] = datetime_attr
                break
        
        # Extract category/tags
        category_selectors = ['.category', '.tag', '.section']
        categories = []
        for selector in category_selectors:
            category_elems = article.select(selector)
            for elem in category_elems:
                cat_text = clean_text(elem.text)
                if cat_text and len(cat_text) < 50:
                    categories.append(cat_text)
        
        if categories:
            article_data['categories'] = categories
            data['categories'].extend(categories)
        
        # Extract article URL
        link_elem = article.find('a', href=True)
        if link_elem:
            article_data['url'] = link_elem['href']
        
        if article_data:  # Only add if we extracted some data
            data['articles'].append(article_data)
    
    # Extract site information
    site_name_elem = soup.find('meta', attrs={'property': 'og:site_name'})
    if site_name_elem:
        data['publication_info']['site_name'] = site_name_elem.get('content')
    
    # Count totals
    data['total_articles'] = len(data['articles'])
    data['total_headlines'] = len(data['headlines'])
    data['unique_categories'] = list(set(data['categories']))
    
    return data


def extract_rss_feed_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract data from RSS/XML feeds
    """
    data = {
        'feed_info': {},
        'items': [],
        'total_items': 0
    }
    
    # Check if this is an RSS feed
    if soup.find('rss') or soup.find('feed'):
        # Extract feed title
        title_elem = soup.find('title')
        if title_elem:
            data['feed_info']['title'] = clean_text(title_elem.text)
        
        # Extract feed description
        desc_elem = soup.find('description')
        if desc_elem:
            data['feed_info']['description'] = clean_text(desc_elem.text)
        
        # Extract items
        items = soup.find_all('item') or soup.find_all('entry')
        
        for item in items:
            item_data = {}
            
            # Title
            title_elem = item.find('title')
            if title_elem:
                item_data['title'] = clean_text(title_elem.text)
            
            # Description/Summary
            desc_elem = item.find('description') or item.find('summary')
            if desc_elem:
                item_data['description'] = clean_text(desc_elem.text)[:300]
            
            # Link
            link_elem = item.find('link')
            if link_elem:
                item_data['link'] = link_elem.text if link_elem.text else link_elem.get('href')
            
            # Publication date
            date_elem = item.find('pubdate') or item.find('published')
            if date_elem:
                item_data['pub_date'] = clean_text(date_elem.text)
            
            # Author
            author_elem = item.find('author') or item.find('creator')
            if author_elem:
                item_data['author'] = clean_text(author_elem.text)
            
            # Category
            category_elem = item.find('category')
            if category_elem:
                item_data['category'] = clean_text(category_elem.text)
            
            data['items'].append(item_data)
        
        data['total_items'] = len(data['items'])
    
    return data


async def async_news_scraping_example():
    """
    Demonstrate asynchronous scraping for faster news collection
    """
    print("\n⚡ Async News Scraping Example")
    print("-" * 40)
    
    # News sites RSS feeds (public and scraping-friendly)
    news_urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.npr.org/1001/rss.xml",
        "https://feeds.reuters.com/reuters/topNews",
        "https://www.techcrunch.com/feed/"
    ]
    
    async_scraper = AsyncWebScraper(
        max_concurrent=3,    # Limit concurrent requests
        delay=1.0,
        timeout=15
    )
    
    try:
        print(f"📰 Scraping {len(news_urls)} news sources asynchronously...")
        
        start_time = datetime.now()
        results = await async_scraper.scrape_multiple_async(news_urls)
        end_time = datetime.now()
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"✅ Completed in {(end_time - start_time).total_seconds():.1f} seconds")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        # Show sample results
        for result in successful[:3]:  # Show first 3
            print(f"\n📄 {result.url}")
            print(f"   Title: {result.data.get('title', 'N/A')[:50]}...")
            print(f"   Length: {result.data.get('text_length', 0)} characters")
        
        return results
    
    except Exception as e:
        print(f"❌ Async scraping error: {str(e)}")
        return []


def main():
    """Main news scraping example"""
    logger = setup_logging('news_example')
    
    print("📰 News Web Scraper Example")
    print("-" * 40)
    
    # Initialize scraper for news sites
    scraper = WebScraper(
        delay=2.0,          # Be respectful to news sites
        max_retries=3,
        timeout=30,
        use_selenium=False
    )
    
    # Set custom extraction function
    scraper.set_custom_extractor(extract_news_data)
    
    try:
        # Example news/blog sites (using safe examples)
        urls = [
            "https://quotes.toscrape.com/",  # Safe example site
            "https://books.toscrape.com/",   # Safe example site
        ]
        
        print(f"📄 Scraping {len(urls)} news sources...")
        
        results = scraper.scrape_multiple_urls(urls)
        
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        print(f"✅ Successful scrapes: {len(successful_results)}")
        print(f"❌ Failed scrapes: {len(failed_results)}")
        
        if successful_results:
            # Aggregate news data
            all_articles = []
            all_headlines = []
            
            for result in successful_results:
                articles = result.data.get('articles', [])
                headlines = result.data.get('headlines', [])
                
                all_articles.extend(articles)
                all_headlines.extend(headlines)
                
                print(f"\n📰 {result.url}")
                print(f"   Articles found: {len(articles)}")
                print(f"   Headlines found: {len(headlines)}")
                
                # Show sample article if available
                if articles:
                    sample = articles[0]
                    print(f"   Sample: {sample.get('title', 'N/A')[:60]}...")
            
            print(f"\n📊 Total Results:")
            print(f"   - Articles: {len(all_articles)}")
            print(f"   - Headlines: {len(all_headlines)}")
            
            # Save results
            print("\n💾 Saving news data...")
            scraper.save_data(results, 'news_results.json', 'json')
            
            # Create news summary
            news_summary = {
                'scrape_timestamp': datetime.now().isoformat(),
                'sources_scraped': len(successful_results),
                'total_articles': len(all_articles),
                'total_headlines': len(all_headlines),
                'articles': all_articles,
                'headlines': all_headlines,
                'failed_sources': [{'url': r.url, 'error': r.error_message} for r in failed_results]
            }
            
            import json
            with open('data/news_summary.json', 'w', encoding='utf-8') as f:
                json.dump(news_summary, f, indent=2, ensure_ascii=False, default=str)
            
            print("✅ Data saved to:")
            print("   - data/news_results.json")
            print("   - data/news_summary.json")
        
        # Show statistics
        stats = scraper.get_stats()
        print(f"\n📈 Scraping Statistics:")
        print(f"   - Total requests: {stats['requests_made']}")
        print(f"   - Success rate: {stats['success_rate']:.1f}%")
        print(f"   - Average delay: {stats['average_delay']:.2f}s")
        
    except Exception as e:
        logger.error(f"News example failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
    
    # Run async example
    print("\n" + "="*50)
    try:
        asyncio.run(async_news_scraping_example())
    except Exception as e:
        print(f"❌ Async example error: {str(e)}")
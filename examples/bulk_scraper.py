"""
Bulk URL Scraper Example

This example demonstrates scraping multiple URLs from a list,
with progress tracking, error handling, and batch processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import WebScraper, AsyncWebScraper
from src.utils import setup_logging, validate_url
from typing import List
import asyncio
from datetime import datetime
import json


def load_urls_from_file(filename: str) -> List[str]:
    """Load URLs from a text file (one URL per line)"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#') and validate_url(url):
                    urls.append(url)
        print(f"✅ Loaded {len(urls)} valid URLs from {filename}")
        return urls
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return []
    except Exception as e:
        print(f"❌ Error loading URLs: {str(e)}")
        return []


def create_sample_urls_file():
    """Create a sample URLs file for demonstration"""
    sample_urls = [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/page/3/",
        "https://quotes.toscrape.com/page/4/",
        "https://quotes.toscrape.com/page/5/",
        "https://books.toscrape.com/",
        "https://books.toscrape.com/catalogue/page-2.html",
        "https://books.toscrape.com/catalogue/page-3.html",
        "https://httpbin.org/html",
        "https://httpbin.org/json",
    ]
    
    filename = "examples/sample_urls.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Sample URLs for bulk scraping\n")
            f.write("# One URL per line, lines starting with # are ignored\n\n")
            for url in sample_urls:
                f.write(f"{url}\n")
        print(f"✅ Created sample URLs file: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error creating sample file: {str(e)}")
        return None


def batch_scrape_sync(urls: List[str], batch_size: int = 5) -> List:
    """Scrape URLs in batches using synchronous scraper"""
    print(f"🔄 Batch scraping {len(urls)} URLs (batch size: {batch_size})")
    
    scraper = WebScraper(
        delay=1.5,
        max_retries=2,
        timeout=20
    )
    
    all_results = []
    
    try:
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(urls) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} URLs)")
            
            batch_results = scraper.scrape_multiple_urls(batch)
            all_results.extend(batch_results)
            
            # Show batch statistics
            successful = sum(1 for r in batch_results if r.success)
            failed = len(batch_results) - successful
            
            print(f"   ✅ Successful: {successful}")
            print(f"   ❌ Failed: {failed}")
            
            # Small delay between batches
            if i + batch_size < len(urls):
                print("   ⏸️  Pausing between batches...")
                import time
                time.sleep(2)
    
    finally:
        scraper.close()
    
    return all_results


async def batch_scrape_async(urls: List[str], max_concurrent: int = 5) -> List:
    """Scrape URLs asynchronously for better performance"""
    print(f"⚡ Async scraping {len(urls)} URLs (max concurrent: {max_concurrent})")
    
    async_scraper = AsyncWebScraper(
        max_concurrent=max_concurrent,
        delay=0.5,  # Can use shorter delay with async
        timeout=15
    )
    
    start_time = datetime.now()
    results = await async_scraper.scrape_multiple_async(urls)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    print(f"⏱️  Completed in {duration:.1f} seconds")
    print(f"📊 Average: {duration/len(urls):.2f} seconds per URL")
    
    return results


def analyze_results(results: List) -> dict:
    """Analyze scraping results and generate statistics"""
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    analysis = {
        'total_urls': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': (len(successful) / len(results) * 100) if results else 0,
        'error_breakdown': {},
        'domain_breakdown': {},
        'size_stats': {}
    }
    
    # Analyze errors
    for result in failed:
        error = result.error_message or 'Unknown error'
        analysis['error_breakdown'][error] = analysis['error_breakdown'].get(error, 0) + 1
    
    # Analyze domains
    for result in results:
        try:
            from urllib.parse import urlparse
            domain = urlparse(result.url).netloc
            analysis['domain_breakdown'][domain] = analysis['domain_breakdown'].get(domain, 0) + 1
        except:
            pass
    
    # Analyze content sizes
    if successful:
        sizes = []
        for result in successful:
            if 'text_content' in result.data:
                sizes.append(len(result.data['text_content']))
            elif 'word_count' in result.data:
                sizes.append(result.data['word_count'] * 5)  # Rough estimate
        
        if sizes:
            analysis['size_stats'] = {
                'min_size': min(sizes),
                'max_size': max(sizes),
                'avg_size': sum(sizes) / len(sizes),
                'total_content': sum(sizes)
            }
    
    return analysis


def save_detailed_results(results: List, analysis: dict, method: str):
    """Save results with detailed analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw results
    results_file = f"data/bulk_results_{method}_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        # Convert results to serializable format
        serializable_results = []
        for result in results:
            if hasattr(result, '__dict__'):
                result_dict = result.__dict__.copy()
                if 'timestamp' in result_dict:
                    result_dict['timestamp'] = result_dict['timestamp'].isoformat()
                serializable_results.append(result_dict)
            else:
                serializable_results.append(result)
        
        json.dump(serializable_results, f, indent=2, ensure_ascii=False, default=str)
    
    # Save analysis report
    report_file = f"data/bulk_analysis_{method}_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        report = {
            'method': method,
            'timestamp': timestamp,
            'analysis': analysis,
            'successful_urls': [r.url for r in results if r.success],
            'failed_urls': [{'url': r.url, 'error': r.error_message} for r in results if not r.success]
        }
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved:")
    print(f"   - Raw data: {results_file}")
    print(f"   - Analysis: {report_file}")


def print_analysis(analysis: dict):
    """Print detailed analysis of scraping results"""
    print(f"\n📊 Scraping Analysis:")
    print(f"   📈 Total URLs: {analysis['total_urls']}")
    print(f"   ✅ Successful: {analysis['successful']}")
    print(f"   ❌ Failed: {analysis['failed']}")
    print(f"   📋 Success Rate: {analysis['success_rate']:.1f}%")
    
    if analysis['error_breakdown']:
        print(f"\n❌ Error Breakdown:")
        for error, count in analysis['error_breakdown'].items():
            print(f"   - {error}: {count}")
    
    if analysis['domain_breakdown']:
        print(f"\n🌐 Domain Breakdown:")
        for domain, count in list(analysis['domain_breakdown'].items())[:5]:  # Top 5
            print(f"   - {domain}: {count}")
    
    if analysis['size_stats']:
        stats = analysis['size_stats']
        print(f"\n📏 Content Size Stats:")
        print(f"   - Min size: {stats['min_size']:,} chars")
        print(f"   - Max size: {stats['max_size']:,} chars")
        print(f"   - Avg size: {stats['avg_size']:,.0f} chars")
        print(f"   - Total content: {stats['total_content']:,} chars")


def main():
    """Main bulk scraping example"""
    logger = setup_logging('bulk_example')
    
    print("📦 Bulk URL Scraper Example")
    print("-" * 40)
    
    # Create sample URLs file if it doesn't exist
    urls_file = "examples/sample_urls.txt"
    if not os.path.exists(urls_file):
        create_sample_urls_file()
    
    # Load URLs
    urls = load_urls_from_file(urls_file)
    
    if not urls:
        print("❌ No valid URLs found. Exiting.")
        return
    
    print(f"🎯 Ready to scrape {len(urls)} URLs")
    
    # Method 1: Synchronous batch scraping
    print("\n" + "="*50)
    print("🔄 SYNCHRONOUS BATCH SCRAPING")
    print("="*50)
    
    sync_results = batch_scrape_sync(urls, batch_size=3)
    sync_analysis = analyze_results(sync_results)
    
    print_analysis(sync_analysis)
    save_detailed_results(sync_results, sync_analysis, "sync")
    
    # Method 2: Asynchronous scraping
    print("\n" + "="*50)
    print("⚡ ASYNCHRONOUS SCRAPING")
    print("="*50)
    
    try:
        async_results = asyncio.run(batch_scrape_async(urls, max_concurrent=3))
        async_analysis = analyze_results(async_results)
        
        print_analysis(async_analysis)
        save_detailed_results(async_results, async_analysis, "async")
        
        # Compare methods
        print("\n" + "="*50)
        print("⚖️  METHOD COMPARISON")
        print("="*50)
        print(f"Synchronous Success Rate: {sync_analysis['success_rate']:.1f}%")
        print(f"Asynchronous Success Rate: {async_analysis['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Async scraping failed: {str(e)}")
        logger.error(f"Async scraping error: {str(e)}")


if __name__ == "__main__":
    main()
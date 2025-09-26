"""
Advanced Scraper Example with Monitoring

This example demonstrates the full capabilities of the web scraper framework
including comprehensive monitoring, logging, and performance tracking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import WebScraper, AsyncWebScraper
from src.monitoring import ScrapingMonitor, PerformanceMonitor, ScrapingLogger
from src.utils import setup_logging, validate_url
from typing import List, Dict, Any
import asyncio
import time
from datetime import datetime


class MonitoredWebScraper(WebScraper):
    """
    Extended WebScraper with integrated monitoring
    """
    
    def __init__(self, session_name: str = "monitored_session", **kwargs):
        super().__init__(**kwargs)
        self.monitor = ScrapingMonitor(session_name)
        self._original_make_request = self._make_request
        self._override_request_method()
    
    def _override_request_method(self):
        """Override request method to include monitoring"""
        def monitored_make_request(url: str):
            start_time = time.time()
            error = None
            status_code = None
            content_size = None
            
            try:
                response = self._original_make_request(url)
                status_code = response.status_code
                content_size = len(response.content) if response.content else 0
                response_time = time.time() - start_time
                
                self.monitor.log_request(
                    url=url,
                    success=True,
                    status_code=status_code,
                    response_time=response_time,
                    content_size=content_size
                )
                
                return response
                
            except Exception as e:
                error = str(e)
                response_time = time.time() - start_time
                
                self.monitor.log_request(
                    url=url,
                    success=False,
                    response_time=response_time,
                    error=error
                )
                raise
        
        self._make_request = monitored_make_request
    
    def scrape_multiple_urls(self, urls: List[str], monitor_session: bool = True):
        """Override to include monitoring session management"""
        if monitor_session:
            self.monitor.start_session(len(urls))
        
        try:
            results = super().scrape_multiple_urls(urls)
            return results
        finally:
            if monitor_session:
                self.monitor.end_session()
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get current monitoring statistics"""
        return self.monitor.get_current_stats()


def advanced_monitoring_example():
    """Demonstrate advanced monitoring capabilities"""
    print("🔍 Advanced Web Scraper with Monitoring")
    print("-" * 50)
    
    # Initialize monitored scraper
    scraper = MonitoredWebScraper(
        session_name="advanced_demo",
        delay=1.0,
        max_retries=2,
        timeout=15
    )
    
    # URLs to scrape (mix of good and bad URLs for demonstration)
    urls = [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/page/3/",
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/status/404",  # Will fail
        "https://nonexistent-domain-12345.com/",  # Will fail
        "https://books.toscrape.com/",
        "https://books.toscrape.com/catalogue/page-2.html",
        "https://httpbin.org/delay/2",  # Slow response
    ]
    
    print(f"📄 Scraping {len(urls)} URLs with full monitoring...")
    
    try:
        # Scrape with monitoring
        results = scraper.scrape_multiple_urls(urls)
        
        # Display results summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"\n📊 Scraping Results:")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        # Show monitoring stats
        stats = scraper.get_monitoring_stats()
        metrics = stats['metrics']
        
        print(f"\n📈 Session Metrics:")
        print(f"   🎯 Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   ⏱️  Average Response Time: {metrics['average_response_time']:.2f}s")
        print(f"   🚀 Requests/Second: {metrics['requests_per_second']:.2f}")
        print(f"   📊 Total Data: {metrics['total_bytes_downloaded']:,} bytes")
        print(f"   ⏰ Duration: {metrics['duration_seconds']:.1f}s")
        
        # Show system performance
        if 'system_performance' in stats:
            perf = stats['system_performance']
            print(f"\n💻 System Performance:")
            print(f"   🖥️  CPU: {perf.get('avg_cpu_percent', 'N/A')}%")
            print(f"   🧠 Memory: {perf.get('avg_memory_percent', 'N/A')}%")
            print(f"   📏 Memory Used: {perf.get('current_memory_mb', 'N/A')} MB")
        
        # Show error breakdown if any
        if metrics['errors_by_type']:
            print(f"\n❌ Error Breakdown:")
            for error, count in metrics['errors_by_type'].items():
                print(f"   - {error}: {count}")
        
        # Show domain statistics
        if metrics['domain_stats']:
            print(f"\n🌐 Domain Statistics:")
            for domain, count in list(metrics['domain_stats'].items())[:5]:
                print(f"   - {domain}: {count} requests")
        
        # Show alerts if any
        alerts_count = stats.get('alerts_count', 0)
        if alerts_count > 0:
            print(f"\n⚠️  Alerts Generated: {alerts_count}")
    
    except Exception as e:
        print(f"❌ Error during scraping: {str(e)}")
    
    finally:
        scraper.close()


def performance_comparison_example():
    """Compare performance with and without monitoring"""
    print("\n" + "="*50)
    print("⚖️  Performance Comparison: With vs Without Monitoring")
    print("="*50)
    
    test_urls = [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/page/3/",
        "https://httpbin.org/html",
        "https://httpbin.org/json",
    ]
    
    # Test without monitoring
    print("\n🏃 Testing without monitoring...")
    start_time = time.time()
    
    scraper_basic = WebScraper(delay=0.5, timeout=10)
    try:
        results_basic = scraper_basic.scrape_multiple_urls(test_urls)
        basic_time = time.time() - start_time
        basic_success = sum(1 for r in results_basic if r.success)
        
        print(f"   ⏱️  Time: {basic_time:.2f}s")
        print(f"   ✅ Success: {basic_success}/{len(test_urls)}")
    finally:
        scraper_basic.close()
    
    # Test with monitoring
    print("\n🔍 Testing with monitoring...")
    start_time = time.time()
    
    scraper_monitored = MonitoredWebScraper(
        session_name="performance_test",
        delay=0.5,
        timeout=10
    )
    
    try:
        results_monitored = scraper_monitored.scrape_multiple_urls(test_urls)
        monitored_time = time.time() - start_time
        monitored_success = sum(1 for r in results_monitored if r.success)
        
        print(f"   ⏱️  Time: {monitored_time:.2f}s")
        print(f"   ✅ Success: {monitored_success}/{len(test_urls)}")
        
        # Show monitoring overhead
        overhead = ((monitored_time - basic_time) / basic_time) * 100
        print(f"\n📊 Monitoring Overhead: {overhead:.1f}%")
        
    finally:
        scraper_monitored.close()


def logging_demonstration():
    """Demonstrate different logging capabilities"""
    print("\n" + "="*50)
    print("📝 Logging System Demonstration")
    print("="*50)
    
    # Create custom logger
    logger = ScrapingLogger(
        name='logging_demo',
        level='DEBUG',
        enable_console=True,
        enable_file=True,
        enable_structured=True
    )
    
    # Demonstrate different log types
    print("\n📄 Generating sample log entries...")
    
    log = logger.get_logger()
    
    # Standard log levels
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    
    # Specialized logging methods
    logger.log_request(
        url="https://example.com/api/data",
        method="GET",
        status_code=200,
        response_time=0.245
    )
    
    logger.log_request(
        url="https://example.com/api/error",
        method="POST",
        status_code=500,
        response_time=1.2,
        error="Internal Server Error"
    )
    
    logger.log_extraction(
        url="https://example.com/products",
        items_extracted=25,
        extraction_time=0.15
    )
    
    logger.log_storage(
        format_type="json",
        filename="products.json",
        record_count=25,
        file_size=4096
    )
    
    print("✅ Log entries generated. Check logs directory for files:")
    print("   - logs/logging_demo.log (general log)")
    print("   - logs/logging_demo_errors.log (errors only)")
    print("   - logs/logging_demo_structured.log (JSON format)")


async def async_monitoring_example():
    """Demonstrate monitoring with async scraping"""
    print("\n" + "="*50)
    print("⚡ Async Scraping with Performance Monitoring")
    print("="*50)
    
    # Start performance monitoring
    perf_monitor = PerformanceMonitor(interval=1.0)
    perf_monitor.start_monitoring()
    
    try:
        async_scraper = AsyncWebScraper(
            max_concurrent=3,
            delay=0.5,
            timeout=10
        )
        
        urls = [
            "https://quotes.toscrape.com/",
            "https://quotes.toscrape.com/page/2/",
            "https://quotes.toscrape.com/page/3/",
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://httpbin.org/uuid",
        ]
        
        print(f"🚀 Async scraping {len(urls)} URLs...")
        start_time = time.time()
        
        results = await async_scraper.scrape_multiple_async(urls)
        
        duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        
        print(f"✅ Completed in {duration:.2f}s")
        print(f"📊 Success rate: {successful}/{len(urls)} ({successful/len(urls)*100:.1f}%)")
        
        # Show performance stats
        stats = perf_monitor.get_current_stats()
        print(f"\n💻 Performance During Async Scraping:")
        print(f"   🖥️  Average CPU: {stats.get('avg_cpu_percent', 'N/A')}%")
        print(f"   🧠 Average Memory: {stats.get('avg_memory_percent', 'N/A')}%")
        print(f"   📏 Current Memory: {stats.get('current_memory_mb', 'N/A')} MB")
        
    except Exception as e:
        print(f"❌ Async example error: {str(e)}")
    
    finally:
        perf_monitor.stop_monitoring()
        
        # Export performance data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        perf_file = f"logs/performance_metrics_{timestamp}.json"
        perf_monitor.export_metrics(perf_file)
        print(f"📊 Performance metrics exported to: {perf_file}")


def main():
    """Run all monitoring and logging examples"""
    print("🚀 Web Scraper Advanced Features Demo")
    print("="*60)
    
    try:
        # 1. Advanced monitoring example
        advanced_monitoring_example()
        
        # 2. Performance comparison
        performance_comparison_example()
        
        # 3. Logging demonstration
        logging_demonstration()
        
        # 4. Async monitoring (if supported)
        try:
            asyncio.run(async_monitoring_example())
        except Exception as e:
            print(f"❌ Async monitoring example failed: {str(e)}")
        
        print("\n" + "="*60)
        print("✨ All demonstrations completed successfully!")
        print("📁 Check the 'logs' and 'data' directories for generated files.")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    main()
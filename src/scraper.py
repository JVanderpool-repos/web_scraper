"""
Main Web Scraper Module

A comprehensive web scraping class that supports multiple scraping methods,
rate limiting, error handling, and flexible data extraction.
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
import random
from typing import Dict, List, Optional, Callable, Union, Any
import json
import yaml
import os
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import asyncio
import aiohttp
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

from .utils import setup_logging, clean_text, parse_price, validate_url
from .storage import DataStorage


@dataclass
class ScrapingResult:
    """Data class for scraping results"""
    url: str
    status_code: int
    success: bool
    data: Dict[str, Any]
    timestamp: datetime
    error_message: Optional[str] = None


class WebScraper:
    """
    A comprehensive web scraper with support for multiple scraping methods,
    rate limiting, error handling, and flexible data storage.
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 delay: float = 1.0,
                 max_retries: int = 3,
                 timeout: int = 30,
                 use_selenium: bool = False,
                 browser: str = 'chrome',
                 headless: bool = True,
                 user_agent: Optional[str] = None,
                 proxies: Optional[Dict[str, str]] = None,
                 custom_headers: Optional[Dict[str, str]] = None):
        """
        Initialize the WebScraper
        
        Args:
            config_path: Path to configuration file
            delay: Delay between requests in seconds
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            use_selenium: Whether to use Selenium for dynamic content
            browser: Browser to use with Selenium ('chrome' or 'firefox')
            headless: Whether to run browser in headless mode
            user_agent: Custom user agent string
            proxies: Proxy configuration
            custom_headers: Custom HTTP headers
        """
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.use_selenium = use_selenium
        self.browser = browser
        self.headless = headless
        self.proxies = proxies
        self.driver = None
        self.custom_extractor = None
        
        # Setup logging
        self.logger = setup_logging('web_scraper')
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup user agent
        self.ua = UserAgent()
        self.user_agent = user_agent or self.ua.random
        
        # Setup session
        self.session = self._create_session(custom_headers)
        
        # Initialize data storage
        self.storage = DataStorage()
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_delay_time': 0
        }
        
        self.logger.info(f"WebScraper initialized with delay={delay}s, retries={max_retries}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _create_session(self, custom_headers: Optional[Dict[str, str]]) -> requests.Session:
        """Create and configure requests session"""
        session = requests.Session()
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        session.headers.update(headers)
        
        if self.proxies:
            session.proxies.update(self.proxies)
        
        return session
    
    def _setup_selenium(self):
        """Setup Selenium webdriver"""
        if self.driver:
            return
        
        try:
            if self.browser.lower() == 'chrome':
                options = ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(f'--user-agent={self.user_agent}')
                self.driver = webdriver.Chrome(options=options)
            
            elif self.browser.lower() == 'firefox':
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.set_preference("general.useragent.override", self.user_agent)
                self.driver = webdriver.Firefox(options=options)
            
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
            
            self.driver.set_page_load_timeout(self.timeout)
            self.logger.info(f"Selenium {self.browser} driver initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium driver: {str(e)}")
            raise
    
    def _make_request(self, url: str) -> requests.Response:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                # Add random delay variation
                if self.delay > 0:
                    delay_time = self.delay + random.uniform(0, self.delay * 0.5)
                    time.sleep(delay_time)
                    self.stats['total_delay_time'] += delay_time
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                self.stats['requests_made'] += 1
                self.stats['successful_requests'] += 1
                self.logger.debug(f"Successfully fetched {url}")
                
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}")
                if attempt == self.max_retries:
                    self.stats['failed_requests'] += 1
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _parse_with_selenium(self, url: str) -> BeautifulSoup:
        """Parse page using Selenium for dynamic content"""
        if not self.driver:
            self._setup_selenium()
        
        try:
            self.driver.get(url)
            
            # Wait for page to load (you can customize this)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and create BeautifulSoup object
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return soup
            
        except Exception as e:
            self.logger.error(f"Selenium parsing failed for {url}: {str(e)}")
            raise
    
    def scrape_url(self, url: str) -> ScrapingResult:
        """
        Scrape a single URL and return structured data
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapingResult object with scraped data
        """
        if not validate_url(url):
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                data={},
                timestamp=datetime.now(),
                error_message="Invalid URL"
            )
        
        try:
            self.logger.info(f"Scraping {url}")
            
            if self.use_selenium:
                soup = self._parse_with_selenium(url)
                status_code = 200  # Selenium doesn't provide status codes directly
            else:
                response = self._make_request(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                status_code = response.status_code
            
            # Extract data using custom extractor or default method
            if self.custom_extractor:
                data = self.custom_extractor(soup)
            else:
                data = self._default_extract(soup, url)
            
            return ScrapingResult(
                url=url,
                status_code=status_code,
                success=True,
                data=data,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {str(e)}")
            return ScrapingResult(
                url=url,
                status_code=0,
                success=False,
                data={},
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def _default_extract(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Default data extraction method"""
        data = {
            'url': url,
            'title': '',
            'meta_description': '',
            'headings': [],
            'links': [],
            'images': [],
            'text_content': '',
            'word_count': 0
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = clean_text(title_tag.text)
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data['meta_description'] = clean_text(meta_desc.get('content', ''))
        
        # Extract headings
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for heading in headings:
                data['headings'].append({
                    'level': i,
                    'text': clean_text(heading.text)
                })
        
        # Extract links
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            data['links'].append({
                'url': absolute_url,
                'text': clean_text(link.text),
                'title': link.get('title', '')
            })
        
        # Extract images
        for img in soup.find_all('img', src=True):
            absolute_url = urljoin(url, img['src'])
            data['images'].append({
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        # Extract text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        data['text_content'] = clean_text(text)
        data['word_count'] = len(data['text_content'].split())
        
        return data
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[ScrapingResult]:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of ScrapingResult objects
        """
        results = []
        total = len(urls)
        
        self.logger.info(f"Starting to scrape {total} URLs")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Scraping URL {i}/{total}: {url}")
            result = self.scrape_url(url)
            results.append(result)
            
            # Progress logging
            if i % 10 == 0 or i == total:
                success_count = sum(1 for r in results if r.success)
                self.logger.info(f"Progress: {i}/{total} completed, {success_count} successful")
        
        return results
    
    def set_custom_extractor(self, extractor_func: Callable[[BeautifulSoup], Dict[str, Any]]):
        """
        Set a custom data extraction function
        
        Args:
            extractor_func: Function that takes BeautifulSoup object and returns dict
        """
        self.custom_extractor = extractor_func
        self.logger.info("Custom extractor function set")
    
    def save_data(self, data: Union[ScrapingResult, List[ScrapingResult]], 
                  filename: str, format: str = 'json'):
        """
        Save scraped data to file
        
        Args:
            data: ScrapingResult or list of ScrapingResults
            filename: Output filename
            format: Output format ('json', 'csv', 'xlsx')
        """
        self.storage.save(data, filename, format)
        self.logger.info(f"Data saved to {filename}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            **self.stats,
            'success_rate': (self.stats['successful_requests'] / max(1, self.stats['requests_made'])) * 100,
            'average_delay': self.stats['total_delay_time'] / max(1, self.stats['requests_made'])
        }
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        if hasattr(self.session, 'close'):
            self.session.close()
        self.logger.info("WebScraper resources cleaned up")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncWebScraper:
    """
    Asynchronous web scraper for better performance with multiple URLs
    """
    
    def __init__(self, 
                 max_concurrent: int = 10,
                 delay: float = 1.0,
                 timeout: int = 30,
                 user_agent: Optional[str] = None):
        """
        Initialize AsyncWebScraper
        
        Args:
            max_concurrent: Maximum number of concurrent requests
            delay: Delay between requests
            timeout: Request timeout
            user_agent: Custom user agent
        """
        self.max_concurrent = max_concurrent
        self.delay = delay
        self.timeout = timeout
        self.user_agent = user_agent or UserAgent().random
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        self.logger = setup_logging('async_web_scraper')
    
    async def _fetch_url(self, session: aiohttp.ClientSession, url: str) -> ScrapingResult:
        """Fetch a single URL asynchronously"""
        async with self.semaphore:
            try:
                # Rate limiting
                await asyncio.sleep(self.delay)
                
                async with session.get(url) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    # Basic data extraction
                    data = {
                        'url': url,
                        'title': soup.find('title').text if soup.find('title') else '',
                        'text_length': len(text)
                    }
                    
                    return ScrapingResult(
                        url=url,
                        status_code=response.status,
                        success=True,
                        data=data,
                        timestamp=datetime.now()
                    )
            
            except Exception as e:
                return ScrapingResult(
                    url=url,
                    status_code=0,
                    success=False,
                    data={},
                    timestamp=datetime.now(),
                    error_message=str(e)
                )
    
    async def scrape_multiple_async(self, urls: List[str]) -> List[ScrapingResult]:
        """
        Scrape multiple URLs asynchronously
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of ScrapingResult objects
        """
        headers = {'User-Agent': self.user_agent}
        
        async with aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            
            tasks = [self._fetch_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            
        return results
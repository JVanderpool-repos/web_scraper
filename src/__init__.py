"""
Web Scraper Package Initialization
"""

from .scraper import WebScraper, AsyncWebScraper, ScrapingResult
from .storage import DataStorage, DataValidator
from .utils import (
    setup_logging, clean_text, parse_price, validate_url,
    extract_domain, safe_filename, extract_numbers,
    get_file_extension, truncate_text, extract_email_addresses,
    extract_phone_numbers, create_user_agents, format_file_size,
    is_image_url, normalize_whitespace
)

__version__ = "1.0.0"
__author__ = "Web Scraper Team"
__description__ = "A comprehensive and flexible web scraping framework"

__all__ = [
    'WebScraper',
    'AsyncWebScraper', 
    'ScrapingResult',
    'DataStorage',
    'DataValidator',
    'setup_logging',
    'clean_text',
    'parse_price',
    'validate_url',
    'extract_domain',
    'safe_filename',
    'extract_numbers',
    'get_file_extension',
    'truncate_text',
    'extract_email_addresses',
    'extract_phone_numbers',
    'create_user_agents',
    'format_file_size',
    'is_image_url',
    'normalize_whitespace'
]
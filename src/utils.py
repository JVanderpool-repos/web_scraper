"""
Utility functions for web scraping
"""

import re
import logging
import os
from typing import Any, Optional
from urllib.parse import urlparse
from pathlib import Path
import unicodedata


def setup_logging(name: str, log_level: str = 'INFO') -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        name: Logger name
        log_level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid adding multiple handlers
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_dir / f'{name}.log')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove control characters but keep basic punctuation
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    return text.strip()


def parse_price(price_text: str) -> Optional[float]:
    """
    Extract numeric price from text
    
    Args:
        price_text: Text containing price information
        
    Returns:
        Numeric price or None if not found
    """
    if not price_text:
        return None
    
    # Remove currency symbols and extract number
    price_pattern = r'[\d,]+\.?\d*'
    matches = re.findall(price_pattern, price_text.replace(',', ''))
    
    if matches:
        try:
            return float(matches[0])
        except ValueError:
            pass
    
    return None


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""


def safe_filename(filename: str) -> str:
    """
    Convert string to safe filename
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename for filesystem
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def extract_numbers(text: str) -> list:
    """
    Extract all numbers from text
    
    Args:
        text: Text to extract numbers from
        
    Returns:
        List of numbers found
    """
    if not text:
        return []
    
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return [float(n) if '.' in n else int(n) for n in numbers]


def get_file_extension(url: str) -> str:
    """
    Get file extension from URL
    
    Args:
        url: URL to check
        
    Returns:
        File extension or empty string
    """
    try:
        parsed = urlparse(url)
        path = parsed.path
        return os.path.splitext(path)[1].lower()
    except:
        return ""


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def extract_email_addresses(text: str) -> list:
    """
    Extract email addresses from text
    
    Args:
        text: Text to search
        
    Returns:
        List of email addresses found
    """
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> list:
    """
    Extract phone numbers from text
    
    Args:
        text: Text to search
        
    Returns:
        List of phone numbers found
    """
    if not text:
        return []
    
    # Simple pattern for common phone number formats
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    matches = re.findall(phone_pattern, text)
    
    return [f"({area}){exchange}-{number}" for area, exchange, number in matches]


def create_user_agents() -> list:
    """
    Create a list of common user agents
    
    Returns:
        List of user agent strings
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return user_agents


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def is_image_url(url: str) -> bool:
    """
    Check if URL points to an image
    
    Args:
        url: URL to check
        
    Returns:
        True if URL appears to be an image
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
    extension = get_file_extension(url)
    return extension in image_extensions


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
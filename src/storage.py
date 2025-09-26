"""
Data Storage Module

Handles saving scraped data to various formats including JSON, CSV, Excel, 
and database storage with support for different data structures.
"""

import json
import csv
import pandas as pd
import sqlite3
import logging
import os
from typing import Dict, List, Any, Union, Optional
from datetime import datetime
from pathlib import Path
import pymongo
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pickle

from .utils import setup_logging, safe_filename


Base = declarative_base()


class ScrapedData(Base):
    """SQLAlchemy model for scraped data"""
    __tablename__ = 'scraped_data'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(500))
    content = Column(Text)
    scraped_metadata = Column(Text)  # JSON string - renamed to avoid conflict
    timestamp = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)
    status_code = Column(Integer)
    error_message = Column(Text)


class DataStorage:
    """
    Comprehensive data storage class supporting multiple formats and destinations
    """
    
    def __init__(self, 
                 data_dir: str = "data",
                 db_url: str = None,
                 mongo_url: str = None):
        """
        Initialize DataStorage
        
        Args:
            data_dir: Directory for file-based storage
            db_url: SQL database URL
            mongo_url: MongoDB connection URL
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.db_url = db_url
        self.mongo_url = mongo_url
        self.logger = setup_logging('data_storage')
        
        # Initialize database connections
        self._setup_sql_database()
        self._setup_mongodb()
    
    def _setup_sql_database(self):
        """Setup SQL database connection"""
        if self.db_url:
            try:
                self.engine = create_engine(self.db_url)
                Base.metadata.create_all(self.engine)
                Session = sessionmaker(bind=self.engine)
                self.session = Session()
                self.logger.info("SQL database connection established")
            except Exception as e:
                self.logger.error(f"Failed to setup SQL database: {str(e)}")
                self.engine = None
                self.session = None
        else:
            self.engine = None
            self.session = None
    
    def _setup_mongodb(self):
        """Setup MongoDB connection"""
        if self.mongo_url:
            try:
                self.mongo_client = pymongo.MongoClient(self.mongo_url)
                self.mongo_db = self.mongo_client.scraper
                self.mongo_collection = self.mongo_db.scraped_data
                self.logger.info("MongoDB connection established")
            except Exception as e:
                self.logger.error(f"Failed to setup MongoDB: {str(e)}")
                self.mongo_client = None
                self.mongo_db = None
                self.mongo_collection = None
        else:
            self.mongo_client = None
            self.mongo_db = None
            self.mongo_collection = None
    
    def save(self, data, filename: str, format: str = 'json', **kwargs):
        """
        Save data in specified format
        
        Args:
            data: Data to save (ScrapingResult or list of ScrapingResults)
            filename: Output filename
            format: Output format ('json', 'csv', 'xlsx', 'sql', 'mongodb', 'pickle')
            **kwargs: Additional format-specific options
        """
        # Ensure data is in list format for consistent handling
        if not isinstance(data, list):
            data = [data]
        
        # Convert ScrapingResult objects to dictionaries if needed
        processed_data = []
        for item in data:
            if hasattr(item, '__dict__'):
                # Convert dataclass/object to dict
                item_dict = item.__dict__ if hasattr(item, '__dict__') else item
                # Handle datetime serialization
                if 'timestamp' in item_dict and isinstance(item_dict['timestamp'], datetime):
                    item_dict['timestamp'] = item_dict['timestamp'].isoformat()
                processed_data.append(item_dict)
            else:
                processed_data.append(item)
        
        # Route to appropriate save method
        save_methods = {
            'json': self._save_json,
            'csv': self._save_csv,
            'xlsx': self._save_xlsx,
            'excel': self._save_xlsx,  # Alias
            'sql': self._save_sql,
            'mongodb': self._save_mongodb,
            'mongo': self._save_mongodb,  # Alias
            'pickle': self._save_pickle,
            'pkl': self._save_pickle  # Alias
        }
        
        if format.lower() not in save_methods:
            raise ValueError(f"Unsupported format: {format}")
        
        save_methods[format.lower()](processed_data, filename, **kwargs)
        self.logger.info(f"Saved {len(processed_data)} records to {filename} in {format} format")
    
    def _save_json(self, data: List[Dict], filename: str, **kwargs):
        """Save data as JSON"""
        filepath = self.data_dir / safe_filename(filename)
        
        # Ensure .json extension
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str, **kwargs)
    
    def _save_csv(self, data: List[Dict], filename: str, **kwargs):
        """Save data as CSV"""
        if not data:
            return
        
        filepath = self.data_dir / safe_filename(filename)
        
        # Ensure .csv extension
        if not filepath.suffix:
            filepath = filepath.with_suffix('.csv')
        
        # Flatten nested dictionaries for CSV format
        flattened_data = []
        for item in data:
            flat_item = self._flatten_dict(item)
            flattened_data.append(flat_item)
        
        # Get all unique keys for CSV headers
        all_keys = set()
        for item in flattened_data:
            all_keys.update(item.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, **kwargs)
            writer.writeheader()
            writer.writerows(flattened_data)
    
    def _save_xlsx(self, data: List[Dict], filename: str, **kwargs):
        """Save data as Excel file"""
        if not data:
            return
        
        filepath = self.data_dir / safe_filename(filename)
        
        # Ensure .xlsx extension
        if not filepath.suffix:
            filepath = filepath.with_suffix('.xlsx')
        
        # Flatten data for Excel
        flattened_data = [self._flatten_dict(item) for item in data]
        
        # Create DataFrame and save
        df = pd.DataFrame(flattened_data)
        df.to_excel(filepath, index=False, **kwargs)
    
    def _save_sql(self, data: List[Dict], table_name: str, **kwargs):
        """Save data to SQL database"""
        if not self.session:
            raise RuntimeError("SQL database not configured")
        
        for item in data:
            record = ScrapedData(
                url=item.get('url', ''),
                title=item.get('data', {}).get('title', ''),
                content=json.dumps(item.get('data', {})),
                scraped_metadata=json.dumps({k: v for k, v in item.items() if k != 'data'}),
                timestamp=datetime.fromisoformat(item['timestamp']) if isinstance(item.get('timestamp'), str) else item.get('timestamp', datetime.now()),
                success=item.get('success', True),
                status_code=item.get('status_code', 200),
                error_message=item.get('error_message')
            )
            self.session.add(record)
        
        self.session.commit()
    
    def _save_mongodb(self, data: List[Dict], collection_name: str = None, **kwargs):
        """Save data to MongoDB"""
        if not self.mongo_collection:
            raise RuntimeError("MongoDB not configured")
        
        collection = self.mongo_collection
        if collection_name:
            collection = self.mongo_db[collection_name]
        
        # Convert timestamp strings back to datetime objects
        for item in data:
            if 'timestamp' in item and isinstance(item['timestamp'], str):
                try:
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                except ValueError:
                    pass  # Keep as string if conversion fails
        
        collection.insert_many(data, **kwargs)
    
    def _save_pickle(self, data: List[Dict], filename: str, **kwargs):
        """Save data as pickle file"""
        filepath = self.data_dir / safe_filename(filename)
        
        # Ensure .pkl extension
        if not filepath.suffix:
            filepath = filepath.with_suffix('.pkl')
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f, **kwargs)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary"""
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to JSON strings for flat storage
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def load_json(self, filename: str) -> List[Dict]:
        """Load data from JSON file"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_csv(self, filename: str) -> List[Dict]:
        """Load data from CSV file"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        return data
    
    def load_excel(self, filename: str, sheet_name: str = 0) -> List[Dict]:
        """Load data from Excel file"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        df = pd.read_excel(filepath, sheet_name=sheet_name)
        return df.to_dict('records')
    
    def query_sql(self, query: str) -> List[Dict]:
        """Execute SQL query and return results"""
        if not self.engine:
            raise RuntimeError("SQL database not configured")
        
        df = pd.read_sql_query(query, self.engine)
        return df.to_dict('records')
    
    def query_mongodb(self, filter_dict: Dict = None, collection_name: str = None) -> List[Dict]:
        """Query MongoDB and return results"""
        if not self.mongo_collection:
            raise RuntimeError("MongoDB not configured")
        
        collection = self.mongo_collection
        if collection_name:
            collection = self.mongo_db[collection_name]
        
        filter_dict = filter_dict or {}
        cursor = collection.find(filter_dict)
        
        results = []
        for doc in cursor:
            # Convert ObjectId to string
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            results.append(doc)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            'data_directory': str(self.data_dir),
            'files_count': len(list(self.data_dir.glob('*'))),
            'sql_configured': self.session is not None,
            'mongodb_configured': self.mongo_collection is not None
        }
        
        # Add file size information
        total_size = 0
        file_info = []
        for file_path in self.data_dir.glob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                file_info.append({
                    'name': file_path.name,
                    'size': size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        stats['total_size_bytes'] = total_size
        stats['files'] = file_info
        
        # SQL stats
        if self.session:
            try:
                count = self.session.query(ScrapedData).count()
                stats['sql_records_count'] = count
            except:
                stats['sql_records_count'] = 'N/A'
        
        # MongoDB stats
        if self.mongo_collection:
            try:
                count = self.mongo_collection.count_documents({})
                stats['mongodb_records_count'] = count
            except:
                stats['mongodb_records_count'] = 'N/A'
        
        return stats
    
    def backup_data(self, backup_name: str = None):
        """Create backup of all data"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.data_dir / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup files
        import shutil
        for file_path in self.data_dir.glob('*'):
            if file_path.is_file():
                shutil.copy2(file_path, backup_dir)
        
        self.logger.info(f"Backup created at {backup_dir}")
        return str(backup_dir)
    
    def close(self):
        """Close database connections"""
        if self.session:
            self.session.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        self.logger.info("Data storage connections closed")


class DataValidator:
    """
    Data validation utilities for scraped content
    """
    
    @staticmethod
    def validate_url_data(data: Dict) -> bool:
        """Validate that scraped URL data has required fields"""
        required_fields = ['url', 'timestamp', 'success']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_product_data(data: Dict) -> bool:
        """Validate product scraping data"""
        product_fields = ['name', 'price', 'url']
        return all(field in data.get('data', {}) for field in product_fields)
    
    @staticmethod
    def clean_scraped_data(data: List[Dict]) -> List[Dict]:
        """Clean and normalize scraped data"""
        cleaned_data = []
        
        for item in data:
            # Skip items without required fields
            if not DataValidator.validate_url_data(item):
                continue
            
            # Ensure data field exists
            if 'data' not in item:
                item['data'] = {}
            
            # Clean text fields
            if 'title' in item['data']:
                item['data']['title'] = str(item['data']['title']).strip()
            
            # Ensure success is boolean
            item['success'] = bool(item.get('success', False))
            
            # Ensure status_code is integer
            if 'status_code' in item:
                try:
                    item['status_code'] = int(item['status_code'])
                except (ValueError, TypeError):
                    item['status_code'] = 0
            
            cleaned_data.append(item)
        
        return cleaned_data
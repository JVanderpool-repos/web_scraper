"""
Monitoring and Logging Module

Provides comprehensive monitoring, progress tracking, and advanced logging
capabilities for web scraping operations.
"""

import logging
import logging.handlers
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import json
import psutil
import os
from collections import defaultdict, deque
import statistics


@dataclass
class ScrapingMetrics:
    """Data class for scraping metrics"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_urls: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_bytes_downloaded: int = 0
    total_processing_time: float = 0.0
    average_response_time: float = 0.0
    requests_per_second: float = 0.0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    status_codes: Dict[int, int] = field(default_factory=dict)
    domain_stats: Dict[str, int] = field(default_factory=dict)
    
    @property
    def duration(self) -> timedelta:
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def success_rate(self) -> float:
        total = self.successful_requests + self.failed_requests
        return (self.successful_requests / total * 100) if total > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization"""
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration.total_seconds(),
            'total_urls': self.total_urls,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.success_rate,
            'total_bytes_downloaded': self.total_bytes_downloaded,
            'total_processing_time': self.total_processing_time,
            'average_response_time': self.average_response_time,
            'requests_per_second': self.requests_per_second,
            'errors_by_type': self.errors_by_type,
            'status_codes': self.status_codes,
            'domain_stats': self.domain_stats
        }


class PerformanceMonitor:
    """
    Monitor system performance during scraping operations
    """
    
    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.monitoring = False
        self.thread = None
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 measurements
        
    def start_monitoring(self):
        """Start performance monitoring in background thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_percent': psutil.cpu_percent(interval=None),
                    'memory_percent': psutil.virtual_memory().percent,
                    'memory_used_mb': psutil.virtual_memory().used / 1024 / 1024,
                    'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                    'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
                    'process_count': len(psutil.pids())
                }
                
                self.metrics_history.append(metrics)
                
            except Exception as e:
                # Silently continue if monitoring fails
                pass
            
            time.sleep(self.interval)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        if not recent_metrics:
            return {}
        
        # Calculate averages
        avg_cpu = statistics.mean([m['cpu_percent'] for m in recent_metrics])
        avg_memory = statistics.mean([m['memory_percent'] for m in recent_metrics])
        current_memory_mb = recent_metrics[-1]['memory_used_mb']
        
        return {
            'avg_cpu_percent': round(avg_cpu, 2),
            'avg_memory_percent': round(avg_memory, 2),
            'current_memory_mb': round(current_memory_mb, 2),
            'measurements_count': len(recent_metrics),
            'monitoring_duration_minutes': len(self.metrics_history) * self.interval / 60
        }
    
    def export_metrics(self, filepath: str):
        """Export collected metrics to JSON file"""
        metrics_data = {
            'export_time': datetime.now().isoformat(),
            'total_measurements': len(self.metrics_history),
            'interval_seconds': self.interval,
            'metrics': list(self.metrics_history)
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)


class ScrapingLogger:
    """
    Advanced logging system for web scraping with structured logging,
    rotation, and different log levels for various components.
    """
    
    def __init__(self, 
                 name: str = 'web_scraper',
                 log_dir: str = 'logs',
                 level: str = 'INFO',
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_structured: bool = True):
        
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        
        self.console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        self.json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "line": %(lineno)d}'
        )
        
        # Setup handlers
        if enable_console:
            self._setup_console_handler()
        
        if enable_file:
            self._setup_file_handlers(max_file_size, backup_count)
        
        if enable_structured:
            self._setup_structured_handler(max_file_size, backup_count)
    
    def _setup_console_handler(self):
        """Setup console logging handler"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self, max_size: int, backup_count: int):
        """Setup rotating file handlers for different log levels"""
        # General log file
        general_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{self.name}.log',
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        general_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(general_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{self.name}_errors.log',
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(error_handler)
    
    def _setup_structured_handler(self, max_size: int, backup_count: int):
        """Setup structured JSON logging"""
        json_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f'{self.name}_structured.log',
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setFormatter(self.json_formatter)
        self.logger.addHandler(json_handler)
    
    def log_request(self, url: str, method: str = 'GET', status_code: int = None, 
                   response_time: float = None, error: str = None):
        """Log HTTP request details"""
        details = {
            'url': url,
            'method': method,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2) if response_time else None,
            'error': error
        }
        
        message = f"REQUEST {method} {url}"
        if status_code:
            message += f" -> {status_code}"
        if response_time:
            message += f" ({response_time*1000:.1f}ms)"
        if error:
            message += f" ERROR: {error}"
        
        if error or (status_code and status_code >= 400):
            self.logger.error(message)
        else:
            self.logger.info(message)
    
    def log_extraction(self, url: str, items_extracted: int, extraction_time: float = None):
        """Log data extraction results"""
        message = f"EXTRACTION {url} -> {items_extracted} items"
        if extraction_time:
            message += f" ({extraction_time*1000:.1f}ms)"
        
        self.logger.info(message)
    
    def log_storage(self, format_type: str, filename: str, record_count: int, 
                   file_size: int = None):
        """Log data storage operations"""
        message = f"STORAGE {format_type.upper()} {filename} -> {record_count} records"
        if file_size:
            message += f" ({file_size / 1024:.1f}KB)"
        
        self.logger.info(message)
    
    def log_metrics(self, metrics: ScrapingMetrics):
        """Log scraping session metrics"""
        message = (
            f"METRICS SESSION COMPLETE - "
            f"URLs: {metrics.total_urls}, "
            f"Success: {metrics.successful_requests}, "
            f"Failed: {metrics.failed_requests}, "
            f"Rate: {metrics.success_rate:.1f}%, "
            f"Duration: {metrics.duration.total_seconds():.1f}s"
        )
        
        self.logger.info(message)
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance"""
        return self.logger


class ProgressTracker:
    """
    Track and display progress for scraping operations
    """
    
    def __init__(self, total_items: int, update_interval: float = 1.0):
        self.total_items = total_items
        self.current_item = 0
        self.start_time = datetime.now()
        self.update_interval = update_interval
        self.last_update = 0
        self.completed_items = []
        self.failed_items = []
        
    def update(self, increment: int = 1, item_info: Dict[str, Any] = None):
        """Update progress counter"""
        self.current_item += increment
        
        if item_info:
            if item_info.get('success', False):
                self.completed_items.append(item_info)
            else:
                self.failed_items.append(item_info)
        
        # Check if we should display progress
        now = time.time()
        if now - self.last_update >= self.update_interval:
            self._display_progress()
            self.last_update = now
    
    def _display_progress(self):
        """Display current progress"""
        if self.total_items == 0:
            return
            
        percentage = (self.current_item / self.total_items) * 100
        elapsed = datetime.now() - self.start_time
        
        if self.current_item > 0:
            avg_time_per_item = elapsed.total_seconds() / self.current_item
            remaining_items = self.total_items - self.current_item
            eta_seconds = avg_time_per_item * remaining_items
            eta = timedelta(seconds=int(eta_seconds))
        else:
            eta = timedelta(0)
        
        # Progress bar
        bar_length = 30
        filled_length = int(bar_length * percentage // 100)
        bar = '█' * filled_length + '▒' * (bar_length - filled_length)
        
        print(f'\r📊 Progress: |{bar}| {percentage:.1f}% '
              f'({self.current_item}/{self.total_items}) '
              f'ETA: {eta} '
              f'✅{len(self.completed_items)} ❌{len(self.failed_items)}', end='')
        
        if self.current_item >= self.total_items:
            print()  # New line when complete
    
    def finish(self):
        """Mark progress as finished and display final stats"""
        self.current_item = self.total_items
        self._display_progress()
        
        duration = datetime.now() - self.start_time
        success_rate = (len(self.completed_items) / self.total_items * 100) if self.total_items > 0 else 0
        
        print(f"\n✨ Scraping completed in {duration.total_seconds():.1f}s")
        print(f"📈 Success rate: {success_rate:.1f}% ({len(self.completed_items)}/{self.total_items})")


class ScrapingMonitor:
    """
    Comprehensive monitoring system that combines logging, metrics, and progress tracking
    """
    
    def __init__(self, name: str = 'scraping_session'):
        self.name = name
        self.metrics = ScrapingMetrics()
        self.logger = ScrapingLogger(name)
        self.performance_monitor = PerformanceMonitor()
        self.progress_tracker = None
        self.alerts = []
        
        # Thresholds for alerts
        self.error_rate_threshold = 20.0  # %
        self.response_time_threshold = 10.0  # seconds
        self.memory_threshold = 80.0  # %
        
    def start_session(self, total_urls: int = None):
        """Start a monitoring session"""
        self.metrics = ScrapingMetrics()
        self.metrics.total_urls = total_urls or 0
        
        if total_urls:
            self.progress_tracker = ProgressTracker(total_urls)
        
        self.performance_monitor.start_monitoring()
        self.logger.get_logger().info(f"Starting scraping session: {self.name}")
        
        if total_urls:
            self.logger.get_logger().info(f"Target URLs: {total_urls}")
    
    def log_request(self, url: str, success: bool, status_code: int = None,
                   response_time: float = None, error: str = None, content_size: int = None):
        """Log a request and update metrics"""
        # Update metrics
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            if error:
                self.metrics.errors_by_type[error] = self.metrics.errors_by_type.get(error, 0) + 1
        
        if status_code:
            self.metrics.status_codes[status_code] = self.metrics.status_codes.get(status_code, 0) + 1
        
        if response_time:
            self.metrics.total_processing_time += response_time
            total_requests = self.metrics.successful_requests + self.metrics.failed_requests
            self.metrics.average_response_time = self.metrics.total_processing_time / total_requests
        
        if content_size:
            self.metrics.total_bytes_downloaded += content_size
        
        # Update domain stats
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            self.metrics.domain_stats[domain] = self.metrics.domain_stats.get(domain, 0) + 1
        except:
            pass
        
        # Log request
        self.logger.log_request(url, 'GET', status_code, response_time, error)
        
        # Update progress
        if self.progress_tracker:
            self.progress_tracker.update(1, {
                'url': url,
                'success': success,
                'status_code': status_code,
                'response_time': response_time
            })
        
        # Check for alerts
        self._check_alerts()
    
    def _check_alerts(self):
        """Check for conditions that should trigger alerts"""
        total_requests = self.metrics.successful_requests + self.metrics.failed_requests
        
        if total_requests >= 10:  # Only check after some requests
            error_rate = (self.metrics.failed_requests / total_requests) * 100
            
            if error_rate > self.error_rate_threshold:
                alert = f"High error rate: {error_rate:.1f}% (threshold: {self.error_rate_threshold}%)"
                if alert not in self.alerts:
                    self.alerts.append(alert)
                    self.logger.get_logger().warning(f"ALERT: {alert}")
        
        if self.metrics.average_response_time > self.response_time_threshold:
            alert = f"Slow response times: {self.metrics.average_response_time:.2f}s average"
            if alert not in self.alerts:
                self.alerts.append(alert)
                self.logger.get_logger().warning(f"ALERT: {alert}")
        
        # Check system resources
        system_stats = self.performance_monitor.get_current_stats()
        if system_stats.get('avg_memory_percent', 0) > self.memory_threshold:
            alert = f"High memory usage: {system_stats['avg_memory_percent']:.1f}%"
            if alert not in self.alerts:
                self.alerts.append(alert)
                self.logger.get_logger().warning(f"ALERT: {alert}")
    
    def end_session(self):
        """End the monitoring session and generate final report"""
        self.metrics.end_time = datetime.now()
        
        # Calculate final metrics
        total_requests = self.metrics.successful_requests + self.metrics.failed_requests
        if total_requests > 0 and self.metrics.duration.total_seconds() > 0:
            self.metrics.requests_per_second = total_requests / self.metrics.duration.total_seconds()
        
        # Finish progress tracking
        if self.progress_tracker:
            self.progress_tracker.finish()
        
        # Stop performance monitoring
        self.performance_monitor.stop_monitoring()
        
        # Log final metrics
        self.logger.log_metrics(self.metrics)
        
        # Generate final report
        self._generate_final_report()
        
        self.logger.get_logger().info(f"Scraping session completed: {self.name}")
    
    def _generate_final_report(self):
        """Generate and save a comprehensive final report"""
        report = {
            'session_name': self.name,
            'metrics': self.metrics.to_dict(),
            'system_performance': self.performance_monitor.get_current_stats(),
            'alerts': self.alerts,
            'top_domains': dict(list(self.metrics.domain_stats.items())[:10]),
            'top_errors': dict(list(self.metrics.errors_by_type.items())[:5])
        }
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/scraping_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.get_logger().info(f"Final report saved: {report_file}")
        except Exception as e:
            self.logger.get_logger().error(f"Failed to save report: {str(e)}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            'metrics': self.metrics.to_dict(),
            'system_performance': self.performance_monitor.get_current_stats(),
            'alerts_count': len(self.alerts),
            'session_duration': self.metrics.duration.total_seconds()
        }
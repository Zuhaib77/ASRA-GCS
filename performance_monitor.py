"""
Performance Monitoring System
Tracks UI updates, tile loading times, memory usage, and system performance
"""

import time
import threading
import psutil
import logging
from collections import deque
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    ui_update_times: deque = field(default_factory=lambda: deque(maxlen=100))
    tile_download_times: deque = field(default_factory=lambda: deque(maxlen=50))
    memory_usage_history: deque = field(default_factory=lambda: deque(maxlen=60))
    cpu_usage_history: deque = field(default_factory=lambda: deque(maxlen=60))
    
    # Counters
    ui_updates_count: int = 0
    tiles_downloaded: int = 0
    tiles_cached: int = 0
    mavlink_messages_count: int = 0
    
    # Averages (calculated)
    avg_ui_update_time: float = 0.0
    avg_tile_download_time: float = 0.0
    avg_memory_usage: float = 0.0
    avg_cpu_usage: float = 0.0
    
    # Performance issues
    slow_ui_updates: int = 0  # Updates > 100ms
    failed_tile_downloads: int = 0
    high_memory_warnings: int = 0

class PerformanceMonitor:
    """Real-time performance monitoring for ASRA GCS"""
    
    def __init__(self, config=None):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.ui_update_threshold_ms = 100  # Warn if UI update > 100ms
        self.memory_threshold_mb = 512     # Warn if memory > 512MB
        self.cpu_threshold_percent = 80    # Warn if CPU > 80%
        
        # Monitoring intervals
        self.system_check_interval = 5.0   # seconds
        self.stats_log_interval = 60.0     # seconds
        
        self.last_stats_log = time.time()
        
    def start(self):
        """Start performance monitoring"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("Performance monitoring started")
            
    def stop(self):
        """Stop performance monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logging.info("Performance monitoring stopped")
        
    def log_ui_update_time(self, time_ms: float):
        """Log UI update time"""
        with self.lock:
            self.metrics.ui_update_times.append(time_ms)
            self.metrics.ui_updates_count += 1
            
            # Track slow updates
            if time_ms > self.ui_update_threshold_ms:
                self.metrics.slow_ui_updates += 1
                logging.warning(f"Slow UI update: {time_ms:.1f}ms")
                
            # Update average
            if self.metrics.ui_update_times:
                self.metrics.avg_ui_update_time = sum(self.metrics.ui_update_times) / len(self.metrics.ui_update_times)
                
    def log_tile_download_time(self, time_ms: float, success: bool = True):
        """Log tile download time"""
        with self.lock:
            if success:
                self.metrics.tile_download_times.append(time_ms)
                self.metrics.tiles_downloaded += 1
            else:
                self.metrics.failed_tile_downloads += 1
                
            # Update average
            if self.metrics.tile_download_times:
                self.metrics.avg_tile_download_time = sum(self.metrics.tile_download_times) / len(self.metrics.tile_download_times)
                
    def log_tile_cached(self):
        """Log tile cache hit"""
        with self.lock:
            self.metrics.tiles_cached += 1
            
    def log_mavlink_message(self):
        """Log MAVLink message received"""
        with self.lock:
            self.metrics.mavlink_messages_count += 1
            
    def get_cache_hit_rate(self) -> float:
        """Calculate tile cache hit rate"""
        with self.lock:
            total_requests = self.metrics.tiles_downloaded + self.metrics.tiles_cached
            if total_requests > 0:
                return (self.metrics.tiles_cached / total_requests) * 100
            return 0.0
            
    def get_current_stats(self) -> Dict:
        """Get current performance statistics"""
        with self.lock:
            # Get current system stats
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            cpu_percent = psutil.Process().cpu_percent()
            
            stats = {
                "ui": {
                    "avg_update_time_ms": round(self.metrics.avg_ui_update_time, 1),
                    "total_updates": self.metrics.ui_updates_count,
                    "slow_updates": self.metrics.slow_ui_updates,
                    "updates_per_sec": self._calculate_rate(self.metrics.ui_update_times, 1.0)
                },
                "tiles": {
                    "avg_download_time_ms": round(self.metrics.avg_tile_download_time, 1),
                    "total_downloaded": self.metrics.tiles_downloaded,
                    "total_cached": self.metrics.tiles_cached,
                    "cache_hit_rate_percent": round(self.get_cache_hit_rate(), 1),
                    "failed_downloads": self.metrics.failed_tile_downloads
                },
                "system": {
                    "memory_mb": round(memory_mb, 1),
                    "cpu_percent": round(cpu_percent, 1),
                    "avg_memory_mb": round(self.metrics.avg_memory_usage, 1),
                    "avg_cpu_percent": round(self.metrics.avg_cpu_usage, 1)
                },
                "mavlink": {
                    "total_messages": self.metrics.mavlink_messages_count,
                    "messages_per_sec": self._calculate_mavlink_rate()
                }
            }
            
            return stats
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_system_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # System resource monitoring
                if current_time - last_system_check >= self.system_check_interval:
                    self._check_system_resources()
                    last_system_check = current_time
                    
                # Log periodic stats
                if current_time - self.last_stats_log >= self.stats_log_interval:
                    self._log_performance_stats()
                    self.last_stats_log = current_time
                    
                time.sleep(1.0)  # Check every second
                
            except Exception as e:
                logging.error(f"Performance monitoring error: {e}")
                time.sleep(5.0)  # Back off on errors
                
    def _check_system_resources(self):
        """Check and log system resource usage"""
        try:
            # Get current process stats
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            
            with self.lock:
                self.metrics.memory_usage_history.append(memory_mb)
                self.metrics.cpu_usage_history.append(cpu_percent)
                
                # Update averages
                if self.metrics.memory_usage_history:
                    self.metrics.avg_memory_usage = sum(self.metrics.memory_usage_history) / len(self.metrics.memory_usage_history)
                if self.metrics.cpu_usage_history:
                    self.metrics.avg_cpu_usage = sum(self.metrics.cpu_usage_history) / len(self.metrics.cpu_usage_history)
                
                # Check thresholds
                if memory_mb > self.memory_threshold_mb:
                    self.metrics.high_memory_warnings += 1
                    logging.warning(f"High memory usage: {memory_mb:.1f}MB")
                    
                if cpu_percent > self.cpu_threshold_percent:
                    logging.warning(f"High CPU usage: {cpu_percent:.1f}%")
                    
        except Exception as e:
            logging.error(f"System resource check error: {e}")
            
    def _log_performance_stats(self):
        """Log performance statistics"""
        try:
            stats = self.get_current_stats()
            
            logging.info("=== Performance Stats ===")
            logging.info(f"UI: {stats['ui']['avg_update_time_ms']}ms avg, {stats['ui']['total_updates']} updates, {stats['ui']['slow_updates']} slow")
            logging.info(f"Tiles: {stats['tiles']['cache_hit_rate_percent']}% hit rate, {stats['tiles']['avg_download_time_ms']}ms avg download")
            logging.info(f"System: {stats['system']['memory_mb']}MB RAM, {stats['system']['cpu_percent']}% CPU")
            logging.info(f"MAVLink: {stats['mavlink']['messages_per_sec']:.1f} msg/sec")
            
        except Exception as e:
            logging.error(f"Stats logging error: {e}")
            
    def _calculate_rate(self, times_deque: deque, window_seconds: float) -> float:
        """Calculate rate over time window"""
        if not times_deque:
            return 0.0
            
        current_time = time.time()
        recent_times = [t for t in times_deque if current_time - t < window_seconds]
        return len(recent_times) / window_seconds
        
    def _calculate_mavlink_rate(self) -> float:
        """Calculate MAVLink message rate"""
        # Simple rate calculation over last 10 seconds
        # This could be improved with timestamp tracking
        return self.metrics.mavlink_messages_count / max(1, time.time() - self.last_stats_log)
        
    def get_performance_summary(self) -> str:
        """Get human-readable performance summary"""
        stats = self.get_current_stats()
        
        summary = f"""
ASRA GCS Performance Summary:
-----------------------------
UI Performance:
  • Average update time: {stats['ui']['avg_update_time_ms']}ms
  • Total updates: {stats['ui']['total_updates']:,}
  • Slow updates (>{self.ui_update_threshold_ms}ms): {stats['ui']['slow_updates']}

Map Performance:
  • Tile cache hit rate: {stats['tiles']['cache_hit_rate_percent']}%
  • Average download time: {stats['tiles']['avg_download_time_ms']}ms
  • Tiles downloaded: {stats['tiles']['total_downloaded']:,}
  • Failed downloads: {stats['tiles']['failed_downloads']}

System Resources:
  • Memory usage: {stats['system']['memory_mb']:.1f}MB
  • CPU usage: {stats['system']['cpu_percent']:.1f}%
  • High memory warnings: {self.metrics.high_memory_warnings}

MAVLink:
  • Total messages: {stats['mavlink']['total_messages']:,}
  • Message rate: {stats['mavlink']['messages_per_sec']:.1f} msg/sec
        """
        
        return summary.strip()
        
    def reset_stats(self):
        """Reset all performance statistics"""
        with self.lock:
            self.metrics = PerformanceMetrics()
        logging.info("Performance statistics reset")

# Decorators for easy performance monitoring
def monitor_ui_update(monitor: PerformanceMonitor):
    """Decorator to monitor UI update performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                monitor.log_ui_update_time((end_time - start_time) * 1000)
        return wrapper
    return decorator

def monitor_tile_download(monitor: PerformanceMonitor):
    """Decorator to monitor tile download performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            try:
                result = func(*args, **kwargs)
                success = result is not None
                return result
            finally:
                end_time = time.time()
                monitor.log_tile_download_time((end_time - start_time) * 1000, success)
        return wrapper
    return decorator
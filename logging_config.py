"""
Advanced Logging Configuration for ASRA GCS
Provides structured logging with file rotation, console output, and performance optimization
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
from config import config

class ColoredConsoleHandler(logging.StreamHandler):
    """Console handler with colored output for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def emit(self, record):
        try:
            # Add color if terminal supports it
            if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
                color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
                record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
            
            super().emit(record)
        except Exception:
            self.handleError(record)

class PerformanceFormatter(logging.Formatter):
    """Custom formatter with performance information"""
    
    def __init__(self, fmt=None, datefmt=None, include_performance=False):
        super().__init__(fmt, datefmt)
        self.include_performance = include_performance
        self.start_time = datetime.now()
        
    def format(self, record):
        # Add custom fields
        record.uptime = str(datetime.now() - self.start_time).split('.')[0]
        
        # Add thread name for debugging
        if not hasattr(record, 'threadName') or record.threadName == 'MainThread':
            record.threadName = 'Main'
        
        # Shorten thread names for readability
        if record.threadName.startswith('Thread-'):
            record.threadName = f"T{record.threadName.split('-')[1]}"
        elif record.threadName.startswith('TileDownload'):
            record.threadName = "Tile"
        
        return super().format(record)

class ASRALogger:
    """Advanced logging system for ASRA GCS"""
    
    def __init__(self):
        self.loggers = {}
        self.handlers = []
        # Only setup logging if not disabled
        if not os.getenv("ASRA_DISABLE_AUTO_INIT"):
            self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        
        # Create logs directory
        log_dir = os.path.dirname(config.get("logging", "file_path", "logs/asra_gcs.log"))
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.get("logging", "level", "INFO")))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler with rotation
        if config.get("logging", "file_enabled", True):
            self._setup_file_handler(root_logger)
        
        # Console handler
        if config.get("logging", "console_enabled", True):
            self._setup_console_handler(root_logger)
        
        # Performance logger (separate file for performance metrics)
        self._setup_performance_logger()
        
        # Error logger (separate file for errors only)
        self._setup_error_logger()
        
        # MAVLink logger (separate file for MAVLink messages)
        self._setup_mavlink_logger()
        
        logging.info("ASRA GCS Logging System Initialized")
        
    def _setup_file_handler(self, logger):
        """Setup rotating file handler"""
        try:
            file_path = config.get("logging", "file_path", "logs/asra_gcs.log")
            max_bytes = config.get("logging", "file_max_size_mb", 10) * 1024 * 1024
            backup_count = config.get("logging", "file_backup_count", 5)
            
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            
            # Detailed format for file logging
            file_format = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(threadName)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            
            logger.addHandler(file_handler)
            self.handlers.append(file_handler)
            
        except Exception as e:
            print(f"Failed to setup file handler: {e}")
            
    def _setup_console_handler(self, logger):
        """Setup colored console handler"""
        try:
            console_handler = ColoredConsoleHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)  # Less verbose on console
            
            # Simpler format for console
            console_format = PerformanceFormatter(
                '%(asctime)s | %(levelname)-8s | %(threadName)-6s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_format)
            
            logger.addHandler(console_handler)
            self.handlers.append(console_handler)
            
        except Exception as e:
            print(f"Failed to setup console handler: {e}")
            
    def _setup_performance_logger(self):
        """Setup dedicated performance logger"""
        try:
            perf_logger = logging.getLogger('performance')
            perf_logger.setLevel(logging.INFO)
            perf_logger.propagate = False  # Don't propagate to root logger
            
            perf_handler = logging.handlers.RotatingFileHandler(
                'logs/performance.log',
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            )
            
            perf_format = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            perf_handler.setFormatter(perf_format)
            perf_logger.addHandler(perf_handler)
            
            self.loggers['performance'] = perf_logger
            
        except Exception as e:
            print(f"Failed to setup performance logger: {e}")
            
    def _setup_error_logger(self):
        """Setup dedicated error logger"""
        try:
            error_logger = logging.getLogger('errors')
            error_logger.setLevel(logging.ERROR)
            error_logger.propagate = True  # Also log to main log
            
            error_handler = logging.handlers.RotatingFileHandler(
                'logs/errors.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            error_format = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            error_handler.setFormatter(error_format)
            error_logger.addHandler(error_handler)
            
            self.loggers['errors'] = error_logger
            
        except Exception as e:
            print(f"Failed to setup error logger: {e}")
            
    def _setup_mavlink_logger(self):
        """Setup dedicated MAVLink message logger"""
        try:
            mavlink_logger = logging.getLogger('mavlink')
            mavlink_logger.setLevel(logging.DEBUG)
            mavlink_logger.propagate = False  # Don't spam main log
            
            mavlink_handler = logging.handlers.RotatingFileHandler(
                'logs/mavlink.log',
                maxBytes=20*1024*1024,  # 20MB (MAVLink can be verbose)
                backupCount=3
            )
            
            mavlink_format = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%H:%M:%S.%f'
            )
            mavlink_handler.setFormatter(mavlink_format)
            mavlink_logger.addHandler(mavlink_handler)
            
            self.loggers['mavlink'] = mavlink_logger
            
        except Exception as e:
            print(f"Failed to setup MAVLink logger: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger by name"""
        if name in self.loggers:
            return self.loggers[name]
        return logging.getLogger(name)
    
    def log_performance(self, message: str):
        """Log performance metrics"""
        if 'performance' in self.loggers:
            self.loggers['performance'].info(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log errors with optional exception info"""
        if 'errors' in self.loggers:
            if exception:
                self.loggers['errors'].exception(f"{message}: {str(exception)}")
            else:
                self.loggers['errors'].error(message)
    
    def log_mavlink(self, message: str):
        """Log MAVLink messages"""
        if 'mavlink' in self.loggers:
            self.loggers['mavlink'].debug(message)
    
    def flush_all(self):
        """Flush all log handlers"""
        for handler in self.handlers:
            try:
                handler.flush()
            except:
                pass
    
    def cleanup(self):
        """Cleanup logging system"""
        try:
            self.flush_all()
            
            # Close all handlers
            for handler in self.handlers:
                try:
                    handler.close()
                except:
                    pass
            
            # Clear loggers
            for logger in self.loggers.values():
                for handler in logger.handlers:
                    try:
                        handler.close()
                    except:
                        pass
                    
            logging.shutdown()
            
        except Exception as e:
            print(f"Error during logging cleanup: {e}")

# Logging utilities
def log_function_call(logger_name: str = None):
    """Decorator to log function calls with arguments"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            
            # Create argument string (limit length to avoid spam)
            arg_str = ', '.join([str(arg)[:50] for arg in args[1:5]])  # Skip self, limit to 4 args
            if len(args) > 5:
                arg_str += ', ...'
            
            if kwargs:
                kwarg_str = ', '.join([f"{k}={str(v)[:20]}" for k, v in list(kwargs.items())[:3]])
                if len(kwargs) > 3:
                    kwarg_str += ', ...'
                arg_str = f"{arg_str}, {kwarg_str}" if arg_str else kwarg_str
            
            logger.debug(f"Calling {func.__name__}({arg_str})")
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def log_execution_time(logger_name: str = None, threshold_ms: float = 100):
    """Decorator to log execution time if it exceeds threshold"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            logger = logging.getLogger(logger_name or func.__module__)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000
                if execution_time > threshold_ms:
                    logger.warning(f"Slow execution: {func.__name__} took {execution_time:.1f}ms")
        return wrapper
    return decorator

# Global logging instance
asra_logger = ASRALogger()

# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return asra_logger.get_logger(name)

def log_performance(message: str):
    """Log performance message"""
    asra_logger.log_performance(message)

def log_error(message: str, exception: Optional[Exception] = None):
    """Log error message"""
    asra_logger.log_error(message, exception)

def log_mavlink(message: str):
    """Log MAVLink message"""
    asra_logger.log_mavlink(message)

def cleanup_logging():
    """Cleanup logging system"""
    asra_logger.cleanup()

# Configure logging for external libraries to reduce noise
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
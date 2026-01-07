"""
ASRA GCS Configuration Management
Centralized configuration system with JSON file support and performance optimization settings
"""

import os
import json
import logging
from enum import Enum
from typing import Dict, Any, Optional

class MapProvider(Enum):
    """Free and open-source map providers only"""
    OPENSTREETMAP = "OpenStreetMap"
    OPENSTREETMAP_HOT = "OpenStreetMap HOT"
    CARTODB_POSITRON = "CartoDB Positron"
    CARTODB_DARK = "CartoDB Dark Matter"
    STAMEN_TERRAIN = "Stamen Terrain"
    STAMEN_TONER = "Stamen Toner"
    ESRI_SATELLITE = "Esri World Imagery"  # Free satellite imagery

class Config:
    """Centralized configuration management"""
    
    # Default configuration values
    _defaults = {
        # Application Settings
        "app": {
            "name": "ASRA Ground Control Station",
            "version": "2.0",
            "log_level": "INFO",
            "auto_save_config": True,
            "window_width": 1600,
            "window_height": 1000
        },
        
        # UI Performance Settings
        "ui": {
            "update_rate_ms": 100,  # Optimized from 150ms
            "button_feedback_ms": 150,  # Reduced from 200ms
            "smooth_updates": True,
            "vsync": True,
            "max_fps": 60
        },
        
        # Map Settings (Free providers only)
        "map": {
            "default_provider": MapProvider.ESRI_SATELLITE.value,
            "default_lat": 28.6139,  # Delhi - can be changed by user
            "default_lon": 77.2090,
            "default_zoom": 12,
            "min_zoom": 10,
            "max_zoom": 19,  # Tile provider maximum
            "tile_size": 256,
            "max_cache_tiles": 400,  # Optimized from 1000
            "cache_cleanup_threshold": 450,
            "preload_radius": 1,  # Tiles to preload around viewport
            "show_grid": False,
            "show_performance_stats": False
        },
        
        # Network & Tile Download Settings
        "network": {
            "max_concurrent_downloads": 4,  # Optimized from 12
            "download_timeout": 5,
            "retry_attempts": 2,
            "retry_delay": 0.1,
            "connection_pool_size": 10,  # Reduced from 20
            "user_agent": "ASRA-GCS/2.0"
        },
        
        # MAVLink Settings
        "mavlink": {
            "heartbeat_timeout": 3.0,
            "connection_timeout": 10.0,
            "max_reconnect_attempts": 3,
            "reconnect_delay": 2.0,
            "default_baud": 57600,
            "data_stream_rates": {
                "extended_status": 2,  # Hz
                "position": 5,  # Reduced from 10Hz
                "extra1": 5,   # Reduced from 10Hz  
                "extra2": 2    # Hz
            },
            "message_validation": True,
            "auto_reconnect": True
        },
        
        # Performance Monitoring
        "performance": {
            "enable_monitoring": True,
            "log_performance_stats": False,
            "ui_update_history_size": 100,
            "tile_download_history_size": 50,
            "memory_usage_check_interval": 30.0,  # seconds
            "max_memory_usage_mb": 512
        },
        
        # Logging Settings
        "logging": {
            "level": "INFO",
            "file_enabled": True,
            "file_path": "logs/asra_gcs.log",
            "file_max_size_mb": 10,
            "file_backup_count": 5,
            "console_enabled": True,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        
        # User Preferences
        "user": {
            "auto_center_on_uav": True,
            "flight_path_color": "#FF0000",
            "uav_marker_size": 20,
            "home_marker_size": 15,
            "waypoint_marker_size": 12,
            "geofence_color": "#FFFF00",
            "theme": "dark"
        }
    }
    
    # Free tile provider URLs (no API keys required)
    _provider_urls = {
        MapProvider.OPENSTREETMAP: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        MapProvider.OPENSTREETMAP_HOT: "https://tile-{s}.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        MapProvider.CARTODB_POSITRON: "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
        MapProvider.CARTODB_DARK: "https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png",
        MapProvider.STAMEN_TERRAIN: "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
        MapProvider.STAMEN_TONER: "https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png",
        MapProvider.ESRI_SATELLITE: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._defaults.copy()
        self._setup_directories()
        self.load()
        
    def _setup_directories(self):
        """Create necessary directories"""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("cache", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        
    def load(self) -> bool:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(self.config, user_config)
                logging.info(f"Configuration loaded from {self.config_file}")
                return True
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            logging.info("Using default configuration")
        return False
        
    def save(self) -> bool:
        """Save current configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            logging.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
            
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]):
        """Recursively merge user config with defaults"""
        for key, value in user.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
                    
    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            if key is None:
                return self.config.get(section, default)
            return self.config.get(section, {}).get(key, default)
        except:
            return default
            
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        
        if self.get("app", "auto_save_config", True):
            self.save()
            
    def get_provider_url(self, provider: MapProvider) -> str:
        """Get tile URL for provider"""
        return self._provider_urls.get(provider, self._provider_urls[MapProvider.OPENSTREETMAP])
        
    def get_available_providers(self) -> list:
        """Get list of available free map providers"""
        return [provider.value for provider in MapProvider]
        
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._defaults.copy()
        self.save()
        
    def validate_config(self) -> list:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate numeric ranges
        if not (1 <= self.get("map", "min_zoom") <= 22):
            issues.append("map.min_zoom must be between 1 and 22")
            
        if not (1 <= self.get("map", "max_zoom") <= 22):
            issues.append("map.max_zoom must be between 1 and 22")
            
        if not (50 <= self.get("map", "max_cache_tiles") <= 2000):
            issues.append("map.max_cache_tiles must be between 50 and 2000")
            
        if not (1 <= self.get("network", "max_concurrent_downloads") <= 20):
            issues.append("network.max_concurrent_downloads must be between 1 and 20")
            
        # Validate file paths
        log_dir = os.path.dirname(self.get("logging", "file_path"))
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except:
                issues.append(f"Cannot create log directory: {log_dir}")
                
        return issues

# Global configuration instance
config = Config()

# Performance-optimized settings based on config
class PerformanceSettings:
    """Performance settings derived from config"""
    
    @staticmethod
    def get_optimal_settings():
        """Get optimal performance settings based on system"""
        import psutil
        
        # Get system specs
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Adjust settings based on system capabilities
        optimal = {
            "ui_update_rate": 100 if memory_gb >= 8 else 150,
            "max_cache_tiles": min(400, int(memory_gb * 50)),
            "max_concurrent_downloads": min(6, cpu_count),
            "preload_radius": 1 if memory_gb >= 4 else 0,
            "enable_performance_monitoring": memory_gb >= 4
        }
        
        return optimal

# Export commonly used values
UI_UPDATE_RATE = config.get("ui", "update_rate_ms", 100)
BUTTON_FEEDBACK_DURATION = config.get("ui", "button_feedback_ms", 150)
MAX_CACHE_TILES = config.get("map", "max_cache_tiles", 400)
MAX_CONCURRENT_DOWNLOADS = config.get("network", "max_concurrent_downloads", 4)
HEARTBEAT_TIMEOUT = config.get("mavlink", "heartbeat_timeout", 3.0)
CONNECTION_TIMEOUT = config.get("mavlink", "connection_timeout", 10.0)
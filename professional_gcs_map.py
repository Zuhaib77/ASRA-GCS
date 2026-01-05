"""
Professional GCS Map Widget
High-performance mapping like Mission Planner and QGroundControl
Features: Satellite imagery, smooth pan/zoom, professional overlays, flight planning
"""

import math
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from collections import deque, OrderedDict
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import List, Tuple, Optional
import logging
import hashlib
import sqlite3
from PIL import Image
import io

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal, QThread, QMutex, QMutexLocker
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap, QPolygonF, QPainterPath
from PyQt5.QtWidgets import QWidget, QMenu, QAction

# Import our optimized config and monitoring
try:
    from config import config, MapProvider as ConfigMapProvider
    from performance_monitor import PerformanceMonitor, monitor_tile_download
    from logging_config import get_logger
except ImportError:
    # Fallback for standalone use
    config = None
    ConfigMapProvider = None
    PerformanceMonitor = None
    get_logger = logging.getLogger

class MapProvider(Enum):
    """Free and open-source map providers only"""
    OPENSTREETMAP = "OpenStreetMap"
    OPENSTREETMAP_HOT = "OpenStreetMap HOT"
    CARTODB_POSITRON = "CartoDB Positron"
    CARTODB_DARK = "CartoDB Dark Matter"
    STAMEN_TERRAIN = "Stamen Terrain"
    STAMEN_TONER = "Stamen Toner"
    ESRI_SATELLITE = "Esri World Imagery"

class FlightMode(Enum):
    """Flight modes for UAV display"""
    MANUAL = "Manual"
    STABILIZE = "Stabilize" 
    ALT_HOLD = "Alt Hold"
    AUTO = "Auto"
    GUIDED = "Guided"
    LOITER = "Loiter"
    RTL = "RTL"
    LAND = "Land"

class PersistentTileCache:
    """SQLite-based persistent tile cache for offline use"""
    
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.db_path = os.path.join(cache_dir, "tiles.db")
        self.logger = get_logger("tile_cache")
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for tile storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tiles (
                        key TEXT PRIMARY KEY,
                        provider TEXT,
                        z INTEGER,
                        x INTEGER,
                        y INTEGER,
                        data BLOB,
                        timestamp INTEGER,
                        size INTEGER
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_provider_z ON tiles(provider, z)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON tiles(timestamp)")
        except Exception as e:
            self.logger.error(f"Failed to initialize tile database: {e}")
    
    def get_tile_key(self, provider: str, z: int, x: int, y: int) -> str:
        """Generate unique key for tile"""
        return f"{provider}_{z}_{x}_{y}"
    
    def get_tile(self, provider: str, z: int, x: int, y: int) -> Optional[QPixmap]:
        """Get tile from cache"""
        try:
            key = self.get_tile_key(provider, z, x, y)
            # Use check_same_thread=False and timeout to prevent blocking
            with sqlite3.connect(self.db_path, timeout=0.5, check_same_thread=False) as conn:
                cursor = conn.execute("SELECT data FROM tiles WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(row[0]):
                        return pixmap
        except Exception as e:
            self.logger.debug(f"Cache miss for {provider} {z}/{x}/{y}: {e}")
        return None
    
    def store_tile(self, provider: str, z: int, x: int, y: int, data: bytes):
        """Store tile in cache (non-blocking)"""
        try:
            key = self.get_tile_key(provider, z, x, y)
            timestamp = int(time.time())
            size = len(data)
            
            # Use timeout and check_same_thread=False to prevent blocking
            with sqlite3.connect(self.db_path, timeout=0.5, check_same_thread=False) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO tiles (key, provider, z, x, y, data, timestamp, size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (key, provider, z, x, y, data, timestamp, size))
                
        except Exception as e:
            # Don't log errors aggressively to avoid spam
            pass
    
    def cleanup_old_tiles(self, max_age_days: int = 30, max_size_mb: int = 500):
        """Clean up old tiles to maintain cache size"""
        try:
            cutoff_time = int(time.time()) - (max_age_days * 24 * 3600)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            with sqlite3.connect(self.db_path) as conn:
                # Remove old tiles
                conn.execute("DELETE FROM tiles WHERE timestamp < ?", (cutoff_time,))
                
                # Check total size and remove oldest if needed
                cursor = conn.execute("SELECT SUM(size) FROM tiles")
                total_size = cursor.fetchone()[0] or 0
                
                if total_size > max_size_bytes:
                    # Remove oldest tiles until under limit
                    conn.execute("""
                        DELETE FROM tiles WHERE key IN (
                            SELECT key FROM tiles ORDER BY timestamp ASC 
                            LIMIT (SELECT COUNT(*) / 4 FROM tiles)
                        )
                    """)
                    
                conn.execute("VACUUM")
                
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")

class TileDownloadManager(QThread):
    """Optimized tile download manager with persistent cache"""
    tile_ready = pyqtSignal(int, int, int, bytes, str)  # z, x, y, raw_image_data, provider
    
    def __init__(self):
        super().__init__()
        self.download_queue = deque()
        self.active_downloads = set()
        self.running = True
        self.lock = threading.Lock()
        
        # Use config values if available
        max_workers = config.get("network", "max_concurrent_downloads", 4) if config else 4
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="TileDownload")
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor() if PerformanceMonitor else None
        self.logger = get_logger("tile_downloader")
        
        # Persistent cache
        self.cache = PersistentTileCache()
        
        # Statistics
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Optimized HTTP session for faster downloads
        self.session = requests.Session()
        
        # Use config values if available
        retry_total = config.get("network", "retry_attempts", 2) if config else 2
        retry_delay = config.get("network", "retry_delay", 0.1) if config else 0.1
        pool_size = config.get("network", "connection_pool_size", 10) if config else 10
        timeout = config.get("network", "download_timeout", 5) if config else 5
        
        retry_strategy = Retry(
            total=retry_total,
            backoff_factor=retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=pool_size, pool_maxsize=pool_size)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Free and open-source provider URLs only
        self.providers = {
            MapProvider.OPENSTREETMAP: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            MapProvider.OPENSTREETMAP_HOT: 'https://tile-{s}.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            MapProvider.CARTODB_POSITRON: 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
            MapProvider.CARTODB_DARK: 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png',
            MapProvider.STAMEN_TERRAIN: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            MapProvider.STAMEN_TONER: 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png',
            MapProvider.ESRI_SATELLITE: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
        }
        
        # Server list for providers that support multiple servers
        self.server_lists = {
            MapProvider.OPENSTREETMAP_HOT: ['a', 'b', 'c'],
            MapProvider.CARTODB_POSITRON: ['a', 'b', 'c', 'd'],
            MapProvider.CARTODB_DARK: ['a', 'b', 'c', 'd'],
            MapProvider.STAMEN_TERRAIN: ['a', 'b', 'c', 'd'],
            MapProvider.STAMEN_TONER: ['a', 'b', 'c', 'd']
        }
        
    def request_tile(self, provider: MapProvider, z: int, x: int, y: int):
        """Request tile download with cache check"""
        # First check persistent cache
        cached_tile = self.cache.get_tile(provider.value, z, x, y)
        if cached_tile:
            self.cache_hits += 1
            if self.performance_monitor:
                self.performance_monitor.log_tile_cached()
            # Convert QPixmap to bytes before emitting
            byte_array = QtCore.QByteArray()
            buffer = QtCore.QBuffer(byte_array)
            buffer.open(QtCore.QIODevice.WriteOnly)
            cached_tile.save(buffer, "PNG")  # Assuming PNG format for cached tiles
            
            self.tile_ready.emit(z, x, y, byte_array.data(), provider.value)
            return
            
        self.cache_misses += 1
        tile_key = (provider.value, z, x, y)
        
        with self.lock:
            # Check if already downloading or in queue
            if tile_key not in self.active_downloads:
                # Check if not already in queue
                queue_keys = {(item[0], item[1], item[2], item[3]) for item in self.download_queue}
                if tile_key not in queue_keys:
                    self.download_queue.append((provider.value, z, x, y))
                    self.active_downloads.add(tile_key)
    
    def run(self):
        """Optimized download loop"""
        self.logger.info("Tile download manager started")
        
        while self.running:
            try:
                if self.download_queue:
                    with self.lock:
                        if self.download_queue:
                            provider_name, z, x, y = self.download_queue.popleft()  # Use deque.popleft() for efficiency
                            provider = MapProvider(provider_name)
                        else:
                            time.sleep(0.05)
                            continue
                    
                    # Submit download task
                    future = self.executor.submit(self._download_tile, provider, z, x, y)
                    future.add_done_callback(lambda f, p=provider_name, zz=z, xx=x, yy=y: self._download_complete(p, zz, xx, yy))
                else:
                    time.sleep(0.1)  # Longer sleep when queue is empty
                    
            except Exception as e:
                self.logger.error(f"Error in download loop: {e}")
                time.sleep(1.0)  # Back off on errors
    
    def _download_tile(self, provider: MapProvider, z: int, x: int, y: int) -> Optional[QPixmap]:
        """Download single tile with caching and performance monitoring"""
        start_time = time.time()
        
        try:
            url = self._get_tile_url(provider, z, x, y)
            
            # Use configured user agent
            user_agent = config.get("network", "user_agent", "ASRA-GCS/2.0") if config else "ASRA-GCS/2.0"
            timeout = config.get("network", "download_timeout", 5) if config else 5
            
            headers = {
                'User-Agent': user_agent,
                'Accept': 'image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=3600'  # Hint for caching
            }
            
            response = self.session.get(url, timeout=timeout, headers=headers, stream=False)
            
            if response.status_code == 200:
                image_data = response.content
                
                # Store in persistent cache
                self.cache.store_tile(provider.value, z, x, y, image_data)
                
                # Log performance if monitoring enabled
                download_time = (time.time() - start_time) * 1000
                if self.performance_monitor:
                    self.performance_monitor.log_tile_download_time(download_time, True)
                
                self.tile_ready.emit(z, x, y, image_data, provider.value)
                return None # No longer returning pixmap from here
            else:
                self.logger.warning(f"HTTP {response.status_code} for {provider.value} {z}/{x}/{y}")
                    
        except requests.exceptions.Timeout:
            self.logger.debug(f"Timeout downloading {provider.value} {z}/{x}/{y}")
        except requests.exceptions.ConnectionError:
            self.logger.debug(f"Connection error for {provider.value} {z}/{x}/{y}")
        except Exception as e:
            self.logger.error(f"Tile download error {provider.value} {z}/{x}/{y}: {e}")
        
        # Log failed download
        if self.performance_monitor:
            download_time = (time.time() - start_time) * 1000
            self.performance_monitor.log_tile_download_time(download_time, False)
        
        return None
    
    def _get_tile_url(self, provider: MapProvider, z: int, x: int, y: int) -> str:
        """Generate tile URL for free providers"""
        url_template = self.providers[provider]
        
        # Handle providers with multiple servers for load balancing
        if provider in self.server_lists:
            servers = self.server_lists[provider]
            # Use simple hash-based server selection for consistency
            server_index = (x + y + z) % len(servers)
            server = servers[server_index]
            return url_template.format(z=z, x=x, y=y, s=server)
        else:
            return url_template.format(z=z, x=x, y=y)
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_percent': round(hit_rate, 1),
            'total_requests': total_requests
        }
    
    def _download_complete(self, provider: str, z: int, x: int, y: int):
        """Mark download as complete"""
        with self.lock:
            tile_key = (provider, z, x, y)
            self.active_downloads.discard(tile_key)
    
    def stop(self):
        """Stop downloader"""
        self.running = False
        self.executor.shutdown(wait=True)

class ProfessionalGCSMap(QWidget):
    """Professional GCS Map Widget - Optimized with free providers only"""
    
    # Signals
    position_changed = pyqtSignal(float, float)  # lat, lon
    zoom_changed = pyqtSignal(int)
    right_clicked = pyqtSignal(float, float)  # lat, lon
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        
        # Initialize logger
        self.logger = get_logger("map_widget")
        
        # Load configuration
        if config:
            self.center_lat = config.get("map", "default_lat", 28.6139)
            self.center_lon = config.get("map", "default_lon", 77.2090)
            self.zoom = config.get("map", "default_zoom", 12)
            self.min_zoom = config.get("map", "min_zoom", 3)
            self.max_zoom = config.get("map", "max_zoom", 18)
            self.tile_size = config.get("map", "tile_size", 256)
            provider_name = config.get("map", "default_provider", "OpenStreetMap")
            # Find matching provider
            self.current_provider = MapProvider.OPENSTREETMAP
            for provider in MapProvider:
                if provider.value == provider_name:
                    self.current_provider = provider
                    break
        else:
            # Fallback defaults
            self.center_lat = 28.6139  # Delhi
            self.center_lon = 77.2090
            self.zoom = 12
            self.min_zoom = 3
            self.max_zoom = 18
            self.tile_size = 256
            self.current_provider = MapProvider.ESRI_SATELLITE
        
        # Optimized tile cache with configuration
        self.tile_cache = OrderedDict()  # In-memory cache (provider, z, x, y) -> QPixmap
        self.max_cache_tiles = config.get("map", "max_cache_tiles", 400) if config else 400
        self.cache_cleanup_threshold = config.get("map", "cache_cleanup_threshold", 450) if config else 450
        self.cache_lock = QMutex()
        self.cache_access_times = {}  # Track access times for better LRU
        
        # Performance monitoring (don't auto-start to prevent threading issues on init)
        self.performance_monitor = PerformanceMonitor(config) if PerformanceMonitor else None
        # Will be started after map is fully initialized
        
        # Tile downloader (don't auto-start to prevent Qt conflicts)
        self.tile_downloader = TileDownloadManager()
        self.tile_downloader.tile_ready.connect(self._on_tile_ready, Qt.QueuedConnection)  # Use queued connection
        # Note: tile_downloader.start() moved to after widget is fully shown
        # Start tile downloader after a delay to prevent blocking
        QTimer.singleShot(500, self._start_tile_downloader)  # Reduced delay
        
        # UAV state
        self.uav_position = None  # (lat, lon)
        self.uav_heading = 0.0
        self.uav_altitude = 0.0
        self.uav_speed = 0.0
        self.flight_mode = FlightMode.MANUAL
        
        # Home position
        self.home_position = None  # (lat, lon)
        
        # Flight path
        self.flight_path = deque(maxlen=1000)
        self.show_flight_path = True
        
        # Waypoints for mission planning
        self.waypoints = []
        self.show_waypoints = True
        
        # Geofence
        self.geofence_points = []
        self.show_geofence = True
        
        # Rally points
        self.rally_points = []
        self.show_rally_points = True
        
        # Display options - like Mission Planner
        self.show_uav = True
        self.show_home = True
        self.show_grid = False
        self.show_scale = True
        self.show_coordinates = True
        
        # Colors - Mission Planner style
        self.colors = {
            'background': QColor(50, 50, 50),
            'uav': QColor(255, 0, 0),
            'uav_heading': QColor(255, 255, 0),
            'home': QColor(0, 255, 0),
            'flight_path': QColor(255, 0, 255),
            'waypoint': QColor(255, 255, 0),
            'waypoint_line': QColor(255, 255, 255),
            'geofence': QColor(255, 0, 0),
            'rally_point': QColor(0, 255, 255),
            'grid': QColor(100, 100, 100),
            'text': QColor(255, 255, 255),
            'scale': QColor(255, 255, 255)
        }
        
        # Interaction state
        self.dragging = False
        self.drag_start = None
        self.last_pan_pos = None
        
        # Wheel event accumulation for smooth zoom
        self.wheel_accumulator = 0
        self.last_wheel_time = 0
        
        # Performance optimization
        self.render_lock = QMutex()
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update)
        
        # Timer for batching tile updates
        self.tile_update_timer = QTimer(self)
        self.tile_update_timer.setSingleShot(True)
        self.tile_update_timer.setInterval(50)  # Update UI every 50ms after tiles are ready
        self.tile_update_timer.timeout.connect(self.update)
        
        # Setup widget
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Initial tile request - minimal delay
        QTimer.singleShot(100, self._request_visible_tiles)
    
    def _start_tile_downloader(self):
        """Start tile downloader after UI is ready"""
        if hasattr(self, 'tile_downloader') and self.tile_downloader:
            if not self.tile_downloader.isRunning():
                self.tile_downloader.start()
                print("Tile downloader started")
    
    def _deg2tile(self, lat_deg: float, lon_deg: float, zoom: int) -> Tuple[float, float]:
        """Convert lat/lon to tile coordinates (precise)"""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = (lon_deg + 180.0) / 360.0 * n
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        return x, y
    
    def _tile2deg(self, x: float, y: float, zoom: int) -> Tuple[float, float]:
        """Convert tile coordinates to lat/lon"""
        n = 2.0 ** zoom
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg
    
    def _latlon_to_screen(self, lat: float, lon: float) -> Tuple[int, int]:
        """Convert lat/lon to screen coordinates"""
        tile_x, tile_y = self._deg2tile(lat, lon, self.zoom)
        center_x, center_y = self._deg2tile(self.center_lat, self.center_lon, self.zoom)
        
        screen_x = self.width() / 2 + (tile_x - center_x) * self.tile_size
        screen_y = self.height() / 2 + (tile_y - center_y) * self.tile_size
        
        return int(screen_x), int(screen_y)
    
    def _screen_to_latlon(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to lat/lon"""
        center_x, center_y = self._deg2tile(self.center_lat, self.center_lon, self.zoom)
        
        tile_x = center_x + (screen_x - self.width() / 2) / self.tile_size
        tile_y = center_y + (screen_y - self.height() / 2) / self.tile_size
        
        return self._tile2deg(tile_x, tile_y, self.zoom)
    
    def _get_visible_tiles(self) -> List[Tuple[int, int]]:
        """Get visible tile coordinates"""
        if self.width() <= 0 or self.height() <= 0:
            return []
        
        # Add margin for smooth panning
        margin = 2
        nw_lat, nw_lon = self._screen_to_latlon(-margin * self.tile_size, -margin * self.tile_size)
        se_lat, se_lon = self._screen_to_latlon(self.width() + margin * self.tile_size, 
                                                self.height() + margin * self.tile_size)
        
        nw_x, nw_y = self._deg2tile(nw_lat, nw_lon, self.zoom)
        se_x, se_y = self._deg2tile(se_lat, se_lon, self.zoom)
        
        min_x = max(0, int(min(nw_x, se_x)))
        max_x = min((2 ** self.zoom) - 1, int(max(nw_x, se_x)))
        min_y = max(0, int(min(nw_y, se_y)))
        max_y = min((2 ** self.zoom) - 1, int(max(nw_y, se_y)))
        
        tiles = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                tiles.append((x, y))
        
        return tiles
    
    def _request_visible_tiles(self):
        """Request visible tiles with priority for center tiles"""
        # Check if tile downloader is ready
        if not hasattr(self, 'tile_downloader') or not self.tile_downloader:
            return
            
        visible_tiles = self._get_visible_tiles()
        
        # Sort tiles by distance from center for faster visual loading
        center_x, center_y = self._deg2tile(self.center_lat, self.center_lon, self.zoom)
        
        def tile_priority(tile):
            x, y = tile
            # Distance from center (closer tiles load first)
            return (x - center_x) ** 2 + (y - center_y) ** 2
        
        sorted_tiles = sorted(visible_tiles, key=tile_priority)
        
        for x, y in sorted_tiles:
            tile_key = (self.current_provider.value, self.zoom, x, y)
            
            with QMutexLocker(self.cache_lock):
                if tile_key not in self.tile_cache:
                    self.tile_downloader.request_tile(self.current_provider, self.zoom, x, y)
    
    def _on_tile_ready(self, z: int, x: int, y: int, image_data: bytes, provider: str):
        """Handle tile ready (optimized for non-blocking)"""
        # Quick check without expensive operations
        if z != self.zoom or provider != self.current_provider.value:
            return
        
        try:
            pixmap = QPixmap()
            if not pixmap.loadFromData(image_data):
                return  # Silent failure to avoid log spam

            tile_key = (provider, z, x, y)
            
            # Fast cache update with minimal locking
            with QMutexLocker(self.cache_lock):
                # Quick cache size check
                if len(self.tile_cache) >= self.cache_cleanup_threshold:
                    # Remove oldest tiles efficiently
                    for _ in range(min(50, len(self.tile_cache) // 4)):
                        if self.tile_cache:
                            self.tile_cache.popitem(last=False)
                
                self.tile_cache[tile_key] = pixmap
                self.tile_cache.move_to_end(tile_key)
            
            # Schedule update if not already pending
            if not self.tile_update_timer.isActive():
                self.tile_update_timer.start()
        except Exception:
            pass  # Silent failure to avoid blocking
    

    
    def paintEvent(self, event):
        """Paint the map - professional rendering"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            
            # Clear background
            painter.fillRect(self.rect(), self.colors['background'])
            
            # Draw tiles
            self._draw_tiles(painter)
            
            # Draw overlays
            try:
                if self.show_grid:
                    self._draw_grid(painter)
            except Exception as e:
                self.logger.error(f"Error drawing grid: {e}")
            
            try:
                if self.show_geofence and self.geofence_points:
                    self._draw_geofence(painter)
            except Exception as e:
                self.logger.error(f"Error drawing geofence: {e}")
            
            try:
                if self.show_waypoints and self.waypoints:
                    self._draw_waypoints(painter)
            except Exception as e:
                self.logger.error(f"Error drawing waypoints: {e}")
            
            try:
                if self.show_rally_points and self.rally_points:
                    self._draw_rally_points(painter)
            except Exception as e:
                self.logger.error(f"Error drawing rally points: {e}")
            
            try:
                if self.show_flight_path and len(self.flight_path) > 1:
                    self._draw_flight_path(painter)
            except Exception as e:
                self.logger.error(f"Error drawing flight path: {e}")
            
            try:
                if self.show_home and self.home_position:
                    self._draw_home(painter)
            except Exception as e:
                self.logger.error(f"Error drawing home: {e}")
            
            try:
                if self.show_uav and self.uav_position:
                    self._draw_uav(painter)
            except Exception as e:
                self.logger.error(f"Error drawing UAV: {e}")
            
            # Draw UI elements
            try:
                if self.show_scale:
                    self._draw_scale(painter)
            except Exception as e:
                self.logger.error(f"Error drawing scale: {e}")
            
            try:
                if self.show_coordinates:
                    self._draw_coordinates(painter)
            except Exception as e:
                self.logger.error(f"Error drawing coordinates: {e}")
            
            try:
                self._draw_status(painter)
            except Exception as e:
                self.logger.error(f"Error drawing status: {e}")
            
        except Exception as e:
            print(f"Paint error: {e}")
        finally:
            painter.end()
    
    def _draw_tiles(self, painter: QPainter):
        """Draw map tiles"""
        visible_tiles = self._get_visible_tiles()
        center_x, center_y = self._deg2tile(self.center_lat, self.center_lon, self.zoom)
        
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)  # Fast tile rendering
        
        for x, y in visible_tiles:
            tile_key = (self.current_provider.value, self.zoom, x, y)
            
            with QMutexLocker(self.cache_lock):
                if tile_key in self.tile_cache:
                    pixmap = self.tile_cache[tile_key]
                    self.tile_cache.move_to_end(tile_key)  # Mark as recently used
                    
                    # Calculate screen position
                    screen_x = self.width() / 2 + (x - center_x) * self.tile_size
                    screen_y = self.height() / 2 + (y - center_y) * self.tile_size
                    
                    if pixmap.isNull():
                        # Draw placeholder if pixmap is null
                        painter.fillRect(int(screen_x), int(screen_y), self.tile_size, self.tile_size,
                                       QColor(70, 70, 70))
                        painter.setPen(QColor(100, 100, 100))
                        painter.drawRect(int(screen_x), int(screen_y), self.tile_size, self.tile_size)
                    else:
                        painter.drawPixmap(int(screen_x), int(screen_y), pixmap)
                else:
                    # Draw placeholder
                    screen_x = self.width() / 2 + (x - center_x) * self.tile_size
                    screen_y = self.height() / 2 + (y - center_y) * self.tile_size
                    
                    painter.fillRect(int(screen_x), int(screen_y), self.tile_size, self.tile_size,
                                   QColor(70, 70, 70))
                    painter.setPen(QColor(100, 100, 100))
                    painter.drawRect(int(screen_x), int(screen_y), self.tile_size, self.tile_size)
        
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    def _draw_uav(self, painter: QPainter):
        """Draw UAV - Mission Planner style"""
        if not self.uav_position:
            return
        
        lat, lon = self.uav_position
        x, y = self._latlon_to_screen(lat, lon)
        
        # Draw UAV aircraft symbol
        painter.save()
        painter.translate(x, y)
        painter.rotate(self.uav_heading)
        
        # Aircraft body
        painter.setPen(QPen(self.colors['uav'], 2))
        painter.setBrush(QBrush(self.colors['uav']))
        
        # Fuselage
        painter.drawEllipse(-3, -12, 6, 24)
        
        # Wings
        painter.drawRect(-15, -3, 30, 6)
        
        # Tail
        painter.drawRect(-8, -15, 16, 4)
        
        painter.restore()
        
        # Draw heading line
        if self.uav_heading != 0:
            painter.setPen(QPen(self.colors['uav_heading'], 2))
            end_x = x + 30 * math.sin(math.radians(self.uav_heading))
            end_y = y - 30 * math.cos(math.radians(self.uav_heading))
            painter.drawLine(x, y, int(end_x), int(end_y))
        
        # Draw info text
        painter.setPen(self.colors['text'])
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        info_text = f"ALT: {self.uav_altitude:.1f}m\nSPD: {self.uav_speed:.1f}m/s\nMODE: {self.flight_mode.value}"
        painter.drawText(x + 20, y - 10, info_text)
    
    def _draw_home(self, painter: QPainter):
        """Draw home position - Mission Planner style"""
        if not self.home_position:
            return
        
        lat, lon = self.home_position
        x, y = self._latlon_to_screen(lat, lon)
        
        # Home symbol (house)
        painter.setPen(QPen(self.colors['home'], 2))
        painter.setBrush(QBrush(self.colors['home']))
        
        # House base
        painter.drawRect(x - 8, y - 4, 16, 8)
        
        # Roof
        roof = QPolygonF([
            QPointF(x, y - 12),
            QPointF(x - 10, y - 4),
            QPointF(x + 10, y - 4)
        ])
        painter.drawPolygon(roof)
        
        # Label
        painter.setPen(self.colors['text'])
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)
        painter.drawText(x - 15, y + 20, "HOME")
    
    def _draw_flight_path(self, painter: QPainter):
        """Draw flight path"""
        if len(self.flight_path) < 2:
            return
        
        painter.setPen(QPen(self.colors['flight_path'], 2))
        
        points = []
        for lat, lon in self.flight_path:
            x, y = self._latlon_to_screen(lat, lon)
            points.append(QPointF(x, y))
        
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])
    
    def _draw_waypoints(self, painter: QPainter):
        """Draw waypoints"""
        painter.setPen(QPen(self.colors['waypoint'], 2))
        painter.setBrush(QBrush(self.colors['waypoint']))
        
        # Draw waypoint connections
        if len(self.waypoints) > 1:
            painter.setPen(QPen(self.colors['waypoint_line'], 1))
            points = []
            for lat, lon, _ in self.waypoints:
                x, y = self._latlon_to_screen(lat, lon)
                points.append(QPointF(x, y))
            
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
        
        # Draw waypoint markers
        painter.setPen(QPen(self.colors['waypoint'], 2))
        painter.setBrush(QBrush(self.colors['waypoint']))
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)
        
        for i, (lat, lon, alt) in enumerate(self.waypoints):
            x, y = self._latlon_to_screen(lat, lon)
            
            # Waypoint circle
            painter.drawEllipse(x - 8, y - 8, 16, 16)
            
            # Waypoint number
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(x - 4, y + 4, str(i + 1))
            
            # Altitude label
            painter.setPen(self.colors['text'])
            painter.drawText(x + 12, y - 5, f"{alt:.0f}m")
    
    def _draw_geofence(self, painter: QPainter):
        """Draw geofence"""
        if len(self.geofence_points) < 3:
            return
        
        painter.setPen(QPen(self.colors['geofence'], 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
        
        points = []
        for lat, lon in self.geofence_points:
            x, y = self._latlon_to_screen(lat, lon)
            points.append(QPointF(x, y))
        
        polygon = QPolygonF(points)
        painter.drawPolygon(polygon)
    
    def _draw_rally_points(self, painter: QPainter):
        """Draw rally points"""
        painter.setPen(QPen(self.colors['rally_point'], 2))
        painter.setBrush(QBrush(self.colors['rally_point']))
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        for i, (lat, lon) in enumerate(self.rally_points):
            x, y = self._latlon_to_screen(lat, lon)
            
            # Rally point symbol (flag)
            painter.drawRect(x - 2, y - 15, 4, 15)
            painter.drawRect(x + 2, y - 15, 10, 8)
            
            painter.setPen(self.colors['text'])
            painter.drawText(x + 15, y - 5, f"R{i + 1}")
    
    def _draw_grid(self, painter: QPainter):
        """Draw coordinate grid"""
        painter.setPen(QPen(self.colors['grid'], 1))
        
        # Draw grid lines every tile
        center_x, center_y = self._deg2tile(self.center_lat, self.center_lon, self.zoom)
        
        # Vertical lines
        for i in range(-10, 11):
            x = self.width() / 2 + i * self.tile_size
            if 0 <= x <= self.width():
                painter.drawLine(int(x), 0, int(x), self.height())
        
        # Horizontal lines  
        for i in range(-10, 11):
            y = self.height() / 2 + i * self.tile_size
            if 0 <= y <= self.height():
                painter.drawLine(0, int(y), self.width(), int(y))
    
    def _draw_scale(self, painter: QPainter):
        """Draw scale bar"""
        painter.setPen(QPen(self.colors['scale'], 2))
        painter.setBrush(QBrush(QColor(0, 0, 0, 128)))
        
        # Calculate scale
        lat_rad = math.radians(self.center_lat)
        meters_per_pixel = 156543.03392 * math.cos(lat_rad) / (2 ** self.zoom)
        
        # Scale lengths
        scale_lengths = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
        scale_meters = None
        
        for length in scale_lengths:
            pixels = length / meters_per_pixel
            if 50 <= pixels <= 200:
                scale_meters = length
                scale_pixels = int(pixels)
                break
        
        if scale_meters:
            # Draw scale bar
            x = 20
            y = self.height() - 40
            
            painter.fillRect(x - 2, y - 12, scale_pixels + 4, 16, QColor(0, 0, 0, 128))
            painter.drawRect(x, y - 8, scale_pixels, 8)
            
            # Scale text
            font = QFont("Arial", 9)
            painter.setFont(font)
            
            if scale_meters >= 1000:
                text = f"{scale_meters // 1000}km"
            else:
                text = f"{scale_meters}m"
            
            painter.drawText(x, y + 10, text)
    
    def _draw_coordinates(self, painter: QPainter):
        """Draw current coordinates"""
        painter.setPen(self.colors['text'])
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        coord_text = f"Lat: {self.center_lat:.6f}°  Lon: {self.center_lon:.6f}°"
        painter.drawText(10, 20, coord_text)
    
    def _draw_status(self, painter: QPainter):
        """Draw status information"""
        painter.setPen(self.colors['text'])
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # Cache info
        with QMutexLocker(self.cache_lock):
            cache_count = len(self.tile_cache)
        
        status_lines = [
            f"Provider: {self.current_provider.value}",
            f"Zoom: {self.zoom}",
            f"Tiles: {cache_count}"
        ]
        
        y_offset = self.height() - 60
        for line in status_lines:
            painter.drawText(10, y_offset, line)
            y_offset += 15
    
    def _show_context_menu(self, position):
        """Show context menu"""
        lat, lon = self._screen_to_latlon(position.x(), position.y())
        
        menu = QMenu(self)
        
        # Set as home
        set_home_action = QAction("Set Home Position", self)
        set_home_action.triggered.connect(lambda: self.set_home_position(lat, lon))
        menu.addAction(set_home_action)
        
        # Add waypoint
        add_waypoint_action = QAction("Add Waypoint", self)
        add_waypoint_action.triggered.connect(lambda: self.add_waypoint(lat, lon, 100))
        menu.addAction(add_waypoint_action)
        
        menu.addSeparator()
        
        # Provider selection
        provider_menu = menu.addMenu("Map Provider")
        for provider in MapProvider:
            action = QAction(provider.value, self)
            action.setCheckable(True)
            action.setChecked(provider == self.current_provider)
            action.triggered.connect(lambda checked, p=provider: self.set_provider(p))
            provider_menu.addAction(action)
        
        # Display options
        display_menu = menu.addMenu("Display Options")
        
        options = [
            ("Show Grid", self.show_grid, self.set_show_grid),
            ("Show Flight Path", self.show_flight_path, self.set_show_flight_path),
            ("Show Waypoints", self.show_waypoints, self.set_show_waypoints),
            ("Show Geofence", self.show_geofence, self.set_show_geofence),
        ]
        
        for name, current_value, setter in options:
            action = QAction(name, self)
            action.setCheckable(True)
            action.setChecked(current_value)
            action.triggered.connect(lambda checked, s=setter: s(checked))
            display_menu.addAction(action)
        
        menu.exec_(self.mapToGlobal(position))
    
    # Mouse events
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.last_pan_pos = (self.center_lat, self.center_lon)
        elif event.button() == Qt.RightButton:
            lat, lon = self._screen_to_latlon(event.x(), event.y())
            self.right_clicked.emit(lat, lon)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move with smooth panning"""
        if self.dragging and self.drag_start and self.last_pan_pos:
            # Calculate movement delta
            dx = event.x() - self.drag_start.x()
            dy = event.y() - self.drag_start.y()
            
            # Use original pan position as reference for smooth dragging
            start_lat, start_lon = self.last_pan_pos
            
            # Convert pixel offset to lat/lon offset based on current zoom
            # This gives more natural panning behavior
            center_x, center_y = self._deg2tile(start_lat, start_lon, self.zoom)
            
            # Calculate new center based on pixel drag
            new_center_x = center_x - dx / self.tile_size
            new_center_y = center_y - dy / self.tile_size
            
            # Convert back to lat/lon
            self.center_lat, self.center_lon = self._tile2deg(new_center_x, new_center_y, self.zoom)
            
            # Update immediately for smooth panning
            self.update()
            
            # Emit position change (but not too frequently)
            if abs(dx) > 5 or abs(dy) > 5:  # Only emit every few pixels
                self.position_changed.emit(self.center_lat, self.center_lon)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.drag_start = None
            self._request_visible_tiles()
    
    def wheelEvent(self, event):
        """Handle zoom with proper sensitivity like Mission Planner"""
        import time
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Get wheel delta
        delta = event.angleDelta().y()
        
        # Accumulate scroll events within a short time window
        if current_time - self.last_wheel_time < 100:  # 100ms window
            self.wheel_accumulator += delta
        else:
            self.wheel_accumulator = delta
        
        self.last_wheel_time = current_time
        
        # Require significant accumulated scroll to change zoom (like Mission Planner)
        zoom_threshold = 120  # Standard wheel "click" is 120 units
        
        if abs(self.wheel_accumulator) < zoom_threshold:
            return  # Not enough scroll accumulated
        
        old_zoom = self.zoom
        
        # Calculate zoom steps - only change by 1 level per accumulated threshold
        if self.wheel_accumulator > 0:
            self.zoom = min(self.zoom + 1, self.max_zoom)
        else:
            self.zoom = max(self.zoom - 1, self.min_zoom)
        
        # Reset accumulator after zoom change
        self.wheel_accumulator = 0
        
        if self.zoom != old_zoom:
            # Smooth zoom to mouse cursor position (like Mission Planner)
            self._zoom_to_cursor(event.pos())
            self._request_visible_tiles()
            self.update()
            self.zoom_changed.emit(self.zoom)
    
    def _zoom_to_cursor(self, cursor_pos):
        """Zoom to cursor position like Mission Planner/QGroundControl"""
        # Get the lat/lon under the cursor before zoom
        cursor_lat, cursor_lon = self._screen_to_latlon(cursor_pos.x(), cursor_pos.y())
        
        # After zoom change, adjust center so cursor point stays in same place
        # This creates smooth zoom-to-cursor behavior
        new_cursor_x, new_cursor_y = self._latlon_to_screen(cursor_lat, cursor_lon)
        
        # Calculate offset from cursor to center
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        offset_x = new_cursor_x - cursor_pos.x()
        offset_y = new_cursor_y - cursor_pos.y()
        
        # Adjust map center to compensate for offset
        if abs(offset_x) > 1 or abs(offset_y) > 1:  # Only adjust if offset is significant
            adjust_lat, adjust_lon = self._screen_to_latlon(center_x + offset_x, center_y + offset_y)
            self.center_lat = adjust_lat
            self.center_lon = adjust_lon
    
    def resizeEvent(self, event):
        """Handle resize"""
        super().resizeEvent(event)
        QTimer.singleShot(100, self._request_visible_tiles)
    
    # Public API - Mission Planner/QGroundControl compatible
    def set_provider(self, provider: MapProvider):
        """Change map provider"""
        if provider != self.current_provider:
            self.current_provider = provider
            with QMutexLocker(self.cache_lock):
                pass  # Clear cache if needed
            self._request_visible_tiles()
            self.update()
    
    def set_position(self, lat: float, lon: float):
        """Set map center position"""
        self.center_lat = lat
        self.center_lon = lon
        self._request_visible_tiles()
        self.update()
        self.position_changed.emit(lat, lon)
    
    def set_zoom(self, zoom: int):
        """Set zoom level"""
        zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        if zoom != self.zoom:
            self.zoom = zoom
            self._request_visible_tiles()
            self.update()
            self.zoom_changed.emit(zoom)
    
    def update_uav_position(self, lat: float, lon: float, heading: float = 0, altitude: float = 0, speed: float = 0):
        """Update UAV position and status"""
        self.uav_position = (lat, lon)
        self.uav_heading = heading
        self.uav_altitude = altitude
        self.uav_speed = speed
        
        # Add to flight path (deque auto-evicts when maxlen is reached)
        if lat != 0 or lon != 0:
            self.flight_path.append((lat, lon))
        self.update()
    
    def set_home_position(self, lat: float, lon: float):
        """Set home position"""
        self.home_position = (lat, lon)
        self.update()
    
    def set_flight_mode(self, mode: FlightMode):
        """Set flight mode"""
        self.update()
    
    def add_waypoint(self, lat: float, lon: float, altitude: float = 100):
        """Add waypoint for mission planning"""
        self.waypoints.append((lat, lon, altitude))
        self.update()
    
    def clear_waypoints(self):
        """Clear all waypoints"""
        self.waypoints.clear()
        self.update()
    
    def set_geofence(self, points: List[Tuple[float, float]]):
        """Set geofence points"""
        self.geofence_points = points
        self.update()
    
    def add_rally_point(self, lat: float, lon: float):
        """Add rally point"""
        self.rally_points.append((lat, lon))
        self.update()
    
    def clear_flight_path(self):
        """Clear flight path"""
        self.update()
    
    # Display option setters
    def set_show_grid(self, show: bool):
        self.show_grid = show
        self._schedule_update()
    
    def set_show_flight_path(self, show: bool):
        self.show_flight_path = show
        self._schedule_update()
    
    def set_show_waypoints(self, show: bool):
        self.show_waypoints = show
        self._schedule_update()
    
    def set_show_geofence(self, show: bool):
        self.show_geofence = show
        self._schedule_update()
    
    def closeEvent(self, event):
        """Cleanup on close"""
        if hasattr(self, 'tile_downloader'):
            self.tile_downloader.stop()
            self.tile_downloader.wait()
        event.accept()

# Compatibility alias
OfflineMapWidget = ProfessionalGCSMap
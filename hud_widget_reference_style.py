import math
from PyQt5 import QtCore, QtGui, QtWidgets

# HUD Configuration constants
PIXELS_PER_PITCH_DEGREE = 8  # Pixels per degree of pitch
PIXELS_PER_HEADING_DEGREE = 10  # Pixels per degree of heading
HEADING_TAPE_RANGE_DEGREES = 30  # Degrees to show on each side of current heading

class ReferenceStyleHUDWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll = 0.0
        self.pitch = 0.0
        self.heading = 0
        self.airspeed = 0.0
        self.groundspeed = 0.0
        self.altitude = 0.0
        self.flight_mode = "Unknown"
        self.battery_level = 100.0
        self.gps_sats = 0
        self.gps_fix = 0
        self.warning = ""
        self._connected = False
        self._is_armed = False
        self.setMinimumSize(800, 600)

        # --- Reference Style Color Scheme ---
        self.color_primary = QtGui.QColor(255, 255, 255)    # White
        self.color_secondary = QtGui.QColor(0, 255, 255)    # Cyan
        self.color_accent = QtGui.QColor(255, 255, 0)       # Yellow
        self.color_heading = QtGui.QColor(255, 100, 100)    # Light Red
        self.color_warning = QtGui.QColor(255, 50, 50)      # Red
        self.color_danger = QtGui.QColor(255, 0, 0)         # Bright Red
        self.color_success = QtGui.QColor(0, 255, 0)        # Green
        self.color_sky = QtGui.QColor(0, 100, 200, 180)     # Sky Blue
        self.color_ground = QtGui.QColor(150, 100, 50, 180) # Brown
        self.color_background = QtGui.QColor(0, 0, 0)       # Black

        # --- Fonts ---
        self.font_large = QtGui.QFont("Arial", 16, QtGui.QFont.Bold)
        self.font_medium = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)
        self.font_small = QtGui.QFont("Arial", 10)
        self.font_tiny = QtGui.QFont("Arial", 8)

    def update_flight_mode(self, mode):
        self.flight_mode = mode
        self.update()

    def update_attitude(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.heading = int(math.degrees(yaw) % 360)
        self.update()

    def update_vfr(self, heading, airspeed, groundspeed, alt):
        self.heading = int(heading % 360)
        self.airspeed = airspeed
        self.groundspeed = groundspeed
        self.altitude = alt
        self.update()

    def update_battery(self, level):
        self.battery_level = level
        self.update()

    def update_gps(self, fix_type, satellites):
        self.gps_fix = fix_type
        self.gps_sats = satellites
        self.update()

    def update_connection_status(self, connected):
        self._connected = connected
        self.update()

    def update_armed_status(self, armed):
        self._is_armed = armed
        self.update()

    def set_warning(self, warning):
        self.warning = warning
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        try:
            painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
            
            # Draw background
            painter.fillRect(self.rect(), self.color_background)
            
            # Draw main HUD elements
            self.draw_artificial_horizon(painter)
            self.draw_crosshair(painter)
            self.draw_heading_indicator(painter)
            self.draw_side_tapes(painter)
            self.draw_flight_mode(painter)
            self.draw_status_indicators(painter)
            self.draw_warnings(painter)
        finally:
            painter.end()

    def draw_artificial_horizon(self, painter):
        """Draw the artificial horizon with pitch ladder"""
        painter.save()
        center = self.rect().center()
        
        # Translate to center and apply roll rotation
        painter.translate(center)
        painter.rotate(-math.degrees(self.roll))
        
        # Calculate pitch offset
        pitch_offset = math.degrees(self.pitch) * PIXELS_PER_PITCH_DEGREE
        painter.translate(0, pitch_offset)
        
        # Draw sky and ground
        sky_rect = QtCore.QRect(-2000, -2000, 4000, 2000)
        ground_rect = QtCore.QRect(-2000, 0, 4000, 2000)
        
        painter.fillRect(sky_rect, self.color_sky)
        painter.fillRect(ground_rect, self.color_ground)
        
        # Draw horizon line
        horizon_pen = QtGui.QPen(self.color_primary, 2)
        painter.setPen(horizon_pen)
        painter.drawLine(-1000, 0, 1000, 0)
        
        # Draw pitch ladder
        self.draw_pitch_ladder(painter)
        
        painter.restore()

    def draw_pitch_ladder(self, painter):
        """Draw the pitch ladder"""
        painter.save()
        ladder_pen = QtGui.QPen(self.color_primary, 1.5)
        painter.setPen(ladder_pen)
        painter.setFont(self.font_tiny)
        
        for deg in range(-30, 31, 5):
            if deg == 0:
                continue
                
            y = -deg * PIXELS_PER_PITCH_DEGREE
            width = 40 if abs(deg) < 20 else 60 if abs(deg) < 30 else 80
            
            # Draw ladder rungs
            painter.drawLine(int(-width/2), int(y), int(width/2), int(y))
            
            # Draw pitch numbers
            if deg % 10 == 0:
                text = str(abs(deg))
                text_rect = QtCore.QRectF(-width/2 - 30, y - 8, 25, 16)
                painter.drawText(text_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, text)
                text_rect = QtCore.QRectF(width/2 + 5, y - 8, 25, 16)
                painter.drawText(text_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, text)
        
        painter.restore()

    def draw_crosshair(self, painter):
        """Draw the aircraft crosshair"""
        painter.save()
        center = self.rect().center()
        painter.translate(center)
        
        # Crosshair lines
        crosshair_pen = QtGui.QPen(self.color_primary, 2)
        painter.setPen(crosshair_pen)
        
        # Horizontal line
        painter.drawLine(-100, 0, -20, 0)
        painter.drawLine(20, 0, 100, 0)
        
        # Vertical line
        painter.drawLine(0, -100, 0, -20)
        painter.drawLine(0, 20, 0, 100)
        
        # Small aircraft symbol
        aircraft_pen = QtGui.QPen(self.color_primary, 2)
        painter.setPen(aircraft_pen)
        painter.drawLine(-15, 0, -5, 0)
        painter.drawLine(5, 0, 15, 0)
        painter.drawLine(0, -5, 0, 5)
        
        # Roll indicator arc (180 degrees)
        roll_pen = QtGui.QPen(self.color_secondary, 2)
        painter.setPen(roll_pen)
        rect = QtCore.QRectF(-180, -180, 360, 360)
        painter.drawArc(rect, 0, 180*16)  # 180 degrees in 1/16th degrees
        
        # Roll indicator marks and labels
        for angle in range(-180, 181, 15):
            painter.save()
            painter.rotate(angle)
            if angle % 45 == 0:
                painter.drawLine(0, -180, 0, -170)
                # Add labels for major angles (level, not tilted)
                label_pen = QtGui.QPen(self.color_primary, 1)
                painter.setPen(label_pen)
                painter.setFont(self.font_tiny)
                # Save current transform and reset rotation for level text
                painter.save()
                painter.rotate(-angle)  # Counter-rotate to keep text level
                # Position labels with 0° at top, positive angles on right, negative on left
                if angle == -180 or angle == 180:
                    text_rect = QtCore.QRectF(-20, -210, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "0°")
                elif angle == -135:
                    text_rect = QtCore.QRectF(-180, -160, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "-45°")
                elif angle == -90:
                    text_rect = QtCore.QRectF(-200, -20, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "-90°")
                elif angle == -45:
                    text_rect = QtCore.QRectF(-180, 120, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "-135°")
                elif angle == 0:
                    text_rect = QtCore.QRectF(-20, 150, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "180°")
                elif angle == 45:
                    text_rect = QtCore.QRectF(140, 120, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "135°")
                elif angle == 90:
                    text_rect = QtCore.QRectF(160, -20, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "90°")
                elif angle == 135:
                    text_rect = QtCore.QRectF(140, -160, 40, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, "45°")
                painter.restore()
            elif angle % 15 == 0:
                painter.drawLine(0, -180, 0, -175)
            painter.restore()
        
        # Roll pointer
        pointer_pen = QtGui.QPen(self.color_heading, 3)
        painter.setPen(pointer_pen)
        painter.setBrush(self.color_heading)
        painter.rotate(math.degrees(self.roll))
        triangle = QtGui.QPolygonF([
            QtCore.QPointF(0, -175),
            QtCore.QPointF(-6, -185),
            QtCore.QPointF(6, -185)
        ])
        painter.drawPolygon(triangle)
        
        # Roll label
        painter.setPen(self.color_secondary)
        painter.setFont(self.font_small)
        painter.drawText(QtCore.QRectF(-50, -220, 100, 20), QtCore.Qt.AlignCenter, "ROLL")
        
        painter.restore()

    def draw_heading_indicator(self, painter):
        """Draw the heading indicator at the top"""
        painter.save()
        w, h = self.width(), self.height()
        
        # Heading tape
        tape_height = 40
        tape_width = w * 0.6
        rect = QtCore.QRectF((w - tape_width) / 2, 20, tape_width, tape_height)
        
        # Background
        painter.fillRect(rect, QtGui.QColor(0, 0, 0, 150))
        painter.setPen(QtGui.QPen(self.color_primary, 1))
        painter.drawRect(rect)
        
        # Scale
        center_x = rect.center().x()
        offset = self.heading * PIXELS_PER_HEADING_DEGREE
        
        painter.setFont(self.font_tiny)
        painter.setPen(self.color_primary)
        
        cardinals = {0: "N", 90: "E", 180: "S", 270: "W"}
        
        # Draw heading marks
        for deg in range(self.heading - HEADING_TAPE_RANGE_DEGREES, self.heading + HEADING_TAPE_RANGE_DEGREES + 1):
            x = center_x - offset + (deg * PIXELS_PER_HEADING_DEGREE)
            if x < rect.left() + 10 or x > rect.right() - 10:
                continue
                
            d = deg % 360
            
            # Major marks (every 10 degrees) with actual degree labels
            if d % 10 == 0:
                painter.drawLine(int(x), int(rect.top()), int(x), int(rect.top() + 10))
                if d % 30 == 0:
                    label = cardinals.get(d, str(d))
                    text_rect = QtCore.QRectF(x - 15, rect.top() + 15, 30, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, label)
                else:
                    # Show actual degree values for non-cardinal marks
                    text_rect = QtCore.QRectF(x - 15, rect.top() + 15, 30, 20)
                    painter.drawText(text_rect, QtCore.Qt.AlignCenter, str(d))
            # Minor marks (every 5 degrees)
            elif d % 5 == 0:
                painter.drawLine(int(x), int(rect.top()), int(x), int(rect.top() + 5))
        
        # Center marker (heading indicator)
        painter.setPen(QtGui.QPen(self.color_heading, 3))
        painter.drawLine(int(center_x), int(rect.top()), int(center_x), int(rect.bottom()))
        
        # Heading number at the top of the compass box
        painter.setFont(self.font_medium)
        painter.setPen(self.color_heading)
        heading_text = f"{self.heading:03d}°"
        painter.drawText(QtCore.QRectF(center_x - 30, rect.top() - 25, 60, 25), QtCore.Qt.AlignCenter, heading_text)
        
        painter.restore()

    def draw_side_tapes(self, painter):
        """Draw the airspeed and altitude tapes on the sides"""
        w, h = self.width(), self.height()
        
        # Airspeed tape (left)
        airspeed_rect = QtCore.QRectF(30, 100, 80, h - 200)
        self.draw_vertical_tape(painter, airspeed_rect, self.airspeed, 5, "ASPD", "m/s")
        
        # Altitude tape (right)
        alt_rect = QtCore.QRectF(w - 110, 100, 80, h - 200)
        self.draw_vertical_tape(painter, alt_rect, self.altitude, 10, "ALT", "m")

    def draw_vertical_tape(self, painter, rect, value, step, label, unit):
        """Draw a vertical tape instrument"""
        painter.save()
        
        # Background
        painter.fillRect(rect, QtGui.QColor(0, 0, 0, 150))
        painter.setPen(QtGui.QPen(self.color_primary, 1))
        painter.drawRect(rect)
        
        # Label
        painter.setFont(self.font_small)
        painter.setPen(self.color_secondary)
        label_rect = QtCore.QRectF(rect.left(), rect.top() - 25, rect.width(), 20)
        painter.drawText(label_rect, QtCore.Qt.AlignCenter, f"{label}")
        
        # Unit
        unit_rect = QtCore.QRectF(rect.left(), rect.top() - 45, rect.width(), 20)
        painter.drawText(unit_rect, QtCore.Qt.AlignCenter, f"({unit})")
        
        # Value display
        painter.setFont(self.font_medium)
        value_rect = QtCore.QRectF(rect.left(), rect.center().y() - 15, rect.width(), 30)
        painter.fillRect(value_rect, QtGui.QColor(0, 0, 0, 200))
        painter.setPen(self.color_primary)
        painter.drawText(value_rect, QtCore.Qt.AlignCenter, f"{value:.0f}")
        
        # Scale
        center_y = rect.center().y()
        pixels_per_unit = rect.height() / 100
        
        painter.setFont(self.font_tiny)
        painter.setPen(self.color_primary)
        
        # Draw scale marks
        for i in range(int(value - 50), int(value + 51), step):
            y = center_y - (i - value) * pixels_per_unit
            if y < rect.top() + 10 or y > rect.bottom() - 10:
                continue
                
            # Major marks
            if i % (step * 2) == 0:
                painter.drawLine(int(rect.right() - 15), int(y), int(rect.right()), int(y))
                text_rect = QtCore.QRectF(rect.left() + 5, y - 8, rect.width() - 25, 16)
                painter.drawText(text_rect, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, str(i))
            # Minor marks
            else:
                painter.drawLine(int(rect.right() - 10), int(y), int(rect.right()), int(y))
        
        painter.restore()

    def draw_flight_mode(self, painter):
        """Draw the flight mode indicator"""
        painter.save()
        w, h = self.width(), self.height()
        
        # Flight mode background - moved to bottom of HUD
        mode_rect = QtCore.QRectF(w/2 - 150, h - 50, 300, 40)
        painter.fillRect(mode_rect, QtGui.QColor(0, 0, 0, 150))
        painter.setPen(QtGui.QPen(self.color_primary, 1))
        painter.drawRect(mode_rect)
        
        # Flight mode text
        painter.setFont(self.font_medium)
        painter.setPen(self.color_secondary)
        mode_text = f"MODE: {self.flight_mode.upper()}"
        painter.drawText(mode_rect, QtCore.Qt.AlignCenter, mode_text)
        
        painter.restore()

    def draw_status_indicators(self, painter):
        """Draw status indicators in corners"""
        painter.save()
        w, h = self.width(), self.height()
        
        # Top-left indicators (removed connection status)
        painter.setFont(self.font_small)
        
        # Armed status - aligned with connection status height
        armed_color = self.color_danger if self._is_armed else self.color_success
        painter.setPen(armed_color)
        armed_text = "ARMED: YES" if self._is_armed else "ARMED: NO"
        painter.drawText(20, 30, armed_text)
        
        # Top-right indicators (connection status moved here and shifted right)
        painter.setPen(self.color_primary)
        
        # Connection status - moved 10 pixels to the right
        conn_color = self.color_success if self._connected else self.color_warning
        painter.setPen(conn_color)
        conn_text = "CONN: ON" if self._connected else "CONN: OFF"
        painter.drawText(w - 140, 30, conn_text)
        
        # Bottom-right indicators (GPS and battery moved here)
        painter.setPen(self.color_primary)
        
        # GPS status
        fix_map = {0: "NO GPS", 1: "NO FIX", 2: "2D", 3: "3D", 4: "DGPS", 5: "RTK FLT", 6: "RTK FIX"}
        gps_text = f"GPS: {self.gps_sats} sats ({fix_map.get(self.gps_fix, 'N/A')})"
        painter.drawText(w - 250, h - 60, gps_text)
        
        # Battery status
        bat_color = self.color_success
        if self.battery_level < 50:
            bat_color = self.color_warning
        if self.battery_level < 20:
            bat_color = self.color_danger
        painter.setPen(bat_color)
        painter.drawText(w - 250, h - 40, f"BAT: {self.battery_level:.0f}%")
        
        # Bottom indicators
        painter.setPen(self.color_secondary)
        painter.setFont(self.font_small)
        painter.drawText(20, h - 40, f"ASPD: {self.airspeed:.1f} m/s")
        painter.drawText(20, h - 25, f"GSPD: {self.groundspeed:.1f} m/s")
        
        painter.restore()

    def draw_warnings(self, painter):
        """Draw warning messages"""
        if not self.warning:
            return
            
        painter.save()
        w, h = self.width(), self.height()
        
        # Warning background
        warning_rect = QtCore.QRectF(w/2 - 200, h/2 - 40, 400, 80)
        painter.fillRect(warning_rect, QtGui.QColor(200, 0, 0, 180))
        painter.setPen(QtGui.QPen(self.color_warning, 2))
        painter.drawRect(warning_rect)
        
        # Warning icon
        painter.setFont(self.font_large)
        painter.setPen(self.color_warning)
        painter.drawText(QtCore.QRectF(w/2 - 190, h/2 - 35, 30, 30), QtCore.Qt.AlignCenter, "⚠")
        
        # Warning text
        painter.setFont(self.font_medium)
        painter.drawText(QtCore.QRectF(w/2 - 150, h/2 - 15, 300, 30), QtCore.Qt.AlignCenter, self.warning)
        
        painter.restore()
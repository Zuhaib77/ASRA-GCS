"use client"

import type { DroneData } from "./types"
import { Satellite, MapPin, Crosshair, Navigation2, TrendingUp } from "lucide-react"

interface GPSPanelProps {
  drone: DroneData
}

export function GPSPanel({ drone }: GPSPanelProps) {
  const getFixTypeLabel = (fixType: number) => {
    switch (fixType) {
      case 0:
        return { label: "NO FIX", color: "#ff3333" }
      case 1:
        return { label: "NO FIX", color: "#ff3333" }
      case 2:
        return { label: "2D FIX", color: "#ffa500" }
      case 3:
        return { label: "3D FIX", color: "#00ff88" }
      case 4:
        return { label: "DGPS", color: "#00ff88" }
      case 5:
        return { label: "RTK FLOAT", color: "#00d4ff" }
      case 6:
        return { label: "RTK FIXED", color: "#00d4ff" }
      default:
        return { label: "UNKNOWN", color: "#71717a" }
    }
  }

  const getDOPColor = (value: number) => {
    if (value <= 1) return "#00ff88"
    if (value <= 2) return "#00d4ff"
    if (value <= 5) return "#ffa500"
    return "#ff3333"
  }

  const getDOPLabel = (value: number) => {
    if (value <= 1) return "Ideal"
    if (value <= 2) return "Excellent"
    if (value <= 5) return "Good"
    if (value <= 10) return "Moderate"
    return "Poor"
  }

  const formatCoordinate = (value: number, isLat: boolean) => {
    const direction = isLat ? (value >= 0 ? "N" : "S") : value >= 0 ? "E" : "W"
    const absValue = Math.abs(value)
    const degrees = Math.floor(absValue)
    const minutes = (absValue - degrees) * 60
    const minutesInt = Math.floor(minutes)
    const seconds = (minutes - minutesInt) * 60

    return {
      decimal: `${value.toFixed(6)}°`,
      dms: `${degrees}° ${minutesInt}' ${seconds.toFixed(2)}" ${direction}`,
    }
  }

  const fixType = getFixTypeLabel(drone.gpsFixType)
  const lat = formatCoordinate(drone.latitude, true)
  const lon = formatCoordinate(drone.longitude, false)

  // Generate satellite signal bars
  const satelliteBars = Array.from({ length: 12 }, (_, i) => {
    const isActive = i < drone.satellites
    const strength = isActive ? 40 + Math.random() * 60 : 0
    return { isActive, strength }
  })

  return (
    <div className="gcs-panel p-4">
      <div className="gcs-panel-header -mx-4 -mt-4 mb-4 px-4 py-2 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Satellite className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-semibold text-white">GPS Status</h3>
          </div>
          <div
            className="px-2 py-0.5 rounded text-xs font-mono font-bold"
            style={{
              backgroundColor: `${fixType.color}20`,
              color: fixType.color,
              border: `1px solid ${fixType.color}50`,
            }}
          >
            {fixType.label}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {/* Satellite Count & Visualization */}
        <div className="p-3 rounded bg-secondary/50 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-muted-foreground">SATELLITES</span>
            <span className="text-sm font-mono text-[#00ff88] font-bold">{drone.satellites}</span>
          </div>
          <div className="flex items-end gap-1 h-8">
            {satelliteBars.map((bar, i) => (
              <div
                key={i}
                className="flex-1 rounded-t transition-all"
                style={{
                  height: bar.isActive ? `${bar.strength}%` : "10%",
                  backgroundColor: bar.isActive
                    ? bar.strength > 70
                      ? "#00ff88"
                      : bar.strength > 40
                        ? "#ffa500"
                        : "#ff3333"
                    : "#2e2e3e",
                }}
              />
            ))}
          </div>
        </div>

        {/* DOP Values */}
        <div className="grid grid-cols-3 gap-2">
          <div className="p-2 rounded bg-secondary/50 border border-border text-center">
            <span className="text-[10px] font-mono text-muted-foreground block">HDOP</span>
            <span className="text-sm font-mono font-bold" style={{ color: getDOPColor(drone.hdop) }}>
              {drone.hdop.toFixed(1)}
            </span>
            <span className="text-[9px] font-mono block" style={{ color: getDOPColor(drone.hdop) }}>
              {getDOPLabel(drone.hdop)}
            </span>
          </div>
          <div className="p-2 rounded bg-secondary/50 border border-border text-center">
            <span className="text-[10px] font-mono text-muted-foreground block">VDOP</span>
            <span className="text-sm font-mono font-bold" style={{ color: getDOPColor(drone.vdop) }}>
              {drone.vdop.toFixed(1)}
            </span>
            <span className="text-[9px] font-mono block" style={{ color: getDOPColor(drone.vdop) }}>
              {getDOPLabel(drone.vdop)}
            </span>
          </div>
          <div className="p-2 rounded bg-secondary/50 border border-border text-center">
            <span className="text-[10px] font-mono text-muted-foreground block">PDOP</span>
            <span className="text-sm font-mono font-bold" style={{ color: getDOPColor(drone.pdop) }}>
              {drone.pdop.toFixed(1)}
            </span>
            <span className="text-[9px] font-mono block" style={{ color: getDOPColor(drone.pdop) }}>
              {getDOPLabel(drone.pdop)}
            </span>
          </div>
        </div>

        {/* Coordinates */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <MapPin className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs font-mono text-muted-foreground">POSITION</span>
          </div>
          <div className="p-3 rounded bg-secondary/50 border border-border space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-mono text-muted-foreground">LAT</span>
              <div className="text-right">
                <span className="text-xs font-mono text-primary block">{lat.decimal}</span>
                <span className="text-[9px] font-mono text-muted-foreground">{lat.dms}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-mono text-muted-foreground">LON</span>
              <div className="text-right">
                <span className="text-xs font-mono text-primary block">{lon.decimal}</span>
                <span className="text-[9px] font-mono text-muted-foreground">{lon.dms}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Altitude */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded bg-secondary/50 border border-border">
            <div className="flex items-center gap-1 mb-1">
              <TrendingUp className="w-3 h-3 text-muted-foreground" />
              <span className="text-[10px] font-mono text-muted-foreground">ALT MSL</span>
            </div>
            <span className="text-sm font-mono text-foreground font-bold">{drone.altitudeMSL.toFixed(1)} m</span>
          </div>
          <div className="p-2 rounded bg-secondary/50 border border-border">
            <div className="flex items-center gap-1 mb-1">
              <Crosshair className="w-3 h-3 text-muted-foreground" />
              <span className="text-[10px] font-mono text-muted-foreground">ALT AGL</span>
            </div>
            <span className="text-sm font-mono text-[#00ff88] font-bold">{drone.altitudeAGL.toFixed(1)} m</span>
          </div>
        </div>

        {/* Ground Speed & Course */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded bg-secondary/50 border border-border">
            <div className="flex items-center gap-1 mb-1">
              <Navigation2 className="w-3 h-3 text-muted-foreground" />
              <span className="text-[10px] font-mono text-muted-foreground">GND SPD</span>
            </div>
            <span className="text-sm font-mono text-foreground font-bold">{drone.groundSpeed.toFixed(1)} m/s</span>
          </div>
          <div className="p-2 rounded bg-secondary/50 border border-border">
            <div className="flex items-center gap-1 mb-1">
              <Navigation2
                className="w-3 h-3 text-muted-foreground"
                style={{ transform: `rotate(${drone.heading}deg)` }}
              />
              <span className="text-[10px] font-mono text-muted-foreground">COURSE</span>
            </div>
            <span className="text-sm font-mono text-foreground font-bold">{drone.heading.toFixed(0)}°</span>
          </div>
        </div>
      </div>
    </div>
  )
}

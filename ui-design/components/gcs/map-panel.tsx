"use client"

import { useRef, useEffect, useState } from "react"
import type { DroneData } from "./types"
import { Map, ZoomIn, ZoomOut, Layers, Home, Crosshair, Navigation } from "lucide-react"
import { Button } from "@/components/ui/button"

interface MapPanelProps {
  drones: DroneData[]
  showBothDrones?: boolean
}

export function MapPanel({ drones, showBothDrones = false }: MapPanelProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [zoom, setZoom] = useState(15)
  const [mapStyle, setMapStyle] = useState<"satellite" | "terrain">("satellite")

  // Track flight paths
  const [flightPaths, setFlightPaths] = useState<{ [key: string]: { lat: number; lon: number }[] }>({
    alpha: [],
    bravo: [],
  })

  useEffect(() => {
    drones.forEach((drone) => {
      setFlightPaths((prev) => ({
        ...prev,
        [drone.id]: [...(prev[drone.id] || []).slice(-100), { lat: drone.latitude, lon: drone.longitude }],
      }))
    })
  }, [drones])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height

    // Dark satellite-style background
    if (mapStyle === "satellite") {
      // Create dark textured background
      const gradient = ctx.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, width / 2)
      gradient.addColorStop(0, "#1a2632")
      gradient.addColorStop(1, "#0f1a24")
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, width, height)

      // Add some terrain texture
      ctx.fillStyle = "rgba(255, 255, 255, 0.02)"
      for (let i = 0; i < 200; i++) {
        const x = Math.random() * width
        const y = Math.random() * height
        const size = Math.random() * 3 + 1
        ctx.beginPath()
        ctx.arc(x, y, size, 0, Math.PI * 2)
        ctx.fill()
      }
    } else {
      ctx.fillStyle = "#0d1117"
      ctx.fillRect(0, 0, width, height)
    }

    // Draw grid lines
    ctx.strokeStyle = "rgba(0, 212, 255, 0.1)"
    ctx.lineWidth = 1
    const gridSize = 50

    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }

    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }

    // Calculate center and scale
    const centerLat = showBothDrones
      ? (drones[0].latitude + (drones[1]?.latitude || drones[0].latitude)) / 2
      : drones[0].latitude
    const centerLon = showBothDrones
      ? (drones[0].longitude + (drones[1]?.longitude || drones[0].longitude)) / 2
      : drones[0].longitude

    const scale = zoom * 50000

    const latToY = (lat: number) => height / 2 - (lat - centerLat) * scale
    const lonToX = (lon: number) => width / 2 + (lon - centerLon) * scale

    // Draw flight paths
    const droneColors: { [key: string]: string } = {
      alpha: "#00d4ff",
      bravo: "#a78bfa",
    }

    Object.entries(flightPaths).forEach(([droneId, path]) => {
      if (path.length < 2) return
      if (!showBothDrones && droneId !== drones[0].id) return

      ctx.strokeStyle = droneColors[droneId] || "#00d4ff"
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.beginPath()

      path.forEach((point, i) => {
        const x = lonToX(point.lon)
        const y = latToY(point.lat)
        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      ctx.stroke()
      ctx.setLineDash([])
    })

    // Draw home position for each drone
    drones.forEach((drone) => {
      if (!showBothDrones && drone.id !== drones[0].id) return

      const homeX = lonToX(drone.homeLongitude)
      const homeY = latToY(drone.homeLatitude)

      // Home marker
      ctx.fillStyle = "#ffa500"
      ctx.strokeStyle = "#ffa500"
      ctx.lineWidth = 2

      ctx.beginPath()
      ctx.arc(homeX, homeY, 8, 0, Math.PI * 2)
      ctx.stroke()

      ctx.font = "bold 10px sans-serif"
      ctx.textAlign = "center"
      ctx.fillText("H", homeX, homeY + 4)
    })

    // Draw drone positions
    drones.forEach((drone, index) => {
      if (!showBothDrones && index > 0) return

      const x = lonToX(drone.longitude)
      const y = latToY(drone.latitude)

      const color = droneColors[drone.id] || "#00d4ff"

      // Draw heading line
      const headingRad = (drone.heading - 90) * (Math.PI / 180)
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(x, y)
      ctx.lineTo(x + Math.cos(headingRad) * 30, y + Math.sin(headingRad) * 30)
      ctx.stroke()

      // Draw drone icon (aircraft shape)
      ctx.save()
      ctx.translate(x, y)
      ctx.rotate(headingRad + Math.PI / 2)

      ctx.fillStyle = color
      ctx.beginPath()
      // Aircraft body
      ctx.moveTo(0, -15)
      ctx.lineTo(5, 5)
      ctx.lineTo(0, 0)
      ctx.lineTo(-5, 5)
      ctx.closePath()
      ctx.fill()

      // Wings
      ctx.beginPath()
      ctx.moveTo(-12, 0)
      ctx.lineTo(12, 0)
      ctx.lineTo(10, 3)
      ctx.lineTo(-10, 3)
      ctx.closePath()
      ctx.fill()

      ctx.restore()

      // Drone label
      ctx.fillStyle = "rgba(0, 0, 0, 0.8)"
      ctx.fillRect(x + 15, y - 25, 70, 35)
      ctx.strokeStyle = color
      ctx.strokeRect(x + 15, y - 25, 70, 35)

      ctx.fillStyle = color
      ctx.font = "bold 10px monospace"
      ctx.textAlign = "left"
      ctx.fillText(drone.name.toUpperCase(), x + 20, y - 12)

      ctx.fillStyle = "#e4e4e7"
      ctx.font = "9px monospace"
      ctx.fillText(`ALT: ${drone.altitudeAGL.toFixed(0)}m`, x + 20, y)
      ctx.fillText(`SPD: ${drone.groundSpeed.toFixed(1)}m/s`, x + 20, y + 10)
    })

    // Draw scale bar
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)"
    ctx.fillRect(10, height - 35, 100, 25)
    ctx.strokeStyle = "#71717a"
    ctx.strokeRect(10, height - 35, 100, 25)

    ctx.fillStyle = "#e4e4e7"
    ctx.font = "10px monospace"
    ctx.textAlign = "center"
    const scaleDistance = (100 / scale) * 111000
    ctx.fillText(`${scaleDistance.toFixed(0)}m`, 60, height - 18)

    ctx.strokeStyle = "#e4e4e7"
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(20, height - 15)
    ctx.lineTo(90, height - 15)
    ctx.moveTo(20, height - 18)
    ctx.lineTo(20, height - 12)
    ctx.moveTo(90, height - 18)
    ctx.lineTo(90, height - 12)
    ctx.stroke()

    // Draw compass
    const compassX = width - 40
    const compassY = 40
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)"
    ctx.beginPath()
    ctx.arc(compassX, compassY, 25, 0, Math.PI * 2)
    ctx.fill()
    ctx.strokeStyle = "#71717a"
    ctx.beginPath()
    ctx.arc(compassX, compassY, 25, 0, Math.PI * 2)
    ctx.stroke()

    ctx.fillStyle = "#ff3333"
    ctx.beginPath()
    ctx.moveTo(compassX, compassY - 18)
    ctx.lineTo(compassX - 5, compassY)
    ctx.lineTo(compassX + 5, compassY)
    ctx.closePath()
    ctx.fill()

    ctx.fillStyle = "#e4e4e7"
    ctx.beginPath()
    ctx.moveTo(compassX, compassY + 18)
    ctx.lineTo(compassX - 5, compassY)
    ctx.lineTo(compassX + 5, compassY)
    ctx.closePath()
    ctx.fill()

    ctx.fillStyle = "#e4e4e7"
    ctx.font = "bold 10px sans-serif"
    ctx.textAlign = "center"
    ctx.fillText("N", compassX, compassY - 5)
  }, [drones, zoom, mapStyle, flightPaths, showBothDrones])

  return (
    <div className="gcs-panel p-0 overflow-hidden relative flex flex-col h-full">
      {/* Header */}
      <div className="gcs-panel-header px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Map className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-white">Map View</h3>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setMapStyle(mapStyle === "satellite" ? "terrain" : "satellite")}
            className="h-7 px-2 text-muted-foreground hover:text-white hover:bg-muted"
          >
            <Layers className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative">
        <canvas ref={canvasRef} width={600} height={400} className="w-full h-full" />

        {/* Zoom Controls */}
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setZoom((z) => Math.min(z + 1, 20))}
            className="h-7 w-7 p-0 bg-black/50 text-white hover:bg-black/70"
          >
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setZoom((z) => Math.max(z - 1, 10))}
            className="h-7 w-7 p-0 bg-black/50 text-white hover:bg-black/70"
          >
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 bg-black/50 text-white hover:bg-black/70">
            <Home className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 bg-black/50 text-white hover:bg-black/70">
            <Crosshair className="w-4 h-4" />
          </Button>
        </div>

        {/* Drone Legend */}
        {showBothDrones && (
          <div className="absolute bottom-2 left-2 flex flex-col gap-1 bg-black/70 rounded p-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-primary" />
              <span className="text-xs text-white font-mono">ALPHA</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-[#a78bfa]" />
              <span className="text-xs text-white font-mono">BRAVO</span>
            </div>
          </div>
        )}

        {/* Quick Info */}
        <div className="absolute top-2 right-12 flex flex-col gap-1">
          {drones.slice(0, showBothDrones ? 2 : 1).map((drone) => (
            <div
              key={drone.id}
              className="flex items-center gap-2 px-2 py-1 rounded bg-black/70 border"
              style={{ borderColor: drone.id === "alpha" ? "rgba(0, 212, 255, 0.5)" : "rgba(167, 139, 250, 0.5)" }}
            >
              <Navigation
                className="w-3 h-3"
                style={{
                  color: drone.id === "alpha" ? "#00d4ff" : "#a78bfa",
                  transform: `rotate(${drone.heading}deg)`,
                }}
              />
              <span className="text-[10px] font-mono text-foreground">{drone.heading.toFixed(0)}°</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

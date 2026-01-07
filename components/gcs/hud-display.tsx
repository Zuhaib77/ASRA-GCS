"use client"

import { useRef, useEffect } from "react"
import type { DroneData } from "./types"
import { Battery, Signal, Navigation } from "lucide-react"

interface HUDDisplayProps {
  drone: DroneData
  compact?: boolean
}

export function HUDDisplay({ drone, compact = false }: HUDDisplayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2

    // Clear canvas
    ctx.fillStyle = "#0a0a0f"
    ctx.fillRect(0, 0, width, height)

    // Draw artificial horizon background
    ctx.save()
    ctx.translate(centerX, centerY)
    ctx.rotate((drone.roll * Math.PI) / 180)

    // Sky
    const pitchOffset = (drone.pitch / 90) * (height / 2)
    ctx.fillStyle = "#1a3a5c"
    ctx.fillRect(-width, -height + pitchOffset, width * 2, height)

    // Ground
    ctx.fillStyle = "#3d2817"
    ctx.fillRect(-width, pitchOffset, width * 2, height)

    // Horizon line
    ctx.strokeStyle = "#00d4ff"
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(-width, pitchOffset)
    ctx.lineTo(width, pitchOffset)
    ctx.stroke()

    // Pitch ladder
    ctx.strokeStyle = "#ffffff"
    ctx.fillStyle = "#ffffff"
    ctx.font = compact ? "10px monospace" : "12px monospace"
    ctx.textAlign = "center"
    ctx.lineWidth = 1

    for (let i = -80; i <= 80; i += 10) {
      if (i === 0) continue
      const y = pitchOffset - (i / 90) * (height / 2)
      const lineWidth = i % 20 === 0 ? 60 : 30

      ctx.beginPath()
      ctx.moveTo(-lineWidth, y)
      ctx.lineTo(-10, y)
      ctx.moveTo(10, y)
      ctx.lineTo(lineWidth, y)
      ctx.stroke()

      if (i % 20 === 0) {
        ctx.fillText(`${i}`, -lineWidth - 15, y + 4)
        ctx.fillText(`${i}`, lineWidth + 15, y + 4)
      }
    }

    ctx.restore()

    // Draw fixed elements (not affected by roll)
    // Center crosshair / aircraft symbol
    ctx.strokeStyle = "#ffa500"
    ctx.lineWidth = 3
    ctx.beginPath()
    // Left wing
    ctx.moveTo(centerX - 80, centerY)
    ctx.lineTo(centerX - 30, centerY)
    ctx.lineTo(centerX - 30, centerY + 10)
    // Right wing
    ctx.moveTo(centerX + 80, centerY)
    ctx.lineTo(centerX + 30, centerY)
    ctx.lineTo(centerX + 30, centerY + 10)
    // Center dot
    ctx.moveTo(centerX + 5, centerY)
    ctx.arc(centerX, centerY, 5, 0, Math.PI * 2)
    ctx.stroke()

    // Draw heading tape at top
    const headingTapeY = compact ? 20 : 30
    const headingTapeWidth = compact ? 200 : 300
    ctx.fillStyle = "rgba(10, 10, 15, 0.8)"
    ctx.fillRect(centerX - headingTapeWidth / 2, 0, headingTapeWidth, headingTapeY + 15)

    ctx.strokeStyle = "#ffffff"
    ctx.fillStyle = "#ffffff"
    ctx.font = compact ? "9px monospace" : "11px monospace"
    ctx.textAlign = "center"
    ctx.lineWidth = 1

    const headingRange = compact ? 40 : 60
    for (let i = -headingRange; i <= headingRange; i += 5) {
      const hdg = (drone.heading + i + 360) % 360
      const x = centerX + (i / headingRange) * (headingTapeWidth / 2)

      if (x < centerX - headingTapeWidth / 2 || x > centerX + headingTapeWidth / 2) continue

      ctx.beginPath()
      ctx.moveTo(x, headingTapeY)
      ctx.lineTo(x, headingTapeY + (i % 10 === 0 ? 8 : 4))
      ctx.stroke()

      if (i % 10 === 0) {
        let label = Math.round(hdg).toString()
        if (hdg === 0 || hdg === 360) label = "N"
        else if (hdg === 90) label = "E"
        else if (hdg === 180) label = "S"
        else if (hdg === 270) label = "W"

        ctx.fillText(label, x, headingTapeY - 3)
      }
    }

    // Heading indicator triangle
    ctx.fillStyle = "#00d4ff"
    ctx.beginPath()
    ctx.moveTo(centerX, headingTapeY + 12)
    ctx.lineTo(centerX - 6, headingTapeY + 20)
    ctx.lineTo(centerX + 6, headingTapeY + 20)
    ctx.closePath()
    ctx.fill()

    // Current heading display
    ctx.fillStyle = "#0a0a0f"
    ctx.fillRect(centerX - 25, headingTapeY + 22, 50, 18)
    ctx.strokeStyle = "#00d4ff"
    ctx.strokeRect(centerX - 25, headingTapeY + 22, 50, 18)
    ctx.fillStyle = "#00d4ff"
    ctx.font = compact ? "11px monospace" : "13px monospace"
    ctx.fillText(`${Math.round(drone.heading)}°`, centerX, headingTapeY + 35)

    // Altitude tape (right side)
    const altTapeX = width - (compact ? 50 : 70)
    const altTapeHeight = height - 80
    ctx.fillStyle = "rgba(10, 10, 15, 0.8)"
    ctx.fillRect(altTapeX - 10, 50, compact ? 60 : 80, altTapeHeight)

    ctx.strokeStyle = "#ffffff"
    ctx.fillStyle = "#ffffff"
    ctx.font = compact ? "9px monospace" : "10px monospace"
    ctx.textAlign = "left"

    const altRange = 50
    for (let i = -altRange; i <= altRange; i += 10) {
      const alt = Math.round(drone.altitudeAGL + i)
      if (alt < 0) continue
      const y = centerY - (i / altRange) * (altTapeHeight / 2)

      ctx.beginPath()
      ctx.moveTo(altTapeX, y)
      ctx.lineTo(altTapeX + 8, y)
      ctx.stroke()

      ctx.fillText(`${alt}`, altTapeX + 12, y + 3)
    }

    // Current altitude box
    ctx.fillStyle = "#0a0a0f"
    ctx.fillRect(altTapeX - 15, centerY - 12, compact ? 55 : 65, 24)
    ctx.strokeStyle = "#00ff88"
    ctx.strokeRect(altTapeX - 15, centerY - 12, compact ? 55 : 65, 24)
    ctx.fillStyle = "#00ff88"
    ctx.font = compact ? "12px monospace" : "14px monospace"
    ctx.fillText(`${Math.round(drone.altitudeAGL)}m`, altTapeX - 10, centerY + 5)

    // Speed tape (left side)
    const speedTapeX = compact ? 50 : 70
    ctx.fillStyle = "rgba(10, 10, 15, 0.8)"
    ctx.fillRect(0, 50, speedTapeX + 10, altTapeHeight)

    ctx.strokeStyle = "#ffffff"
    ctx.fillStyle = "#ffffff"
    ctx.textAlign = "right"

    const speedRange = 20
    for (let i = -speedRange; i <= speedRange; i += 5) {
      const spd = Math.round(drone.groundSpeed + i)
      if (spd < 0) continue
      const y = centerY - (i / speedRange) * (altTapeHeight / 2)

      ctx.beginPath()
      ctx.moveTo(speedTapeX - 8, y)
      ctx.lineTo(speedTapeX, y)
      ctx.stroke()

      ctx.fillText(`${spd}`, speedTapeX - 12, y + 3)
    }

    // Current speed box
    ctx.fillStyle = "#0a0a0f"
    ctx.fillRect(5, centerY - 12, compact ? 50 : 60, 24)
    ctx.strokeStyle = "#00ff88"
    ctx.strokeRect(5, centerY - 12, compact ? 50 : 60, 24)
    ctx.fillStyle = "#00ff88"
    ctx.font = compact ? "12px monospace" : "14px monospace"
    ctx.textAlign = "right"
    ctx.fillText(`${drone.groundSpeed.toFixed(1)}`, speedTapeX - 15, centerY + 5)

    // Labels
    ctx.fillStyle = "#71717a"
    ctx.font = "9px monospace"
    ctx.textAlign = "center"
    ctx.fillText("GS m/s", speedTapeX / 2, height - 15)
    ctx.fillText("ALT m", altTapeX + 20, height - 15)
  }, [drone, compact])

  const getBatteryColor = (percent: number) => {
    if (percent > 50) return "#00ff88"
    if (percent > 25) return "#ffa500"
    return "#ff3333"
  }

  const getSignalColor = (rssi: number) => {
    if (rssi > 70) return "#00ff88"
    if (rssi > 40) return "#ffa500"
    return "#ff3333"
  }

  return (
    <div className="gcs-panel p-0 overflow-hidden relative">
      {/* Canvas HUD */}
      <canvas ref={canvasRef} width={compact ? 320 : 500} height={compact ? 240 : 350} className="w-full h-auto" />

      {/* Overlay Info */}
      <div className="absolute top-2 left-2 flex flex-col gap-1">
        {/* Flight Mode */}
        <div
          className={`px-2 py-1 rounded text-xs font-mono font-bold ${
            drone.isArmed
              ? "bg-[#00ff88]/20 text-[#00ff88] border border-[#00ff88]/50"
              : "bg-muted-foreground/20 text-muted-foreground border border-muted-foreground/50"
          }`}
        >
          {drone.isArmed ? "ARMED" : "DISARMED"}
        </div>
        <div className="px-2 py-1 rounded text-xs font-mono bg-primary/20 text-primary border border-primary/50">
          {drone.flightMode}
        </div>
      </div>

      {/* Right side overlay */}
      <div className="absolute top-2 right-2 flex flex-col gap-1 items-end">
        {/* Battery */}
        <div className="flex items-center gap-1 px-2 py-1 rounded bg-black/50 border border-border">
          <Battery className="w-3 h-3" style={{ color: getBatteryColor(drone.batteryPercent) }} />
          <span className="text-xs font-mono" style={{ color: getBatteryColor(drone.batteryPercent) }}>
            {drone.batteryPercent.toFixed(0)}%
          </span>
          <span className="text-[10px] font-mono text-muted-foreground">{drone.batteryVoltage.toFixed(1)}V</span>
        </div>

        {/* Signal */}
        <div className="flex items-center gap-1 px-2 py-1 rounded bg-black/50 border border-border">
          <Signal className="w-3 h-3" style={{ color: getSignalColor(drone.rssi) }} />
          <span className="text-xs font-mono" style={{ color: getSignalColor(drone.rssi) }}>
            {drone.rssi}%
          </span>
        </div>
      </div>

      {/* Bottom overlay */}
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex items-center gap-3 px-3 py-1 rounded bg-black/50 border border-border">
        <div className="flex items-center gap-1">
          <Navigation className="w-3 h-3 text-primary" />
          <span className="text-xs font-mono text-foreground">{drone.distanceToHome.toFixed(0)}m</span>
        </div>
        <div className="text-[10px] font-mono text-muted-foreground">
          VS {drone.climbRate >= 0 ? "+" : ""}
          {drone.climbRate.toFixed(1)} m/s
        </div>
      </div>
    </div>
  )
}

"use client"

import { useState, useEffect } from "react"
import { Radio, Wifi, WifiOff, AlertTriangle, Clock, Satellite } from "lucide-react"

interface GCSHeaderProps {
  isConnected: boolean
  totalSatellites: number
  systemAlerts: number
}

export function GCSHeader({ isConnected, totalSatellites, systemAlerts }: GCSHeaderProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTime = (date: Date) => {
    return date.toISOString().slice(11, 19) + " UTC"
  }

  const formatDate = (date: Date) => {
    return date.toISOString().slice(0, 10)
  }

  return (
    <header className="h-12 bg-background border-b border-border flex items-center justify-between px-4">
      {/* Left Section - Logo & Title */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-primary to-[#0088aa] flex items-center justify-center">
            <Radio className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white tracking-wide">GROUND CONTROL STATION</h1>
            <p className="text-[10px] text-muted-foreground font-mono">MAVLink v2.0 Protocol</p>
          </div>
        </div>
      </div>

      {/* Center Section - Connection Status */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-[#00ff88]" />
              <span className="text-xs font-mono text-[#00ff88]">LINK ACTIVE</span>
              <span className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse-glow" />
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-destructive" />
              <span className="text-xs font-mono text-destructive">NO LINK</span>
            </>
          )}
        </div>

        <div className="h-6 w-px bg-border" />

        <div className="flex items-center gap-2">
          <Satellite className="w-4 h-4 text-primary" />
          <span className="text-xs font-mono text-foreground">
            {totalSatellites} <span className="text-muted-foreground">SATS</span>
          </span>
        </div>

        {systemAlerts > 0 && (
          <>
            <div className="h-6 w-px bg-border" />
            <div className="flex items-center gap-2 px-2 py-1 rounded bg-[#ffa500]/10 border border-[#ffa500]/30">
              <AlertTriangle className="w-4 h-4 text-[#ffa500]" />
              <span className="text-xs font-mono text-[#ffa500]">{systemAlerts} ALERTS</span>
            </div>
          </>
        )}
      </div>

      {/* Right Section - Time */}
      <div className="flex items-center gap-4">
        <div className="text-right">
          <div className="flex items-center gap-2">
            <Clock className="w-3 h-3 text-muted-foreground" />
            <span className="text-xs font-mono text-foreground">{formatTime(currentTime)}</span>
          </div>
          <p className="text-[10px] font-mono text-muted-foreground">{formatDate(currentTime)}</p>
        </div>
      </div>
    </header>
  )
}

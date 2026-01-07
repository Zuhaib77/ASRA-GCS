"use client"

import type { DroneData, TelemetryMessage } from "./types"
import { HUDDisplay } from "./hud-display"
import { TelemetryPanel } from "./telemetry-panel"
import { MapPanel } from "./map-panel"
import { Battery, Signal, Satellite, Navigation, Power, Gauge } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CombinedViewProps {
  droneAlpha: DroneData
  droneBravo: DroneData
  messages: TelemetryMessage[]
  isConnected: boolean
  onArmDisarm: (droneId: string) => void
  onClearMessages: () => void
}

function DroneStatusCard({
  drone,
  color,
  isConnected,
  onArmDisarm,
}: {
  drone: DroneData
  color: string
  isConnected: boolean
  onArmDisarm: () => void
}) {
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
    <div className="gcs-panel p-3" style={{ borderColor: `${color}30` }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
          <span className="text-sm font-semibold text-white">{drone.name}</span>
        </div>
        <div
          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
            drone.isArmed
              ? "bg-[#00ff88]/20 text-[#00ff88] border border-[#00ff88]/50"
              : "bg-muted-foreground/20 text-muted-foreground border border-muted-foreground/50"
          }`}
        >
          {drone.isArmed ? "ARMED" : "DISARMED"}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        <div className="text-center p-2 rounded bg-secondary/50">
          <Battery className="w-3 h-3 mx-auto mb-1" style={{ color: getBatteryColor(drone.batteryPercent) }} />
          <span className="text-xs font-mono" style={{ color: getBatteryColor(drone.batteryPercent) }}>
            {drone.batteryPercent.toFixed(0)}%
          </span>
        </div>
        <div className="text-center p-2 rounded bg-secondary/50">
          <Signal className="w-3 h-3 mx-auto mb-1" style={{ color: getSignalColor(drone.rssi) }} />
          <span className="text-xs font-mono" style={{ color: getSignalColor(drone.rssi) }}>
            {drone.rssi}%
          </span>
        </div>
        <div className="text-center p-2 rounded bg-secondary/50">
          <Satellite className="w-3 h-3 mx-auto mb-1 text-primary" />
          <span className="text-xs font-mono text-foreground">{drone.satellites}</span>
        </div>
        <div className="text-center p-2 rounded bg-secondary/50">
          <Navigation className="w-3 h-3 mx-auto mb-1 text-[#ffa500]" />
          <span className="text-xs font-mono text-foreground">{drone.distanceToHome.toFixed(0)}m</span>
        </div>
      </div>

      {/* Flight Data */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="p-2 rounded bg-secondary/50">
          <span className="text-[9px] font-mono text-muted-foreground block">ALT</span>
          <span className="text-sm font-mono text-[#00ff88]">{drone.altitudeAGL.toFixed(0)}m</span>
        </div>
        <div className="p-2 rounded bg-secondary/50">
          <span className="text-[9px] font-mono text-muted-foreground block">SPD</span>
          <span className="text-sm font-mono text-foreground">{drone.groundSpeed.toFixed(1)}</span>
        </div>
        <div className="p-2 rounded bg-secondary/50">
          <span className="text-[9px] font-mono text-muted-foreground block">HDG</span>
          <span className="text-sm font-mono text-foreground">{drone.heading.toFixed(0)}°</span>
        </div>
      </div>

      {/* Mode & Actions */}
      <div className="flex items-center gap-2">
        <div
          className="flex-1 px-2 py-1.5 rounded text-xs font-mono text-center"
          style={{ backgroundColor: `${color}20`, color: color, border: `1px solid ${color}50` }}
        >
          {drone.flightMode}
        </div>
        <Button
          size="sm"
          onClick={onArmDisarm}
          disabled={!isConnected}
          className={`h-8 ${
            drone.isArmed
              ? "bg-destructive/20 hover:bg-destructive/30 text-destructive border border-destructive/50"
              : "bg-[#00ff88]/20 hover:bg-[#00ff88]/30 text-[#00ff88] border border-[#00ff88]/50"
          }`}
        >
          <Power className="w-3 h-3" />
        </Button>
      </div>
    </div>
  )
}

export function CombinedView({
  droneAlpha,
  droneBravo,
  messages,
  isConnected,
  onArmDisarm,
  onClearMessages,
}: CombinedViewProps) {
  return (
    <div className="h-full grid grid-cols-12 gap-4">
      {/* Left Column - Status Cards & Mini HUDs */}
      <div className="col-span-4 flex flex-col gap-4 overflow-y-auto">
        {/* Alpha Status */}
        <DroneStatusCard
          drone={droneAlpha}
          color="#00d4ff"
          isConnected={isConnected}
          onArmDisarm={() => onArmDisarm("alpha")}
        />

        {/* Alpha Mini HUD */}
        <HUDDisplay drone={droneAlpha} compact />

        {/* Bravo Status */}
        <DroneStatusCard
          drone={droneBravo}
          color="#a78bfa"
          isConnected={isConnected}
          onArmDisarm={() => onArmDisarm("bravo")}
        />

        {/* Bravo Mini HUD */}
        <HUDDisplay drone={droneBravo} compact />
      </div>

      {/* Center Column - Map */}
      <div className="col-span-5 flex flex-col gap-4">
        <div className="flex-1">
          <MapPanel drones={[droneAlpha, droneBravo]} showBothDrones />
        </div>

        {/* Comparison Panel */}
        <div className="gcs-panel p-4">
          <div className="flex items-center gap-2 mb-3">
            <Gauge className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-semibold text-white">Comparison</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-primary" />
                <span className="text-xs font-mono text-muted-foreground">ALPHA</span>
              </div>
              <div className="space-y-1 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Altitude</span>
                  <span className="text-foreground">{droneAlpha.altitudeAGL.toFixed(1)}m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Speed</span>
                  <span className="text-foreground">{droneAlpha.groundSpeed.toFixed(1)}m/s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Battery</span>
                  <span className="text-foreground">{droneAlpha.batteryPercent.toFixed(0)}%</span>
                </div>
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-[#a78bfa]" />
                <span className="text-xs font-mono text-muted-foreground">BRAVO</span>
              </div>
              <div className="space-y-1 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Altitude</span>
                  <span className="text-foreground">{droneBravo.altitudeAGL.toFixed(1)}m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Speed</span>
                  <span className="text-foreground">{droneBravo.groundSpeed.toFixed(1)}m/s</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Battery</span>
                  <span className="text-foreground">{droneBravo.batteryPercent.toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column - Telemetry */}
      <div className="col-span-3 h-full">
        <TelemetryPanel messages={messages} onClear={onClearMessages} />
      </div>
    </div>
  )
}

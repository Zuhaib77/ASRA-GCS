"use client"

import type { DroneData, TelemetryMessage } from "./types"
import { HUDDisplay } from "./hud-display"
import { GPSPanel } from "./gps-panel"
import { ControlPanel } from "./control-panel"
import { TelemetryPanel } from "./telemetry-panel"
import { MapPanel } from "./map-panel"

interface DroneTabProps {
  drone: DroneData
  messages: TelemetryMessage[]
  isConnected: boolean
  onArmDisarm: () => void
  onSetFlightMode: (mode: string) => void
  onClearMessages: () => void
}

export function DroneTab({
  drone,
  messages,
  isConnected,
  onArmDisarm,
  onSetFlightMode,
  onClearMessages,
}: DroneTabProps) {
  const droneMessages = messages.filter((m) => m.droneId === drone.id || m.droneId === "system")

  return (
    <div className="h-full grid grid-cols-12 gap-4">
      {/* Left Column - HUD & Controls */}
      <div className="col-span-3 flex flex-col gap-4">
        <ControlPanel
          drone={drone}
          isConnected={isConnected}
          onArmDisarm={onArmDisarm}
          onSetFlightMode={onSetFlightMode}
        />
        <GPSPanel drone={drone} />
      </div>

      {/* Center Column - HUD & Map */}
      <div className="col-span-6 flex flex-col gap-4">
        <div className="flex-1">
          <HUDDisplay drone={drone} />
        </div>
        <div className="flex-1">
          <MapPanel drones={[drone]} />
        </div>
      </div>

      {/* Right Column - Telemetry */}
      <div className="col-span-3 h-full">
        <TelemetryPanel messages={droneMessages} onClear={onClearMessages} />
      </div>
    </div>
  )
}

"use client"

import { useState, useEffect, useCallback } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { GCSHeader } from "@/components/gcs/gcs-header"
import { ConnectionPanel } from "@/components/gcs/connection-panel"
import { DroneTab } from "@/components/gcs/drone-tab"
import { CombinedView } from "@/components/gcs/combined-view"
import type { DroneData, TelemetryMessage } from "@/components/gcs/types"
import { Plane, Layers } from "lucide-react"

// Initial drone data
const createInitialDroneData = (id: string, name: string, latOffset = 0): DroneData => ({
  id,
  name,
  isArmed: false,
  flightMode: "STABILIZE",
  pitch: 0,
  roll: 0,
  yaw: 0,
  heading: 0,
  latitude: 37.7749 + latOffset,
  longitude: -122.4194 + latOffset,
  altitudeMSL: 50,
  altitudeAGL: 0,
  groundSpeed: 0,
  airSpeed: 0,
  climbRate: 0,
  gpsFixType: 3,
  satellites: 12,
  hdop: 0.9,
  vdop: 1.2,
  pdop: 1.5,
  batteryVoltage: 16.8,
  batteryPercent: 100,
  batteryCurrent: 0,
  rssi: 95,
  homeLatitude: 37.7749 + latOffset,
  homeLongitude: -122.4194 + latOffset,
  distanceToHome: 0,
  bearingToHome: 0,
})

export default function GCSPage() {
  const [isConnected, setIsConnected] = useState(false)
  const [activeTab, setActiveTab] = useState("combined")
  const [droneAlpha, setDroneAlpha] = useState<DroneData>(createInitialDroneData("alpha", "Drone Alpha", 0))
  const [droneBravo, setDroneBravo] = useState<DroneData>(createInitialDroneData("bravo", "Drone Bravo", 0.001))
  const [messages, setMessages] = useState<TelemetryMessage[]>([])

  // Simulate telemetry data updates
  useEffect(() => {
    if (!isConnected) return

    const interval = setInterval(() => {
      // Update Alpha
      setDroneAlpha((prev) => {
        const newHeading = (prev.heading + 0.5) % 360
        const newLat = prev.latitude + (Math.random() - 0.5) * 0.0001
        const newLon = prev.longitude + (Math.random() - 0.5) * 0.0001
        const distanceToHome = Math.sqrt(
          Math.pow((newLat - prev.homeLatitude) * 111000, 2) + Math.pow((newLon - prev.homeLongitude) * 111000, 2),
        )

        return {
          ...prev,
          pitch: Math.sin(Date.now() / 2000) * 15,
          roll: Math.cos(Date.now() / 3000) * 10,
          heading: newHeading,
          yaw: newHeading,
          altitudeAGL: prev.isArmed ? 50 + Math.sin(Date.now() / 5000) * 5 : 0,
          altitudeMSL: prev.isArmed ? 100 + Math.sin(Date.now() / 5000) * 5 : 50,
          groundSpeed: prev.isArmed ? 12 + Math.random() * 2 : 0,
          airSpeed: prev.isArmed ? 14 + Math.random() * 2 : 0,
          climbRate: prev.isArmed ? Math.sin(Date.now() / 3000) * 2 : 0,
          satellites: 10 + Math.floor(Math.random() * 5),
          batteryPercent: Math.max(0, prev.batteryPercent - 0.01),
          batteryVoltage: 14.8 + (prev.batteryPercent / 100) * 2,
          latitude: newLat,
          longitude: newLon,
          rssi: 85 + Math.floor(Math.random() * 15),
          distanceToHome,
        }
      })

      // Update Bravo
      setDroneBravo((prev) => {
        const newHeading = (prev.heading + 0.3) % 360
        const newLat = prev.latitude + (Math.random() - 0.5) * 0.00008
        const newLon = prev.longitude + (Math.random() - 0.5) * 0.00008
        const distanceToHome = Math.sqrt(
          Math.pow((newLat - prev.homeLatitude) * 111000, 2) + Math.pow((newLon - prev.homeLongitude) * 111000, 2),
        )

        return {
          ...prev,
          pitch: Math.sin(Date.now() / 2500) * 12,
          roll: Math.cos(Date.now() / 3500) * 8,
          heading: newHeading,
          yaw: newHeading,
          altitudeAGL: prev.isArmed ? 35 + Math.sin(Date.now() / 4000) * 3 : 0,
          altitudeMSL: prev.isArmed ? 85 + Math.sin(Date.now() / 4000) * 3 : 50,
          groundSpeed: prev.isArmed ? 8 + Math.random() * 2 : 0,
          airSpeed: prev.isArmed ? 10 + Math.random() * 2 : 0,
          climbRate: prev.isArmed ? Math.sin(Date.now() / 4000) * 1.5 : 0,
          satellites: 8 + Math.floor(Math.random() * 6),
          batteryPercent: Math.max(0, prev.batteryPercent - 0.008),
          batteryVoltage: 14.8 + (prev.batteryPercent / 100) * 2,
          latitude: newLat,
          longitude: newLon,
          rssi: 80 + Math.floor(Math.random() * 18),
          distanceToHome,
        }
      })
    }, 100)

    return () => clearInterval(interval)
  }, [isConnected])

  // Generate telemetry messages
  useEffect(() => {
    if (!isConnected) return

    const messageInterval = setInterval(() => {
      const messageTypes: TelemetryMessage["type"][] = ["HEARTBEAT", "ATTITUDE", "GPS_RAW", "SYS_STATUS", "BATTERY"]
      const droneIds = ["alpha", "bravo"]

      const newMessage: TelemetryMessage = {
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date(),
        droneId: droneIds[Math.floor(Math.random() * droneIds.length)],
        type: messageTypes[Math.floor(Math.random() * messageTypes.length)],
        severity: "info",
        message: `Telemetry update received`,
      }

      setMessages((prev) => [newMessage, ...prev].slice(0, 100))
    }, 500)

    return () => clearInterval(messageInterval)
  }, [isConnected])

  const handleConnect = useCallback(() => {
    setIsConnected(true)
    setMessages([
      {
        id: "connect",
        timestamp: new Date(),
        droneId: "system",
        type: "HEARTBEAT",
        severity: "info",
        message: "MAVLink connection established",
      },
    ])
  }, [])

  const handleDisconnect = useCallback(() => {
    setIsConnected(false)
    setDroneAlpha(createInitialDroneData("alpha", "Drone Alpha", 0))
    setDroneBravo(createInitialDroneData("bravo", "Drone Bravo", 0.001))
  }, [])

  const handleArmDisarm = useCallback((droneId: string) => {
    if (droneId === "alpha") {
      setDroneAlpha((prev) => ({ ...prev, isArmed: !prev.isArmed }))
    } else {
      setDroneBravo((prev) => ({ ...prev, isArmed: !prev.isArmed }))
    }
  }, [])

  const handleSetFlightMode = useCallback((droneId: string, mode: string) => {
    if (droneId === "alpha") {
      setDroneAlpha((prev) => ({ ...prev, flightMode: mode }))
    } else {
      setDroneBravo((prev) => ({ ...prev, flightMode: mode }))
    }
  }, [])

  const handleClearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const totalSatellites = droneAlpha.satellites + droneBravo.satellites

  return (
    <div className="min-h-screen h-screen bg-background flex flex-col overflow-hidden">
      <GCSHeader isConnected={isConnected} totalSatellites={totalSatellites} systemAlerts={0} />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Connection */}
        <aside className="w-64 border-r border-border p-4 flex flex-col gap-4 overflow-y-auto">
          <ConnectionPanel isConnected={isConnected} onConnect={handleConnect} onDisconnect={handleDisconnect} />
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-4 overflow-hidden flex flex-col">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="bg-card border border-border p-1 w-fit mb-4 shrink-0">
              <TabsTrigger
                value="combined"
                className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary text-muted-foreground px-4"
              >
                <Layers className="w-4 h-4 mr-2" />
                Combined View
              </TabsTrigger>
              <TabsTrigger
                value="alpha"
                className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary text-muted-foreground px-4"
              >
                <Plane className="w-4 h-4 mr-2" />
                Drone Alpha
              </TabsTrigger>
              <TabsTrigger
                value="bravo"
                className="data-[state=active]:bg-[#a78bfa]/20 data-[state=active]:text-[#a78bfa] text-muted-foreground px-4"
              >
                <Plane className="w-4 h-4 mr-2" />
                Drone Bravo
              </TabsTrigger>
            </TabsList>

            <TabsContent value="combined" className="flex-1 mt-0 overflow-hidden">
              <CombinedView
                droneAlpha={droneAlpha}
                droneBravo={droneBravo}
                messages={messages}
                isConnected={isConnected}
                onArmDisarm={handleArmDisarm}
                onClearMessages={handleClearMessages}
              />
            </TabsContent>

            <TabsContent value="alpha" className="flex-1 mt-0 overflow-hidden">
              <DroneTab
                drone={droneAlpha}
                messages={messages}
                isConnected={isConnected}
                onArmDisarm={() => handleArmDisarm("alpha")}
                onSetFlightMode={(mode) => handleSetFlightMode("alpha", mode)}
                onClearMessages={handleClearMessages}
              />
            </TabsContent>

            <TabsContent value="bravo" className="flex-1 mt-0 overflow-hidden">
              <DroneTab
                drone={droneBravo}
                messages={messages}
                isConnected={isConnected}
                onArmDisarm={() => handleArmDisarm("bravo")}
                onSetFlightMode={(mode) => handleSetFlightMode("bravo", mode)}
                onClearMessages={handleClearMessages}
              />
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
}

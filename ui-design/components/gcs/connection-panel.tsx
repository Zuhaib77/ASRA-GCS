"use client"

import { useState } from "react"
import { Plug, Unplug, RefreshCw, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface ConnectionPanelProps {
  isConnected: boolean
  onConnect: () => void
  onDisconnect: () => void
}

const BAUD_RATES = ["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]
const COM_PORTS = ["COM1", "COM2", "COM3", "COM4", "COM5", "/dev/ttyUSB0", "/dev/ttyACM0"]

export function ConnectionPanel({ isConnected, onConnect, onDisconnect }: ConnectionPanelProps) {
  const [baudRate, setBaudRate] = useState("57600")
  const [comPort, setComPort] = useState("COM3")
  const [isScanning, setIsScanning] = useState(false)

  const handleScan = () => {
    setIsScanning(true)
    setTimeout(() => setIsScanning(false), 2000)
  }

  return (
    <div className="gcs-panel p-4">
      <div className="gcs-panel-header -mx-4 -mt-4 mb-4 px-4 py-2 rounded-t-lg">
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-white">MAVLink Connection</h3>
        </div>
      </div>

      <div className="space-y-4">
        {/* COM Port Selection */}
        <div className="space-y-2">
          <label className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Serial Port</label>
          <div className="flex gap-2">
            <Select value={comPort} onValueChange={setComPort} disabled={isConnected}>
              <SelectTrigger className="flex-1 bg-secondary border border-border text-foreground h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-secondary border border-border">
                {COM_PORTS.map((port) => (
                  <SelectItem key={port} value={port} className="text-foreground focus:bg-primary/20">
                    {port}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="sm"
              onClick={handleScan}
              disabled={isConnected || isScanning}
              className="bg-secondary border border-border text-foreground hover:bg-muted h-9 px-3"
            >
              <RefreshCw className={`w-4 h-4 ${isScanning ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        {/* Baud Rate Selection */}
        <div className="space-y-2">
          <label className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Baud Rate</label>
          <Select value={baudRate} onValueChange={setBaudRate} disabled={isConnected}>
            <SelectTrigger className="w-full bg-secondary border border-border text-foreground h-9">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-secondary border border-border">
              {BAUD_RATES.map((rate) => (
                <SelectItem key={rate} value={rate} className="text-foreground focus:bg-primary/20">
                  {rate} bps
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Connection Status */}
        <div className="p-3 rounded bg-secondary/50 border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-muted-foreground">STATUS</span>
            <span className={`text-xs font-mono ${isConnected ? "text-[#00ff88]" : "text-destructive"}`}>
              {isConnected ? "CONNECTED" : "DISCONNECTED"}
            </span>
          </div>
          {isConnected && (
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-[10px] text-muted-foreground">Heartbeat</span>
                <span className="text-[10px] text-[#00ff88] font-mono">1 Hz</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[10px] text-muted-foreground">Packet Loss</span>
                <span className="text-[10px] text-foreground font-mono">0.2%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[10px] text-muted-foreground">Latency</span>
                <span className="text-[10px] text-foreground font-mono">12ms</span>
              </div>
            </div>
          )}
        </div>

        {/* Connect/Disconnect Button */}
        {isConnected ? (
          <Button
            onClick={onDisconnect}
            className="w-full bg-destructive/20 hover:bg-destructive/30 text-destructive border border-destructive/50"
          >
            <Unplug className="w-4 h-4 mr-2" />
            Disconnect
          </Button>
        ) : (
          <Button
            onClick={onConnect}
            className="w-full bg-[#00ff88]/20 hover:bg-[#00ff88]/30 text-[#00ff88] border border-[#00ff88]/50"
          >
            <Plug className="w-4 h-4 mr-2" />
            Connect
          </Button>
        )}
      </div>
    </div>
  )
}

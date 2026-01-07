"use client"

import { useState, useRef, useEffect } from "react"
import type { TelemetryMessage } from "./types"
import { MessageSquare, Filter, Pause, Play, Trash2, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface TelemetryPanelProps {
  messages: TelemetryMessage[]
  onClear: () => void
}

export function TelemetryPanel({ messages, onClear }: TelemetryPanelProps) {
  const [isPaused, setIsPaused] = useState(false)
  const [filterDrone, setFilterDrone] = useState<string>("all")
  const [filterType, setFilterType] = useState<string>("all")
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isPaused && containerRef.current) {
      containerRef.current.scrollTop = 0
    }
  }, [messages, isPaused])

  const filteredMessages = messages.filter((msg) => {
    if (filterDrone !== "all" && msg.droneId !== filterDrone) return false
    if (filterType !== "all" && msg.type !== filterType) return false
    return true
  })

  const displayMessages = isPaused ? filteredMessages : filteredMessages.slice(0, 50)

  const getMessageColor = (type: TelemetryMessage["type"], severity: TelemetryMessage["severity"]) => {
    if (severity === "error") return "text-destructive"
    if (severity === "warning") return "text-[#ffa500]"

    switch (type) {
      case "HEARTBEAT":
        return "text-[#00ff88]"
      case "ATTITUDE":
        return "text-primary"
      case "GPS_RAW":
        return "text-[#a78bfa]"
      case "BATTERY":
        return "text-[#fbbf24]"
      case "SYS_STATUS":
        return "text-[#38bdf8]"
      default:
        return "text-foreground"
    }
  }

  const formatTime = (date: Date) => {
    return date.toISOString().slice(11, 23)
  }

  const getMessageContent = (msg: TelemetryMessage) => {
    switch (msg.type) {
      case "HEARTBEAT":
        return `System heartbeat - ${msg.droneId.toUpperCase()}`
      case "ATTITUDE":
        return `Attitude update received`
      case "GPS_RAW":
        return `GPS position updated`
      case "BATTERY":
        return `Battery status update`
      case "SYS_STATUS":
        return `System status nominal`
      default:
        return msg.message
    }
  }

  return (
    <div className="gcs-panel p-0 flex flex-col h-full">
      {/* Header */}
      <div className="gcs-panel-header px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-white">Telemetry Messages</h3>
          <span className="text-xs text-muted-foreground font-mono">({messages.length})</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsPaused(!isPaused)}
            className="h-7 px-2 text-muted-foreground hover:text-white hover:bg-muted"
          >
            {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClear}
            className="h-7 px-2 text-muted-foreground hover:text-white hover:bg-muted"
          >
            <Trash2 className="w-3 h-3" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 px-2 text-muted-foreground hover:text-white hover:bg-muted">
            <Download className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="px-4 py-2 border-b border-border flex items-center gap-3">
        <Filter className="w-3 h-3 text-muted-foreground" />
        <Select value={filterDrone} onValueChange={setFilterDrone}>
          <SelectTrigger className="w-28 h-7 text-xs bg-secondary border border-border text-foreground">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-secondary border border-border">
            <SelectItem value="all" className="text-xs text-foreground">
              All Drones
            </SelectItem>
            <SelectItem value="alpha" className="text-xs text-foreground">
              Alpha
            </SelectItem>
            <SelectItem value="bravo" className="text-xs text-foreground">
              Bravo
            </SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-32 h-7 text-xs bg-secondary border border-border text-foreground">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-secondary border border-border">
            <SelectItem value="all" className="text-xs text-foreground">
              All Types
            </SelectItem>
            <SelectItem value="HEARTBEAT" className="text-xs text-foreground">
              Heartbeat
            </SelectItem>
            <SelectItem value="ATTITUDE" className="text-xs text-foreground">
              Attitude
            </SelectItem>
            <SelectItem value="GPS_RAW" className="text-xs text-foreground">
              GPS
            </SelectItem>
            <SelectItem value="BATTERY" className="text-xs text-foreground">
              Battery
            </SelectItem>
            <SelectItem value="SYS_STATUS" className="text-xs text-foreground">
              System
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Messages List */}
      <div ref={containerRef} className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin">
        {displayMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
            No messages to display
          </div>
        ) : (
          displayMessages.map((msg) => (
            <div
              key={msg.id}
              className="flex items-start gap-2 px-2 py-1.5 rounded bg-secondary/50 hover:bg-secondary transition-colors"
            >
              <span className="text-[10px] font-mono text-muted-foreground whitespace-nowrap">
                {formatTime(msg.timestamp)}
              </span>
              <span
                className={`text-[10px] font-mono font-bold uppercase min-w-[50px] ${
                  msg.droneId === "alpha"
                    ? "text-primary"
                    : msg.droneId === "bravo"
                      ? "text-[#a78bfa]"
                      : "text-muted-foreground"
                }`}
              >
                {msg.droneId === "system" ? "SYS" : msg.droneId.slice(0, 3).toUpperCase()}
              </span>
              <span
                className={`text-[10px] font-mono font-semibold min-w-[80px] ${getMessageColor(msg.type, msg.severity)}`}
              >
                [{msg.type}]
              </span>
              <span className="text-xs text-foreground truncate">{getMessageContent(msg)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

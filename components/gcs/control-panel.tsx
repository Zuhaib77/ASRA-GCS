"use client"

import { useState } from "react"
import type { DroneData, FlightMode } from "./types"
import {
  Power,
  AlertTriangle,
  Play,
  Pause,
  Home,
  ArrowDown,
  Shield,
  Settings2,
  Rocket,
  RotateCcw,
  Zap,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

interface ControlPanelProps {
  drone: DroneData
  isConnected: boolean
  onArmDisarm: () => void
  onSetFlightMode: (mode: string) => void
}

const FLIGHT_MODES: { value: FlightMode; label: string; description: string }[] = [
  { value: "STABILIZE", label: "Stabilize", description: "Manual throttle, auto-level" },
  { value: "ALT_HOLD", label: "Altitude Hold", description: "Maintain altitude automatically" },
  { value: "LOITER", label: "Loiter", description: "Hold position using GPS" },
  { value: "AUTO", label: "Auto", description: "Follow mission waypoints" },
  { value: "GUIDED", label: "Guided", description: "Fly to commanded position" },
  { value: "RTL", label: "Return to Launch", description: "Return to home position" },
  { value: "LAND", label: "Land", description: "Land at current position" },
  { value: "POSHOLD", label: "Position Hold", description: "Hold position with manual control" },
]

export function ControlPanel({ drone, isConnected, onArmDisarm, onSetFlightMode }: ControlPanelProps) {
  const [showForceArm, setShowForceArm] = useState(false)

  const handleModeChange = (mode: string) => {
    onSetFlightMode(mode)
  }

  return (
    <div className="gcs-panel p-4">
      <div className="gcs-panel-header -mx-4 -mt-4 mb-4 px-4 py-2 rounded-t-lg">
        <div className="flex items-center gap-2">
          <Settings2 className="w-4 h-4 text-[#00d4ff]" />
          <h3 className="text-sm font-semibold text-white">Flight Control</h3>
        </div>
      </div>

      <div className="space-y-4">
        {/* Arm/Disarm Section */}
        <div className="space-y-2">
          <label className="text-xs font-mono text-[#71717a] uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-3 h-3" />
            Arming
          </label>

          <div className="grid grid-cols-2 gap-2">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  disabled={!isConnected}
                  className={`h-12 font-mono font-bold ${
                    drone.isArmed
                      ? "bg-[#ff3333]/20 hover:bg-[#ff3333]/30 text-[#ff3333] border border-[#ff3333]/50"
                      : "bg-[#00ff88]/20 hover:bg-[#00ff88]/30 text-[#00ff88] border border-[#00ff88]/50"
                  }`}
                >
                  <Power className="w-4 h-4 mr-2" />
                  {drone.isArmed ? "DISARM" : "ARM"}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-card border border-border">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-white">
                    {drone.isArmed ? "Disarm Motors?" : "Arm Motors?"}
                  </AlertDialogTitle>
                  <AlertDialogDescription className="text-[#71717a]">
                    {drone.isArmed
                      ? "This will immediately stop all motors. Ensure the drone is safely landed."
                      : "This will enable the motors and allow flight. Ensure all pre-flight checks are complete."}
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-secondary border border-border text-white hover:bg-muted">
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={onArmDisarm}
                    className={
                      drone.isArmed
                        ? "bg-[#ff3333] hover:bg-[#cc2929] text-white"
                        : "bg-[#00ff88] hover:bg-[#00cc6d] text-black"
                    }
                  >
                    {drone.isArmed ? "Disarm" : "Arm"}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <AlertDialog open={showForceArm} onOpenChange={setShowForceArm}>
              <AlertDialogTrigger asChild>
                <Button
                  disabled={!isConnected || drone.isArmed}
                  variant="outline"
                  className="h-12 font-mono bg-[#ffa500]/10 hover:bg-[#ffa500]/20 text-[#ffa500] border-[#ffa500]/50"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  FORCE
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-card border border-[#ffa500]/50">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-[#ffa500] flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    Force Arm Warning
                  </AlertDialogTitle>
                  <AlertDialogDescription className="text-[#71717a]">
                    Force arming bypasses all safety checks. This is extremely dangerous and should only be used in
                    emergency situations. Are you absolutely sure?
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-secondary border border-border text-white hover:bg-muted">
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => {
                      onArmDisarm()
                      setShowForceArm(false)
                    }}
                    className="bg-[#ffa500] hover:bg-[#cc8400] text-black"
                  >
                    Force Arm
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        {/* Flight Mode Selection */}
        <div className="space-y-2">
          <label className="text-xs font-mono text-[#71717a] uppercase tracking-wider flex items-center gap-2">
            <Rocket className="w-3 h-3" />
            Flight Mode
          </label>
          <Select value={drone.flightMode} onValueChange={handleModeChange} disabled={!isConnected}>
            <SelectTrigger className="w-full h-10 bg-secondary border border-border text-foreground">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-secondary border border-border">
              {FLIGHT_MODES.map((mode) => (
                <SelectItem key={mode.value} value={mode.value} className="text-foreground focus:bg-primary/20">
                  <div className="flex flex-col">
                    <span className="font-mono">{mode.label}</span>
                    <span className="text-[10px] text-muted-foreground">{mode.description}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Quick Mode Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={!isConnected}
            onClick={() => handleModeChange("LOITER")}
            className="h-9 bg-secondary border border-border text-foreground hover:bg-primary/20 hover:text-primary hover:border-primary/50"
          >
            <RotateCcw className="w-3 h-3 mr-2" />
            Loiter
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={!isConnected}
            onClick={() => handleModeChange("RTL")}
            className="h-9 bg-secondary border border-border text-foreground hover:bg-[#ffa500]/20 hover:text-[#ffa500] hover:border-[#ffa500]/50"
          >
            <Home className="w-3 h-3 mr-2" />
            RTL
          </Button>
        </div>

        {/* Mission Controls */}
        <div className="space-y-2">
          <label className="text-xs font-mono text-[#71717a] uppercase tracking-wider">Mission</label>
          <div className="grid grid-cols-3 gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!isConnected || !drone.isArmed}
              className="h-9 bg-[#00ff88]/10 border border-[#00ff88]/30 text-[#00ff88] hover:bg-[#00ff88]/20"
            >
              <Play className="w-3 h-3 mr-1" />
              Start
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!isConnected || !drone.isArmed}
              className="h-9 bg-[#ffa500]/10 border border-[#ffa500]/30 text-[#ffa500] hover:bg-[#ffa500]/20"
            >
              <Pause className="w-3 h-3 mr-1" />
              Pause
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!isConnected}
              onClick={() => handleModeChange("LAND")}
              className="h-9 bg-primary/10 border border-primary/30 text-primary hover:bg-primary/20"
            >
              <ArrowDown className="w-3 h-3 mr-1" />
              Land
            </Button>
          </div>
        </div>

        {/* Emergency Stop */}
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              disabled={!isConnected || !drone.isArmed}
              className="w-full h-10 bg-destructive hover:bg-[#cc2929] text-white font-bold"
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              EMERGENCY STOP
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="bg-card border border-destructive/50">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-destructive flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Emergency Motor Stop
              </AlertDialogTitle>
              <AlertDialogDescription className="text-muted-foreground">
                This will immediately cut power to all motors. The drone will fall from the sky. Only use in absolute
                emergencies.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="bg-secondary border border-border text-white hover:bg-muted">
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction onClick={onArmDisarm} className="bg-destructive hover:bg-[#cc2929] text-white">
                KILL MOTORS
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  )
}

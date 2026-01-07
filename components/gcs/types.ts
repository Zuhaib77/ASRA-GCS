export interface DroneData {
  id: string
  name: string
  isArmed: boolean
  flightMode: string

  // Attitude
  pitch: number
  roll: number
  yaw: number
  heading: number

  // Position
  latitude: number
  longitude: number
  altitudeMSL: number
  altitudeAGL: number

  // Speed
  groundSpeed: number
  airSpeed: number
  climbRate: number

  // GPS
  gpsFixType: number
  satellites: number
  hdop: number
  vdop: number
  pdop: number

  // Battery
  batteryVoltage: number
  batteryPercent: number
  batteryCurrent: number

  // Signal
  rssi: number

  // Home
  homeLatitude: number
  homeLongitude: number
  distanceToHome: number
  bearingToHome: number
}

export interface TelemetryMessage {
  id: string
  timestamp: Date
  droneId: string
  type:
    | "HEARTBEAT"
    | "ATTITUDE"
    | "GPS_RAW"
    | "SYS_STATUS"
    | "BATTERY"
    | "RC_CHANNELS"
    | "MISSION"
    | "WARNING"
    | "ERROR"
  severity: "info" | "warning" | "error"
  message: string
  rawData?: string
}

export type FlightMode =
  | "STABILIZE"
  | "ALT_HOLD"
  | "LOITER"
  | "AUTO"
  | "GUIDED"
  | "RTL"
  | "LAND"
  | "ACRO"
  | "SPORT"
  | "POSHOLD"

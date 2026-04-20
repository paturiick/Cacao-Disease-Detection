#include <WiFi.h>
#include <WiFiUdp.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>
#include <esp_wifi.h>
#include <esp_pm.h>            // Power Management
#include "soc/soc.h"           // Power management registers
#include "soc/rtc_cntl_reg.h"  // Brown-out control

// Network Credentials
const char *ssid = "RMTT-GPS";
const char *password = "123456789";
const int udpPort = 8891;
IPAddress targetIP(192, 168, 4, 255); // Broadcast to everything on the AP

WiFiUDP udp;
TinyGPSPlus gps;
HardwareSerial GPSserial(1);

static const int GPS_RX_PIN = 4;   
static const int GPS_TX_PIN = 5; 

// --- RSSI TRACKING FUNCTION ---
// This retrieves the signal strength of the laptop connected to the ESP32
int getLaptopRSSI() {
    wifi_sta_list_t stationList;
    esp_wifi_ap_get_sta_list(&stationList);
    return (stationList.num > 0) ? stationList.sta[0].rssi : 0;
}

void setup() {
  // 1. POWER OPTIMIZATIONS
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Stops reboots during drone motor surges
  setCpuFrequencyMhz(80);                    // Drops to 80MHz to save aircraft battery

  Serial.begin(115200);
  GPSserial.begin(115200, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  // 2. WIFI SETUP (Direct Connection Mode)
  WiFi.softAP(ssid, password);
  esp_wifi_set_ps(WIFI_PS_MIN_MODEM);        // Radio "Modem Sleep" saves power

  udp.begin(udpPort);
  Serial.println("RMTT GPS + RSSI Pipeline Active.");
}

void loop() {
  while (GPSserial.available() > 0) {
    gps.encode(GPSserial.read());
  }

  static unsigned long lastUpdate = 0;
  
  if (millis() - lastUpdate >= 1000) { // 1-Second Heartbeat
    lastUpdate = millis();

    if (WiFi.softAPgetStationNum() > 0) {
      int signalStrength = getLaptopRSSI(); // Retrieve RSSI here
      String payload;
      
      if (gps.location.isValid()) {
        // payload format: loc:LAT,LNG,RSSI
        payload = "loc:" + String(gps.location.lat(), 6) + "," + 
                  String(gps.location.lng(), 6) + "," + 
                  String(signalStrength);
      } else {
        // payload format: sch:SATS,RSSI
        payload = "sch:" + String(gps.satellites.value()) + "," + 
                  String(signalStrength);
      }

      udp.beginPacket(targetIP, udpPort);
      udp.print(payload);
      udp.endPacket();
      
      Serial.println("Transmitting: " + payload);
    }
  }
  delay(1); // Yield to RTOS for power saving
}
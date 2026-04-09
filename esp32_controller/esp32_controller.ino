#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>
#include "soc/soc.h"             // Power management
#include "soc/rtc_cntl_reg.h"    // Power management

BLEServer *pServer = NULL;
BLECharacteristic *pTxCharacteristic;
bool deviceConnected = false;
bool oldDeviceConnected = false;

#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" 
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

TinyGPSPlus gps;
HardwareSerial GPSserial(1);

static const int GPS_RX_PIN = 4;   
static const int GPS_TX_PIN = 5;   

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) { deviceConnected = true; };
    void onDisconnect(BLEServer* pServer) { deviceConnected = false; }
};

void setup() {
  // --- THE CRITICAL WIRELESS FIX ---
  // Disables the detector that reboots the chip during power dips
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 
  
  Serial.begin(115200);
  GPSserial.begin(115200, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  BLEDevice::init("RMTT-GPS-BLE");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  pTxCharacteristic = pService->createCharacteristic(
                        CHARACTERISTIC_UUID_TX,
                        BLECharacteristic::PROPERTY_NOTIFY
                      );
  pTxCharacteristic->addDescriptor(new BLE2902());
  pService->start();
  
  // Advertise with parameters that help Windows stability
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pServer->getAdvertising()->start();

  Serial.println("Wireless Pipeline Active.");
}

void loop() {
  while (GPSserial.available() > 0) {
    gps.encode(GPSserial.read());
  }

  // Auto-reconnect logic
  if (!deviceConnected && oldDeviceConnected) {
    delay(500); 
    pServer->startAdvertising(); 
    oldDeviceConnected = deviceConnected;
  }
  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }

  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate >= 1000) {
    lastUpdate = millis();

    if (deviceConnected) {
      String payload;
      
      // Always send data if connected so Python stays "alive"
      if (gps.location.isValid()) {
        payload = "{\"lat\":" + String(gps.location.lat(), 6) + ",\"lng\":" + String(gps.location.lng(), 6) + "}";
      } else {
        // This will show up in your Python terminal every second
        payload = "{\"status\":\"searching\",\"sats\":" + String(gps.satellites.value()) + "}";
      }

      pTxCharacteristic->setValue(payload.c_str());
      pTxCharacteristic->notify(); // Push to laptop
    }
  }
}
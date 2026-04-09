import asyncio
import json
import requests
import threading
from bleak import BleakScanner, BleakClient

# Configuration matching the ESP32 setup
DEVICE_NAME = "RMTT-GPS-BLE"
UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

# Adjust to include your /api/ prefix
DJANGO_API_URL = "http://127.0.0.1:8000/api/telemetry/gps/" 
DJANGO_CONTROL_URL = "http://127.0.0.1:8000/api/telemetry/ble-control/"

def check_if_user_enabled():
    """Asks Django if the UI button is toggled ON."""
    try:
        response = requests.get(DJANGO_CONTROL_URL, timeout=1.0)
        return response.json().get("active", False)
    except Exception:
        return False # If Django is offline, stay safely asleep

def push_to_django(payload):
    """Sends the data to Docker and prints the response."""
    try:
        response = requests.post(DJANGO_API_URL, json=payload, timeout=2.0)
        print(f"API Response: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"API Connection Failed: {e}")

def notification_handler(sender, data):
    raw_data = data.decode('utf-8')
    print(f"RAW RECEIVED: {raw_data}")
    try:
        gps_json = json.loads(raw_data)
        threading.Thread(target=push_to_django, args=(gps_json,), daemon=True).start()
    except Exception as e:
        print(f"JSON Error: {e}")

async def run():
    while True:
        # 1. Wait until the user clicks "Start" on the web app
        if not check_if_user_enabled():
            print("Idling... waiting for user to click Start in Web UI.")
            await asyncio.sleep(2.0)
            continue

        print(f"UI Triggered! Scanning for {DEVICE_NAME}...")
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name == DEVICE_NAME
        )
        
        if not device:
            print("Drone not found. Retrying in 2 seconds...")
            await asyncio.sleep(2.0)
            continue

        print(f"Connected to {device.address}. Pipeline active.")
        
        try:
            async with BleakClient(device) as client:
                await client.start_notify(UART_TX_UUID, notification_handler)
                
                # 2. Keep running UNTIL the user clicks "Stop"
                while client.is_connected:
                    if not check_if_user_enabled():
                        print("User clicked Stop. Disconnecting...")
                        break 
                    await asyncio.sleep(1.0)
        except Exception as e:
            print(f"Connection dropped: {e}")
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")
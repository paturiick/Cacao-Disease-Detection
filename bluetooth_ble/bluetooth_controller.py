import asyncio
import json
import requests
import threading
from bleak import BleakScanner, BleakClient, BleakError

# Configuration
DEVICE_NAME = "RMTT-GPS-BLE"
UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
DJANGO_API_URL = "http://127.0.0.1:8000/api/telemetry/gps/" 
DJANGO_CONTROL_URL = "http://127.0.0.1:8000/api/telemetry/ble-control/"

def report_failure_to_django(reason):
    """Tells Django to turn off the 'Active' switch because of a hardware error."""
    try:
        requests.post(DJANGO_CONTROL_URL, json={"active": False, "error": reason}, timeout=1.0)
        print(f"REPORTED ERROR: {reason}")
    except Exception as e:
        print(f"Could not notify Django of error: {e}")

def check_if_user_enabled():
    try:
        response = requests.get(DJANGO_CONTROL_URL, timeout=1.0)
        data = response.json()
        active_status = data.get("active", False)
        
        print(f"DEBUG: Active Status from Server = {active_status}")
        
        return active_status
    except requests.exceptions.ConnectionError:
        print("DEBUG: Cannot reach Django server. Is Docker running?")
        return False
    except Exception as e:
        print(f"DEBUG: Unexpected error checking Django: {e}")
        return False

def push_to_django(payload):
    try:
        requests.post(DJANGO_API_URL, json=payload, timeout=2.0)
    except Exception:
        pass # Silently fail data pushes to keep the thread lean

def notification_handler(sender, data):
    try:
        # 1. Decode bytes to string
        raw_data = data.decode('utf-8')
        
        # 2. Parse string to JSON dictionary
        gps_json = json.loads(raw_data)
        
        # --- ADDED PRINT STATEMENT ---
        print(f"--- DATA RECEIVED ---")
        print(json.dumps(gps_json, indent=2)) 
        print(f"----------------------\n")
        
        # 3. Existing logic: Push to Django in a separate thread
        threading.Thread(target=push_to_django, args=(gps_json,), daemon=True).start()
        
    except Exception as e:
        print(f"Data Decode Error: {e}")
        # Print the raw data even if JSON parsing fails to help with debugging
        print(f"Raw data was: {data}")

async def run():
    print("Background Controller Started. Monitoring Django for orders...")

    # --- STARTUP HARDWARE CHECK ---
    # This checks if Bluetooth is ON as soon as the script starts
    try:
        await BleakScanner.discover(timeout=0.5)
        print("Hardware Check: Local Bluetooth is ON.")
    except (BleakError, Exception) as e:
        error_msg = "HOST_BLUETOOTH_OFF"
        print(f"CRITICAL ERROR: Your computer's Bluetooth is OFF or unavailable: {e}")
        report_failure_to_django(error_msg)
        # We don't exit here so the script can keep monitoring Django 
        # in case the user turns Bluetooth on later.
    
    while True:
        # 1. Check if the User toggled the "Active" switch in the UI
        if not check_if_user_enabled():
            await asyncio.sleep(2.0)
            continue

        print(f"UI Triggered! Checking local Bluetooth hardware...")
        
        try:
            # 2. Check hardware again before attempting connection
            devices = await BleakScanner.discover(timeout=1.0)
        except (BleakError, Exception) as e:
            error_msg = "HOST_BLUETOOTH_OFF"
            print(f"ERROR: Local Bluetooth is unavailable: {e}")
            report_failure_to_django(error_msg)
            await asyncio.sleep(5.0) 
            continue

        print(f"Scanning for {DEVICE_NAME}...")
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name == DEVICE_NAME
        )
        
        if not device:
            error_msg = "DEVICE_NOT_FOUND"
            print(f"ERROR: {DEVICE_NAME} not found. Ensure the ESP32 is powered on.")
            report_failure_to_django(error_msg)
            await asyncio.sleep(5.0)
            continue

        try:
            print(f"Connected to {device.address}. Pipeline active.")
            async with BleakClient(device) as client:
                await client.start_notify(UART_TX_UUID, notification_handler)
                
                while client.is_connected:
                    if not check_if_user_enabled():
                        print("User clicked Stop. Disconnecting...")
                        break 
                    await asyncio.sleep(1.0)
                    
        except Exception as e:
            print(f"Connection dropped unexpectedly: {e}")
            report_failure_to_django("CONNECTION_LOST")
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")
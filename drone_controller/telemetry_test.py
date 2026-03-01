# test_telemetry.py
import socket
import time

def main():
    # 1. Setup the listener on port 8890
    state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    state_sock.bind(("", 8890))
    state_sock.settimeout(2.0)
    
    # 2. Setup the command sender
    cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tello_address = ("192.168.10.1", 8889)
    
    print("\n--- Sending 'command' to wake up Tello SDK ---")
    # The drone WILL NOT send telemetry until it receives this command
    cmd_sock.sendto(b"command", tello_address)
    
    print("--- Listening on UDP Port 8890 for Telemetry ---\n")
    
    try:
        while True:
            try:
                data, _ = state_sock.recvfrom(2048)
                # Print the raw string (e.g., "pitch:0;roll:0;yaw:0;...")
                print(f"[DATA] {data.decode('utf-8').strip()}")
                time.sleep(0.5) # Throttle the print so it's readable
            except socket.timeout:
                print("[TIMEOUT] Waiting for data... (Is firewall blocking 8890?)")
    except KeyboardInterrupt:
        print("\nTest stopped.")
    finally:
        state_sock.close()
        cmd_sock.close()

if __name__ == "__main__":
    main()
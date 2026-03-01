import cv2
import socket
import time
import os

# 1. Windows UDP Packet Fix: Forces OpenCV to drop broken frames instantly
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "protocol_whitelist;file,rtp,udp|fflags;nobuffer|flags;low_delay"

TELLO_IP = "192.168.10.1"
CMD_PORT = 8889
LOCAL_CMD_PORT = 9001
VIDEO_PORT = 11111

def main():
    # Setup the command socket
    cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_sock.bind(("", LOCAL_CMD_PORT))
    cmd_sock.settimeout(3.0) # Strict 3-second timeout
    tello_address = (TELLO_IP, CMD_PORT)

    def send_command(cmd):
        print(f"> Sending: {cmd}")
        cmd_sock.sendto(cmd.encode('utf-8'), tello_address)
        try:
            response, _ = cmd_sock.recvfrom(1024)
            print(f"< Response: {response.decode('utf-8')}")
        except Exception as e:
            print(f"< No response from Tello (Timeout: {e})")

    # 2. Establish the Handshake
    print("\n--- Initiating Tello Connection ---")
    send_command("command")
    time.sleep(1) # Give the drone a second to process SDK mode
    
    send_command("streamon")
    time.sleep(1) # Give the hardware encoder a second to start broadcasting

    # 3. Open the Video Stream
    print(f"\n--- Starting OpenCV on UDP Port {VIDEO_PORT} ---")
    video_url = f"udp://@0.0.0.0:{VIDEO_PORT}"
    cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print("ERROR: OpenCV could not open the stream.")
        print("Check if your Windows Firewall is blocking port 11111 or if another Python script is running in the background.")
        return

    print("\n--- Stream Active! Press 'q' in the video window to quit ---")
    
    try:
        while True:
            success, frame = cap.read()
            if success:
                # Bypass the browser completely and draw directly to a Windows GUI
                cv2.imshow("Tello Live Feed (Standalone)", frame)
            else:
                # If we drop a frame, just wait a millisecond and try again
                time.sleep(0.01)

            # Wait for the 'q' key to be pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        # 4. Safe Shutdown Routine
        print("\n--- Shutting down gracefully ---")
        send_command("streamoff")
        cap.release()
        cv2.destroyAllWindows()
        cmd_sock.close()
        print("Cleaned up ports successfully.")

if __name__ == "__main__":
    main()
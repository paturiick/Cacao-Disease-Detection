import socket

# The default IP when connected directly to RMTT-XXXXXX
TELLO_IP = "192.168.10.1" 
CMD_PORT = 8889
STATE_PORT = 8890
VIDEO_PORT = 11111

LOCAL_CMD_PORT = 8889
LOCAL_VIDEO_PORT = 11111
LOCAL_STATE_PORT = 8890

CMD_TIMEOUT_S = 2
LOCAL_GPS_PORT = 8891

def get_ip_for_subnet(subnet_prefix: str, fallback: str) -> str:
    """Scans Windows network adapters and returns the IP matching the subnet."""
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        for ip in ips:
            if ip.startswith(subnet_prefix):
                return ip
    except Exception as e:
        print(f"Warning: Could not auto-detect IP for {subnet_prefix} - {e}")
    
    return fallback

# Your laptop's IP on the drone's network
LOCAL_WIFI_IP = get_ip_for_subnet("192.168.10.", "0.0.0.0")

print(f"[NETWORKING] Bound Tello Drone Client to: {TELLO_IP}")
print(f"[NETWORKING] Local Interface IP: {LOCAL_WIFI_IP}")
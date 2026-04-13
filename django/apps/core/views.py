import socket
import json
import asyncio
import platform
import subprocess
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async

from apps.drone_runtime.services import status as drone_status, connect, send
from drone_controller.config import TELLO_IP  # Import this to get the 192.168.10.1 IP safely

def is_drone_reachable(ip=TELLO_IP):
    """
    Validates connection by sending a lightweight UDP ping instead of ICMP.
    This bypasses Docker ICMP restrictions and ensures the Tello SDK is actually responsive.
    """
    try:
        # Open a temporary, fast-failing UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0) # Fail fast in 1 second
        
        # Send the Tello SDK initialization string
        sock.sendto(b"command", (ip, 8889))
        
        
        sock.recvfrom(1024)
        sock.close()
        return True
    except socket.timeout:
        # The 1 second expired with no response
        return False
    except Exception as e:
        print(f"[NETWORK] Drone reachability error: {e}")
        return False

@csrf_exempt
@require_http_methods(["GET"])
def health(request):
    return JsonResponse({"ok": True, "context": "xxxxxxxxx"})

@csrf_exempt
@require_http_methods(["GET"])
def drone_status_view(request):
    return JsonResponse(drone_status())

@csrf_exempt
@require_http_methods(["POST"])
def drone_connect_view(request):
    # --- 1. THE GATEKEEPER: Check Wi-Fi First ---
    if not is_drone_reachable():
        return JsonResponse({
            "ok": False, 
            "res": "Wi-Fi Not Reachable. Please check your PC's connection to the Tello network."
        })

    # --- 2. THE ACTUAL CONNECTION ---
    r = connect()
    return JsonResponse({
        "ok": r.get("ok", False), 
        "res": r.get("text", "Failed to connect")
    })

# --- SSE ENDPOINT (Unchanged) ---
@sync_to_async
def get_async_drone_status():
    return drone_status()

async def stream_drone_status(request):
    async def event_stream():
        last_status = None
        while True:
            current_status = await get_async_drone_status()
            is_connected = current_status.get("connected", False)
            if is_connected != last_status:
                yield f"data: {json.dumps(current_status)}\n\n"
                last_status = is_connected
            await asyncio.sleep(2.0)
            
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
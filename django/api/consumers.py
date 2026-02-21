import socket
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class DroneVideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # 1. Bind to the drone's video port (RoboMaster TT streams to 11111)
        self.udp_ip = '0.0.0.0'
        self.udp_port = 11111
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            self.sock.bind((self.udp_ip, self.udp_port))
            self.sock.setblocking(False)
        except OSError:
            # Prevent crashes if the port is already in use by another worker
            pass 
        
        # 2. Start the background task to relay video
        self.keep_running = True
        self.relay_task = asyncio.create_task(self.relay_udp())

    async def disconnect(self, close_code):
        self.keep_running = False
        if hasattr(self, 'relay_task'):
            self.relay_task.cancel()
        self.sock.close()

    async def relay_udp(self):
        loop = asyncio.get_running_loop()
        while self.keep_running:
            try:
                # Read raw H.264 packets (2048 bytes at a time)
                data, addr = await loop.sock_recv(self.sock, 2048)
                
                # Send raw bytes straight to the Vue/Nuxt frontend
                await self.send(bytes_data=data)
            except Exception:
                # Ignore minor socket timeouts/errors to keep the stream alive
                pass
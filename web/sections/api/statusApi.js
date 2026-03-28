import { ref, onMounted, onUnmounted } from 'vue';

export function useDrone() {
  const isConnected = ref(false);
  const isConnecting = ref(false);
  let statusStream = null;
  const BASE = import.meta.env.VITE_API_BASE_URL;

  const startStatusStream = () => {
    if (statusStream) return;
    if (import.meta.server) return; 

    // Connect to the new Django SSE endpoint
    statusStream = new EventSource(`${BASE}/api/core/drone/status/stream/`);

    statusStream.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        isConnected.value = !!data.connected;
      } catch (error) {
        console.error("Failed to parse status stream", error);
      }
    };

    statusStream.onerror = () => {
      isConnected.value = false;
      console.warn("[Drone Status] SSE interrupted. Auto-reconnecting...");
    };
  };

  const stopStatusStream = () => {
    if (statusStream) {
      statusStream.close();
      statusStream = null;
    }
  };

  const connectDrone = async () => {
    if (import.meta.server || isConnecting.value) return;
    
    if (isConnected.value) {
      console.log("Drone is already linked.");
      return;
    }

    isConnecting.value = true;
    try {
      const res = await fetch(`${BASE}/api/core/drone/connect/`, { 
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      const data = await res.json();
      if (data.ok) {
        // Fixed: views.py sends "res", not "text"
        console.log("Handshake successful: " + data.res); 
        isConnected.value = true;
      } else {
        console.warn("Handshake failed: " + data.res);
        isConnected.value = false;
      }
    } catch (error) {
      console.error("Network Error: Is the Django server running?");
      isConnected.value = false;
    } finally {
      isConnecting.value = false;
    }
  };

  onMounted(() => {
    startStatusStream(); 
  });

  onUnmounted(() => {
    stopStatusStream();
  });

  return { isConnected, isConnecting, connectDrone };
}
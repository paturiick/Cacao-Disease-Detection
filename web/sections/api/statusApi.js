import { ref, onMounted, onUnmounted } from 'vue';

export function useDrone() {
  const isConnected = ref(false);
  const isConnecting = ref(false);
  let statusInterval = null;


  const checkStatus = async () => {
    if (import.meta.server) return; 
    try {
      const res = await fetch('http://127.0.0.1:8000/api/core/drone/status/');
      if (!res.ok) throw new Error('Status check failed');
      
      const data = await res.json();
      isConnected.value = !!data.connected;
    } catch (error) {
      isConnected.value = false; 
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
   
      const res = await fetch('http://127.0.0.1:8000/api/core/drone/connect/', { 
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      const data = await res.json();
      if (data.ok) {
        console.log("Handshake successful: " + data.text);
        isConnected.value = true;
      } else {
        console.warn("Server reached, but Tello is unreachable: " + data.text);
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
    checkStatus(); 
    statusInterval = setInterval(checkStatus, 5000); 
  });

  onUnmounted(() => {
    if (statusInterval) clearInterval(statusInterval);
  });

  return { isConnected, isConnecting, connectDrone };
}
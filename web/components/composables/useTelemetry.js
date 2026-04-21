import { reactive, nextTick } from 'vue';
import { telemetryApi } from '~/sections/api/telemetryApi';

const state = reactive({
  recorded_at: null,
  connected: false,
  battery: 0,
  altitude_m: 0,
  pitch: 0,
  roll: 0,
  yaw: 0,
  tof_cm: 0,
  temp_c: 0,
  templ_c: 0,
  vgx: 0,
  vgy: 0,
  vgz: 0,
  agx: 0,
  agy: 0,
  agz: 0,
  baro: 0,
  flight_time: 0,
  
  // --- NATIVE GPS STATE ---
  gps_lat: 8.4803, 
  gps_lon: 124.6498,
  gps_sats: 0,             
  gps_status: 'searching', 
  
  // --- INTERFERENCE TRACKING ---
  drone_snr: 0,       // New: 5GHz Signal-to-Noise Ratio 
  esp32_rssi: 0,      // New: 2.4GHz Signal Strength Indicator
  
  heading: 0, 
  speed: 0,   
});

let eventSource = null; 
let activeSubscribers = 0; 

export function useTelemetry() {
  
  const updateState = (data) => {
    if (!data) return;

    state.recorded_at = data.recorded_at ?? state.recorded_at;
    state.connected = data.connected ?? state.connected;
    state.battery = data.battery ?? state.battery;
    state.altitude_m = data.altitude_m ?? state.altitude_m;
    state.pitch = data.pitch ?? state.pitch;
    state.roll = data.roll ?? state.roll;
    state.yaw = data.yaw ?? state.yaw;
    state.tof_cm = data.tof_cm ?? state.tof_cm;
    state.temp_c = data.temp_c ?? state.temp_c;
    state.templ_c = data.templ_c ?? state.templ_c;
    state.vgx = data.vgx ?? state.vgx;
    state.vgy = data.vgy ?? state.vgy;
    state.vgz = data.vgz ?? state.vgz;
    state.agx = data.agx ?? state.agx;
    state.agy = data.agy ?? state.agy;
    state.agz = data.agz ?? state.agz;
    state.baro = data.baro ?? state.baro;
    state.flight_time = data.flight_time ?? state.flight_time;

    // --- UPDATE GPS & SIGNAL DATA ---
    state.gps_sats = data.gps_sats ?? state.gps_sats;
    state.gps_status = data.gps_status ?? state.gps_status;
    state.drone_snr = data.drone_snr ?? state.drone_snr;
    state.esp32_rssi = data.esp32_rssi ?? state.esp32_rssi;

    if (data.gps_lat && data.gps_lat !== 0) {
      state.gps_lat = data.gps_lat;
    }
    if (data.gps_lon && data.gps_lon !== 0) {
      state.gps_lon = data.gps_lon;
    }

    state.heading = state.yaw >= 0 ? state.yaw : 360 + state.yaw;
    state.speed = Math.round(Math.sqrt((state.vgx ** 2) + (state.vgy ** 2)));
  };

  const startStreaming = () => {
    activeSubscribers++;
    
    if (activeSubscribers === 1 && !eventSource) {
      console.log("Opening Native Signal & Telemetry SSE Stream...");
      
      eventSource = telemetryApi.connectStream();

      eventSource.onmessage = async (event) => {
        const receiveTime = performance.now(); 

        try {
          const data = JSON.parse(event.data); 
          updateState(data); 
          
          await nextTick(); 
          
          const renderTime = performance.now();
          console.log(`⏱️ UT-09 UI Latency: ${(renderTime - receiveTime).toFixed(2)} ms`);

        } catch (err) {
          console.error("SSE Parse Error", err);
        }
      };;

      eventSource.onerror = (err) => {
        state.connected = false;
        console.warn("Telemetry Stream Interrupted. Auto-reconnecting...");
      };
    }
  };

  const stopStreaming = () => {
    activeSubscribers--;
    if (activeSubscribers <= 0) {
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
      activeSubscribers = 0; 
      console.log("Closed Telemetry SSE Stream.");
    }
  };

  return {
    telemetryState: state,
    startPolling: startStreaming, 
    stopPolling: stopStreaming
  };
}
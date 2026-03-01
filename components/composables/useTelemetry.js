import { reactive } from 'vue';
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
  
  gps_lat: 8.4803, 
  gps_lon: 124.6498,

  heading: 0, 
  speed: 0,   
});

let pollInterval = null;
let activeSubscribers = 0; 

export function useTelemetry() {
  
  const fetchLatest = async () => {
    try {
      const data = await telemetryApi.getLatest();
      
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

      if (data.gps_lat !== 0 && data.gps_lat !== undefined) {
        state.gps_lat = data.gps_lat;
      }
      if (data.gps_lon !== 0 && data.gps_lon !== undefined) {
        state.gps_lon = data.gps_lon;
      }

      state.heading = state.yaw >= 0 ? state.yaw : 360 + state.yaw;
      
      state.speed = Math.round(Math.sqrt((state.vgx ** 2) + (state.vgy ** 2)));

    } catch (error) {
      state.connected = false;
      console.error("Global Telemetry Poll Failed", error);
    }
  };

  const startPolling = () => {
    activeSubscribers++;
    if (activeSubscribers === 1 && !pollInterval) {
      fetchLatest(); 
      pollInterval = setInterval(fetchLatest, 1000); 
      console.log("Started Global Telemetry Polling");
    }
  };

  const stopPolling = () => {
    activeSubscribers--;
    if (activeSubscribers <= 0) {
      clearInterval(pollInterval);
      pollInterval = null;
      activeSubscribers = 0; 
      console.log("Stopped Global Telemetry Polling");
    }
  };

  return {
    telemetryState: state,
    startPolling,
    stopPolling,
    fetchLatest
  };
}
<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue';

// --- Global Telemetry Store ---
import { useTelemetry } from '~/components/composables/useTelemetry';
import { mappingApi } from '~/sections/api/mappingApi';
import { activeSessionId } from '~/components/composables/droneStore';

// --- Components ---
import DashboardNavBar from '~/components/organisms/NavBar.vue';
import DataCard from '~/components/molecules/map_geotagging_molecules/DataCard.vue';
import TreeDataCard from '~/components/molecules/map_geotagging_molecules/TreeDataCard.vue';
import LiveMapCard from '~/components/molecules/map_geotagging_molecules/LiveMapCard.vue';

// 1. Initialize Global Telemetry
const { telemetryState, startPolling, stopPolling } = useTelemetry();

// --- Local State ---
const detectedTreesArray = ref([]);

const healthyCount = computed(() => detectedTreesArray.value.filter(tree => tree.status === 'healthy').length);
const diseasedCount = computed(() => detectedTreesArray.value.filter(tree => tree.status === 'diseased').length);

let mappingSource = null;

// Ensure Vue knows where your Django server is to fetch the images
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const gpsData = computed(() => {
  // 1. Calculate the color first
  let batColor = 'bg-red-500'; 
  if (telemetryState.battery >= 50) {
    batColor = 'bg-green-500'; 
  } else if (telemetryState.battery >= 20) {
    batColor = 'bg-yellow-500'; 
  }

  // 2. Return it inside the object
  return {
    lat: telemetryState.gps_lat, 
    lng: telemetryState.gps_lon,
    heading: telemetryState.heading,
    accuracy: 2.1, 

    alt: telemetryState.altitude_m,
    speed: telemetryState.speed,
    
    battery: telemetryState.battery,
    batteryColor: batColor, 
    
    pitch: telemetryState.pitch,
    roll: telemetryState.roll,
    yaw: telemetryState.yaw,
    tof: telemetryState.tof_cm,
    temp: telemetryState.temp_c,
    flight_time: telemetryState.flight_time,
    
    healthy: healthyCount.value,
    diseased: diseasedCount.value 
  };
});

const signalStatus = computed(() => telemetryState.connected ? 'Online' : 'Offline');

// --- Lifecycle Hooks ---
onMounted(() => {
  startPolling();

  // Grab the active session from your store, or default to latest
  const currentSessionId = activeSessionId.value || "latest"; 
  
  mappingSource = mappingApi.connectCaptureStream(currentSessionId);
  
  if (mappingSource) {
    mappingSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.pods) {
        detectedTreesArray.value = data.pods.map(p => {
          const captureDate = new Date(p.first_seen);
          return {
            id: p.track_id,
            // Prepend BASE_URL so the image loads correctly from Django
            imageUrl: p.image ? `${BASE_URL}/media/${p.image}` : null,
            status: p.status === 'unhealthy' ? 'diseased' : 'healthy',
            lat: p.latitude ? p.latitude.toFixed(6) : 'N/A',
            lng: p.longitude ? p.longitude.toFixed(6) : 'N/A',
            recordedDate: captureDate.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }),
            recordedTime: captureDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          };
        });
      }
    };
  }
});

onUnmounted(() => {
  stopPolling();
  if (mappingSource) mappingSource.close();
});
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-cover bg-center relative font-inter"
       style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');">
    
    <div class="absolute inset-0 bg-black/60 z-0"></div>
    
    <div class="z-20 relative">
      <DashboardNavBar active-page="map-geotagging" :droneStatus="signalStatus" :battery="telemetryState.battery"/>
    </div>

    <div class="flex-1 z-10 p-6 overflow-hidden relative">
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1800px] mx-auto">
        
        <div class="w-full xl:w-1/5 min-w-[300px] flex flex-col h-full overflow-y-auto">
          <DataCard :data="gpsData" />
        </div>
        
        <div class="w-full xl:w-2/5 h-full">
          <TreeDataCard :detected-trees="detectedTreesArray" />
        </div>

        <div class="w-full xl:flex-1 h-full">
          <LiveMapCard 
            :gps-data="gpsData" 
            :trees="detectedTreesArray" 
          />
        </div>

      </div>
    </div>
  </div>
</template>
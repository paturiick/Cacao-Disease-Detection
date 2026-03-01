<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue';

// --- Global Telemetry Store ---
import { useTelemetry } from '~/components/composables/useTelemetry';

// --- Components ---
import DashboardNavBar from '~/components/organisms/NavBar.vue';
import GPSDataCard from '~/components/molecules/map_geotagging_molecules/GPSDataCard.vue';
import TreeDataCard from '~/components/molecules/map_geotagging_molecules/TreeDataCard.vue';
import LiveMapCard from '~/components/molecules/map_geotagging_molecules/LiveMapCard.vue';

// 1. Initialize Global Telemetry
const { telemetryState, startPolling, stopPolling } = useTelemetry();

// --- Local State ---
const detectedTreesArray = ref([
  // Image detected trees will populate here
]);

const healthyCount = computed(() => detectedTreesArray.value.filter(tree => tree.status === 'healthy').length);
const diseasedCount = computed(() => detectedTreesArray.value.filter(tree => tree.status === 'diseased').length);

// 2. Computed GPS Data Wrapper
// This automatically pushes the latest global telemetry down to your UI cards
// 2. Computed GPS Data Wrapper
const gpsData = computed(() => {
  
  // 1. Calculate the color first
  let batColor = 'bg-red-500'; 
  if (telemetryState.battery >= 50) {
    batColor = 'bg-green-500'; 
  } else if (telemetryState.battery >= 20) {
    batColor = 'bg-yellow-500'; // <-- 28% will trigger this!
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
    batteryColor: batColor, // <--- THIS IS THE MAGIC LINK!
    
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
  // Start the global hardware polling when the user opens the map
  startPolling();
});

onUnmounted(() => {
  // Cleanly stop the polling when leaving the page
  stopPolling();
});
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-cover bg-center relative font-inter"
       style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');">
    
    <div class="absolute inset-0 bg-black/60 z-0"></div>
    
    <div class="z-20 relative">
      <DashboardNavBar active-page="map-geotagging" :droneStatus="signalStatus" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-hidden relative">
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1800px] mx-auto">
        
        <div class="w-full xl:w-1/5 min-w-[300px] flex flex-col h-full overflow-y-auto">
          <GPSDataCard :data="gpsData" />
        </div>
        
        <div class="w-full xl:w-2/5 h-full">
          <TreeDataCard :detected-trees="detectedTreesArray" />
        </div>

        <div class="w-full xl:flex-1 h-full">
          <LiveMapCard :gps-data="gpsData" />
        </div>

      </div>
    </div>
  </div>
</template>
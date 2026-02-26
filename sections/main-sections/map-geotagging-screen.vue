<script setup>
import { reactive, onMounted, onUnmounted } from 'vue';

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import GPSDataCard from '~/components/molecules/map_geotagging_molecules/GPSDataCard.vue';
import TreeDataCard from '~/components/molecules/map_geotagging_molecules/TreeDataCard.vue';
import LiveMapCard from '~/components/molecules/map_geotagging_molecules/LiveMapCard.vue';

// Initialize directly with active coordinates to bypass any waiting states
const gpsData = reactive({
  lat: 6.9444, 
  lng: 124.8422,
  alt: 125.4,
  accuracy: 2.1,
  speed: 14.8,
  heading: 45,
  treeCount: 0 
});

let simulationTimer = null;

// Start telemetry simulation immediately
onMounted(() => {
  simulationTimer = setInterval(() => {
    // Wiggle coordinates slightly
    gpsData.lat += (Math.random() - 0.5) * 0.0001;
    gpsData.lng += (Math.random() - 0.5) * 0.0001;
    gpsData.alt += (Math.random() - 0.5) * 0.5;
    gpsData.speed = 14 + (Math.random() - 0.5);
    
    // Rotate heading continuously
    gpsData.heading = (gpsData.heading + 2) % 360;
  }, 1000); 
});

onUnmounted(() => {
  if (simulationTimer) clearInterval(simulationTimer);
});
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden bg-cover bg-center relative font-inter"
       style="background-image: url('https://images.unsplash.com/photo-1542319084-2a6c38210350?q=80&w=2574&auto=format&fit=crop');">
    
    <div class="absolute inset-0 bg-black/60 z-0"></div>

    <div class="z-20 relative">
      <DashboardNavBar active-page="map-geotagging"/>
    </div>

    <div class="flex-1 z-10 p-6 overflow-hidden relative">
      
      <div class="flex flex-col xl:flex-row gap-6 h-full max-w-[1800px] mx-auto">
        
        <div class="w-full xl:w-1/5 min-w-[300px] flex flex-col h-full overflow-y-auto">
          <GPSDataCard :data="gpsData" />
        </div>

        <div class="w-full xl:flex-1 h-full">
          <LiveMapCard :gps-data="gpsData" />
        </div>

        <div class="w-full xl:w-2/5 h-full">
          <TreeDataCard 
            :treeCount="gpsData.treeCount" 
          />
        </div>

      </div>

    </div>

  </div>
</template>
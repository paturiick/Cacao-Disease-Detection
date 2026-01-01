<script setup>
import { reactive, onMounted, onUnmounted } from 'vue';

import DashboardNavBar from '~/components/organisms/NavBar.vue';
import GPSDataCard from '~/components/molecules/map_geotagging_molecules/GPSDataCard.vue';
import LiveMapCard from '~/components/molecules/map_geotagging_molecules/LiveMapCard.vue';

// Reactive State for "Live" Data
const gpsData = reactive({
  lat: 37.774900,
  lng: -122.419400,
  alt: 125.4,
  accuracy: 2.1,
  speed: 14.8,
  heading: 45 // Initial heading (North-East)
});

let simulationTimer = null;

// Simulate Live GPS Movement
onMounted(() => {
  simulationTimer = setInterval(() => {
    // Wiggle coordinates slightly
    gpsData.lat += (Math.random() - 0.5) * 0.0001;
    gpsData.lng += (Math.random() - 0.5) * 0.0001;
    gpsData.alt += (Math.random() - 0.5) * 0.5;
    gpsData.speed = 14 + (Math.random() - 0.5);
    
    // Rotate heading continuously
    gpsData.heading = (gpsData.heading + 2) % 360;
  }, 1000); // Updates every second
});

onUnmounted(() => {
  if (simulationTimer) clearInterval(simulationTimer);
});
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter">
    
    <div class="z-10">
      <DashboardNavBar active-page="map-geotagging" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto">
      <div class="flex flex-col md:flex-row gap-6 h-full max-w-[1600px] mx-auto">
        
        <div class="w-full md:w-1/4 min-w-[250px]">
          <GPSDataCard :data="gpsData" />
        </div>

        <div class="w-full md:w-3/4 flex flex-col h-full">
          <LiveMapCard :gps-data="gpsData" />
        </div>

      </div>
    </div>

  </div>
</template>
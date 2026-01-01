<script setup>
import DashboardNavBar from '~/components/organisms/NavBar.vue';
import GPSDataCard from '~/components/molecules/map_geotagging_molecules/GPSDataCard.vue';
import LiveMapCard from '~/components/molecules/map_geotagging_molecules/LiveMapCard.vue';
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden font-inter">
    
    <div class="z-10">
      <DashboardNavBar active-page="map-geotagging" />
    </div>

    <div class="flex-1 z-10 p-6 overflow-y-auto">
      <div class="flex flex-col md:flex-row gap-6 h-full max-w-[1600px] mx-auto">
        
        <div class="w-full md:w-1/4 min-w-[250px]">
          <GPSDataCard />
        </div>

        <div class="w-full md:w-3/4 flex flex-col h-full">
          <LiveMapCard />
        </div>

      </div>
    </div>

  </div>
</template>
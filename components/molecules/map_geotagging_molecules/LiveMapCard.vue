<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import MapCanvas from '~/components/atoms/MapCanvas.vue'; 

defineProps({
  gpsData: {
    type: Object,
    required: true
  }
});

// Reactive state for the map zoom level
const currentZoom = ref(18);

// Zoom handler functions (These update the variable passed to MapCanvas)
const zoomIn = () => {
  if (currentZoom.value < 22) currentZoom.value += 1;
};

const zoomOut = () => {
  if (currentZoom.value > 1) currentZoom.value -= 1;
};
</script>

<template>
  <BaseCard class="h-full flex flex-col">
    <div class="flex items-center gap-2 mb-4 border-b border-gray-100 pb-2 shrink-0">
      <div class="w-5 h-5 text-gray-600">
         <IconMap />
      </div>
      <h3 class="font-bold text-gray-700 font-poppins text-sm">Live Map View</h3>
    </div>

    <div class="flex-1 min-h-[400px] relative rounded-lg overflow-hidden border border-gray-200 bg-slate-50">
      
      <div class="absolute top-4 left-4 z-[1000] flex flex-col shadow-lg rounded-md overflow-hidden bg-white border border-gray-200">
        <button 
          @click="zoomIn" 
          class="w-8 h-8 flex items-center justify-center font-black text-gray-700 hover:bg-gray-100 border-b border-gray-200 text-lg transition-colors" 
          title="Zoom In"
        >
          +
        </button>
        <button 
          @click="zoomOut" 
          class="w-8 h-8 flex items-center justify-center font-black text-gray-700 hover:bg-gray-100 text-lg transition-colors" 
          title="Zoom Out"
        >
          −
        </button>
      </div>

      <MapCanvas 
        :heading="gpsData.heading" 
        :lat="gpsData.lat"
        :lng="gpsData.lng"
        :zoom="currentZoom"
        class="w-full h-full z-0"
      />
      
    </div>
  </BaseCard>
</template>
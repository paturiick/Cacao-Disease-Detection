<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import MapCanvas from '~/components/atoms/MapCanvas.vue'; 

defineProps({
  gpsData: {
    type: Object,
    required: true
  },
  // Added this so you can pass dynamic trees from the parent later!
  trees: {
    type: Array,
    default: () => []
  }
});

const currentZoom = ref(19);

const zoomIn = () => {
  if (currentZoom.value < 22) currentZoom.value += 1;
};

const zoomOut = () => {
  if (currentZoom.value > 1) currentZoom.value -= 1;
};
</script>

<template>
  <BaseCard class="h-full flex flex-col">
    
    <div class="flex items-center gap-2 mb-3 border-b border-gray-100 pb-2 shrink-0">
      <div class="w-5 h-5 text-gray-600">
         <IconMap />
      </div>
      <h3 class="font-bold text-gray-700 font-poppins text-sm">Live Map View</h3>
    </div>

    <div class="flex items-center justify-between mb-3 bg-slate-50 p-2.5 px-4 rounded-lg border border-slate-100 shrink-0 shadow-sm">
      <span class="font-mono text-sm font-black text-slate-800">
        Drone Position: {{ gpsData.lat?.toFixed(6) ?? '0.000000' }}, {{ gpsData.lng?.toFixed(6) ?? '0.000000' }}
      </span>
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
        :trees="trees" 
        class="w-full h-full z-0"
      />
      
    </div>
  </BaseCard>
</template>
<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import MapCanvas from '~/components/atoms/MapCanvas.vue'; 

const mapRef = ref(null);

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
  if (currentZoom.value < 100) currentZoom.value += 1;
};

const zoomOut = () => {
  if (currentZoom.value > 1) currentZoom.value -= 1;
};

const recenterMap = () => {
  mapRef.value?.recenter(); 
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
  
  <div class="flex items-center gap-2">
    <span class="text-[9px] font-bold uppercase text-slate-400">Sats: {{ gpsData.sats }}</span>
    <div 
      class="px-2 py-0.5 rounded text-[10px] font-black uppercase border"
      :class="gpsData.status === 'locked' ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-amber-50 text-amber-600 border-amber-200 animate-pulse'"
    >
      {{ gpsData.status }}
    </div>
  </div>
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
          class="w-8 h-8 flex items-center justify-center font-black text-gray-700 hover:bg-gray-100 border-b border-gray-200 text-lg transition-colors" 
          title="Zoom Out"
        >
          −
        </button>

        <button 
          @click="recenterMap" 
          class="w-8 h-8 flex items-center justify-center text-blue-500 hover:bg-gray-100 transition-colors" 
          title="Recenter Drone"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M3 12h3m12 0h3M12 3v3m0 12v3" />
          </svg>
        </button>
      </div>

      <MapCanvas 
        ref="mapRef"
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
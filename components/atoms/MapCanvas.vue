<script setup>
import { computed } from 'vue';

const bgImage = "url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg')"; 

const props = defineProps({
  heading: { type: Number, default: 0 },
  lat: { type: Number, default: 0 },
  lng: { type: Number, default: 0 },
  zoom: { type: Number, default: 18 } // Accepts the zoom value from LiveMapCard
});

// 1. Dynamic Background Scaling
// Divides the zoom prop by a baseline (e.g., 10) to create a CSS scale multiplier.
const mapBgStyle = computed(() => ({
  backgroundImage: bgImage,
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  transform: `scale(${Math.max(1, props.zoom / 10)})`, 
  transition: 'transform 0.3s ease-out'
}));

// 2. Drone Rotation Logic
// Rotates the SVG based on the drone's actual compass heading.
const markerStyle = computed(() => ({
  transform: `translate(-50%, -50%) rotate(${props.heading}deg)`,
  transformOrigin: 'center center'
}));
</script>

<template>
  <div class="relative w-full h-full bg-slate-200 overflow-hidden rounded-lg flex items-center justify-center">
    
    <div 
      class="absolute inset-0 opacity-50 origin-center"
      :style="mapBgStyle"
    ></div>

    <div class="absolute inset-0 border border-gray-300/30 grid grid-cols-4 grid-rows-4 pointer-events-none z-0"></div>

    <div 
      class="absolute top-1/2 left-1/2 w-10 h-10 text-blue-600 transition-transform duration-300 ease-out z-10"
      :style="markerStyle"
    >
      <svg fill="currentColor" viewBox="0 0 24 24" class="drop-shadow-md">
        <path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z" />
      </svg>
    </div>

    <div class="absolute bottom-4 left-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded shadow-sm text-xs font-mono text-gray-700 z-20">
      Loc: {{ lat.toFixed(6) }}, {{ lng.toFixed(6) }}
    </div>
  </div>
</template>
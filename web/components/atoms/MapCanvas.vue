<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import 'leaflet/dist/leaflet.css';

const props = defineProps({
  lat: { type: Number, default: 0 },
  lng: { type: Number, default: 0 },
  heading: { type: Number, default: 0 },
  zoom: { type: Number, default: 18 },
  trees: { type: Array, default: () => [] }
});

const mapContainer = ref(null);
let map = null;
let droneMarker = null;
let L = null;

const recenter = () => {
  if (map && props.lat !== 0 && props.lng !== 0) {
    map.flyTo([props.lat, props.lng], props.zoom, {
      duration: 1.5, // seconds
      easeLinearity: 0.25
    });
  }
};

defineExpose({
  recenter
});

// --- Custom Drone Icon Generator ---
const getDroneIcon = (heading) => {
  return L.divIcon({
    className: 'bg-transparent', // Removes default leaflet white square
    iconSize: [56, 56],
    iconAnchor: [28, 28], // Centers the 56x56 box perfectly over the coordinates
    html: `
      <div class="relative flex items-center justify-center w-[56px] h-[56px]">
        <div class="absolute w-full h-full bg-red-500/40 rounded-full animate-ping"></div>
        
        <div style="transform: rotate(${heading}deg); transition: transform 0.3s ease-out;" class="relative z-10 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0px 3px 4px rgba(0,0,0,0.6)); color: #ef4444;">
            
            <rect x="9" y="9" width="6" height="6" rx="1" fill="#1f2937" stroke="#1f2937" />
            
            <polygon points="12,3 9,7 15,7" fill="#3b82f6" stroke="none" />
            
            <path d="M9 9L4 4" />
            <path d="M15 9L20 4" />
            <path d="M9 15L4 20" />
            <path d="M15 15L20 20" />
            
            <circle cx="4" cy="4" r="2.5" stroke="#9ca3af" fill="white" fill-opacity="0.2"/>
            <circle cx="20" cy="4" r="2.5" stroke="#9ca3af" fill="white" fill-opacity="0.2"/>
            <circle cx="4" cy="20" r="2.5" stroke="#9ca3af" fill="white" fill-opacity="0.2"/>
            <circle cx="20" cy="20" r="2.5" stroke="#9ca3af" fill="white" fill-opacity="0.2"/>
          </svg>
        </div>
      </div>
    `
  });
};

onMounted(async () => {
  L = (await import('leaflet')).default;

  // Center map. If no GPS lock yet, default to target area
  const startLat = (props.lat !== 0) ? props.lat : 8.49918;
  const startLng = (props.lng !== 0) ? props.lng : 124.31046;

  map = L.map(mapContainer.value, {
    zoomControl: false 
  }).setView([startLat, startLng], props.zoom);

  L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 22,
    attribution: '© Google'
  }).addTo(map);

  // Draw trees if any exist
  if (props.trees && props.trees.length > 0) {
    props.trees.forEach(tree => {
      L.circleMarker([tree.lat, tree.lng], {
        radius: 4, color: '#10B981', fillColor: '#10B981', fillOpacity: 1
      }).addTo(map);
      
      if (tree.accuracy) {
        L.circle([tree.lat, tree.lng], {
          radius: tree.accuracy, color: '#34D399', weight: 1, fillColor: '#34D399', fillOpacity: 0.2
        }).addTo(map);
      }
    });
  }

  // Draw Drone using the new Custom Icon
  if (props.lat !== 0 && props.lng !== 0) {
    droneMarker = L.marker([props.lat, props.lng], { 
      icon: getDroneIcon(props.heading) 
    }).addTo(map);
  }
});

// --- Watch for Drone Movement & Heading Changes ---
// Notice we now watch `props.heading` alongside lat/lng
watch(() => [props.lat, props.lng, props.heading], ([newLat, newLng, newHeading]) => {
  if (newLat !== 0 && newLng !== 0 && map && L) {
    
    if (droneMarker) {
      // 1. Update Position
      droneMarker.setLatLng([newLat, newLng]);
      // 2. Update Icon (This applies the new rotation)
      droneMarker.setIcon(getDroneIcon(newHeading || 0));
    } else {
      // Create it the first time it connects
      droneMarker = L.marker([newLat, newLng], { 
        icon: getDroneIcon(newHeading || 0) 
      }).addTo(map);
    }
    
    // Smoothly pan camera to follow drone
    map.panTo([newLat, newLng]);
  }
});

watch(() => props.zoom, (newZoom) => {
  if (map) map.setZoom(newZoom);
});

onUnmounted(() => {
  if (map) map.remove();
});
</script>

<template>
  <div ref="mapContainer" class="w-full h-full z-0"></div>
</template>
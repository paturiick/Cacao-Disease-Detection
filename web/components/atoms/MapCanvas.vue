<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';

// 1. KEEP the CSS import (Nuxt handles CSS fine on the server)
import 'leaflet/dist/leaflet.css';

// 2. REMOVE the static Leaflet import.
// DO NOT do this: import L from 'leaflet'; 

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
let L = null; // We will store the Leaflet library here once it loads

onMounted(async () => {
  L = (await import('leaflet')).default;

  // Center the map on your first cacao tree since we know where that is
  const startLat = props.trees[0]?.lat || 8.499;
  const startLng = props.trees[0]?.lng || 124.310;

  map = L.map(mapContainer.value, {
    zoomControl: false 
  }).setView([startLat, startLng], props.zoom);

  L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 22,
    attribution: '© Google'
  }).addTo(map);

  // Draw the trees
  if (props.trees.length > 0) {
    props.trees.forEach(tree => {
      // Create the solid green dot and add a hover tooltip
      L.circleMarker([tree.lat, tree.lng], {
        radius: 4,
        color: '#10B981',
        fillColor: '#10B981',
        fillOpacity: 1
      })
      .bindTooltip(
        `<div class="font-inter text-xs">
          <strong>Tree ID:</strong> ${tree.id || 'N/A'}<br>
          <strong>Lat:</strong> ${tree.lat.toFixed(6)}<br>
          <strong>Lng:</strong> ${tree.lng.toFixed(6)}
         </div>`, 
        { 
          direction: 'top', // Position the tooltip above the dot
          offset: [0, -5],  // Shift it slightly up so it doesn't cover the dot
          opacity: 0.9,     // Make it slightly transparent
          className: 'custom-tree-tooltip' // Optional class for custom CSS
        }
      )
      .addTo(map);

      // Create the accuracy radius
      L.circle([tree.lat, tree.lng], {
        radius: tree.accuracy,
        color: '#34D399',
        weight: 1,
        fillColor: '#34D399',
        fillOpacity: 0.2
      }).addTo(map);
    });
  }

  // ONLY draw the drone if we have REAL coordinates (not 0)
  if (props.lat !== 0 && props.lng !== 0) {
    droneMarker = L.circleMarker([props.lat, props.lng], {
      radius: 6, color: '#EF4444', fillColor: '#EF4444', fillOpacity: 1
    }).addTo(map);
  }
});

// --- Watch for Drone Movement ---
watch(() => [props.lat, props.lng], ([newLat, newLng]) => {
  // Only update or create the marker if the coordinates are not 0
  if (newLat !== 0 && newLng !== 0) {
    if (droneMarker) {
      droneMarker.setLatLng([newLat, newLng]);
    } else if (map && L) {
      // Create it the very first time the drone gets a GPS lock!
      droneMarker = L.circleMarker([newLat, newLng], {
        radius: 6, color: '#EF4444', fillColor: '#EF4444', fillOpacity: 1
      }).addTo(map);
    }
  }
});

// --- Watchers for Reactivity ---

watch(() => [props.lat, props.lng], ([newLat, newLng]) => {
  if (newLat && newLng) {
    if (droneMarker) {
      droneMarker.setLatLng([newLat, newLng]);
    } else if (map && L) {
      // If marker didn't exist, create it (making sure L is loaded)
      droneMarker = L.circleMarker([newLat, newLng], {
        radius: 6, color: '#EF4444', fillColor: '#EF4444', fillOpacity: 1
      }).addTo(map);
    }
  }
});

watch(() => props.zoom, (newZoom) => {
  if (map) {
    map.setZoom(newZoom);
  }
});

onUnmounted(() => {
  if (map) {
    map.remove();
  }
});
</script>

<template>
  <div ref="mapContainer" class="w-full h-full z-0"></div>
</template>
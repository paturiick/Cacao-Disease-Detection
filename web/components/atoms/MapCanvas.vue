<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import 'leaflet/dist/leaflet.css';

const props = defineProps({
  lat: { type: Number, default: 0 },
  lng: { type: Number, default: 0 },
  heading: { type: Number, default: 0 },
  zoom: { type: Number, default: 18 },
  // Array of detection objects from map-geotagging-screen.vue
  trees: { type: Array, default: () => [] }
});

const mapContainer = ref(null);
let map = null;
let droneMarker = null;
let treeLayerGroup = null; // Layer group for dynamic cacao pod markers
let L = null;

const recenter = () => {
  if (map && props.lat !== 0 && props.lng !== 0) {
    map.flyTo([props.lat, props.lng], props.zoom, {
      duration: 1.5,
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
    className: 'bg-transparent',
    iconSize: [56, 56],
    iconAnchor: [28, 28],
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

// --- Cacao Pod Marker Rendering ---
const renderTrees = (trees) => {
  if (!map || !L || !treeLayerGroup) return;

  // Clear existing markers before re-rendering the updated list
  treeLayerGroup.clearLayers();

  trees.forEach(tree => {
    // RED for diseased (unhealthy), GREEN for healthy
    const statusColor = tree.status === 'diseased' ? '#ef4444' : '#22c55e';
    
    // Core dot representing the detection location
    const marker = L.circleMarker([tree.lat, tree.lng], {
      radius: 6,
      color: '#ffffff', // White border for visual clarity
      weight: 2,
      fillColor: statusColor,
      fillOpacity: 1
    });

    // Optional: Accuracy/Detection radius ring
    if (tree.accuracy) {
        L.circle([tree.lat, tree.lng], {
          radius: tree.accuracy,
          color: statusColor,
          weight: 1,
          fillColor: statusColor,
          fillOpacity: 0.15
        }).addTo(treeLayerGroup);
    }

    // Attach a popup for detailed view upon clicking the marker
    marker.bindPopup(`
      <div class="font-sans text-center min-w-[120px] p-1">
        <div class="text-[10px] font-bold uppercase tracking-wider mb-2" style="color: ${statusColor}">
          ${tree.status === 'diseased' ? 'Black Pod Detected' : 'Healthy Cacao'}
        </div>
        <img src="${tree.imageUrl}" class="w-full h-24 object-cover rounded-md border border-gray-100 mb-1" />
        <div class="text-[8px] text-gray-400 uppercase font-mono">
          ID: ${tree.id} | ${tree.lat}, ${tree.lng}
        </div>
      </div>
    `);

    marker.addTo(treeLayerGroup);
  });
};

onMounted(async () => {
  L = (await import('leaflet')).default;

  // Center map on drone, or default coordinates if GPS isn't locked
  const startLat = (props.lat !== 0) ? props.lat : 8.49918;
  const startLng = (props.lng !== 0) ? props.lng : 124.31046;

  map = L.map(mapContainer.value, {
    zoomControl: false 
  }).setView([startLat, startLng], props.zoom);

  L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 22,
    attribution: '© Google'
  }).addTo(map);

  // Initialize and attach the LayerGroup to the map
  treeLayerGroup = L.layerGroup().addTo(map);

  // Initial render of existing trees
  renderTrees(props.trees);

  if (props.lat !== 0 && props.lng !== 0) {
    droneMarker = L.marker([props.lat, props.lng], { 
      icon: getDroneIcon(props.heading) 
    }).addTo(map);
  }
});

// --- Watchers for Reactive Updates ---

// Watch for new detections (SSE stream updates the trees array)
watch(() => props.trees, (newTrees) => {
  renderTrees(newTrees);
}, { deep: true });

// Watch for Drone Movement & Orientation
watch(() => [props.lat, props.lng, props.heading], ([newLat, newLng, newHeading]) => {
  if (newLat !== 0 && newLng !== 0 && map && L) {
    if (droneMarker) {
      droneMarker.setLatLng([newLat, newLng]);
      droneMarker.setIcon(getDroneIcon(newHeading || 0));
    } else {
      droneMarker = L.marker([newLat, newLng], { 
        icon: getDroneIcon(newHeading || 0) 
      }).addTo(map);
    }
    
    // Automatically pan camera to follow drone flight
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
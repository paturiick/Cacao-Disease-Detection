<script setup>
import { ref, onMounted, watch, onUnmounted, createVNode, render } from 'vue';
import 'leaflet/dist/leaflet.css';
import DroneModel from '~/components/atoms/DroneModel.vue';

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

// --- STATE: MAP TRACKING ---
// Tracks whether the camera should auto-follow the drone
const isTracking = ref(true);

const recenterMap = () => {
  isTracking.value = true;
  if (map && props.lat !== 0 && props.lng !== 0) {
    map.flyTo([props.lat, props.lng], props.zoom, {
      duration: 1.5,
      easeLinearity: 0.25
    });
  }
};

// Exposing for parent components that might use either naming convention
defineExpose({
  recenter: recenterMap,
  recenterMap
});

// --- Custom Drone Icon Generator ---
const getDroneIcon = (heading) => {
  const tempContainer = document.createElement('div');

  // REDUCED SIZE: Changed from 56px to 36px to look like a proper map marker
  const vnode = createVNode('div', { class: 'relative flex items-center justify-center w-[36px] h-[36px]' }, [
    createVNode('div', { class: 'absolute w-full h-full bg-[#658D1B]/30 rounded-full animate-ping' }),
    
    createVNode('svg', {
      viewBox: '-24 -24 48 48',
      class: 'relative z-10 w-9 h-9', // w-9 is 36px
      style: `transform: rotate(${heading}deg); transition: transform 0.3s ease-out; filter: drop-shadow(0px 3px 4px rgba(0,0,0,0.5));`
    }, [
      createVNode(DroneModel, { isRunning: true })
    ])
  ]);

  render(vnode, tempContainer);

  return L.divIcon({
    className: 'bg-transparent',
    iconSize: [36, 36],     // Scaled down
    iconAnchor: [18, 18],   // Centered for the new 36px size
    html: tempContainer.innerHTML
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

  // Initialize and attach the LayerGroup to the map for dynamic pod rendering
  treeLayerGroup = L.layerGroup().addTo(map);

  // Initial render of existing trees
  renderTrees(props.trees);

  // If the user drags the map manually, turn off auto-tracking so they aren't forced back
  map.on('dragstart', () => {
    isTracking.value = false;
  });

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
    
    // Only pan the map if the user hasn't dragged away (isTracking is true)
    if (isTracking.value) {
      map.panTo([newLat, newLng]);
    }
  }
});

watch(() => props.zoom, (newZoom) => {
  if (map) map.setZoom(newZoom);
});

onUnmounted(() => {
  if (map) {
    map.off('dragstart');
    map.remove();
  }
});
</script>

<template>
  <div class="relative w-full h-full">
    <div ref="mapContainer" class="w-full h-full z-0"></div>

    <button 
      @click="recenterMap"
      class="absolute bottom-4 right-4 z-[400] p-2.5 rounded-xl shadow-lg border transition-all flex items-center justify-center"
      :class="isTracking 
        ? 'bg-[#658D1B] border-[#658D1B] text-white' 
        : 'bg-white border-slate-200 text-slate-500 hover:text-[#658D1B]'"
      title="Recenter on Drone"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12h4m10 0h4M12 3v4m0 10v4m0-11a3 3 0 100 6 3 3 0 000-6z" />
      </svg>
    </button>
  </div>
</template>
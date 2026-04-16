<script setup>
import { ref, onMounted, watch, onUnmounted, createVNode, render } from 'vue';
import 'leaflet/dist/leaflet.css';
import DroneModel from '~/components/atoms/DroneModel.vue';

const props = defineProps({
  lat: { type: Number, default: 0 },
  lng: { type: Number, default: 0 },
  heading: { type: Number, default: 0 },
  // 1. INCREASED INITIAL ZOOM: Set to 21 based on your reference image
  zoom: { type: Number, default: 21 },
  // Array of detection objects from map-geotagging-screen.vue
  trees: { type: Array, default: () => [] }
});

const mapContainer = ref(null);
let map = null;
let droneMarker = null;
let treeLayerGroup = null; // Layer group for dynamic cacao pod markers
let L = null;

// --- STATE: MAP TRACKING ---
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

defineExpose({
  recenter: recenterMap,
  recenterMap
});

// --- Custom Drone Icon Generator ---
const getDroneIcon = (heading) => {
  const tempContainer = document.createElement('div');

  const vnode = createVNode('div', { class: 'relative flex items-center justify-center w-[24px] h-[24px]' }, [
    createVNode('div', { class: 'absolute w-full h-full bg-[#658D1B]/30 rounded-full animate-ping' }),
    
    createVNode('svg', {
      viewBox: '-24 -24 48 48',
      class: 'relative z-10 w-6 h-6', 
      style: `transform: rotate(${heading}deg); transition: transform 0.3s ease-out; filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.5));`
    }, [
      createVNode(DroneModel, { isRunning: true })
    ])
  ]);

  render(vnode, tempContainer);

  return L.divIcon({
    className: 'bg-transparent',
    iconSize: [24, 24],     
    iconAnchor: [12, 12],   
    html: tempContainer.innerHTML
  });
};

// --- Cacao Pod Marker Rendering ---
const renderTrees = (trees) => {
  if (!map || !L || !treeLayerGroup) return;

  treeLayerGroup.clearLayers();

  trees.forEach(tree => {
    const statusColor = tree.status === 'diseased' ? '#ef4444' : '#22c55e';
    
    // 2. ADJUSTED PIN SIZE: radius increased to 5 for better visibility at high zoom
    const marker = L.circleMarker([tree.lat, tree.lng], {
      radius: 5, 
      color: '#ffffff', 
      weight: 1.5,        
      fillColor: statusColor,
      fillOpacity: 1
    });

    // Green area/Accuracy ring remains removed as requested

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

  const startLat = (props.lat !== 0) ? props.lat : 8.49918;
  const startLng = (props.lng !== 0) ? props.lng : 124.31046;

  map = L.map(mapContainer.value, {
    zoomControl: false 
  }).setView([startLat, startLng], props.zoom);

  L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 22,
    attribution: '© Google'
  }).addTo(map);

  treeLayerGroup = L.layerGroup().addTo(map);

  renderTrees(props.trees);

  map.on('dragstart', () => {
    isTracking.value = false;
  });

  if (props.lat !== 0 && props.lng !== 0) {
    droneMarker = L.marker([props.lat, props.lng], { 
      icon: getDroneIcon(props.heading) 
    }).addTo(map);
  }
});

watch(() => props.trees, (newTrees) => {
  renderTrees(newTrees);
}, { deep: true });

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
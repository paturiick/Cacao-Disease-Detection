<script setup>
import { ref, onMounted, watch, onUnmounted, createVNode, render } from 'vue';
import 'leaflet/dist/leaflet.css';
import DroneModel from '~/components/atoms/DroneModel.vue';

const props = defineProps({
  lat: { type: Number, default: 0 },
  lng: { type: Number, default: 0 },
  heading: { type: Number, default: 0 },
  zoom: { type: Number, default: 21 },
  trees: { type: Array, default: () => [] }
});

const mapContainer = ref(null);
let map = null;
let droneMarker = null;
let treeLayerGroup = null;
let L = null;

// Track rendered trees to prevent redundant DOM updates
const renderedTreeMarkers = new Map();

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

defineExpose({ recenterMap });

// --- Custom Drone Icon Generator (Called ONCE) ---
const createDroneIcon = (heading) => {
  const tempContainer = document.createElement('div');

  const vnode = createVNode('div', { class: 'relative flex items-center justify-center w-[24px] h-[24px]' }, [
    createVNode('div', { class: 'absolute w-full h-full bg-[#658D1B]/30 rounded-full animate-ping' }),
    
    // FIXED: Changed back to 'svg' and restored the viewBox
    createVNode('svg', {
      viewBox: '-24 -24 48 48',
      class: 'drone-icon-wrapper relative z-10 w-6 h-6', 
      style: `transform: rotate(${heading}deg); transition: transform 0.15s linear; filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.5));`
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

// --- Smart Cacao Pod Marker Rendering ---
const renderTrees = (trees) => {
  if (!map || !L || !treeLayerGroup) return;

  trees.forEach(tree => {
    // Skip if we already rendered this specific tree
    if (renderedTreeMarkers.has(tree.id)) return;

    const statusColor = tree.status === 'diseased' ? '#ef4444' : '#22c55e';
    
    const marker = L.circleMarker([tree.lat, tree.lng], {
      radius: 5, 
      color: '#ffffff', 
      weight: 1.5,        
      fillColor: statusColor,
      fillOpacity: 1
    });

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
    
    // Save to map so we don't redraw it next time
    renderedTreeMarkers.set(tree.id, marker);
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
      icon: createDroneIcon(props.heading) 
    }).addTo(map);
  }
});

// Watch specifically for trees
watch(() => props.trees, (newTrees) => {
  renderTrees(newTrees);
}, { deep: true });

// Watch for Drone Movement
watch(() => [props.lat, props.lng, props.heading], ([newLat, newLng, newHeading]) => {
  if (newLat !== 0 && newLng !== 0 && map && L) {
    
    if (droneMarker) {
      // Update Position
      droneMarker.setLatLng([newLat, newLng]);
      
      // Update Heading via raw DOM manipulation instead of rebuilding the icon
      const iconEl = droneMarker.getElement();
      if (iconEl) {
        const wrapper = iconEl.querySelector('.drone-icon-wrapper');
        if (wrapper) wrapper.style.transform = `rotate(${newHeading}deg)`;
      }
    } else {
      droneMarker = L.marker([newLat, newLng], { 
        icon: createDroneIcon(newHeading || 0) 
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
  renderedTreeMarkers.clear();
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
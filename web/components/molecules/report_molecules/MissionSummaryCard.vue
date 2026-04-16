<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import VisualBoard from '~/components/organisms/mission_planner_organism/VisualBoard.vue'; 
import 'leaflet/dist/leaflet.css'; 

const props = defineProps({
  steps: { type: Array, default: () => [] },
  trees: { type: Array, default: () => [] }
});

const activeLeftTab = ref('commands'); 
const activeRightTab = ref('database'); 

const focusedTreeId = ref(null);

let mapInstance = null;
let L = null;
let treeMarkers = {}; 

const mappedQueue = computed(() => {
  return props.steps.map(step => ({
    id: step.step_id,
    type: step.command,
    val: step.value
  }));
});

// Format the tree data with a tiny jitter to ensure overlapping pins are visible
const mapReadyTrees = computed(() => {
  return props.trees.map((tree, index) => {
    // Micro-jitter: Offsets markers by a few centimeters so stacked pins are distinct
    const jitter = index * 0.000005; 
    return {
      id: tree.tree_id,
      lat: parseFloat(tree.lat) + jitter,
      lng: parseFloat(tree.lon) + jitter,
      image: tree.image || 'https://images.unsplash.com/photo-1597848212624-a19eb35e2656?w=400&q=60'
    };
  });
});

const mapCenter = computed(() => {
  if (focusedTreeId.value !== null) {
    const targetTree = mapReadyTrees.value.find(t => t.id === focusedTreeId.value);
    if (targetTree) return { lat: targetTree.lat, lng: targetTree.lng };
  }
  if (mapReadyTrees.value.length > 0) {
    return { lat: mapReadyTrees.value[0].lat, lng: mapReadyTrees.value[0].lng };
  }
  return { lat: 8.49918, lng: 124.31046 }; 
});

const initMap = async () => {
  if (!L) L = (await import('leaflet')).default;

  // INITIAL ZOOM LEVEL 21
  mapInstance = L.map('database-map', {
    zoomControl: true 
  }).setView([mapCenter.value.lat, mapCenter.value.lng], 21);

  L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
    maxZoom: 22,
    attribution: '© Google'
  }).addTo(mapInstance);

  treeMarkers = {};

  mapReadyTrees.value.forEach(tree => {
    // MINIMIZED PIN SIZE
    const iconHtml = `
      <div class="relative flex flex-col items-center group cursor-pointer transition-transform hover:scale-110">
        <div class="w-5 h-5 bg-[#658D1B] rounded-full shadow-md flex items-center justify-center border border-white z-10">
          <span class="text-white font-black text-[9px]">${tree.id}</span>
        </div>
        <div class="w-0 h-0 border-l-[4px] border-r-[4px] border-t-[5px] border-transparent border-t-[#658D1B] -mt-0.5 z-0 filter drop-shadow-sm"></div>
      </div>
    `;

    const icon = L.divIcon({
      className: 'bg-transparent',
      iconSize: [20, 25],
      iconAnchor: [10, 25], 
      popupAnchor: [0, -22], 
      html: iconHtml
    });

    const popupContent = `
      <div class="w-48 flex flex-col font-sans">
        <div class="w-full h-32 rounded-t-lg overflow-hidden bg-slate-100 border-b border-slate-200">
          <img src="${tree.image}" alt="Tree Capture" class="w-full h-full object-cover" />
        </div>
        <div class="p-3 bg-white rounded-b-lg">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-black text-slate-400 uppercase tracking-widest">Pod ID</span>
            <span class="text-sm font-black text-[#658D1B]">${tree.id}</span>
          </div>
          <div class="space-y-1 mt-2">
            <p class="text-[10px] font-mono text-slate-500">Lat: ${tree.lat.toFixed(6)}</p>
            <p class="text-[10px] font-mono text-slate-500">Lng: ${tree.lng.toFixed(6)}</p>
          </div>
        </div>
      </div>
    `;

    const marker = L.marker([tree.lat, tree.lng], { icon })
      .bindPopup(popupContent, { closeButton: false, className: 'custom-tree-popup', minWidth: 192 })
      .addTo(mapInstance);

    treeMarkers[tree.id] = marker;
  });

  if (focusedTreeId.value !== null && treeMarkers[focusedTreeId.value]) {
    treeMarkers[focusedTreeId.value].openPopup();
  }
};

watch(activeRightTab, async (newTab) => {
  if (newTab === 'map') {
    await nextTick();
    initMap();
  } else {
    if (mapInstance) {
      mapInstance.remove();
      mapInstance = null;
    }
  }
});

const viewOnMap = (treeId) => {
  focusedTreeId.value = treeId;
  activeRightTab.value = 'map'; 
};

onUnmounted(() => {
  if (mapInstance) mapInstance.remove();
});
</script>

<template>
  <div class="grid grid-cols-2 gap-8 print:grid-cols-2">
    
    <section class="flex flex-col h-[calc(100vh-280px)] min-h-[400px] print:h-[500px]">
      <div class="flex items-center gap-6 mb-3 print:hidden">
        <button 
          @click="activeLeftTab = 'commands'" 
          class="text-xs font-bold uppercase tracking-widest pb-1 border-b-2 transition-colors duration-200"
          :class="activeLeftTab === 'commands' ? 'text-slate-700 border-[#658D1B]' : 'text-slate-400 border-transparent hover:text-slate-500'"
        >
          Command Sequence
        </button>
        <button 
          @click="activeLeftTab = 'visualization'" 
          class="text-xs font-bold uppercase tracking-widest pb-1 border-b-2 transition-colors duration-200"
          :class="activeLeftTab === 'visualization' ? 'text-slate-700 border-[#658D1B]' : 'text-slate-400 border-transparent hover:text-slate-500'"
        >
          Visualization
        </button>
      </div>
      
      <h3 class="hidden print:block text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
        Command Sequence / Map
      </h3>

      <div class="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 flex flex-col overflow-hidden print:shadow-none print:border-slate-300 print:rounded-none">
        
        <div v-show="activeLeftTab === 'commands'" class="flex-1 flex flex-col overflow-hidden">
          <div class="grid grid-cols-4 bg-slate-50 border-b border-slate-200 p-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0 print:bg-white print:border-black">
            <div class="col-span-1 text-center">Order</div>
            <div class="col-span-1">Step ID</div>
            <div class="col-span-1">Command</div>
            <div class="col-span-1 text-right">Value</div>
          </div>
          <div class="overflow-y-auto flex-1 p-1 print:overflow-visible custom-scrollbar">
            <div v-if="steps.length === 0" class="text-center p-6 text-slate-400 text-xs font-bold uppercase tracking-wider">No sequence data</div>
            <div v-for="step in steps" :key="step.step_id" class="grid grid-cols-4 p-2.5 border-b border-slate-50 last:border-0 hover:bg-slate-50 text-sm print:border-slate-200 print:py-1">
              <div class="col-span-1 text-center font-bold text-slate-400 print:text-black">{{ step.order }}</div>
              <div class="col-span-1 font-mono text-slate-500 print:text-black">{{ step.step_id }}</div>
              <div class="col-span-1 font-bold text-[#0F172A] uppercase text-xs">{{ step.command }}</div>
              <div class="col-span-1 text-right font-black text-[#658D1B] print:text-black">{{ step.value }}</div>
            </div>
          </div>
        </div>

        <div v-if="activeLeftTab === 'visualization'" class="flex-1 flex flex-col bg-[#F8FAFC]">
          <VisualBoard 
            :queue="mappedQueue" 
            :isRunning="false" 
            :activeIndex="-1"
            mode="report" 
            class="h-full w-full rounded-none border-0"
          />
        </div>

      </div>
    </section>

    <section class="flex flex-col h-[calc(100vh-280px)] min-h-[400px] print:h-[500px]">
      <div class="flex items-center gap-6 mb-3 print:hidden">
        <button 
          @click="activeRightTab = 'database'" 
          class="text-xs font-bold uppercase tracking-widest pb-1 border-b-2 transition-colors duration-200"
          :class="activeRightTab === 'database' ? 'text-slate-700 border-[#658D1B]' : 'text-slate-400 border-transparent hover:text-slate-500'"
        >
          Geotagged Database
        </button>
        <button 
          @click="activeRightTab = 'map'" 
          class="text-xs font-bold uppercase tracking-widest pb-1 border-b-2 transition-colors duration-200"
          :class="activeRightTab === 'map' ? 'text-slate-700 border-[#658D1B]' : 'text-slate-400 border-transparent hover:text-slate-500'"
        >
          Map View
        </button>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 flex flex-col overflow-hidden print:shadow-none print:border-slate-300 print:rounded-none">
        <div v-show="activeRightTab === 'database'" class="flex-1 flex flex-col overflow-hidden">
          <div class="grid grid-cols-5 bg-slate-50 border-b border-slate-200 p-3 text-[10px] font-bold text-slate-500 uppercase tracking-wider shrink-0 print:bg-white print:border-black">
            <div class="col-span-1 text-center">Pod ID</div>
            <div class="col-span-1">Latitude</div>
            <div class="col-span-1">Longitude</div>
            <div class="col-span-1 text-center print:hidden">Action</div>
          </div>
          <div class="overflow-y-auto flex-1 p-1 print:overflow-visible custom-scrollbar">
            <div v-if="trees.length === 0" class="text-center p-6 text-slate-400 text-xs font-bold uppercase tracking-wider">No pods mapped</div>
            <div v-for="tree in trees" :key="tree.tree_id" class="grid grid-cols-5 items-center p-2.5 border-b border-slate-50 last:border-0 hover:bg-slate-50 text-sm print:border-slate-200 print:py-1">
              <div class="col-span-1 text-center font-bold text-slate-400 print:text-black">{{ tree.tree_id }}</div>
              <div class="col-span-1 font-mono text-[#0F172A]">{{ tree.lat }}</div>
              <div class="col-span-1 font-mono text-[#0F172A]">{{ tree.lon }}</div>
              <div class="col-span-1 flex justify-center print:hidden">
                <button @click="viewOnMap(tree.tree_id)" class="p-1.5 bg-white border border-slate-200 text-slate-400 hover:text-white hover:bg-[#658D1B] hover:border-[#658D1B] rounded-md shadow-sm transition-all">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeRightTab === 'map'" class="flex-1 relative bg-slate-50">
          <div id="database-map" class="w-full h-full rounded-b-xl z-0"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<style>
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.3); border-radius: 10px; }
.leaflet-div-icon { background: transparent !important; border: none !important; }
.custom-tree-popup .leaflet-popup-content-wrapper { padding: 0 !important; border-radius: 0.5rem !important; overflow: hidden; }
.custom-tree-popup .leaflet-popup-content { margin: 0 !important; }
</style>
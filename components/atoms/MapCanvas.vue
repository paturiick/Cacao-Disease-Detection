<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';

const props = defineProps({
  heading: { type: Number, default: 0 },
  lat:     { type: Number, default: 0 },
  lng:     { type: Number, default: 0 },
  zoom:    { type: Number, default: 18 }
});

// ── DOM ref ────────────────────────────────────────────────────────────────
const mapContainer = ref(null);

// ── Runtime refs (not reactive – just imperative Leaflet state) ────────────
let map         = null;
let droneMarker = null;
let L           = null;

// ── Default location fallback (Davao Region, Philippines – cacao belt) ─────
const DEFAULT_LAT = 7.1907;
const DEFAULT_LNG = 125.4553;

const effectiveLat = computed(() => (props.lat  !== 0 || props.lng !== 0) ? props.lat  : DEFAULT_LAT);
const effectiveLng = computed(() => (props.lat  !== 0 || props.lng !== 0) ? props.lng  : DEFAULT_LNG);

// ── Build a rotating drone DivIcon ─────────────────────────────────────────
const makeDroneIcon = (leaflet, heading) =>
  leaflet.divIcon({
    html: `
      <div style="
        width:38px; height:38px;
        display:flex; align-items:center; justify-content:center;
        transform:rotate(${heading}deg);
        transform-origin:50% 50%;
        transition:transform 0.3s ease;
      ">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24"
             fill="#1D4ED8"
             style="filter:drop-shadow(0 2px 4px rgba(0,0,0,0.45));">
          <path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z"/>
        </svg>
      </div>`,
    className:  '',
    iconSize:   [38, 38],
    iconAnchor: [19, 19],
  });

// ── Initialise Leaflet on mount (browser-only via dynamic import) ──────────
onMounted(async () => {
  L = (await import('leaflet')).default ?? (await import('leaflet'));

  // Prevent Vite from erroring on the default marker image resolution
  // (we use a custom DivIcon so the defaults don't matter, but this
  //  silences the console warning)
  delete (L.Icon.Default.prototype)._getIconUrl;
  L.Icon.Default.mergeOptions({ iconUrl: '', shadowUrl: '' });

  map = L.map(mapContainer.value, {
    center:         [effectiveLat.value, effectiveLng.value],
    zoom:           props.zoom,
    zoomControl:    false,   // provided by parent card
    attributionControl: true,
  });

  // OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom:     22,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  // Drone marker
  droneMarker = L.marker([effectiveLat.value, effectiveLng.value], {
    icon: makeDroneIcon(L, props.heading),
  }).addTo(map);

  // Accuracy circle (50 m)
  L.circle([effectiveLat.value, effectiveLng.value], {
    radius: 50, color: '#1D4ED8', fillColor: '#3B82F6',
    fillOpacity: 0.08, weight: 1.5,
  }).addTo(map);
});

// ── Tear down on unmount ───────────────────────────────────────────────────
onUnmounted(() => {
  if (map) { map.remove(); map = null; }
  droneMarker = null;
  L = null;
});

// ── Reactively follow GPS ──────────────────────────────────────────────────
watch([effectiveLat, effectiveLng], ([lat, lng]) => {
  if (!map || !droneMarker) return;
  const pos = [lat, lng];
  droneMarker.setLatLng(pos);
  map.panTo(pos, { animate: true, duration: 0.6 });
});

// ── Reactively rotate marker ───────────────────────────────────────────────
watch(() => props.heading, (heading) => {
  if (!droneMarker || !L) return;
  droneMarker.setIcon(makeDroneIcon(L, heading));
});

// ── Sync zoom from parent controls ────────────────────────────────────────
watch(() => props.zoom, (zoom) => {
  if (!map) return;
  map.setZoom(zoom, { animate: true });
});
</script>

<template>
  <div ref="mapContainer" class="w-full h-full min-h-0" />
</template>
<script setup>
import { ref, computed } from 'vue';
import BaseCard      from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import MapCanvas     from '~/components/atoms/MapCanvas.vue';

const props = defineProps({
  gpsData: { type: Object, required: true }
});

// ── Zoom ───────────────────────────────────────────────────────────────────
const MIN_ZOOM     = 1;
const MAX_ZOOM     = 22;
const DEFAULT_ZOOM = 18;
const currentZoom  = ref(DEFAULT_ZOOM);

const zoomIn  = () => { if (currentZoom.value < MAX_ZOOM) currentZoom.value++; };
const zoomOut = () => { if (currentZoom.value > MIN_ZOOM) currentZoom.value--; };

// ── GPS helpers (safe defaults so template stays expression-free) ──────────
const lat      = computed(() => props.gpsData?.lat     ?? 0);
const lng      = computed(() => props.gpsData?.lng     ?? 0);
const heading  = computed(() => props.gpsData?.heading ?? 0);
const coordLabel = computed(() =>
  `${lat.value.toFixed(6)},  ${lng.value.toFixed(6)}`
);
</script>

<template>
  <BaseCard class="h-full flex flex-col">

    <!-- ── Header ────────────────────────────────────────────────────────── -->
    <div class="flex items-center justify-between mb-3 border-b border-gray-100 pb-3 shrink-0">
      <SectionHeader class="!mb-0">
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
          </svg>
        </template>
        Live Map View
      </SectionHeader>

      <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
        Zoom {{ currentZoom }}
      </span>
    </div>

    <!-- ── Map container ─────────────────────────────────────────────────── -->
    <div class="flex-1 min-h-[400px] relative rounded-lg overflow-hidden border border-gray-200">

      <!-- Zoom controls — z-[1000] places them above Leaflet tile layer -->
      <div class="absolute top-3 right-3 z-[1000] flex flex-col shadow-md rounded-lg overflow-hidden border border-gray-200 bg-white">
        <button
          @click="zoomIn"
          :disabled="currentZoom >= MAX_ZOOM"
          title="Zoom In"
          class="w-8 h-8 flex items-center justify-center font-bold text-gray-600 hover:bg-gray-50 border-b border-gray-200 text-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >+</button>
        <button
          @click="zoomOut"
          :disabled="currentZoom <= MIN_ZOOM"
          title="Zoom Out"
          class="w-8 h-8 flex items-center justify-center font-bold text-gray-600 hover:bg-gray-50 text-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >−</button>
      </div>

      <!-- GPS coordinate overlay -->
      <div class="absolute bottom-3 left-3 z-[1000] bg-white/90 backdrop-blur-sm border border-gray-200 px-2.5 py-1.5 rounded-lg shadow-sm text-[10px] font-mono text-gray-700 leading-none">
        {{ coordLabel }}
      </div>

      <!-- Leaflet map (fills container) -->
      <MapCanvas
        :lat="lat"
        :lng="lng"
        :heading="heading"
        :zoom="currentZoom"
        class="w-full h-full"
      />

    </div>

  </BaseCard>
</template>

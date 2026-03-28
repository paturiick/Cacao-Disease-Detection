<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  queue: { type: Array, default: () => [] },
  activeIndex: { type: Number, default: -1 },
  isRunning: { type: Boolean, default: false }
});

// --- STATE FOR DRONE POSITION & YAW ---
const currentDronePos = ref({ x: 0, y: 0 });
const currentDroneYaw = ref(0);

// --- ZOOM STATE & LIMITS ---
const zoomMultiplier = ref(1);
const MIN_ZOOM = 0.2; 
const MAX_ZOOM = 1.5; 

const handleZoomIn = () => {
  zoomMultiplier.value = Math.max(MIN_ZOOM, zoomMultiplier.value - 0.2);
};

const handleZoomOut = () => {
  zoomMultiplier.value = Math.min(MAX_ZOOM, zoomMultiplier.value + 0.2);
};

const handleZoomReset = () => {
  zoomMultiplier.value = 1;
};

const handleWheel = (e) => {
  const zoomStep = 0.05; 
  if (e.deltaY < 0) {
    zoomMultiplier.value = Math.max(MIN_ZOOM, zoomMultiplier.value - zoomStep);
  } else if (e.deltaY > 0) {
    zoomMultiplier.value = Math.min(MAX_ZOOM, zoomMultiplier.value + zoomStep);
  }
};

// --- DRONE VISUALIZATION LOGIC ---
const visualData = computed(() => {
  let x = 0;
  let y = 0;
  let currentYaw = 0;
  const segments = [];
  let minX = 0, maxX = 0, minY = 0, maxY = 0;

  props.queue.forEach((cmd, idx) => {
    let startX = x;
    let startY = y;
    let val = Number(cmd.val) || 0;
    let isMovement = false;
    let unit = '';
    let labelPrefix = cmd.type.toUpperCase();

    const rad = currentYaw * (Math.PI / 180);

    if (['forward', 'back', 'left', 'right'].includes(cmd.type)) {
      isMovement = true;
      unit = 'cm';
      if (cmd.type === 'forward') { x += val * Math.sin(rad); y -= val * Math.cos(rad); }
      else if (cmd.type === 'back') { x -= val * Math.sin(rad); y += val * Math.cos(rad); }
      else if (cmd.type === 'right') { x += val * Math.cos(rad); y += val * Math.sin(rad); }
      else if (cmd.type === 'left') { x -= val * Math.cos(rad); y -= val * Math.sin(rad); }
    } 
    else if (cmd.type === 'go') {
      isMovement = true;
      const parts = String(cmd.val).split(' ');
      let localX = parseInt(parts[0]) || 0;
      let localY = parseInt(parts[1]) || 0;
      x += (localX * Math.cos(rad)) + (localY * Math.sin(rad));
      y += (localX * Math.sin(rad)) - (localY * Math.cos(rad)); 
      labelPrefix = 'GO';
      val = cmd.val;
    } 
    else if (cmd.type === 'cw') { currentYaw += val; unit = '°'; } 
    else if (cmd.type === 'ccw') { currentYaw -= val; unit = '°'; } 
    else {
      if (['up', 'down'].includes(cmd.type)) unit = 'cm';
      else if (cmd.type === 'hover') unit = 's';
    }

    minX = Math.min(minX, x);
    maxX = Math.max(maxX, x);
    minY = Math.min(minY, y);
    maxY = Math.max(maxY, y);

    const isActive = props.activeIndex === idx + 1;

    segments.push({
      id: cmd.id || idx,
      type: cmd.type,
      label: `${labelPrefix} ${val}${unit}`,
      startX, startY, endX: x, endY: y, endYaw: currentYaw,
      midX: isMovement ? (startX + x) / 2 : x,
      midY: isMovement ? (startY + y) / 2 : y,
      isMovement,
      isActive
    });
  });

  return { segments, minX, maxX, minY, maxY };
});

watch(() => props.activeIndex, (newIdx) => {
  if (newIdx === 0) { currentDronePos.value = { x: 0, y: 0 }; currentDroneYaw.value = 0; } 
  else if (newIdx > 0 && visualData.value.segments[newIdx - 1]) {
    const activeSeg = visualData.value.segments[newIdx - 1];
    currentDronePos.value = { x: activeSeg.endX, y: activeSeg.endY };
    currentDroneYaw.value = activeSeg.endYaw;
  }
  else if (newIdx === -1 && props.queue.length === 0) { currentDronePos.value = { x: 0, y: 0 }; currentDroneYaw.value = 0; }
}, { immediate: true });

const svgViewBox = computed(() => {
  const { minX, maxX, minY, maxY } = visualData.value;
  const pad = 150; 
  const baseW = Math.max(400, maxX - minX);
  const baseH = Math.max(400, maxY - minY);
  const cx = (maxX + minX) / 2;
  const cy = (maxY + minY) / 2;
  const finalW = (baseW + pad * 2) * zoomMultiplier.value;
  const finalH = (baseH + pad * 2) * zoomMultiplier.value;
  return `${cx - finalW/2} ${cy - finalH/2} ${finalW} ${finalH}`;
});

// Dynamic label scale logic: labels get physically larger when zooming out to stay readable
const labelScale = computed(() => Math.max(1, zoomMultiplier.value * 1.5));
</script>

<template>
  <div 
    class="flex flex-col h-full bg-[#F8FAFC] relative z-0 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.02)] border-l border-slate-200 rounded-r-lg"
    @wheel.prevent="handleWheel"
  >
    <div class="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-md px-3 py-2 rounded-lg border border-slate-200 shadow-sm flex items-center gap-2 pointer-events-none">
       <span class="relative flex h-2 w-2">
         <span v-if="props.isRunning" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#658D1B] opacity-75"></span>
         <span class="relative inline-flex rounded-full h-2 w-2" :class="props.isRunning ? 'bg-[#658D1B]' : 'bg-slate-400'"></span>
       </span>
       <span class="text-[10px] font-black text-slate-700 uppercase tracking-widest">Drone Command Visualization</span>
    </div>

    <div class="absolute top-4 right-4 z-10 flex flex-col items-center pointer-events-none opacity-80">
      <svg class="w-6 h-8 filter drop-shadow-md" viewBox="0 0 24 32">
        <path d="M12 0 L18 16 L12 12 L6 16 Z" fill="#EF4444" />
        <path d="M12 32 L18 16 L12 12 L6 16 Z" fill="#CBD5E1" />
        <circle cx="12" cy="14" r="2" fill="white" />
      </svg>
      <span class="text-[11px] font-black text-slate-600 mt-1 uppercase tracking-widest">N</span>
    </div>

    <div class="absolute bottom-6 right-4 z-10 flex flex-col bg-white/90 backdrop-blur-md rounded-lg border border-slate-200 shadow-sm overflow-hidden">
      <button @click="handleZoomIn" :disabled="zoomMultiplier <= MIN_ZOOM" class="p-2 text-slate-600 hover:bg-slate-100 hover:text-[#658D1B] border-b border-slate-100 transition-colors disabled:opacity-30">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
      </button>
      <button @click="handleZoomReset" class="p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 border-b border-slate-100 transition-colors">
        <svg class="w-4 h-4 mx-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path></svg>
      </button>
      <button @click="handleZoomOut" :disabled="zoomMultiplier >= MAX_ZOOM" class="p-2 text-slate-600 hover:bg-slate-100 hover:text-[#658D1B] transition-colors disabled:opacity-30">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>
      </button>
    </div>

    <svg :viewBox="svgViewBox" class="w-full h-full transition-all duration-[100ms] ease-out cursor-crosshair">
      <defs>
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#E2E8F0" stroke-width="1" />
        </pattern>
      </defs>

      <rect x="-50000" y="-50000" width="100000" height="100000" fill="url(#grid)" />
      <line x1="-50000" y1="0" x2="50000" y2="0" stroke="#CBD5E1" stroke-width="2" opacity="0.6" />
      <line x1="0" y1="-50000" x2="0" y2="50000" stroke="#CBD5E1" stroke-width="2" opacity="0.6" />

      <g v-for="seg in visualData.segments" :key="'path-'+seg.id">
        <line 
          v-if="seg.isMovement"
          :x1="seg.startX" :y1="seg.startY" 
          :x2="seg.endX" :y2="seg.endY" 
          :stroke="seg.isActive ? '#658D1B' : '#94A3B8'" 
          :stroke-width="seg.isActive ? 5 : 3" 
          stroke-linecap="round"
        />
        
        <circle 
          v-if="!seg.isMovement"
          :cx="seg.endX" :cy="seg.endY" 
          :r="seg.isActive ? 12 : 6" 
          :fill="seg.isActive ? '#F59E0B' : '#E2E8F0'" 
          :stroke="seg.isActive ? '#FFF' : '#94A3B8'"
          stroke-width="2"
        />

        <g :transform="`translate(${seg.midX}, ${seg.isMovement ? seg.midY : seg.midY + 30}) scale(${labelScale})`">
          <rect x="-45" y="-14" width="90" height="28" rx="14" fill="#0F172A" fill-opacity="0.95" />
          <text 
            x="0" y="4" 
            font-size="12" 
            font-weight="900" 
            fill="#FFFFFF" 
            text-anchor="middle" 
            font-family="Inter, sans-serif" 
            letter-spacing="0.5"
          >
            {{ seg.label }}
          </text>
        </g>
      </g>

      <g>
        <circle cx="0" cy="0" r="5" fill="#EF4444" />
        <text x="0" y="-25" font-size="14" font-weight="900" fill="#EF4444" text-anchor="middle" font-family="Inter, sans-serif">ORIGIN</text>
      </g>

      <g :transform="`translate(${currentDronePos.x}, ${currentDronePos.y}) rotate(${currentDroneYaw})`" class="transition-transform duration-[1200ms] ease-in-out">
        <ellipse cx="0" cy="14" rx="16" ry="6" fill="rgba(0,0,0,0.06)" />
        <g>
          <circle v-if="props.isRunning" cx="0" cy="0" r="26" fill="#84CC16" opacity="0.15" class="animate-pulse" />
          <path d="M-14,-14 L14,14 M-14,14 L14,-14" stroke="#CBD5E1" stroke-width="6" stroke-linecap="round" />
          <circle cx="-16" cy="-16" r="7" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <circle cx="16" cy="-16" r="7" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <circle cx="-16" cy="16" r="7" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <circle cx="16" cy="16" r="7" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <rect x="-12" y="-12" width="24" height="24" rx="10" fill="#FFFFFF" stroke="#658D1B" stroke-width="1.5" />
          <rect x="-8" y="-10" width="16" height="9" rx="4" fill="#0F172A" />
          <circle cx="-3" cy="-5.5" r="1.5" fill="#38BDF8" />
          <circle cx="3" cy="-5.5" r="1.5" fill="#38BDF8" />
          <circle cx="0" cy="7" r="2.5" :fill="props.isRunning ? '#84CC16' : '#F59E0B'" />
        </g>
      </g>
    </svg>
  </div>
</template>
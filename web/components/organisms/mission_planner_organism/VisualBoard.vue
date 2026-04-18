<script setup>
import { computed, ref, watch } from 'vue';
import DroneModel from '~/components/atoms/DroneModel.vue';

const props = defineProps({
  queue: { type: Array, default: () => [] },
  activeIndex: { type: Number, default: -1 },
  isRunning: { type: Boolean, default: false },
  mode: { type: String, default: 'plan' } 
});

const emit = defineEmits(['emergency-land']);

const STATIC_LINE_LENGTH = 300; 

const currentDronePos = ref({ x: 0, y: 0 });
const currentDroneYaw = ref(0);
const zoomMultiplier = ref(1);
const MIN_ZOOM = 0.5;
const MAX_ZOOM = 2.5;

const panOffset = ref({ x: 0, y: 0 });
const isDragging = ref(false);
let startDragPos = { x: 0, y: 0 };

const hoveredSegId = ref(null);
const selectedSegId = ref(null); // Tracks the clicked segment
const mousePos = ref({ x: 0, y: 0 });

const handleZoomIn = () => { zoomMultiplier.value = Math.max(MIN_ZOOM, zoomMultiplier.value - 0.2); };
const handleZoomOut = () => { zoomMultiplier.value = Math.min(MAX_ZOOM, zoomMultiplier.value + 0.2); };
const handleZoomReset = () => { 
  zoomMultiplier.value = 1; 
  panOffset.value = { x: 0, y: 0 }; 
  selectedSegId.value = null;
};

const handleRecenter = () => {
  const { minX, maxX, minY, maxY } = visualData.value;
  const centerX = (maxX + minX) / 2;
  const centerY = (maxY + minY) / 2;
  panOffset.value = {
    x: currentDronePos.value.x - centerX,
    y: currentDronePos.value.y - centerY
  };
  zoomMultiplier.value = 1;
};

const handleWheel = (e) => {
  const zoomStep = 0.1; 
  if (e.deltaY < 0) zoomMultiplier.value = Math.max(MIN_ZOOM, zoomMultiplier.value - zoomStep);
  else if (e.deltaY > 0) zoomMultiplier.value = Math.min(MAX_ZOOM, zoomMultiplier.value + zoomStep);
};

const handlePointerDown = (e) => {
  isDragging.value = true;
  startDragPos = {
    x: e.clientX || (e.touches && e.touches[0].clientX) || 0,
    y: e.clientY || (e.touches && e.touches[0].clientY) || 0
  };
};

const handlePointerMove = (e) => {
  const currentX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
  const currentY = e.clientY || (e.touches && e.touches[0].clientY) || 0;
  mousePos.value = { x: currentX, y: currentY };
  if (!isDragging.value) return;
  const dx = (currentX - startDragPos.x) * zoomMultiplier.value * 2.5;
  const dy = (currentY - startDragPos.y) * zoomMultiplier.value * 2.5;
  panOffset.value.x -= dx;
  panOffset.value.y -= dy;
  startDragPos = { x: currentX, y: currentY };
};

const handlePointerUp = () => { isDragging.value = false; };

const handleSegmentClick = (id) => {
  // Toggle the selection on click
  selectedSegId.value = selectedSegId.value === id ? null : id;
};

const handleBackgroundClick = () => {
  selectedSegId.value = null;
};

const visualData = computed(() => {
  let x = 0, y = 0, currentYaw = 0;
  const segments = [];
  let minX = 0, maxX = 0, minY = 0, maxY = 0;

  props.queue.forEach((cmd, idx) => {
    let startX = x, startY = y;
    let val = Number(cmd.val) || 0;
    let isMovement = false;
    const rad = currentYaw * (Math.PI / 180);

    if (['forward', 'back', 'left', 'right'].includes(cmd.type)) {
      isMovement = true;
      if (cmd.type === 'forward') { x += STATIC_LINE_LENGTH * Math.sin(rad); y -= STATIC_LINE_LENGTH * Math.cos(rad); }
      else if (cmd.type === 'back') { x -= STATIC_LINE_LENGTH * Math.sin(rad); y += STATIC_LINE_LENGTH * Math.cos(rad); }
      else if (cmd.type === 'right') { x += STATIC_LINE_LENGTH * Math.cos(rad); y += STATIC_LINE_LENGTH * Math.sin(rad); }
      else if (cmd.type === 'left') { x -= STATIC_LINE_LENGTH * Math.cos(rad); y -= STATIC_LINE_LENGTH * Math.sin(rad); }
    } 
    else if (cmd.type === 'go') {
      isMovement = true;
      const parts = String(cmd.val).split(' ');
      let localX = parseInt(parts[0]) || 0;
      let localY = parseInt(parts[1]) || 0;
      let dist = Math.sqrt(localX*localX + localY*localY);
      let moveX = 0, moveY = 0;
      if (dist > 0) {
        moveX = (localX / dist) * STATIC_LINE_LENGTH;
        moveY = (localY / dist) * STATIC_LINE_LENGTH;
      }
      x += (moveX * Math.cos(rad)) + (moveY * Math.sin(rad));
      y += (moveX * Math.sin(rad)) - (moveY * Math.cos(rad)); 
    } 
    else if (cmd.type === 'cw') { currentYaw += val; } 
    else if (cmd.type === 'ccw') { currentYaw -= val; } 

    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y);

    segments.push({
      id: cmd.id || idx, 
      stepNum: idx + 1, 
      type: cmd.type, 
      label: cmd.type.toUpperCase() + (val ? ` ${val}` : ''), 
      startX, startY, endX: x, endY: y, endYaw: currentYaw,
      midX: isMovement ? (startX + x) / 2 : x, 
      midY: isMovement ? (startY + y) / 2 : y,
      isMovement, isActive: props.activeIndex === idx + 1
    });
  });

  return { segments, minX, maxX, minY, maxY };
});

const hoveredSegmentData = computed(() => {
  if (hoveredSegId.value === null) return null;
  return visualData.value.segments.find(s => s.id === hoveredSegId.value);
});

watch(() => props.activeIndex, (newIdx) => {
  if (newIdx === 0 || (newIdx === -1 && props.queue.length === 0)) { 
    currentDronePos.value = { x: 0, y: 0 }; currentDroneYaw.value = 0; 
  } 
  else if (newIdx > 0 && visualData.value.segments[newIdx - 1]) {
    const activeSeg = visualData.value.segments[newIdx - 1];
    currentDronePos.value = { x: activeSeg.endX, y: activeSeg.endY };
    currentDroneYaw.value = activeSeg.endYaw;
  }
}, { immediate: true });

const svgViewBox = computed(() => {
  const { minX, maxX, minY, maxY } = visualData.value;
  const baseW = 2400;
  const baseH = 2400;
  const cx = ((maxX + minX) / 2) + panOffset.value.x;
  const cy = ((maxY + minY) / 2) + panOffset.value.y;
  const finalW = baseW * zoomMultiplier.value;
  const finalH = baseH * zoomMultiplier.value;
  return `${cx - finalW/2} ${cy - finalH/2} ${finalW} ${finalH}`;
});

const getOpacity = (segId) => {
  if (hoveredSegId.value !== null) return hoveredSegId.value === segId ? 1 : 0.3;
  if (selectedSegId.value !== null) return selectedSegId.value === segId ? 1 : 0.3;
  return 1; 
};
</script>

<template>
  <div 
    class="flex flex-col h-full bg-[#F8FAFC] relative z-0 overflow-hidden rounded-xl border border-slate-200"
    @wheel.prevent="handleWheel"
    @mousemove="handlePointerMove"
    @mousedown="handlePointerDown"
    @mouseup="handlePointerUp"
    @mouseleave="handlePointerUp"
    @touchstart.prevent="handlePointerDown"
    @touchmove.prevent="handlePointerMove"
    @touchend.prevent="handlePointerUp"
  >
    <div 
      v-if="hoveredSegmentData && !isDragging"
      class="fixed z-50 pointer-events-none transition-opacity duration-150 bg-white text-slate-800 px-5 py-4 rounded-xl shadow-xl border border-slate-200 w-auto min-w-[150px] backdrop-blur-md bg-white/90"
      :style="{ left: mousePos.x + 15 + 'px', top: mousePos.y + 15 + 'px' }"
    >
      <div class="text-xs font-black text-slate-400 uppercase tracking-wider mb-1">Step {{ hoveredSegmentData.stepNum }} of {{ queue.length }}</div>
      <div class="text-xl font-black text-[#658D1B] leading-tight">{{ hoveredSegmentData.label }}</div>
    </div>

    <div v-if="props.mode !== 'rc'" class="absolute top-4 left-4 z-10 bg-white/80 backdrop-blur-md px-3 py-2 rounded-lg border border-slate-200 shadow-sm flex items-center gap-2 pointer-events-none">
       <span class="relative flex h-2.5 w-2.5">
         <span v-if="props.isRunning" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#658D1B] opacity-75"></span>
         <span class="relative inline-flex rounded-full h-2.5 w-2.5" :class="props.isRunning ? 'bg-[#658D1B]' : 'bg-slate-300'"></span>
       </span>
       <span class="text-[10px] font-black text-slate-600 uppercase tracking-widest">Flight Map</span>
    </div>

    <div class="absolute top-4 right-4 z-10 flex flex-col items-center pointer-events-none opacity-60">
      <svg class="w-5 h-7 filter drop-shadow-sm" viewBox="0 0 24 32">
        <path d="M12 0 L18 16 L12 12 L6 16 Z" fill="#EF4444" />
        <path d="M12 32 L18 16 L12 12 L6 16 Z" fill="#94A3B8" />
      </svg>
      <span class="text-[10px] font-black text-slate-500 mt-1 uppercase tracking-widest">N</span>
    </div>

    <div v-if="props.isRunning && props.mode !== 'report'" class="absolute bottom-6 left-4 z-10">
      <button @click.stop="emit('emergency-land')" class="flex items-center gap-2 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-lg border border-red-500 transition-all active:scale-95">
        <span class="font-black text-xs uppercase tracking-widest">Emergency Land</span>
      </button>
    </div>

    <div v-if="props.mode !== 'report'" class="absolute bottom-6 right-4 z-10 flex flex-col bg-white/90 backdrop-blur-md rounded-xl border border-slate-200 shadow-lg overflow-hidden">
      <button @click="handleRecenter" class="p-2.5 text-slate-500 hover:text-[#658D1B] border-b border-slate-100"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg></button>
      <button @click="handleZoomIn" :disabled="zoomMultiplier <= MIN_ZOOM" class="p-2.5 text-slate-500 hover:text-[#658D1B] border-b border-slate-100 disabled:opacity-30"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg></button>
      <button @click="handleZoomReset" class="p-2.5 text-slate-400 hover:text-slate-700 border-b border-slate-100"><svg class="w-4 h-4 mx-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l-5 5m11 5l-5-5m5 5v-4m0 4h-4"></path></svg></button>
      <button @click="handleZoomOut" :disabled="zoomMultiplier >= MAX_ZOOM" class="p-2.5 text-slate-500 hover:text-[#658D1B] disabled:opacity-30"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M20 12H4"></path></svg></button>
    </div>

    <svg :viewBox="svgViewBox" class="w-full h-full" :class="isDragging ? 'cursor-grabbing' : 'cursor-grab'" @click="handleBackgroundClick">
      <defs>
        <pattern id="dotGrid" width="120" height="120" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="3" fill="#CBD5E1" opacity="0.6" /></pattern>
        <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#0F172A" flood-opacity="0.12" /></filter>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#658D1B" flood-opacity="0.4" /></filter>
      </defs>

      <rect x="-500000" y="-500000" width="1000000" height="1000000" fill="url(#dotGrid)" />
      <line x1="-500000" y1="0" x2="500000" y2="0" stroke="#E2E8F0" stroke-width="3" opacity="0.8" />
      <line x1="0" y1="-500000" x2="0" y2="500000" stroke="#E2E8F0" stroke-width="3" opacity="0.8" />

      <g 
        v-for="seg in visualData.segments" 
        :key="'group-'+seg.id"
        :opacity="getOpacity(seg.id)"
        class="transition-opacity duration-200 ease-in-out cursor-pointer"
        @mouseenter="hoveredSegId = seg.id"
        @mouseleave="hoveredSegId = null"
        @click.stop="handleSegmentClick(seg.id)"
      >
        <line 
          v-if="seg.isMovement"
          :x1="seg.startX" :y1="seg.startY" 
          :x2="seg.endX" :y2="seg.endY" 
          :stroke="seg.isActive ? '#658D1B' : ((selectedSegId === seg.id || hoveredSegId === seg.id) ? '#334155' : '#94A3B8')" 
          :stroke-width="(selectedSegId === seg.id || hoveredSegId === seg.id) || seg.isActive ? 24 : 16"
          stroke-linecap="round"
          :stroke-dasharray="seg.isActive ? 'none' : '15, 30'"
          :filter="seg.isActive ? 'url(#glow)' : ''"
        />
        
        <circle 
          v-if="seg.isMovement"
          :cx="seg.endX" :cy="seg.endY" 
          :r="(selectedSegId === seg.id || hoveredSegId === seg.id) || seg.isActive ? 20 : 16" 
          fill="#FFFFFF" 
          :stroke="seg.isActive ? '#658D1B' : ((selectedSegId === seg.id || hoveredSegId === seg.id) ? '#334155' : '#94A3B8')" 
          stroke-width="5"
          filter="url(#soft-shadow)"
        />
        <circle v-if="seg.isMovement && seg.isActive" :cx="seg.endX" :cy="seg.endY" r="8" fill="#658D1B" />

        <circle 
          v-if="!seg.isMovement"
          :cx="seg.endX" :cy="seg.endY" 
          :r="seg.isActive || (selectedSegId === seg.id || hoveredSegId === seg.id) ? 28 : 24" 
          :fill="seg.isActive ? '#F59E0B' : '#FFFFFF'" 
          :stroke="seg.isActive ? '#FFFFFF' : '#F59E0B'"
          stroke-width="4"
          filter="url(#soft-shadow)"
        />

        <g v-if="selectedSegId === seg.id" :transform="`translate(${seg.midX}, ${seg.midY})`">
          <g transform="translate(0, -62)" filter="url(#soft-shadow)">
            <path d="M-14 35 L14 35 L0 50 Z" fill="#334155" />
            
            <rect x="-120" y="-35" width="240" height="70" rx="35" fill="#334155" />
            
            <text 
              x="0" y="2" 
              font-size="40" font-weight="900" fill="#FFFFFF" 
              text-anchor="middle" alignment-baseline="middle"
              font-family="Inter, sans-serif" letter-spacing="1.5"
            >
              {{ seg.label }}
            </text>
          </g>
        </g>

      </g>

      <g :transform="`translate(${currentDronePos.x}, ${currentDronePos.y}) rotate(${currentDroneYaw}) scale(8)`" filter="url(#soft-shadow)">
        <DroneModel :isRunning="props.isRunning" />
      </g>
    </svg>
  </div>
</template>
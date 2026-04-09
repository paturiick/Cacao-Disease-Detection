<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  queue: { type: Array, default: () => [] },
  activeIndex: { type: Number, default: -1 },
  isRunning: { type: Boolean, default: false },
  mode: { type: String, default: 'plan' } 
});

// --- SCALE SETTINGS ---
const CM_TO_PX = 5; 

// --- STATE: POSITION & ZOOM ---
const currentDronePos = ref({ x: 0, y: 0 });
const currentDroneYaw = ref(0);
const zoomMultiplier = ref(1);
const MIN_ZOOM = 0.2; 
const MAX_ZOOM = 1.5; 

// --- STATE: PANNING & INTERACTION ---
const panOffset = ref({ x: 0, y: 0 });
const isDragging = ref(false);
let startDragPos = { x: 0, y: 0 };

// Tooltip State
const hoveredSegId = ref(null);
const mousePos = ref({ x: 0, y: 0 });

// --- INTERACTION ACTIONS ---
const handleZoomIn = () => { zoomMultiplier.value = Math.max(MIN_ZOOM, zoomMultiplier.value - 0.2); };
const handleZoomOut = () => { zoomMultiplier.value = Math.min(MAX_ZOOM, zoomMultiplier.value + 0.2); };
const handleZoomReset = () => { 
  zoomMultiplier.value = 1; 
  panOffset.value = { x: 0, y: 0 }; 
};

// NEW: Instantly snap the camera back to the drone's current position
const handleRecenter = () => {
  const { minX, maxX, minY, maxY } = visualData.value;
  const centerX = (maxX + minX) / 2;
  const centerY = (maxY + minY) / 2;
  
  // Calculate exactly how far off-center the drone is, and offset the pan to match
  panOffset.value = {
    x: currentDronePos.value.x - centerX,
    y: currentDronePos.value.y - centerY
  };
};

const handleWheel = (e) => {
  const zoomStep = 0.05; 
  if (e.deltaY < 0) zoomMultiplier.value = Math.max(MIN_ZOOM, zoomMultiplier.value - zoomStep);
  else if (e.deltaY > 0) zoomMultiplier.value = Math.min(MAX_ZOOM, zoomMultiplier.value + zoomStep);
};

// --- PANNING & MOUSE TRACKING LOGIC ---
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
  
  // Track mouse for tooltip positioning
  mousePos.value = { x: currentX, y: currentY };

  if (!isDragging.value) return;
  
  const dx = (currentX - startDragPos.x) * zoomMultiplier.value;
  const dy = (currentY - startDragPos.y) * zoomMultiplier.value;
  
  panOffset.value.x -= dx;
  panOffset.value.y -= dy;
  
  startDragPos = { x: currentX, y: currentY };
};

const handlePointerUp = () => {
  isDragging.value = false;
};

// --- DATA PROCESSING LOGIC ---
const visualData = computed(() => {
  let x = 0, y = 0, currentYaw = 0;
  const segments = [];
  let minX = 0, maxX = 0, minY = 0, maxY = 0;
  const nodeStackMap = {};

  props.queue.forEach((cmd, idx) => {
    let startX = x, startY = y;
    let val = Number(cmd.val) || 0;
    let pixelVal = val * CM_TO_PX; 
    let isMovement = false, unit = '', labelPrefix = cmd.type.toUpperCase();
    const rad = currentYaw * (Math.PI / 180);

    if (['forward', 'back', 'left', 'right'].includes(cmd.type)) {
      isMovement = true; unit = 'cm';
      if (cmd.type === 'forward') { x += pixelVal * Math.sin(rad); y -= pixelVal * Math.cos(rad); }
      else if (cmd.type === 'back') { x -= pixelVal * Math.sin(rad); y += pixelVal * Math.cos(rad); }
      else if (cmd.type === 'right') { x += pixelVal * Math.cos(rad); y += pixelVal * Math.sin(rad); }
      else if (cmd.type === 'left') { x -= pixelVal * Math.cos(rad); y -= pixelVal * Math.sin(rad); }
    } 
    else if (cmd.type === 'go') {
      isMovement = true;
      const parts = String(cmd.val).split(' ');
      let localX = (parseInt(parts[0]) || 0) * CM_TO_PX;
      let localY = (parseInt(parts[1]) || 0) * CM_TO_PX;
      x += (localX * Math.cos(rad)) + (localY * Math.sin(rad));
      y += (localX * Math.sin(rad)) - (localY * Math.cos(rad)); 
      labelPrefix = 'GO'; val = cmd.val;
    } 
    // NEW: Handle the 5th parameter for the RC Command
    else if (cmd.type === 'rc') {
      const parts = String(cmd.val).split(' ');
      const a = parts[0] || 0;
      const b = parts[1] || 0;
      const c = parts[2] || 0;
      const d = parts[3] || 0;
      const duration = parts[4] || 1; // Extract the 5th parameter for the label
      
      labelPrefix = 'RC';
      val = `[${a}, ${b}, ${c}, ${d}]`;
      unit = ` for ${duration}s`;
    }
    else if (cmd.type === 'cw') { currentYaw += val; unit = '°'; } 
    else if (cmd.type === 'ccw') { currentYaw -= val; unit = '°'; } 
    else {
      if (['up', 'down'].includes(cmd.type)) unit = 'cm';
      else if (cmd.type === 'hover') unit = 's';
    }

    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y);

    let labelText = labelPrefix;
    if (cmd.type === 'go') labelText = `GO ${cmd.val}`;
    else if (cmd.type === 'rc') labelText = `${labelPrefix} ${val}${unit}`;
    else if (val || unit) labelText = `${labelPrefix} ${val}${unit}`.trim();
    if (['takeoff', 'land', 'stop', 'hover'].includes(cmd.type)) labelText = cmd.type.toUpperCase();

    let textRotation = 0, textDy = 0; 

    if (isMovement) {
      textRotation = Math.atan2(y - startY, x - startX) * (180 / Math.PI);
      let normAngle = textRotation % 360;
      if (normAngle > 180) normAngle -= 360;
      if (normAngle <= -180) normAngle += 360;
      
      // INCREASED OFFSET FOR LARGER TEXT PILLS
      if (normAngle > 90 || normAngle < -90) { textRotation += 180; textDy = 28; } 
      else { textDy = -28; }
    } else {
      const key = `${Math.round(x)},${Math.round(y)}`;
      if (!nodeStackMap[key]) nodeStackMap[key] = 0;
      // INCREASED STACK OFFSET FOR LARGER TEXT PILLS
      textDy = 38 + (nodeStackMap[key] * 42); 
      nodeStackMap[key]++;
    }

    segments.push({
      id: cmd.id || idx, 
      stepNum: idx + 1, // Store step number for tooltip
      type: cmd.type, 
      label: labelText,
      startX, startY, endX: x, endY: y, endYaw: currentYaw,
      midX: isMovement ? (startX + x) / 2 : x, midY: isMovement ? (startY + y) / 2 : y,
      isMovement, isActive: props.activeIndex === idx + 1, textRotation, textDy
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
  const pad = 300; 
  const baseW = Math.max(800, maxX - minX);
  const baseH = Math.max(800, maxY - minY);
  
  const cx = ((maxX + minX) / 2) + panOffset.value.x;
  const cy = ((maxY + minY) / 2) + panOffset.value.y;
  
  const finalW = (baseW + pad * 2) * zoomMultiplier.value;
  const finalH = (baseH + pad * 2) * zoomMultiplier.value;
  return `${cx - finalW/2} ${cy - finalH/2} ${finalW} ${finalH}`;
});

// INCREASED BASE SCALE SO IT DOESN'T SHRINK AS MUCH WHEN ZOOMING OUT
const labelScale = computed(() => Math.max(1.2, zoomMultiplier.value * 1.5));

// Helper for hover styling
const getOpacity = (segId) => {
  if (hoveredSegId.value === null) return 1;
  return hoveredSegId.value === segId ? 1 : 0.3; // Dim others
};
</script>

<template>
  <div 
    class="flex flex-col h-full bg-[#F8FAFC] relative z-0 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.02)] border-l border-slate-200 rounded-r-lg"
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
      v-if="hoveredSegmentData"
      class="fixed z-50 pointer-events-none transition-opacity duration-150 bg-[#0F172A] text-white px-3 py-2 rounded-lg shadow-xl border border-slate-700 w-48"
      :style="{ left: mousePos.x + 15 + 'px', top: mousePos.y + 15 + 'px' }"
    >
      <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Step {{ hoveredSegmentData.stepNum }} of {{ queue.length }}</div>
      <div class="text-sm font-black text-[#84CC16] leading-tight mb-2">{{ hoveredSegmentData.label }}</div>
      <div class="flex flex-col gap-1 text-[10px] font-medium text-slate-300">
        <div class="flex justify-between">
          <span>Start:</span>
          <span class="font-mono">{{ Math.round(hoveredSegmentData.startX / CM_TO_PX) }}, {{ -Math.round(hoveredSegmentData.startY / CM_TO_PX) }}</span>
        </div>
        <div class="flex justify-between">
          <span>End:</span>
          <span class="font-mono">{{ Math.round(hoveredSegmentData.endX / CM_TO_PX) }}, {{ -Math.round(hoveredSegmentData.endY / CM_TO_PX) }}</span>
        </div>
      </div>
    </div>

    <div v-if="props.mode !== 'rc'" class="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-md px-3 py-2 rounded-full border border-slate-200 shadow-sm flex items-center gap-2 pointer-events-none">
       <span class="relative flex h-2 w-2">
         <span v-if="props.isRunning" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#658D1B] opacity-75"></span>
         <span class="relative inline-flex rounded-full h-2 w-2" :class="props.isRunning ? 'bg-[#658D1B]' : 'bg-slate-400'"></span>
       </span>
       <span class="text-[11px] font-black text-slate-700 uppercase tracking-widest">Drone Command Visualization</span>
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
      <button @click="handleRecenter" title="Recenter on Drone" class="p-2 text-slate-600 hover:bg-slate-100 hover:text-[#38BDF8] border-b border-slate-200 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
      </button>
      
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

    <svg 
      :viewBox="svgViewBox" 
      class="w-full h-full" 
      :class="isDragging ? 'cursor-grabbing' : 'cursor-grab'"
    >
      <defs>
        <pattern id="grid" width="200" height="200" patternUnits="userSpaceOnUse">
          <path d="M 200 0 L 0 0 0 200" fill="none" stroke="#E2E8F0" stroke-width="1.5" />
        </pattern>
      </defs>

      <rect x="-50000" y="-50000" width="100000" height="100000" fill="url(#grid)" />
      <line x1="-50000" y1="0" x2="50000" y2="0" stroke="#CBD5E1" stroke-width="3" opacity="0.6" />
      <line x1="0" y1="-50000" x2="0" y2="50000" stroke="#CBD5E1" stroke-width="3" opacity="0.6" />

      <g 
        v-for="seg in visualData.segments" 
        :key="'group-'+seg.id"
        :opacity="getOpacity(seg.id)"
        class="transition-opacity duration-200 ease-in-out cursor-pointer"
        @mouseenter="hoveredSegId = seg.id"
        @mouseleave="hoveredSegId = null"
      >
        <line 
          v-if="seg.isMovement"
          :x1="seg.startX" :y1="seg.startY" 
          :x2="seg.endX" :y2="seg.endY" 
          :stroke="seg.isActive ? '#658D1B' : '#0F172A'" 
          :stroke-width="hoveredSegId === seg.id || seg.isActive ? 4 : 2" 
        />
        
        <circle 
          v-if="seg.isMovement"
          :cx="seg.endX" :cy="seg.endY" 
          :r="hoveredSegId === seg.id ? 6 : 4.5" 
          fill="#FFFFFF" 
          :stroke="seg.isActive ? '#658D1B' : '#0F172A'" 
          stroke-width="2"
        />

        <circle 
          v-if="!seg.isMovement"
          :cx="seg.endX" :cy="seg.endY" 
          :r="seg.isActive || hoveredSegId === seg.id ? 12 : 6" 
          :fill="seg.isActive ? '#F59E0B' : '#E2E8F0'" 
          :stroke="seg.isActive ? '#FFF' : '#0F172A'"
          stroke-width="2"
        />

        <g :transform="`translate(${seg.midX}, ${seg.midY}) scale(${labelScale}) rotate(${seg.textRotation || 0})`">
          <rect 
            :x="-(seg.label.length * 5) - 16" :y="seg.textDy - 18" 
            :width="(seg.label.length * 10) + 32" height="36" rx="18" 
            :fill="seg.isActive ? '#658D1B' : (hoveredSegId === seg.id ? '#1E293B' : '#0F172A')" 
            fill-opacity="1" stroke="#FFFFFF" stroke-width="2.5"
          />
          <text 
            x="0" :y="seg.textDy + 5" 
            font-size="16" font-weight="900" fill="#FFFFFF" text-anchor="middle" font-family="Inter, sans-serif" letter-spacing="0.5"
          >
            {{ seg.label }}
          </text>
        </g>
      </g>

      <g>
        <circle cx="0" cy="0" r="5" fill="#EF4444" />
      </g>

      <g :transform="`translate(${currentDronePos.x}, ${currentDronePos.y}) rotate(${currentDroneYaw})`" class="transition-transform duration-[1200ms] ease-in-out pointer-events-none">
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
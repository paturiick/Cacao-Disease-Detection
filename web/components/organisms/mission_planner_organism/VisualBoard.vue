<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  queue: { type: Array, default: () => [] },
  activeIndex: { type: Number, default: -1 },
  isRunning: { type: Boolean, default: false }
});

// --- STATE FOR DRONE POSITION & YAW ---
// Tracked separately from the path so the drone can pause mid-air on emergency stop
const currentDronePos = ref({ x: 0, y: 0 });
const currentDroneYaw = ref(0);

// --- DRONE VISUALIZATION LOGIC ---
const visualData = computed(() => {
  let x = 0;
  let y = 0;
  let currentYaw = 0; // Starts facing North (0 degrees)
  const segments = [];
  
  // Track boundaries to dynamically zoom the camera
  let minX = 0, maxX = 0, minY = 0, maxY = 0;

  props.queue.forEach((cmd, idx) => {
    let startX = x;
    let startY = y;
    let val = Number(cmd.val) || 0;
    let isMovement = false;
    let unit = '';
    let labelPrefix = cmd.type.toUpperCase();

    // Convert yaw from degrees to radians for JS Math functions
    const rad = currentYaw * (Math.PI / 180);

    // Map Relative Directions based on current Yaw
    if (['forward', 'back', 'left', 'right'].includes(cmd.type)) {
      isMovement = true;
      unit = 'cm';
      
      // Standard local vectors projected onto the global map via Rotation Matrix
      if (cmd.type === 'forward') {
        x += val * Math.sin(rad);
        y -= val * Math.cos(rad); // SVG Y is inverted
      } else if (cmd.type === 'back') {
        x -= val * Math.sin(rad);
        y += val * Math.cos(rad);
      } else if (cmd.type === 'right') {
        x += val * Math.cos(rad);
        y += val * Math.sin(rad);
      } else if (cmd.type === 'left') {
        x -= val * Math.cos(rad);
        y -= val * Math.sin(rad);
      }
    } 
    else if (cmd.type === 'go') {
      isMovement = true;
      const parts = String(cmd.val).split(' ');
      let localX = parseInt(parts[0]) || 0; // Relative Right/Left
      let localY = parseInt(parts[1]) || 0; // Relative Forward/Back
      
      x += (localX * Math.cos(rad)) + (localY * Math.sin(rad));
      y += (localX * Math.sin(rad)) - (localY * Math.cos(rad)); 
      
      labelPrefix = 'GO';
      val = cmd.val;
    } 
    else if (cmd.type === 'cw') {
      currentYaw += val; // Rotate Right
      unit = '°';
    } 
    else if (cmd.type === 'ccw') {
      currentYaw -= val; // Rotate Left
      unit = '°';
    } 
    else {
      // In-place commands (Hover, Up, Down)
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

// --- DRONE MOVEMENT TRACKER ---
watch(() => props.activeIndex, (newIdx) => {
  if (newIdx === 0) {
    currentDronePos.value = { x: 0, y: 0 };
    currentDroneYaw.value = 0;
  } 
  else if (newIdx > 0 && visualData.value.segments[newIdx - 1]) {
    const activeSeg = visualData.value.segments[newIdx - 1];
    currentDronePos.value = { x: activeSeg.endX, y: activeSeg.endY };
    currentDroneYaw.value = activeSeg.endYaw; // Turn the drone to match the completed step
  }
  else if (newIdx === -1 && props.queue.length === 0) {
    currentDronePos.value = { x: 0, y: 0 };
    currentDroneYaw.value = 0;
  }
}, { immediate: true });


// --- DYNAMIC CAMERA FRAMING ---
const svgViewBox = computed(() => {
  const { minX, maxX, minY, maxY } = visualData.value;
  const pad = 150; 
  
  const w = Math.max(400, maxX - minX);
  const h = Math.max(400, maxY - minY);
  const cx = (maxX + minX) / 2;
  const cy = (maxY + minY) / 2;
  
  return `${cx - w/2 - pad} ${cy - h/2 - pad} ${w + pad*2} ${h + pad*2}`;
});
</script>

<template>
  <div class="flex flex-col h-full bg-[#F8FAFC] relative z-0 overflow-hidden shadow-[inset_0_0_20px_rgba(0,0,0,0.02)] border-l border-slate-200 rounded-r-lg">
    
    <div class="absolute top-4 left-4 z-10 bg-white/90 backdrop-blur-md px-3 py-2 rounded-lg border border-slate-200 shadow-sm flex items-center gap-2 pointer-events-none">
       <span class="relative flex h-2 w-2">
         <span v-if="props.isRunning" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#658D1B] opacity-75"></span>
         <span class="relative inline-flex rounded-full h-2 w-2" :class="props.isRunning ? 'bg-[#658D1B]' : 'bg-slate-400'"></span>
       </span>
       <span class="text-[10px] font-black text-slate-700 uppercase tracking-widest">Live Map Visualizer</span>
    </div>

    <div class="absolute top-4 right-4 z-10 flex flex-col items-center pointer-events-none opacity-80">
      <svg class="w-6 h-8 filter drop-shadow-md" viewBox="0 0 24 32">
        <path d="M12 0 L18 16 L12 12 L6 16 Z" fill="#EF4444" />
        <path d="M12 32 L18 16 L12 12 L6 16 Z" fill="#CBD5E1" />
        <circle cx="12" cy="14" r="2" fill="white" />
      </svg>
      <span class="text-[11px] font-black text-slate-600 mt-1 uppercase tracking-widest">N</span>
    </div>

    <svg :viewBox="svgViewBox" class="w-full h-full transition-all duration-700 ease-[cubic-bezier(0.4,0,0.2,1)] cursor-crosshair">
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
          :stroke-width="seg.isActive ? 4 : 3" 
          stroke-linecap="round"
          class="transition-colors duration-300"
        />
        
        <circle 
          v-if="!seg.isMovement"
          :cx="seg.endX" :cy="seg.endY" 
          :r="seg.isActive ? 10 : 6" 
          :fill="seg.isActive ? '#F59E0B' : '#E2E8F0'" 
          :stroke="seg.isActive ? '#FFF' : '#94A3B8'"
          stroke-width="2"
          class="transition-all duration-300"
        />

        <g :transform="`translate(${seg.midX}, ${seg.isMovement ? seg.midY : seg.midY + 20})`">
          <rect x="-30" y="-10" width="60" height="20" rx="10" fill="white" fill-opacity="0.85" stroke="#E2E8F0" stroke-width="1" />
          <text x="0" y="3" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle" font-family="Inter, sans-serif">
            {{ seg.label }}
          </text>
        </g>
      </g>

      <g>
        <circle cx="0" cy="0" r="5" fill="#EF4444" />
        <circle cx="0" cy="0" r="14" fill="none" stroke="#EF4444" stroke-width="1.5" opacity="0.4" />
        <text x="0" y="-20" font-size="10" font-weight="bold" fill="#EF4444" text-anchor="middle" font-family="Inter, sans-serif" letter-spacing="1">ORIGIN</text>
      </g>

      <g :transform="`translate(${currentDronePos.x}, ${currentDronePos.y}) rotate(${currentDroneYaw})`" class="transition-transform duration-[1200ms] ease-in-out">
        <ellipse cx="0" cy="12" rx="18" ry="6" fill="rgba(0,0,0,0.08)" />
        
        <g>
          <circle v-if="props.isRunning" cx="0" cy="0" r="22" fill="#84CC16" opacity="0.15" class="animate-pulse" />
          
          <path d="M-12,-12 L12,12 M-12,12 L12,-12" stroke="#CBD5E1" stroke-width="5" stroke-linecap="round" />
          
          <circle cx="-14" cy="-14" r="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <circle cx="14" cy="-14" r="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <circle cx="-14" cy="14" r="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          <circle cx="14" cy="14" r="6" fill="#F8FAFC" stroke="#94A3B8" stroke-width="2" />
          
          <circle cx="-14" cy="-14" r="2" fill="#658D1B" />
          <circle cx="14" cy="-14" r="2" fill="#658D1B" />
          <circle cx="-14" cy="14" r="2" fill="#334155" />
          <circle cx="14" cy="14" r="2" fill="#334155" />

          <rect x="-10" y="-10" width="20" height="20" rx="8" fill="#ffffff" stroke="#658D1B" stroke-width="2.5" />
          
          <circle cx="0" cy="-4" r="3.5" fill="#0F172A" />
          <circle cx="1" cy="-5" r="1.5" fill="#38BDF8" /> 
        </g>
      </g>
    </svg>
  </div>
</template>
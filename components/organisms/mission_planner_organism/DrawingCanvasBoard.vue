<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({ initialLines: { type: Array, default: () => [] } });
const emit = defineEmits(['update-path']);

const canvasRef = ref(null);
const lines = ref([]); 
const isDrawing = ref(false);
const startPt = ref(null);
const currentPt = ref(null);

// Sync lines from manual mode
watch(() => props.initialLines, (newVal) => {
  lines.value = [...newVal];
  draw();
}, { deep: true });

const draw = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw Grid
  ctx.strokeStyle = '#f1f5f9';
  ctx.lineWidth = 1;
  for (let i = 0; i < canvas.width; i += 20) {
    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
  }

  // Draw Lines
  ctx.strokeStyle = '#40623F';
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  lines.value.forEach(line => {
    ctx.beginPath();
    ctx.moveTo(line.x1, line.y1);
    ctx.lineTo(line.x2, line.y2);
    ctx.stroke();
  });

  // Draw Ortho Preview (Dashed)
  if (isDrawing.value && startPt.value && currentPt.value) {
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(startPt.value.x, startPt.value.y);
    ctx.lineTo(currentPt.value.x, currentPt.value.y);
    ctx.stroke();
    ctx.setLineDash([]);
  }
};

const getMousePos = (evt) => {
  const rect = canvasRef.value.getBoundingClientRect();
  return { x: evt.clientX - rect.left, y: evt.clientY - rect.top };
};

const startDraw = (e) => {
  // Continuous Drawing: Start at the end of the last line if it exists
  startPt.value = lines.value.length > 0 
    ? { x: lines.value[lines.value.length - 1].x2, y: lines.value[lines.value.length - 1].y2 } 
    : getMousePos(e);
  isDrawing.value = true;
};

const drawMove = (e) => {
  if (!isDrawing.value) return;
  const pos = getMousePos(e);
  
  // ORTHO LOGIC: Snap to largest displacement
  const dx = Math.abs(pos.x - startPt.value.x);
  const dy = Math.abs(pos.y - startPt.value.y);
  
  if (dx > dy) currentPt.value = { x: pos.x, y: startPt.value.y }; // Horizontal
  else currentPt.value = { x: startPt.value.x, y: pos.y }; // Vertical
  draw();
};

const endDraw = () => {
  if (!isDrawing.value || !currentPt.value) return;
  
  // Prevent zero-length dots
  if (startPt.value.x !== currentPt.value.x || startPt.value.y !== currentPt.value.y) {
    lines.value.push({
      x1: startPt.value.x, y1: startPt.value.y,
      x2: currentPt.value.x, y2: currentPt.value.y
    });
    emit('update-path', lines.value);
  }
  isDrawing.value = false;
  currentPt.value = null;
  draw();
};

const undo = () => {
  if (lines.value.length === 0) return;
  lines.value.pop();
  emit('update-path', lines.value);
  draw();
};

onMounted(() => draw());
</script>

<template>
  <div class="relative w-full aspect-video border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
    <canvas
      ref="canvasRef"
      width="600"
      height="400"
      class="w-full h-full cursor-crosshair"
      @mousedown="startDraw"
      @mousemove="drawMove"
      @mouseup="endDraw"
      @mouseleave="endDraw"
    ></canvas>
    
    <button 
      @click="undo" 
      :disabled="lines.length === 0"
      class="absolute bottom-3 right-3 bg-white border border-gray-200 shadow-sm rounded px-3 py-1.5 text-xs font-bold text-gray-600 hover:text-[#40623F] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 transition-colors z-10"
    >
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path></svg>
      Undo
    </button>
  </div>
</template>
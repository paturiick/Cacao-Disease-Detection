<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

// Import Atomic Components
import UndoButton from '~/components/atoms/UndoButton.vue';
import DrawingCommandPrompt from '~/components/molecules/mission_plan_molecules/DrawingCommandPrompt.vue';

const props = defineProps({
  initialLines: { type: Array, default: () => [] },
  commandOptions: { type: Array, default: () => [] } 
});
const emit = defineEmits(['update-path']);

const containerRef = ref(null);
const canvasRef = ref(null);
const lines = ref([]); 
const isDrawing = ref(false);
const startPt = ref(null);
const currentPt = ref(null);
const mousePos = ref({ x: 0, y: 0 });

// --- RESPONSIVE SCALING LOGIC ---
const canvasScale = ref(1);
const GRID_SIZE = 600; // Fixed virtual coordinate system

let resizeObserver = null;

const handleResize = () => {
  if (!containerRef.value || !canvasRef.value) return;

  const rect = containerRef.value.getBoundingClientRect();
  const availableSpace = Math.min(rect.width, rect.height) - 10; 
  canvasScale.value = availableSpace / GRID_SIZE;
};

onMounted(() => {
  resizeObserver = new ResizeObserver(handleResize);
  resizeObserver.observe(containerRef.value);
  handleResize();
  draw();
});

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect();
});


// --- MODAL / PROMPT STATE ---
const showPrompt = ref(false);
const promptPosition = ref({ top: '0px', left: '0px' });
const pendingLine = ref(null); 
const promptType = ref('line'); 

const draftCommand = ref('');
const draftValue = ref('');

const filteredCommandOptions = computed(() => {
  if (promptType.value === 'point') {
    return props.commandOptions.filter(opt => ['up', 'down', 'hover', 'cw', 'ccw'].includes(opt.value));
  } else {
    return props.commandOptions.filter(opt => ['forward', 'back', 'left', 'right'].includes(opt.value));
  }
});

// --- 3x3 TREE GRID SETUP ---
const TREE_RADIUS = 20;
const SNAP_SIZE = 50; 
const TREES = [];

for (let r = 1; r <= 3; r++) {
  for (let c = 1; c <= 3; c++) {
    TREES.push({ x: c * 150, y: r * 150, r: TREE_RADIUS });
  }
}

const INITIAL_START_PT = { x: 50, y: 100 };

watch(() => props.initialLines, (newVal) => {
  lines.value = [...newVal];
  draw();
}, { deep: true });


// --- DRAWING LOGIC ---
const draw = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  // Clear entire 600x600 space
  ctx.clearRect(0, 0, GRID_SIZE, GRID_SIZE);

  // Background
  ctx.fillStyle = '#fafafa';
  ctx.fillRect(0, 0, GRID_SIZE, GRID_SIZE);

  // Drafting Grid
  ctx.strokeStyle = '#e2e8f0'; 
  ctx.lineWidth = 1;
  ctx.setLineDash([2, 4]);
  for (let i = 0; i <= GRID_SIZE; i += SNAP_SIZE) {
    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, GRID_SIZE); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(GRID_SIZE, i); ctx.stroke();
  }
  ctx.setLineDash([]); 

  // Start Marker
  drawStartMarker(ctx);

  // Trees
  TREES.forEach(tree => {
    ctx.shadowColor = 'rgba(34, 197, 94, 0.2)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 2;

    ctx.beginPath(); 
    ctx.arc(tree.x, tree.y, tree.r, 0, Math.PI * 2);
    ctx.fillStyle = '#f0fdf4'; 
    ctx.fill();
    
    ctx.shadowBlur = 0;
    ctx.shadowColor = 'transparent';
    
    ctx.strokeStyle = '#86efac'; 
    ctx.lineWidth = 2; 
    ctx.stroke();

    ctx.beginPath(); 
    ctx.arc(tree.x, tree.y, tree.r * 0.35, 0, Math.PI * 2);
    ctx.fillStyle = '#22c55e'; 
    ctx.fill();
  });

  // Committed Lines
  lines.value.forEach(line => {
    if (line.isPoint) {
      drawPointMarker(ctx, line.x1, line.y1, '#f59e0b', '#fef3c7'); 
    } else if (line.x1 !== undefined) {
      ctx.strokeStyle = '#0F2830'; 
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      
      ctx.shadowColor = 'rgba(15, 40, 48, 0.15)';
      ctx.shadowBlur = 4;
      ctx.shadowOffsetY = 2;

      ctx.beginPath();
      ctx.moveTo(line.x1, line.y1);
      ctx.lineTo(line.x2, line.y2);
      ctx.stroke();
      
      ctx.shadowBlur = 0; 
    }
    drawLabel(ctx, line); 
  });

  // Ortho Preview Line
  if (isDrawing.value && startPt.value && currentPt.value) {
    ctx.setLineDash([5, 5]);
    ctx.strokeStyle = '#84cc16'; 
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(startPt.value.x, startPt.value.y);
    ctx.lineTo(currentPt.value.x, currentPt.value.y);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Pending Line 
  if (showPrompt.value && pendingLine.value) {
    if (pendingLine.value.isPoint) {
      drawPointMarker(ctx, pendingLine.value.x1, pendingLine.value.y1, '#f59e0b', '#fef3c7');
    } else {
      ctx.strokeStyle = '#eab308'; 
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(pendingLine.value.x1, pendingLine.value.y1);
      ctx.lineTo(pendingLine.value.x2, pendingLine.value.y2);
      ctx.stroke();
    }
  }
  
  // Hover Reticle
  if (!isDrawing.value && !showPrompt.value && mousePos.value.x > 0) {
    ctx.beginPath();
    ctx.arc(mousePos.value.x, mousePos.value.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(101, 141, 27, 0.5)'; 
    ctx.fill();
  }
};

const drawStartMarker = (ctx) => {
  ctx.beginPath();
  ctx.arc(INITIAL_START_PT.x, INITIAL_START_PT.y, 12, 0, Math.PI * 2);
  ctx.fillStyle = '#fecaca'; 
  ctx.fill();
  
  ctx.beginPath();
  ctx.arc(INITIAL_START_PT.x, INITIAL_START_PT.y, 5, 0, Math.PI * 2);
  ctx.fillStyle = '#ef4444'; 
  ctx.fill();
  
  ctx.font = "bold 9px Inter, sans-serif";
  ctx.fillStyle = "#ef4444";
  ctx.textAlign = "center";
  ctx.letterSpacing = "1px";
  ctx.fillText("START", INITIAL_START_PT.x, INITIAL_START_PT.y - 18);
};

const drawPointMarker = (ctx, x, y, innerFill, outerFill) => {
  ctx.beginPath();
  ctx.arc(x, y, 10, 0, Math.PI * 2);
  ctx.fillStyle = outerFill;
  ctx.fill();
  
  ctx.beginPath();
  ctx.arc(x, y, 4, 0, Math.PI * 2);
  ctx.fillStyle = innerFill;
  ctx.fill();
};

const drawLabel = (ctx, line) => {
  if (!line.command) return; 
  
  const midX = (line.x1 + line.x2) / 2;
  const midY = ((line.y1 + line.y2) / 2) - (line.isPoint ? 20 : 0); 
  
  const option = props.commandOptions.find(o => o.value === line.command);
  const labelPrefix = option ? option.label.replace('Fly ', '').replace('Rotate ', '') : line.command;
  const unit = option ? option.unit : '';
  const text = `${labelPrefix} ${line.val}${unit}`;

  ctx.save();
  ctx.font = "bold 10px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const textWidth = ctx.measureText(text).width;
  
  ctx.shadowColor = 'rgba(0, 0, 0, 0.05)';
  ctx.shadowBlur = 4;
  ctx.shadowOffsetY = 2;
  
  ctx.fillStyle = "rgba(255, 255, 255, 0.95)"; 
  ctx.beginPath();
  ctx.roundRect(midX - textWidth / 2 - 8, midY - 10, textWidth + 16, 20, 10); 
  ctx.fill();
  
  ctx.shadowColor = 'transparent';
  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.fillStyle = line.isPoint ? "#b45309" : "#334155"; 
  ctx.fillText(text, midX, midY);
  ctx.restore();
};

// --- MOUSE MAPPER ---
const getMousePos = (evt) => {
  const canvas = canvasRef.value;
  const rect = canvas.getBoundingClientRect();
  
  // Calculate raw mouse position relative to the scaled canvas
  let rawX = (evt.clientX - rect.left) / canvasScale.value;
  let rawY = (evt.clientY - rect.top) / canvasScale.value;
  
  let x = Math.round(rawX / SNAP_SIZE) * SNAP_SIZE;
  let y = Math.round(rawY / SNAP_SIZE) * SNAP_SIZE;

  // Clamp to 600x600 bounds
  x = Math.max(0, Math.min(GRID_SIZE, x));
  y = Math.max(0, Math.min(GRID_SIZE, y));
  
  return { x, y };
};

const preventTreeCollision = (start, end) => {
  let safeEnd = { ...end };
  const buffer = 5; 
  for (const tree of TREES) {
    const obstacleSize = tree.r + buffer;
    if (start.y === end.y) { 
      if (Math.abs(start.y - tree.y) < obstacleSize) {
        if (Math.min(start.x, end.x) <= tree.x && tree.x <= Math.max(start.x, end.x)) {
           if (end.x > start.x) safeEnd.x = Math.min(safeEnd.x, tree.x - obstacleSize); 
           else safeEnd.x = Math.max(safeEnd.x, tree.x + obstacleSize); 
           safeEnd.x = end.x > start.x ? Math.floor(safeEnd.x / SNAP_SIZE) * SNAP_SIZE : Math.ceil(safeEnd.x / SNAP_SIZE) * SNAP_SIZE;
        }
      }
    } else if (start.x === end.x) { 
      if (Math.abs(start.x - tree.x) < obstacleSize) { 
        if (Math.min(start.y, end.y) <= tree.y && tree.y <= Math.max(start.y, end.y)) {
           if (end.y > start.y) safeEnd.y = Math.min(safeEnd.y, tree.y - obstacleSize); 
           else safeEnd.y = Math.max(safeEnd.y, tree.y + obstacleSize); 
           safeEnd.y = end.y > start.y ? Math.floor(safeEnd.y / SNAP_SIZE) * SNAP_SIZE : Math.ceil(safeEnd.y / SNAP_SIZE) * SNAP_SIZE;
        }
      }
    }
  }
  return safeEnd;
};

// --- HANDLERS ---
const handleHover = (e) => {
  if (showPrompt.value || isDrawing.value) return;
  mousePos.value = getMousePos(e);
  draw();
};

const handleLeave = () => {
  if (isDrawing.value) {
    endDraw();
  }
  mousePos.value = { x: 0, y: 0 };
  draw();
};

const startDraw = (e) => {
  if (showPrompt.value) return; 

  startPt.value = lines.value.length > 0 
    ? { x: lines.value[lines.value.length - 1].x2, y: lines.value[lines.value.length - 1].y2 } 
    : { ...INITIAL_START_PT };
  isDrawing.value = true;
};

const drawMove = (e) => {
  if (!isDrawing.value) {
    handleHover(e);
    return;
  }
  const pos = getMousePos(e);
  
  const dx = Math.abs(pos.x - startPt.value.x);
  const dy = Math.abs(pos.y - startPt.value.y);
  
  let nextPt = { ...pos };
  if (dx > dy) nextPt.y = startPt.value.y; 
  else nextPt.x = startPt.value.x; 

  currentPt.value = preventTreeCollision(startPt.value, nextPt);
  draw();
};

const endDraw = () => {
  if (!isDrawing.value) return;
  
  if (!currentPt.value || (startPt.value.x === currentPt.value.x && startPt.value.y === currentPt.value.y)) {
    pendingLine.value = { x1: startPt.value.x, y1: startPt.value.y, x2: startPt.value.x, y2: startPt.value.y, isPoint: true };
    promptType.value = 'point';
    openPrompt();
  } else {
    pendingLine.value = { x1: startPt.value.x, y1: startPt.value.y, x2: currentPt.value.x, y2: currentPt.value.y, isPoint: false };
    promptType.value = 'line';
    openPrompt();
  }
  
  isDrawing.value = false;
  currentPt.value = null;
  draw();
};

// --- MODAL HANDLERS ---
const openPrompt = () => {
  showPrompt.value = true;
  draftCommand.value = '';
  draftValue.value = '';
  
  const wrapperRect = containerRef.value.getBoundingClientRect();
  const canvasRect = canvasRef.value.getBoundingClientRect();
  
  // Calculate prompt position relative to the wrapper, based on scaled canvas
  let screenX = (pendingLine.value.x2 * canvasScale.value) + (canvasRect.left - wrapperRect.left);
  let screenY = (pendingLine.value.y2 * canvasScale.value) + (canvasRect.top - wrapperRect.top);

  let left = screenX + 15;
  let top = screenY - 10;
  
  // Boundary constraints so modal doesn't get cut off
  if (left > wrapperRect.width - 200) left = wrapperRect.width - 220; 
  if (top > wrapperRect.height - 150) top = wrapperRect.height - 160; 
  if (top < 10) top = 10;
  if (left < 10) left = 10;
  
  promptPosition.value = { top: `${top}px`, left: `${left}px` };
};

const confirmCommand = () => {
  if (!draftCommand.value || !draftValue.value) return;
  lines.value.push({ ...pendingLine.value, command: draftCommand.value, val: draftValue.value });
  emit('update-path', lines.value); 
  cancelCommand();
};

const cancelCommand = () => {
  showPrompt.value = false;
  pendingLine.value = null;
  draw();
};

const undo = () => {
  if (lines.value.length === 0) return;
  lines.value.pop();
  emit('update-path', lines.value);
  draw();
};
</script>

<template>
  <div 
    ref="containerRef"
    class="relative w-full h-full flex-1 flex items-center justify-center border border-gray-200 rounded-xl overflow-hidden bg-[#fafafa] shadow-inner touch-none"
    @wheel.prevent
    @touchmove.prevent
  >
    <canvas
      ref="canvasRef"
      width="600"
      height="600"
      class="block bg-white rounded-lg shadow-sm origin-center transition-transform duration-75"
      :style="{ transform: `scale(${canvasScale})` }"
      :class="showPrompt ? 'cursor-default' : 'cursor-crosshair'"
      @mousedown="startDraw"
      @mousemove="drawMove"
      @mouseup="endDraw"
      @mouseleave="handleLeave"
    ></canvas>

    <DrawingCommandPrompt
      v-if="showPrompt"
      :position="promptPosition"
      :options="filteredCommandOptions"
      v-model:command="draftCommand"
      v-model:value="draftValue"
      @save="confirmCommand"
      @cancel="cancelCommand"
    />

    <UndoButton 
      :disabled="lines.length === 0 || showPrompt"
      @click="undo"
    />
  </div>
</template>
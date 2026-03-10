<script setup>
import { ref } from 'vue';

const emit = defineEmits(['command-generated']);

const isDrawing = ref(false);
const lines = ref([]);
const currentLine = ref(null);
const PIXELS_PER_METER = 50; 

const startDrawing = (e) => {
  isDrawing.value = true;
  currentLine.value = { x1: e.offsetX, y1: e.offsetY, x2: e.offsetX, y2: e.offsetY };
};

const draw = (e) => {
  if (!isDrawing.value) return;
  currentLine.value.x2 = e.offsetX;
  currentLine.value.y2 = e.offsetY;
};

const stopDrawing = () => {
  if (!isDrawing.value) return;
  isDrawing.value = false;
  
  const line = { ...currentLine.value };
  lines.value.push(line);
  
  const deltaX = line.x2 - line.x1;
  const deltaY = line.y2 - line.y1;
  
  const meters = (Math.sqrt(deltaX * deltaX + deltaY * deltaY) / PIXELS_PER_METER).toFixed(1);
  let degrees = Math.atan2(deltaY, deltaX) * (180 / Math.PI) + 90;
  if (degrees < 0) degrees += 360;
  
  emit('command-generated', {
    id: Date.now(),
    type: 'MOVE',
    distance: Number(meters),
    degrees: Math.round(degrees)
  });
  
  currentLine.value = null;
};
</script>

<template>
  <div class="canvas-container">
    <div class="tree-grid">
      <div v-for="i in 9" :key="i" class="tree-cell">🌲</div>
    </div>
    <svg 
      class="drawing-layer"
      @mousedown="startDrawing" @mousemove="draw"
      @mouseup="stopDrawing" @mouseleave="stopDrawing"
    >
      <line v-for="(line, idx) in lines" :key="idx"
        :x1="line.x1" :y1="line.y1" :x2="line.x2" :y2="line.y2"
        stroke="#40623F" stroke-width="6" stroke-linecap="round" />
      <line v-if="currentLine"
        :x1="currentLine.x1" :y1="currentLine.y1" :x2="currentLine.x2" :y2="currentLine.y2"
        stroke="#88B04B" stroke-width="6" stroke-dasharray="8,8" stroke-linecap="round" />
    </svg>
  </div>
</template>

<style scoped>
.canvas-container {
  position: relative; width: 450px; height: 450px;
  background: #E4EDD2; border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.tree-grid { display: grid; grid-template-columns: repeat(3, 1fr); height: 100%; }
.tree-cell { display: flex; align-items: center; justify-content: center; font-size: 2.5rem; border: 1px dashed rgba(64,98,63,0.1); opacity: 0.7; }
.drawing-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: crosshair; }
</style>
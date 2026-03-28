<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';

const props = defineProps({
  forcedX: { type: Number, default: 0 },
  forcedY: { type: Number, default: 0 }
});

const emit = defineEmits(['update']);
const joystickZone = ref(null);
const knob = ref(null);

const position = ref({ x: 0, y: 0 });
const mappedValue = ref({ x: 0, y: 0 });
let isDragging = false;
let maxRadius = 50; // Max drag distance in pixels

// NEW: Watch for keyboard inputs and physically move the knob
watch(() => [props.forcedX, props.forcedY], ([newX, newY]) => {
  // Only auto-move if the user isn't currently dragging it with their mouse
  if (!isDragging) {
    position.value = {
      x: (newX / 100) * maxRadius,
      y: -(newY / 100) * maxRadius // Invert Y so UP visually goes UP
    };
  }
});

const calculatePosition = (clientX, clientY) => {
  const rect = joystickZone.value.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;

  let dx = clientX - centerX;
  let dy = clientY - centerY;
  const distance = Math.sqrt(dx * dx + dy * dy);

  if (distance > maxRadius) {
    const ratio = maxRadius / distance;
    dx *= ratio;
    dy *= ratio;
  }

  position.value = { x: dx, y: dy };
  
  mappedValue.value = {
    x: Math.round((dx / maxRadius) * 100),
    y: Math.round(-(dy / maxRadius) * 100)
  };
  
  emit('update', mappedValue.value);
};

const handlePointerDown = (e) => {
  isDragging = true;
  calculatePosition(e.clientX, e.clientY);
  document.body.style.userSelect = 'none'; 
};

const handlePointerMove = (e) => {
  if (!isDragging) return;
  calculatePosition(e.clientX, e.clientY);
};

const handlePointerUp = () => {
  if (isDragging) {
    isDragging = false;
    position.value = { x: 0, y: 0 };
    mappedValue.value = { x: 0, y: 0 };
    emit('update', mappedValue.value);
    document.body.style.userSelect = '';
  }
};

onMounted(() => {
  document.addEventListener('pointermove', handlePointerMove);
  document.addEventListener('pointerup', handlePointerUp);
});

onBeforeUnmount(() => {
  document.removeEventListener('pointermove', handlePointerMove);
  document.removeEventListener('pointerup', handlePointerUp);
});
</script>

<template>
  <div class="flex flex-col items-center">
    <div 
      ref="joystickZone"
      @pointerdown.prevent="handlePointerDown"
      class="w-32 h-32 rounded-full bg-slate-100 border-2 border-slate-200 shadow-inner relative flex items-center justify-center cursor-pointer touch-none"
    >
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
        <div class="w-full h-[1px] bg-slate-400"></div>
        <div class="absolute h-full w-[1px] bg-slate-400"></div>
      </div>

      <div 
        ref="knob"
        :style="{ transform: `translate(${position.x}px, ${position.y}px)` }"
        class="w-12 h-12 rounded-full bg-[#0F172A] shadow-[0_4px_10px_rgba(0,0,0,0.3)] border-2 border-slate-600 transition-transform duration-75 ease-out flex items-center justify-center"
      >
        <div class="w-4 h-4 rounded-full bg-slate-600 opacity-50"></div>
      </div>
    </div>
  </div>
</template>
<script setup>
defineProps({
  label: String,
  value: [String, Number],
  unit: { type: String, default: '' },
  barColor: { type: String, default: 'bg-[#658D1B]' }, // Tailwind class
  percent: { type: Number, default: 0 } // For progress bar width
});
</script>

<template>
  <div class="bg-white/95 backdrop-blur-sm p-5 rounded-lg shadow-sm border border-gray-100 flex flex-col justify-between h-[120px]">
    <div class="flex items-center gap-2 text-gray-500">
        <slot name="icon"></slot>
        <p class="text-xs font-bold uppercase tracking-wide">{{ label }}</p>
    </div>
    <p class="text-2xl font-mono font-bold text-gray-800">{{ value }} <span class="text-sm text-gray-400">{{ unit }}</span></p>
    
    <div v-if="percent > 0" class="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
        <div class="h-full transition-all duration-500" :class="barColor" :style="{ width: percent + '%' }"></div>
    </div>
  </div>
</template>
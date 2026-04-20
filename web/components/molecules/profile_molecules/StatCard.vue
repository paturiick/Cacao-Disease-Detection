<script setup>
defineProps(['label', 'value', 'colorClass', 'icon']);
</script>

<template>
  <div class="flex-1 bg-white/50 border border-gray-100 rounded-xl p-3 flex flex-col items-center justify-center transition-all hover:shadow-md group">
    <div :class="['p-1.5 rounded-lg mb-1', colorClass]">
      <component :is="icon" class="w-3.5 h-3.5" />
    </div>
    <span class="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">{{ label }}</span>
    <span class="text-sm font-black text-slate-800">{{ value }}</span>
  </div>
</template>
<script setup>
defineProps({
  label: String,
  value: [String, Number],
  colorClass: String
});
</script>

<template>
  <div :class="['p-4 rounded-xl flex items-center gap-4', colorClass]">
    <div v-if="$slots.icon" class="w-10 h-10 rounded-lg bg-white/50 flex items-center justify-center shrink-0">
      <slot name="icon"></slot>
    </div>
    <div class="min-w-0">
      <p class="text-[11px] font-bold opacity-60 uppercase tracking-wide leading-none mb-1">{{ label }}</p>
      <p class="text-2xl font-bold font-poppins leading-none">{{ value }}</p>
    </div>
  </div>
</template>
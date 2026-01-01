<script setup>
defineProps({
  label: String,
  value: [String, Number],
  colorClass: String // e.g., 'bg-blue-50 text-blue-800'
});
</script>

<template>
  <div :class="['p-4 rounded-lg flex flex-col gap-2', colorClass]">
    <span class="text-sm font-inter opacity-80">{{ label }}</span>
    <span class="text-xl font-bold font-poppins flex items-center gap-2">
      <slot name="icon"></slot>
      {{ value }}
    </span>
  </div>
</template>
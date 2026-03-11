<script setup>
defineProps({
  label: String,
  value: String
});
</script>

<template>
  <div class="flex flex-col gap-1">
    <span class="text-xs text-gray-500 font-inter">{{ label }}</span>
    <span class="text-sm font-medium text-gray-800 font-poppins flex items-center gap-2">
      <slot name="icon"></slot>
      {{ value }}
    </span>
  </div>
</template>
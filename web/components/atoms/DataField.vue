<script setup>
defineProps({
  label: String,
  value: [String, Number] // Allow numbers too
});
</script>

<template>
  <div class="flex flex-col border-b border-gray-100 pb-3 last:border-0 transition-colors hover:bg-gray-50/50">
    <span class="text-xs text-gray-500 font-inter mb-1">{{ label }}</span>
    <span class="text-sm font-bold text-gray-800 font-poppins">{{ value }}</span>
  </div>
</template>
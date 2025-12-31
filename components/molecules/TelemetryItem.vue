<template>
  <div class="bg-white p-4 rounded-lg shadow h-24 flex flex-col justify-between">
     <span class="text-xs text-gray-500 font-bold font-inter">{{ label }}</span>
     <span class="text-xl font-bold text-gray-800 font-poppins">{{ value || '---' }}</span>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number]
})
</script>
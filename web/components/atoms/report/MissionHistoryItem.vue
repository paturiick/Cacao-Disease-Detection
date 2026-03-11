<script setup>
defineProps({
  id: String,
  date: String,
  isSelected: Boolean
});
</script>

<template>
  <div 
    class="p-3 rounded-lg cursor-pointer transition-colors border"
    :class="isSelected ? 'bg-red-50 border-red-100' : 'bg-gray-50 border-gray-100 hover:bg-gray-100'"
  >
    <div class="flex justify-between items-center mb-1">
      <span class="font-bold text-gray-700 text-sm font-poppins">{{ id }}</span>
      <span class="text-xs text-gray-500 italic font-inter">Click to view</span>
    </div>
    <span class="text-xs text-gray-500 font-inter">{{ date }}</span>
  </div>
</template>
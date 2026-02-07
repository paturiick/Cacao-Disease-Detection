<script setup>
defineProps({ isActive: Boolean });
</script>
<template>
  <span 
    class="text-[10px] px-2 py-1 rounded-full uppercase font-bold tracking-wider transition-colors"
    :class="isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
  >
    {{ isActive ? 'Mission Active' : 'Mission Inactive' }}
  </span>
</template>
<script setup>
defineProps({
  isActive: Boolean
});
</script>

<template>
  <div 
    class="text-xs font-bold px-3 py-1 rounded-full transition-colors select-none"
    :class="isActive ? 'bg-[#AED581] text-white' : 'bg-gray-100 text-gray-400'"
  >
    {{ isActive ? 'Mission Active' : 'Mission Inactive' }}
  </div>
</template>
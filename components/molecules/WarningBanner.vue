<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  }
});
</script>

<template>
  <div class="bg-[#FFF9C4] border-l-4 border-[#FBC02D] p-4 rounded shadow-sm flex items-start gap-3 shrink-0">
    <svg class="w-5 h-5 text-[#FBC02D] mt-0.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
    </svg>
    
    <div>
      <p class="text-[#F57F17] font-bold text-sm">{{ title }}</p>
      <p v-if="message" class="text-[#F9A825] text-xs">{{ message }}</p>
    </div>
  </div>
</template>
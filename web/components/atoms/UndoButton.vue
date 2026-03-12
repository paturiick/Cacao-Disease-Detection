<script setup>
defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
});
defineEmits(['click']);
</script>

<template>
  <button 
    @click="$emit('click')" 
    :disabled="disabled"
    title="Undo"
    class="absolute bottom-4 right-4 bg-white border border-gray-200 shadow-md rounded-full p-2.5 text-gray-500 hover:text-[#658D1B] hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all z-10"
  >
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
    </svg>
  </button>
</template>
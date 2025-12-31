<script setup>
defineProps({
  label: { type: String, required: true },
  colorClass: { type: String, required: true }
});
</script>

<template>
  <div 
    class="relative flex items-center justify-center text-white px-6 py-3 rounded-md shadow w-full max-w-md select-none"
    :class="colorClass"
  >
    <div class="absolute left-6 w-6 h-6 flex items-center justify-center">
      <slot name="icon"></slot>
    </div>
    
    <span class="font-medium text-lg font-poppins">{{ label }}</span>
  </div>
</template>
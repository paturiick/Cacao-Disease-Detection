<script setup>
defineProps({
  label: { type: String, required: true },
  colorClass: { type: String, required: true }
});

defineEmits(['click']);
</script>

<template>
  <button 
    @click="$emit('click')"
    class="w-10 h-10 rounded-full flex items-center justify-center hover:opacity-90 transition shadow-sm border-none outline-none"
    :class="colorClass"
    :title="`Go to ${label}`"
  >
    <div class="w-5 h-5 flex items-center justify-center brightness-0 invert">
      <slot name="icon"></slot>
    </div>
  </button>
</template>
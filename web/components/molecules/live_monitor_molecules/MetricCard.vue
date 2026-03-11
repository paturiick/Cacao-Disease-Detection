<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';

defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true }
});
</script>

<template>
  <BaseCard class="flex flex-col justify-center h-24 px-6 shadow-sm bg-white">
    
    <div class="flex items-center gap-2 mb-1">
      <div v-if="$slots.icon" class="flex items-center justify-center">
        <slot name="icon"></slot>
      </div>
      
      <span class="text-xs font-bold text-gray-500 font-inter">{{ label }}</span>
    </div>

    <span class="text-2xl font-bold text-gray-800 font-poppins">{{ value }}</span>
    
  </BaseCard>
</template>
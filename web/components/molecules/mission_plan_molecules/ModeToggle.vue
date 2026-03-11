<script setup>
import ToggleSwitch from '~/components/atoms/ToggleSwitch.vue';

defineProps({ 
  modelValue: { type: Boolean, required: true } 
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center gap-4 w-fit">
    <span 
      class="text-[10px] font-bold transition-colors duration-300 cursor-pointer select-none uppercase tracking-widest" 
      :class="!modelValue ? 'text-[#40623F]' : 'text-gray-400 hover:text-gray-600'"
      @click="$emit('update:modelValue', false)"
    >
      Manual
    </span>
    
    <ToggleSwitch 
      :modelValue="modelValue" 
      @update:modelValue="$emit('update:modelValue', $event)" 
    />
    
    <span 
      class="text-[10px] font-bold transition-colors duration-300 cursor-pointer select-none uppercase tracking-widest" 
      :class="modelValue ? 'text-[#40623F]' : 'text-gray-400 hover:text-gray-600'"
      @click="$emit('update:modelValue', true)"
    >
      Draw Directions
    </span>
  </div>
</template>
<script setup>
import ToggleSwitch from '~/components/atoms/ToggleSwitch.vue';

defineProps({ modelValue: { type: Boolean, required: true } });
defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center gap-3">
    <span 
      class="text-[10px] font-bold cursor-pointer select-none uppercase tracking-widest transition-colors" 
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
      class="text-[10px] font-bold cursor-pointer select-none uppercase tracking-widest transition-colors" 
      :class="modelValue ? 'text-[#40623F]' : 'text-gray-400 hover:text-gray-600'"
      @click="$emit('update:modelValue', true)"
    >
      Draw Directions
    </span>
  </div>
</template>
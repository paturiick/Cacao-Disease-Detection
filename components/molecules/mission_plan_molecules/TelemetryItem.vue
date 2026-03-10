<script setup>
import ToggleSwitch from '~/components/atoms/ToggleSwitch.vue';

defineProps({ 
  modelValue: { type: Boolean, required: true } 
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex items-center gap-3 bg-white px-4 py-1.5 rounded-full shadow-sm border border-gray-200 w-fit">
    <span 
      class="text-sm font-bold transition-colors duration-300 cursor-pointer select-none" 
      :class="!modelValue ? 'text-[#40623F]' : 'text-gray-500 hover:text-gray-700'"
      @click="$emit('update:modelValue', false)"
    >
      Manual
    </span>
    
    <ToggleSwitch 
      :modelValue="modelValue" 
      @update:modelValue="$emit('update:modelValue', $event)" 
    />
    
    <span 
      class="text-sm font-bold transition-colors duration-300 cursor-pointer select-none" 
      :class="modelValue ? 'text-[#40623F]' : 'text-gray-500 hover:text-gray-700'"
      @click="$emit('update:modelValue', true)"
    >
      Draw Directions
    </span>
  </div>
</template>
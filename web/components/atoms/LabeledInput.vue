<script setup>
import ValidationMessage from '~/components/atoms/ValidationMessage.vue';

defineProps({
  modelValue: String,
  label: String,
  placeholder: String,
  type: { type: String, default: 'text' },
  error: String
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex flex-col">
    <label class="block text-[#3E2723] text-sm font-bold mb-2 font-poppins">
      {{ label }}
    </label>

    <div class="relative">
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <slot name="icon"></slot>
      </div>
      <input 
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="shadow-sm border rounded w-full py-3 pl-10 pr-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-[#658D1B] focus:border-transparent transition font-inter"
        :class="{ 'border-red-500 focus:ring-red-500': error }"
        :placeholder="placeholder"
      >
    </div>

    <ValidationMessage v-if="error">
      {{ error }}
    </ValidationMessage>
    
  </div>
</template>
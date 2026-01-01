<script setup>
defineProps({
  label: String,
  modelValue: String,
  placeholder: String,
  type: { type: String, default: 'text' }
});
defineEmits(['update:modelValue']);
</script>

<template>
  <div class="flex flex-col gap-1">
    <label class="text-xs font-semibold text-gray-600 font-inter">{{ label }}</label>
    <input 
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      class="border border-gray-300 rounded px-3 py-2 text-sm text-gray-700 focus:outline-none focus:border-[#658D1B] transition-colors"
    />
  </div>
</template>
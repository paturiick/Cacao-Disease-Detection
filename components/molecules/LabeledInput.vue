<script setup>
defineProps({
  modelValue: String,
  label: String,
  type: {
    type: String,
    default: 'text'
  },
  placeholder: String
});
</script>

<template>
  <div class="w-full">
    <label class="flex items-center text-gray-600 text-sm font-medium mb-1.5">
       <slot name="icon"></slot>
       {{ label }}
    </label>
    <input 
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :type="type" 
      :placeholder="placeholder" 
      class="w-full border border-gray-300 rounded-md px-4 py-2.5 text-sm focus:outline-none focus:border-[#658D1B] focus:ring-1 focus:ring-[#658D1B] transition placeholder-gray-400"
    />
  </div>
</template>
<script setup>
defineProps({
  modelValue: String,
  label: String, 
  placeholder: String,
  type: { type: String, default: 'text' },
  error: String        // Optional error message
});

defineEmits(['update:modelValue']);
</script>

<template>
  <div class="w-full group animate-slide-up">
    
    <label class="flex items-center text-gray-600 text-sm font-medium mb-1.5 transition-colors duration-300 group-focus-within:text-[#658D1B]">
       <span class="mr-2 transition-transform duration-300 group-focus-within:scale-110">
         <slot name="icon"></slot>
       </span>
       {{ label }}
    </label>

    <input 
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :type="type" 
      :placeholder="placeholder" 
      class="w-full border border-gray-300 rounded-md px-4 py-2.5 text-sm 
             transition-all duration-300 ease-in-out
             focus:outline-none focus:border-[#658D1B] focus:ring-2 focus:ring-[#658D1B]/20 
             placeholder-gray-400 hover:border-gray-400"
      :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-200': error }"
    />

    <p v-if="error" class="text-red-500 text-xs mt-1">{{ error }}</p>
  </div>
</template>

<style scoped>
.animate-slide-up {
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
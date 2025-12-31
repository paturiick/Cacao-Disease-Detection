<script setup>
defineProps({
  modelValue: String,
  placeholder: String
});
</script>

<template>
  <div class="w-full group animate-slide-up">
    
    <label class="flex items-center text-gray-600 text-sm font-medium mb-1.5 transition-colors duration-300 group-focus-within:text-[#658D1B]">
       <svg 
         class="w-4 h-4 mr-2 transition-transform duration-300 group-focus-within:scale-110" 
         fill="none" 
         stroke="currentColor" 
         viewBox="0 0 24 24"
       >
         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
       </svg>
       Username
    </label>

    <input 
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      type="text" 
      :placeholder="placeholder" 
      class="w-full border border-gray-300 rounded-md px-4 py-2.5 text-sm 
             transition-all duration-300 ease-in-out
             focus:outline-none focus:border-[#658D1B] focus:ring-2 focus:ring-[#658D1B]/20 
             placeholder-gray-400 hover:border-gray-400"
    />
  </div>
</template>

<style scoped>
/* Custom Slide Up Animation */
.animate-slide-up {
  animation: slideUp 0.5s ease-out forwards;
  opacity: 0; /* Start invisible */
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
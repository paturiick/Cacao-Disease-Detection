<script setup>
import { ref, computed } from 'vue';

defineProps({
  modelValue: String,
  placeholder: { type: String, default: 'Confirm password' },
  error: String
});
defineEmits(['update:modelValue']);

const isVisible = ref(false);
const inputType = computed(() => isVisible.value ? 'text' : 'password');
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
         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
       </svg>
       Confirm Password
    </label>

    <div class="relative">
      <input 
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :type="inputType" 
        :placeholder="placeholder" 
        class="w-full border rounded-md px-4 py-2.5 pr-10 text-sm 
               transition-all duration-300 ease-in-out
               focus:outline-none focus:ring-2 
               placeholder-gray-400 hover:border-gray-400"
        :class="error ? 'border-red-500 focus:border-red-500 focus:ring-red-200' : 'border-gray-300 focus:border-[#658D1B] focus:ring-[#658D1B]/20'"
      />
      
      <button 
        type="button" 
        @click="isVisible = !isVisible" 
        class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-[#658D1B] transition-colors focus:outline-none"
      >
        <svg v-if="!isVisible" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
      </button>
    </div>

    <p v-if="error" class="text-red-500 text-xs mt-1.5 ml-1 animate-slide-up" style="animation-duration: 0.3s">
      {{ error }}
    </p>
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
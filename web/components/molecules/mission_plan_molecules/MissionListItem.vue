<script setup>
defineProps({
  index: Number,
  label: String,
  value: [String, Number],
  unit: String,
  icon: [String, Object], // Can be string path or module object
  isActive: Boolean,
  isRunning: Boolean,
  isConfig: { type: Boolean, default: false } 
});
defineEmits(['remove']);
</script>

<template>
  <div 
    class="relative flex items-center p-4 rounded-lg border transition-all duration-300 group"
    :class="[
      isActive 
        ? (isConfig ? 'bg-blue-50 border-blue-500 shadow-md ring-1 ring-blue-500' : 'bg-green-50 border-[#658D1B] shadow-md scale-[1.02] ring-1 ring-[#658D1B]') 
        : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
    ]"
  >
    <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-4 shrink-0 transition-colors"
      :class="isActive ? (isConfig ? 'bg-blue-600 text-white' : 'bg-[#658D1B] text-white') : 'bg-gray-100 text-gray-500'">
      {{ isConfig ? 'S' : index + 1 }}
    </div>
    
    <div v-if="!isConfig" class="mr-4 w-6 h-6 flex items-center justify-center">
      
      <div 
        v-if="typeof icon === 'string' && icon.startsWith('<svg')" 
        v-html="icon"
        class="text-gray-400 group-hover:text-[#658D1B] transition-colors"
      ></div>

      <img 
        v-else 
        :src="icon" 
        alt="icon" 
        class="w-full h-full object-contain opacity-60 group-hover:opacity-100 transition-opacity" 
      />
    </div>
    
    <div class="flex-1">
      <h4 class="text-sm font-bold text-gray-800 uppercase tracking-wide">{{ label }}</h4>
      <p v-if="!isConfig" class="text-xs text-gray-500">Duration: <span class="font-mono font-medium text-gray-700">{{ value }} {{ unit }}</span></p>
      <slot name="details"></slot>
    </div>
    
    <div v-if="isRunning && isActive" class="text-xs font-bold animate-pulse mr-2" :class="isConfig ? 'text-blue-600' : 'text-[#658D1B]'">
      {{ isConfig ? 'SETTING UP...' : 'EXECUTING...' }}
    </div>
    
    <button 
      v-if="!isRunning && !isConfig" 
      @click="$emit('remove')" 
      class="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-full transition-all"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
    </button>
  </div>
</template>
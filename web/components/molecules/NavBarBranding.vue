<script setup>
import { computed } from 'vue';
import Logo from '~/components/atoms/Logo.vue';

const props = defineProps({
  title: { type: String, default: 'LUPAD' },
  connectionStatus: { type: String, default: 'No Signal' },
  battery: { type: Number, default: null } // Added battery prop
});

defineEmits(['click']);

// Logic to check if the status string implies a live connection
const isConnected = computed(() => {
  const status = props.connectionStatus?.toLowerCase() || '';
  return ['strong', 'connected', 'streaming'].includes(status);
});
</script>

<template>
  <div class="flex items-center space-x-4 group">
    <button @click="$emit('click')" class="w-16 h-12 flex items-center justify-center group-hover:opacity-70 transition-opacity focus:outline-none">
      <Logo />
    </button>
    <div class="flex flex-col text-left">
      <button @click="$emit('click')" class="text-left group-hover:opacity-70 transition-opacity focus:outline-none">
        <h1 class="text-[#3E2723] font-bold text-xl leading-none tracking-wide font-poppins">{{ title }}</h1>
      </button>
      <div class="flex items-center gap-1.5 mt-0.5 cursor-default">
        
        <span 
          class="w-2 h-2 rounded-full transition-colors duration-300"
          :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
        ></span>
        
        <span
          class="text-xs font-bold font-inter tracking-wide uppercase transition-colors duration-300"
          :class="isConnected ? 'text-green-600' : 'text-red-500'"
        >
          {{ isConnected ? 'Connected' : 'Disconnected' }}
        </span>

        <template v-if="isConnected && battery !== null">
          <span class="text-slate-300 text-[10px] mx-0.5">•</span>
          
          <div class="flex items-center gap-1" :title="`Drone Battery: ${battery}%`">
            <svg 
              class="w-3.5 h-3.5 transition-colors duration-300" 
              :class="battery <= 20 ? 'text-red-500 animate-pulse' : 'text-green-600'" 
              fill="currentColor" 
              viewBox="0 0 24 24"
            >
              <path d="M17 6H3a2 2 0 00-2 2v8a2 2 0 002 2h14a2 2 0 002-2v-8a2 2 0 00-2-2zm4 4v4h-2v-4h2z"/>
            </svg>
            <span 
              class="text-xs font-bold font-inter tracking-wide transition-colors duration-300" 
              :class="battery <= 20 ? 'text-red-500' : 'text-green-600'"
            >
              {{ battery }}%
            </span>
          </div>
        </template>

      </div>
    </div>
  </div>
</template>
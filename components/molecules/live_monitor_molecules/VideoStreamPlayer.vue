<script setup>
import { ref, computed } from 'vue';
import { liveApi } from '~/sections/api/liveApi';
import { isStreamActive } from '~/components/composables/droneStore'; // Adjust path if needed

const isLoading = ref(false);
const streamTimestamp = ref(Date.now());

const videoSrc = computed(() => {
  if (!isStreamActive.value) return '';
  return `${liveApi.getStreamUrl()}?t=${streamTimestamp.value}`;
});


const handleToggle = async () => {
  if (isLoading.value) return;
  
  isLoading.value = true;
  const action = isStreamActive.value ? 'streamoff' : 'streamon';
  
  try {
    await liveApi.toggleHardware(action);
    
    if (action === 'streamon') {
      streamTimestamp.value = Date.now();
      isStreamActive.value = true; 
    } else {
      isStreamActive.value = false; 
    }
  } catch (e) {
    console.error("Hardware Camera Toggle Failed:", e);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm flex flex-col h-full border border-gray-100 p-4">
    
    <div class="flex justify-between items-center mb-4">
      <h3 class="font-bold text-gray-800 text-sm flex items-center gap-2">
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
        </svg>
        Live Video Stream
      </h3>
      
      <button 
        @click="handleToggle"
        :disabled="isLoading"
        :class="isStreamActive ? 'bg-red-50 text-red-600 border-red-200 hover:bg-red-100' : 'bg-[#95C13E] text-white border-transparent hover:bg-[#7fa832]'"
        class="px-4 py-1.5 rounded-md text-xs font-bold border transition-colors flex items-center gap-2 disabled:opacity-50"
      >
        <span v-if="isLoading" class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
        <span v-else-if="isStreamActive" class="w-2 h-2 rounded-full bg-red-600 animate-pulse"></span>
        {{ isStreamActive ? 'Stop Stream' : 'Start Stream' }}
      </button>
    </div>

    <div class="flex-1 bg-[#0B1120] rounded-md overflow-hidden relative flex items-center justify-center border border-slate-800">
      
      <div v-if="!isStreamActive" class="absolute inset-0 flex flex-col items-center justify-center text-gray-500 z-20 bg-slate-900/40 backdrop-blur-[2px]">
        <svg class="w-12 h-12 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"></path>
        </svg>
        <span class="text-sm font-medium opacity-60">No active stream</span>
      </div>

      <img
        v-if="isStreamActive"
        :src="videoSrc" 
        class="w-full h-full object-contain z-10"
        alt="Tello Drone Feed"
      />

    </div>
  </div>
</template>
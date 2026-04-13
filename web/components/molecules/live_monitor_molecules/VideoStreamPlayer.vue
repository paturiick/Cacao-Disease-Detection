<script setup>
import { ref, computed, watch } from 'vue';
import { liveApi } from '~/sections/api/liveApi';
import { isStreamActive, activeSessionId, isRecording } from '~/components/composables/droneStore'; 
import { useTelemetry } from '~/components/composables/useTelemetry'; 

const { telemetryState } = useTelemetry();
const isLoading = ref(false);

const isRecordingLoading = ref(false);

const streamTimestamp = ref(Date.now());

const videoSrc = computed(() => {
  if (!isStreamActive.value || !telemetryState.connected) return '';
  return `${liveApi.getStreamUrl()}?t=${streamTimestamp.value}`;
});

const toggleRecording = async () => {
  if (isRecordingLoading.value) return;
  
  isRecordingLoading.value = true;
  try {
    const action = isRecording.value ? 'stop' : 'start';
    await liveApi.toggleRecording(action);
    isRecording.value = !isRecording.value; 
  } catch (error) {
    console.error(`Failed to ${isRecording.value ? 'stop' : 'start'} recording:`, error);
  } finally {
    isRecordingLoading.value = false;
  }
};

const startStream = async () => {
  if (isStreamActive.value || isLoading.value) return;
  
  isLoading.value = true;
  try {
    const response = await liveApi.toggleHardware('streamon');
    streamTimestamp.value = Date.now();
    isStreamActive.value = true; 
    
    if (response.session_id) {
      activeSessionId.value = response.session_id;
    }
  } catch (e) {
    console.error(`Hardware Camera Toggle (streamon) Failed:`, e);
    isStreamActive.value = false;
  } finally {
    setTimeout(() => {
      isLoading.value = false;
    }, 1500); 
  }
};

const stopStream = async () => {
  if (!isStreamActive.value) return;
  
  isStreamActive.value = false; 
  activeSessionId.value = null;
  
  // Cleanly stop recording if the stream dies
  if (isRecording.value) {
    isRecording.value = false; 
    try { await liveApi.toggleRecording('stop'); } catch(e) {}
  }
  
  try {
    await liveApi.toggleHardware('streamoff');
  } catch (e) {
    console.error(`Hardware Camera Toggle (streamoff) Failed:`, e);
  }
};

watch(() => telemetryState.connected, (isConnected) => {
  if (isConnected) {
    console.log("Drone connected: Automatically starting stream...");
    startStream();
  } else {
    console.log("Drone disconnected: Stopping stream...");
    stopStream();
  }
}, { immediate: true }); 
</script>

<template>
  <div class="rounded-xl shadow-2xl flex flex-col w-full h-full bg-[#0F172A] border border-slate-700/60 overflow-hidden relative">
    
    <div class="flex justify-between items-center px-5 py-4 bg-slate-900/50 border-b border-slate-700/60 shrink-0">
      <h3 class="font-bold text-slate-200 text-sm flex items-center gap-2 uppercase tracking-wide">
        <svg class="w-5 h-5 text-emerald-500" v-if="isStreamActive && telemetryState.connected" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
        <svg class="w-5 h-5 text-slate-500" v-else fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
        Live Feed
      </h3>
      
      <div class="flex items-center gap-3">
        <slot name="header-actions"></slot>

        <button
          v-if="isStreamActive && telemetryState.connected"
          @click="toggleRecording"
          :disabled="isRecordingLoading"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px] font-bold border transition-all duration-300 shadow-lg backdrop-blur-md uppercase tracking-wider focus:outline-none disabled:opacity-50"
          :class="isRecording ? 'bg-red-500/20 text-red-400 border-red-500/50 hover:bg-red-500/30' : 'bg-slate-800/80 text-slate-300 border-slate-700 hover:bg-slate-700/80'"
        >
          <span v-if="isRecordingLoading" class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
          <template v-else>
            <span v-if="!isRecording" class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            <span v-else class="w-2.5 h-2.5 rounded-sm bg-red-500 animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
          </template>
          {{ isRecording ? 'REC' : 'Record' }}
        </button>

        <div 
          :class="isStreamActive ? 'bg-emerald-500/20 text-emerald-500 border-emerald-500/50' : 'bg-slate-800/80 text-slate-400 border-slate-700'"
          class="px-3 py-1.5 rounded-lg text-[11px] font-bold border transition-all duration-300 flex items-center gap-2 shadow-lg backdrop-blur-md uppercase tracking-wider"
        >
          <span v-if="isLoading" class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
          <span v-else-if="isStreamActive" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
          <span v-else class="w-2 h-2 rounded-full bg-slate-500"></span>
          
          {{ isLoading ? 'Initializing...' : (isStreamActive ? 'Live' : 'Offline') }}
        </div>
      </div>
    </div>

    <div class="bg-black relative flex items-center justify-center w-full h-full overflow-hidden">
      
      <div v-if="!isStreamActive || !telemetryState.connected" class="absolute inset-0 flex flex-col items-center justify-center text-slate-500 z-20 bg-[#0A0A0A]">
        <div class="bg-slate-900/80 p-6 rounded-2xl flex flex-col items-center border border-slate-700/50 backdrop-blur-sm shadow-2xl">
          <svg class="w-12 h-12 mb-3 opacity-50" :class="{'animate-pulse': isLoading}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"></path>
          </svg>
          <span class="text-sm font-semibold tracking-wide uppercase text-slate-400 text-center">
            {{ !telemetryState.connected ? 'Awaiting Drone Connection...' : (isLoading ? 'Synchronizing Feed...' : 'Stream Ready') }}
          </span>
        </div>
      </div>

      <img
        v-if="isStreamActive && telemetryState.connected"
        :src="videoSrc" 
        class="w-full h-full object-cover z-10"
        alt="Tello Drone Feed"
      />

    </div>
  </div>
</template>
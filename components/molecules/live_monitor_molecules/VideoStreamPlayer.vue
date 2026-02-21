<script setup>
import { ref, watch, onBeforeUnmount } from 'vue';

const props = defineProps({
  isConnected: { type: Boolean, required: true }
});

const emit = defineEmits(['toggle-stream']);

// Reference to the actual video HTML element
const videoRef = ref(null);
let jmuxer = null;
let ws = null;

const startRealTimeStream = async () => {
  // Dynamically import JMuxer to avoid Nuxt SSR crashes
  const module = await import('jmuxer/dist/jmuxer.js');
  const JMuxer = module.default;

  if (videoRef.value) {
    jmuxer = new JMuxer({
      node: videoRef.value,
      mode: 'video',
      flushingTime: 0, // 0 ensures lowest possible latency
      clearBuffer: true,
      fps: 30,
      debug: false
    });

    // Connect to your Django ASGI Server
    ws = new WebSocket('ws://localhost:8000/ws/video-feed/');
    ws.binaryType = 'arraybuffer';

    ws.onmessage = (event) => {
      // Feed raw H.264 packets directly into the video player
      jmuxer.feed({ video: new Uint8Array(event.data) });
    };

    ws.onerror = (error) => {
      console.error("WebSocket Error:", error);
      emit('toggle-stream'); // Auto-toggle off on error
    };
  }
};

const stopRealTimeStream = () => {
  if (ws) {
    ws.close();
    ws = null;
  }
  if (jmuxer) {
    jmuxer.destroy();
    jmuxer = null;
  }
};

// Watch for the user clicking the "Start Stream" / "Disconnect" button
watch(() => props.isConnected, (newVal) => {
  if (newVal) {
    startRealTimeStream();
  } else {
    stopRealTimeStream();
  }
});

// Clean up memory if the user navigates away from the page
onBeforeUnmount(() => {
  stopRealTimeStream();
});
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm flex flex-col h-full border border-gray-100 p-4">
    
    <div class="flex justify-between items-center mb-4">
      <h3 class="font-bold text-gray-800 text-sm flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
        Live Video Stream
      </h3>
      
      <button 
        @click="$emit('toggle-stream')"
        :class="isConnected ? 'bg-red-50 text-red-600 border-red-200' : 'bg-[#95C13E] text-white border-transparent hover:bg-[#7fa832]'"
        class="px-4 py-1.5 rounded-md text-xs font-bold border transition-colors flex items-center gap-2"
      >
        <span v-if="isConnected" class="w-2 h-2 rounded-full bg-red-600 animate-pulse"></span>
        {{ isConnected ? 'Disconnect' : 'Start Stream' }}
      </button>
    </div>

    <div class="flex-1 bg-[#0B1120] rounded-md overflow-hidden relative flex items-center justify-center">
      
      <div v-if="!isConnected" class="absolute inset-0 flex flex-col items-center justify-center text-gray-500 z-20">
        <svg class="w-12 h-12 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"></path></svg>
        <span class="text-sm font-medium">No active stream</span>
      </div>

      <ClientOnly>
        <video
          v-show="isConnected"
          ref="videoRef" 
          autoplay 
          muted 
          class="w-full h-full object-contain z-10"
        ></video>
      </ClientOnly>

    </div>
  </div>
</template>
<script setup>
import { computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import VideoDisplay from '~/components/atoms/VideoDisplay.vue';

const props = defineProps({
  isConnected: Boolean,
  streamUrl: String
});

defineEmits(['toggle-stream']);

const statusLabel = computed(() => props.isConnected ? 'Live' : 'Disconnected');
const statusClass = computed(() => props.isConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600');
const statusDotClass = computed(() => props.isConnected ? 'bg-green-600 animate-pulse' : 'bg-red-600');
</script>

<template>
  <BaseCard class="flex flex-col h-full min-h-[500px]">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
        <h3 class="font-bold text-gray-700 font-poppins text-sm">Live Video Stream</h3>
      </div>

      <div class="flex items-center gap-3">
        <span :class="['px-3 py-1 rounded text-xs font-bold flex items-center gap-1 transition-colors', statusClass]">
          <span :class="['w-2 h-2 rounded-full', statusDotClass]"></span>
          {{ statusLabel }}
        </span>

        <button 
          @click="$emit('toggle-stream')"
          :class="[
            'text-white px-4 py-1.5 rounded text-xs font-bold shadow-sm flex items-center gap-1 transition',
            isConnected ? 'bg-red-500 hover:bg-red-600' : 'bg-[#AED581] hover:bg-[#9CCC65]'
          ]"
        >
          {{ isConnected ? 'Stop Stream' : 'Start Stream' }}
        </button>
      </div>
    </div>

    <div class="flex-1 bg-[#0F172A] rounded flex items-center justify-center relative overflow-hidden border border-gray-800">
      
      <VideoDisplay 
        v-if="isConnected && streamUrl"
        :src="streamUrl"
      />

      <div v-else class="text-gray-500 text-sm font-medium flex flex-col items-center gap-2 select-none">
        <svg class="w-12 h-12 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
        <span>No active stream</span>
      </div>
      
    </div>
  </BaseCard>
</template>
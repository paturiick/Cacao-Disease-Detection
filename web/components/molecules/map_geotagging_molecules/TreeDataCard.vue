<script setup>
import { computed, ref, watch } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

const props = defineProps({
  detectedTrees: {
    type: Array,
    default: () => [] 
  },
  
  selectedIndex: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['update:selectedIndex']);

// Automatically reset the index if the drone starts a new mission/session
watch(() => props.detectedTrees.length, (newLength) => {
  if (newLength === 0) currentIndex.value = 0;
});

// Derives the currently viewed pod from the array
const currentTree = computed(() => {
  return props.detectedTrees[props.selectedIndex] || null;
});

// Navigation logic for the carousel
const nextTree = () => {
  if (props.selectedIndex < props.detectedTrees.length - 1) {
    emit('update:selectedIndex', props.selectedIndex + 1);
  }
};

const prevTree = () => {
  if (props.selectedIndex > 0) {
    emit('update:selectedIndex', props.selectedIndex - 1);
  }
};
</script>

<template>
  <BaseCard class="h-full flex flex-col border-2 border-[#658D1B]/20 bg-white">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </template>
      Captured Detections ({{ detectedTrees.length }})
    </SectionHeader>

    <div class="mt-4 flex-1 relative bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center group">
      <template v-if="currentTree">
        <img 
          :key="currentTree.id"
          :src="currentTree.imageUrl" 
          class="w-full h-full object-cover" 
          alt="Detected Cacao Pod"
        />
        
        <div 
          class="absolute top-4 left-4 px-3 py-1.5 rounded-md text-[10px] font-black uppercase shadow-lg border backdrop-blur-md text-white transition-colors duration-300"
          :class="currentTree.status === 'diseased' ? 'bg-red-500/90 border-red-400' : 'bg-green-500/90 border-green-400'"
        >
          {{ currentTree.status === 'diseased' ? 'Black Pod Detected' : 'Healthy Cacao' }}
        </div>
        
        <div class="absolute top-4 right-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-white text-[10px] font-mono border border-white/20">
          INDEX: {{ selectedIndex + 1 }} / {{ detectedTrees.length }}
        </div>

        <button 
          v-if="selectedIndex > 0" 
          @click="prevTree"
          class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-[#658D1B] text-white p-2 rounded-full backdrop-blur-sm transition-all shadow-lg border border-white/10 opacity-0 group-hover:opacity-100 z-10"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        </button>

        <button 
          v-if="selectedIndex < detectedTrees.length - 1" 
          @click="nextTree"
          class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-[#658D1B] text-white p-2 rounded-full backdrop-blur-sm transition-all shadow-lg border border-white/10 opacity-0 group-hover:opacity-100 z-10"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </button>

        <div class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent pt-12 pb-4 px-4 pointer-events-none">
          <div class="flex justify-between items-end text-white font-mono">
            <div class="text-[10px]">
              <div class="text-white/50 uppercase text-[8px] mb-1">Location</div>
              <div>LAT: {{ currentTree.lat }}</div>
              <div>LNG: {{ currentTree.lng }}</div>
            </div>

            <div class="text-right text-[10px]">
              <div class="text-white/50 uppercase text-[8px] mb-1">Recorded At</div>
              <div>{{ currentTree.recordedDate }}</div>
              <div>{{ currentTree.recordedTime }}</div>
            </div>
          </div>
        </div>
      </template>
      
      <div v-else class="text-white text-xs opacity-40 italic flex flex-col items-center gap-2">
        <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
        Awaiting drone captures...
      </div>
    </div>
  </BaseCard>
</template>
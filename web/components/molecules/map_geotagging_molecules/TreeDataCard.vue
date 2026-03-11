<script setup>
import { ref, computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

const props = defineProps({
  detectedTrees: { 
    type: Array, 
    default: () => [] 
  }
});

const currentIndex = ref(0);

// Get the current tree based on the index
const currentTree = computed(() => {
  if (!props.detectedTrees || props.detectedTrees.length === 0) return null;
  return props.detectedTrees[currentIndex.value];
});

// Navigation Functions
const nextTree = () => {
  if (currentIndex.value < props.detectedTrees.length - 1) {
    currentIndex.value++;
  }
};

const prevTree = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
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
      Captured Detections
    </SectionHeader>

    <div class="mt-4 flex-1 relative bg-slate-900 rounded-lg overflow-hidden shadow-inner group flex items-center justify-center">
      
      <template v-if="currentTree">
        <img 
          :src="currentTree.imageUrl" 
          alt="Cacao Tree Capture" 
          class="w-full h-full object-cover transition-transform duration-500"
        />
        
        <div 
          class="absolute top-4 left-4 px-3 py-1.5 rounded-md text-[10px] font-black tracking-widest uppercase shadow-lg border backdrop-blur-md flex items-center gap-1.5"
          :class="currentTree.status === 'diseased' ? 'bg-red-500/90 border-red-400 text-white' : 'bg-green-500/90 border-green-400 text-white'"
        >
          <span v-if="currentTree.status === 'diseased'" class="w-2 h-2 rounded-full bg-red-200 animate-pulse"></span>
          <span v-else class="w-2 h-2 rounded-full bg-green-200"></span>
          {{ currentTree.status === 'diseased' ? 'Black Pod Detected' : 'Healthy Tree' }}
        </div>

        <div class="absolute top-4 right-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-white text-[10px] font-mono shadow-lg border border-white/20">
          {{ currentIndex + 1 }} / {{ detectedTrees.length }}
        </div>

        <button 
          @click="prevTree" 
          :disabled="currentIndex === 0"
          class="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-black/50 hover:bg-black/80 text-white rounded-full transition-all disabled:opacity-30 disabled:cursor-not-allowed border border-white/20 hover:scale-110"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>

        <button 
          @click="nextTree" 
          :disabled="currentIndex === detectedTrees.length - 1"
          class="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-black/50 hover:bg-black/80 text-white rounded-full transition-all disabled:opacity-30 disabled:cursor-not-allowed border border-white/20 hover:scale-110"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
      </template>

      <div v-else class="w-full h-full flex flex-col items-center justify-center text-slate-500">
        <svg class="w-10 h-10 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span class="text-xs font-medium uppercase tracking-widest">Waiting for drone captures...</span>
      </div>

    </div>
  </BaseCard>
</template>
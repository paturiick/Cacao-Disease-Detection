<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

defineProps({
  // The URL of your Tello/OpenCV stream (e.g., http://localhost:8000/api/video/stream/)
  streamUrl: { type: String, default: '' },
  treeCount: { type: Number, default: 0 }
});
</script>

<template>
  <BaseCard class="h-full flex flex-col border-2 border-[#658D1B]/20">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4 text-[#658D1B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5S19.832 5.477 21 6.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </template>
      Tree Detection View
    </SectionHeader>

    <div class="mt-4 flex-1 relative bg-slate-900 rounded-lg overflow-hidden shadow-inner group">
      <img 
        v-if="streamUrl"
        :src="streamUrl" 
        alt="Live Tree Detection Feed" 
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
      />
      
      <div v-else class="w-full h-full flex flex-col items-center justify-center text-slate-500">
        <svg class="w-12 h-12 mb-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <span class="text-xs font-medium uppercase tracking-widest">Awaiting Video Feed...</span>
      </div>

      <div class="absolute top-4 left-4 bg-[#658D1B] px-3 py-1 rounded-full text-white text-[10px] font-black tracking-tighter uppercase shadow-lg border border-white/20">
        Live Detection Active
      </div>

      <div class="absolute bottom-4 right-4 bg-white/90 backdrop-blur px-4 py-2 rounded-lg border border-slate-200 shadow-xl">
        <p class="text-[10px] text-slate-500 font-bold uppercase leading-none mb-1">Total Trees</p>
        <p class="text-2xl font-black text-[#3E2723] leading-none">{{ treeCount }}</p>
      </div>
    </div>
  </BaseCard>
</template>
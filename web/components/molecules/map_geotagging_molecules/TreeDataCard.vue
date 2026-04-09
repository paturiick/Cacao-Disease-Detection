<script setup>
import { computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

const props = defineProps({
  selectedIndex: { type: Number, default: 0 },
  // These URLs are now optimized for speed (smaller dimensions & lower quality)
  detectedTrees: {

    // These data are just STATIC IMAGES for testing purposes.
    type: Array,
    default: () => [
      { id: 1, status: 'diseased', imageUrl: 'https://images.unsplash.com/photo-1597848212624-a19eb35e2656?w=600&q=60&auto=format' },
      { id: 2, status: 'healthy',  imageUrl: 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?w=600&q=60&auto=format' },
      { id: 3, status: 'diseased', imageUrl: 'https://images.unsplash.com/photo-1505672678657-cc7037095e60?w=600&q=60&auto=format' },
      { id: 4, status: 'healthy',  imageUrl: 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=600&q=60&auto=format' },
      { id: 5, status: 'healthy',  imageUrl: 'https://images.unsplash.com/photo-1466692476877-626759c5d013?w=600&q=60&auto=format' },
      { id: 6, status: 'diseased', imageUrl: 'https://images.unsplash.com/photo-1504567961542-e24d9439a724?w=600&q=60&auto=format' }
    ]
  }
});

const currentTree = computed(() => {
  return props.detectedTrees[props.selectedIndex] || null;
});
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

    <div class="mt-4 flex-1 relative bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center">
      <template v-if="currentTree">
        <img 
          :key="currentTree.imageUrl"
          :src="currentTree.imageUrl" 
          class="w-full h-full object-cover" 
          loading="lazy"
        />
        
        <div 
          class="absolute top-4 left-4 px-3 py-1.5 rounded-md text-[10px] font-black uppercase shadow-lg border backdrop-blur-md text-white transition-colors duration-300"
          :class="currentTree.status === 'diseased' ? 'bg-red-500/90 border-red-400' : 'bg-green-500/90 border-green-400'"
        >
          {{ currentTree.status === 'diseased' ? 'Black Pod Detected' : 'Healthy Tree' }}
        </div>
        
        <div class="absolute top-4 right-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-white text-[10px] font-mono border border-white/20">
          INDEX: {{ selectedIndex + 1 }}
        </div>
      </template>
      
      <div v-else class="text-white text-xs opacity-40 italic">
        Select a capture to preview
      </div>
    </div>
  </BaseCard>
</template>
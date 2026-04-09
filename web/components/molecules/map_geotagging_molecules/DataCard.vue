<script setup>
import { computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

const props = defineProps({
  data: { type: Object, required: true },
  selectedIndex: { type: Number, default: 0 },
  detectedTrees: { 
    type: Array,

    // These data are just STATIC IMAGES for testing purposes.
    default: () => [
      { id: 1, status: 'diseased', imageUrl: 'https://images.unsplash.com/photo-1597848212624-a19eb35e2656?w=600&q=60' },
      { id: 2, status: 'healthy',  imageUrl: 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?w=600&q=60' },
      { id: 3, status: 'diseased', imageUrl: 'https://images.unsplash.com/photo-1505672678657-cc7037095e60?w=600&q=60' },
      { id: 4, status: 'healthy',  imageUrl: 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=600&q=60' },
      { id: 5, status: 'healthy',  imageUrl: 'https://images.unsplash.com/photo-1466692476877-626759c5d013?w=600&q=60' },
      { id: 6, status: 'diseased', imageUrl: 'https://images.unsplash.com/photo-1504567961542-e24d9439a724?w=600&q=60' }
    ] 
  }
});

const emit = defineEmits(['update:selectedIndex']);

// Telemetry Logic
const calculatedSpeed = computed(() => {
  if (props.data.speed !== undefined && props.data.speed !== 0) return props.data.speed;
  if (props.data.vgx === undefined || props.data.vgy === undefined) return 0.0;
  return Math.sqrt((props.data.vgx ** 2) + (props.data.vgy ** 2)) / 10; 
});

// Selection Logic
const unhealthyTrees = computed(() => {
  return props.detectedTrees
    .map((tree, index) => ({ ...tree, originalIndex: index }))
    .filter(t => t.status === 'diseased');
});

const healthyTrees = computed(() => {
  return props.detectedTrees
    .map((tree, index) => ({ ...tree, originalIndex: index }))
    .filter(t => t.status === 'healthy');
});

const selectImage = (index) => {
  emit('update:selectedIndex', index);
};
</script>

<template>
  <BaseCard class="h-full flex flex-col bg-white/95 overflow-y-auto custom-scrollbar pr-1">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </template>
      Status & Analytics
    </SectionHeader>

    <div class="mt-4 flex flex-col gap-5">
      
      <div class="grid grid-cols-2 gap-2">
        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center gap-3">
          <div class="p-1.5 bg-white rounded-lg shadow-sm">
            <svg class="w-3.5 h-3.5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </div>
          <div>
            <p class="text-[8px] font-bold text-slate-400 uppercase leading-none">Speed</p>
            <p class="text-xs font-black text-slate-700 mt-0.5">{{ calculatedSpeed.toFixed(1) }} m/s</p>
          </div>
        </div>

        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center gap-3">
          <div class="p-1.5 bg-white rounded-lg shadow-sm">
            <svg class="w-3.5 h-3.5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          </div>
          <div>
            <p class="text-[8px] font-bold text-slate-400 uppercase leading-none">Temp</p>
            <p class="text-xs font-black text-slate-700 mt-0.5">{{ data.temp ?? 0 }}°C</p>
          </div>
        </div>

        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-100 flex items-center gap-3">
          <div class="p-1.5 bg-white rounded-lg shadow-sm">
            <svg class="w-3.5 h-3.5" :class="data.battery < 20 ? 'text-red-500' : 'text-slate-700'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12H3m14-3v6m-4-6v6m-4-6v6m-4-6v6m-4-6v6"/></svg>
          </div>
          <div>
            <p class="text-[8px] font-bold text-slate-400 uppercase leading-none">Battery</p>
            <p class="text-xs font-black text-slate-700 mt-0.5">{{ data.battery ?? 0 }}%</p>
          </div>
        </div>
      </div>

      <hr class="border-slate-100" />

      <div class="space-y-2.5">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-3.5 bg-red-500 rounded-full"></div>
          <p class="text-[10px] font-bold text-red-600 uppercase tracking-widest">Infected (Black Pod)</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tree in unhealthyTrees"
            :key="tree.id"
            @click="selectImage(tree.originalIndex)"
            class="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs transition-all border-2"
            :class="[
              selectedIndex === tree.originalIndex 
                ? 'bg-slate-800 border-slate-800 text-white shadow-md scale-110 z-10' 
                : 'bg-red-50 border-red-100 text-red-600 hover:border-red-400'
            ]"
          >
            {{ tree.originalIndex + 1 }}
          </button>
        </div>
      </div>

      <div class="space-y-2.5">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-3.5 bg-green-500 rounded-full"></div>
          <p class="text-[10px] font-bold text-green-600 uppercase tracking-widest">Healthy Cacao</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tree in healthyTrees"
            :key="tree.id"
            @click="selectImage(tree.originalIndex)"
            class="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs transition-all border-2"
            :class="[
              selectedIndex === tree.originalIndex 
                ? 'bg-slate-800 border-slate-800 text-white shadow-md scale-110 z-10' 
                : 'bg-green-50 border-green-100 text-green-600 hover:border-green-400'
            ]"
          >
            {{ tree.originalIndex + 1 }}
          </button>
        </div>
      </div>

    </div>
  </BaseCard>
</template>
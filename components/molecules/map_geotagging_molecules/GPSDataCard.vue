<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

defineProps({
  data: { type: Object, required: true }
});
</script>

<template>
  <BaseCard class="h-full flex flex-col bg-white/95">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </template>
      Flight Telemetry
    </SectionHeader>

    <div class="mt-6 flex flex-col gap-4">
      <div class="space-y-1">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Location</p>
        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 font-mono text-sm font-black text-slate-800">
          {{ data.lat.toFixed(6) }}, {{ data.lng.toFixed(6) }}
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Altitude</p>
          <p class="text-lg font-black text-[#3E2723]">{{ data.alt.toFixed(1) }}m</p>
        </div>
        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Speed</p>
          <p class="text-lg font-black text-[#3E2723]">{{ data.speed.toFixed(1) }}m/s</p>
        </div>
      </div>

      <hr class="border-slate-100 my-2" />

      <div class="space-y-3">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-[#658D1B]">Cacao Analysis</p>
        
        <div class="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-red-700 uppercase leading-none mb-1">Marked with</span>
            <span class="text-xs font-black text-red-900 uppercase">Disease</span>
          </div>
          <span class="text-2xl font-black text-red-800">{{ data.diseasedCacao }}</span>
        </div>

        <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-100">
          <div class="flex flex-col">
            <span class="text-[10px] font-bold text-green-700 uppercase leading-none mb-1">Marked as</span>
            <span class="text-xs font-black text-green-900 uppercase">Healthy</span>
          </div>
          <span class="text-2xl font-black text-green-800">{{ data.healthyCacao }}</span>
        </div>
      </div>
    </div>
  </BaseCard>
</template>
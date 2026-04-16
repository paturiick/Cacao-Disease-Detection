<script setup>
import { computed } from 'vue';

const props = defineProps({
  detection: { type: Object, required: true },
  avgAccuracy: { type: [String, Number], required: true }
});

const healthyPods = computed(() => {
  return Math.max(0, props.detection.total_pods - props.detection.unhealthy);
});
</script>

<template>
  <section>
    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Detection Summary</h3>
    <div class="grid grid-cols-4 gap-4 print:grid-cols-4">
      
      <div class="col-span-1 p-5 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col print:shadow-none print:border-slate-300">
        <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Total Pods</span>
        <span class="text-4xl font-black text-[#0F172A]">{{ detection.total_pods }}</span>
      </div>
      
      <div class="col-span-1 p-5 bg-white border border-[#658D1B]/30 rounded-xl shadow-sm flex flex-col relative overflow-hidden print:shadow-none print:border-[#658D1B]">
        <span class="text-[10px] font-bold text-[#658D1B] uppercase tracking-wider mb-1 z-10">Healthy</span>
        <span class="text-4xl font-black text-[#0F172A] z-10">{{ healthyPods }}</span>
        <svg class="absolute -right-4 -bottom-4 w-24 h-24 text-[#658D1B] opacity-5 print:hidden" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
      </div>
      
      <div class="col-span-1 p-5 bg-white border border-[#C60C0C]/30 rounded-xl shadow-sm flex flex-col relative overflow-hidden print:shadow-none print:border-[#C60C0C]">
        <span class="text-[10px] font-bold text-[#C60C0C] uppercase tracking-wider mb-1 z-10">Black Pod (Infected)</span>
        <span class="text-4xl font-black text-[#0F172A] z-10">{{ detection.unhealthy }}</span>
        <svg class="absolute -right-4 -bottom-4 w-24 h-24 text-[#C60C0C] opacity-5 print:hidden" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5z"/></svg>
      </div>

    </div>
  </section>
</template>
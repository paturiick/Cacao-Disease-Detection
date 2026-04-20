<script setup>
import { computed } from 'vue';

const props = defineProps({
  detection: { type: Object, required: true },
  avgAccuracy: { type: [String, Number], required: true }
});

const healthyPods = computed(() => {
  return Math.max(0, props.detection.total_pods - props.detection.unhealthy);
});

// Analytics Calculations for the Donut Chart
const healthyPercentage = computed(() => {
  if (!props.detection.total_pods) return 0;
  return Math.round((healthyPods.value / props.detection.total_pods) * 100);
});

const unhealthyPercentage = computed(() => {
  if (!props.detection.total_pods) return 0;
  return Math.round((props.detection.unhealthy / props.detection.total_pods) * 100);
});
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
        Detection Summary
      </h3>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 print:grid-cols-4">
      
      <div class="group col-span-1 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between print:shadow-none print:border-slate-300">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Pods</span>
          <div class="p-1.5 bg-slate-50 rounded-lg text-slate-400 group-hover:text-slate-600 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
          </div>
        </div>
        <span class="text-4xl font-black text-slate-800 tracking-tight">{{ detection.total_pods }}</span>
      </div>
      
      <div class="group col-span-1 p-5 bg-gradient-to-br from-[#658D1B]/5 to-transparent border border-[#658D1B]/20 rounded-2xl shadow-sm hover:shadow-md hover:border-[#658D1B]/40 hover:-translate-y-1 transition-all duration-300 flex flex-col relative overflow-hidden print:shadow-none print:border-[#658D1B]">
        <div class="flex items-center justify-between mb-2 z-10">
          <span class="text-[10px] font-bold text-[#658D1B] uppercase tracking-wider flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-[#658D1B]"></span> Healthy
          </span>
        </div>
        <span class="text-4xl font-black text-slate-800 tracking-tight z-10">{{ healthyPods }}</span>
        <svg class="absolute -right-4 -bottom-4 w-24 h-24 text-[#658D1B] opacity-10 group-hover:scale-110 transition-transform duration-500 print:hidden" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
      </div>
      
      <div class="group col-span-1 p-5 bg-gradient-to-br from-[#C60C0C]/5 to-transparent border border-[#C60C0C]/20 rounded-2xl shadow-sm hover:shadow-md hover:border-[#C60C0C]/40 hover:-translate-y-1 transition-all duration-300 flex flex-col relative overflow-hidden print:shadow-none print:border-[#C60C0C]">
        <div class="flex items-center justify-between mb-2 z-10">
          <span class="text-[10px] font-bold text-[#C60C0C] uppercase tracking-wider flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-[#C60C0C] animate-pulse"></span> Black Pod
          </span>
        </div>
        <span class="text-4xl font-black text-slate-800 tracking-tight z-10">{{ detection.unhealthy }}</span>
        <svg class="absolute -right-4 -bottom-4 w-24 h-24 text-[#C60C0C] opacity-10 group-hover:scale-110 transition-transform duration-500 print:hidden" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9v-2h2v2zm0-4H9V7h2v5z"/></svg>
      </div>

      <div class="group col-span-1 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-center relative print:shadow-none print:border-slate-300">
        <span class="absolute top-4 left-5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Health Ratio</span>
        
        <div class="flex items-center justify-center gap-5 mt-4 w-full">
          <div class="relative w-16 h-16 shrink-0">
            <svg viewBox="0 0 42 42" class="w-full h-full transform -rotate-90">
              <circle cx="21" cy="21" r="15.91549431" fill="transparent" stroke="#F1F5F9" stroke-width="7"></circle>
              
              <circle cx="21" cy="21" r="15.91549431" fill="transparent" stroke="#658D1B" stroke-width="7"
                :stroke-dasharray="`${healthyPercentage} ${100 - healthyPercentage}`"
                stroke-dashoffset="0"
                class="transition-all duration-1000 ease-out"
                stroke-linecap="round"
              ></circle>

              <circle cx="21" cy="21" r="15.91549431" fill="transparent" stroke="#C60C0C" stroke-width="7"
                :stroke-dasharray="`${unhealthyPercentage} ${100 - unhealthyPercentage}`"
                :stroke-dashoffset="100 - healthyPercentage"
                class="transition-all duration-1000 ease-out"
                stroke-linecap="round"
              ></circle>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"></path></svg>
            </div>
          </div>

          <div class="flex flex-col gap-2 text-[10px] font-bold uppercase tracking-wider">
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full bg-[#658D1B] shadow-sm"></div> 
              <span class="text-slate-700 w-7 text-right">{{ healthyPercentage }}%</span> 
              <span class="text-slate-400">Good</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full bg-[#C60C0C] shadow-sm animate-pulse"></div> 
              <span class="text-slate-700 w-7 text-right">{{ unhealthyPercentage }}%</span> 
              <span class="text-slate-400">Black</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  </section>
</template>
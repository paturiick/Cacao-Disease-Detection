<script setup>
import { computed } from 'vue';

const props = defineProps({
  mission: { type: Object, required: true }
});

const formatTime = (seconds) => {
  if (!seconds) return '0m 0s';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
};

// Helper to check for low battery state to update card styling
const isLowBattery = computed(() => {
  const bat = props.mission.telemetry?.battery_end;
  return bat <= 30 && bat > 0;
});
</script>

<template>
  <section>
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
        Flight Metrics
      </h3>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-4 print:grid-cols-5">
      
      <div class="group col-span-1 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between print:shadow-none print:border-slate-300">
        <div class="flex items-center justify-between mb-3">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Air Time</span>
          <div class="p-1.5 bg-slate-50 rounded-lg text-slate-400 group-hover:text-blue-500 group-hover:bg-blue-50 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
        </div>
        <span class="text-3xl font-black text-slate-800 tracking-tight">{{ formatTime(mission.telemetry?.flight_time) }}</span>
      </div>
      
      <div class="group col-span-1 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between print:shadow-none print:border-slate-300">
        <div class="flex items-center justify-between mb-3">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Target Speed</span>
          <div class="p-1.5 bg-slate-50 rounded-lg text-slate-400 group-hover:text-teal-500 group-hover:bg-teal-50 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 14a9 9 0 0118 0M12 14v-4m-4 4a4 4 0 118 0"></path></svg>
          </div>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-black text-slate-800 tracking-tight">{{ mission.speed || 0 }}</span>
          <span class="text-xs text-slate-400 font-bold uppercase tracking-wider">cm/s</span>
        </div>
      </div>
      
      <div class="group col-span-1 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between print:shadow-none print:border-slate-300">
        <div class="flex items-center justify-between mb-3">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Start Battery</span>
          <div class="p-1.5 bg-slate-50 rounded-lg text-slate-400 group-hover:text-emerald-500 group-hover:bg-emerald-50 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a1 1 0 00-1-1h-1V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h12a2 2 0 002-2v-2h1a1 1 0 001-1z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11h10v2H7z"></path>
            </svg>
          </div>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="text-3xl font-black text-slate-800 tracking-tight">{{ mission.telemetry?.battery_start || 0 }}</span>
          <span class="text-lg font-black text-slate-400">%</span>
        </div>
      </div>

      <div 
        class="group col-span-1 p-5 rounded-2xl shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between print:shadow-none"
        :class="isLowBattery ? 'bg-gradient-to-br from-[#C60C0C]/5 to-transparent border border-[#C60C0C]/30 hover:border-[#C60C0C]/50' : 'bg-white border border-slate-200 print:border-slate-300'"
      >
        <div class="flex items-center justify-between mb-3">
          <span 
            class="text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5"
            :class="isLowBattery ? 'text-[#C60C0C]' : 'text-slate-400'"
          >
            <span v-if="isLowBattery" class="w-1.5 h-1.5 rounded-full bg-[#C60C0C] animate-pulse"></span>
            End Battery
          </span>
          <div 
            class="p-1.5 rounded-lg transition-colors"
            :class="isLowBattery ? 'text-[#C60C0C] bg-[#C60C0C]/10' : 'bg-slate-50 text-slate-400 group-hover:text-emerald-500 group-hover:bg-emerald-50'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a1 1 0 00-1-1h-1V9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h12a2 2 0 002-2v-2h1a1 1 0 001-1z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11h2v2H7z"></path>
            </svg>
          </div>
        </div>
        <div class="flex items-baseline gap-1">
          <span 
            class="text-3xl font-black tracking-tight" 
            :class="isLowBattery ? 'text-[#C60C0C]' : 'text-slate-800'"
          >
            {{ mission.telemetry?.battery_end || 0 }}
          </span>
          <span 
            class="text-lg font-black"
            :class="isLowBattery ? 'text-[#C60C0C]/70' : 'text-slate-400'"
          >%</span>
        </div>
      </div>

    </div>
  </section>
</template>
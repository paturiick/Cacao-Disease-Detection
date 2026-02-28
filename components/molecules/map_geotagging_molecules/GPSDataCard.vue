<script setup>
import { computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';

const props = defineProps({
  data: { type: Object, required: true }
});

// Calculate 2D horizontal speed from vgx and vgy (dm/s to m/s)
const calculatedSpeed = computed(() => {
  if (props.data.vgx === undefined || props.data.vgy === undefined) return 0.0;
  const speedDm = Math.sqrt((props.data.vgx ** 2) + (props.data.vgy ** 2));
  return speedDm / 10; 
});
</script>

<template>
  <BaseCard class="h-full flex flex-col bg-white/95 overflow-y-auto">
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
          {{ data.lat?.toFixed(6) ?? '0.000000' }}, {{ data.lng?.toFixed(6) ?? '0.000000' }}
        </div>
      </div>

      <div class="grid grid-cols-3 gap-3">
        
        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Altitude</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.altitude_m?.toFixed(1) ?? '0.0' }}<span class="text-xs text-slate-500 ml-0.5">m</span></p>
        </div>
        
        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Speed</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ calculatedSpeed.toFixed(1) }}<span class="text-xs text-slate-500 ml-0.5">m/s</span></p>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center relative overflow-hidden">
          <p class="text-[9px] font-bold text-slate-400 uppercase z-10">Battery</p>
          <p class="text-lg font-black leading-none mt-1 z-10" :class="data.battery <= 20 ? 'text-red-600' : 'text-[#3E2723]'">
            {{ data.battery ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">%</span>
          </p>
          <div class="absolute bottom-0 left-0 h-1 bg-green-500 transition-all duration-1000" :style="{ width: `${data.battery ?? 0}%` }" :class="{ 'bg-red-500': data.battery <= 20 }"></div>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Pitch</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.pitch ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">°</span></p>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Roll</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.roll ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">°</span></p>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Yaw</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.yaw ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">°</span></p>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">ToF Dist</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.tof_cm ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">cm</span></p>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Temp</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.temp_c ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">°C</span></p>
        </div>

        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100 flex flex-col items-center justify-center text-center">
          <p class="text-[9px] font-bold text-slate-400 uppercase">Air Time</p>
          <p class="text-lg font-black text-[#3E2723] leading-none mt-1">{{ data.flight_time ?? 0 }}<span class="text-xs text-slate-500 ml-0.5">s</span></p>
        </div>

      </div>

      <hr class="border-slate-100 my-1" />

      <div class="space-y-3">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-[#658D1B]">Live Image Analysis</p>
        
        <div class="flex items-center justify-between p-3 bg-red-50/80 rounded-lg border border-red-100 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-2 h-8 bg-red-500 rounded-full"></div>
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-red-600 uppercase tracking-wider mb-0.5">Detected</span>
              <span class="text-xs font-black text-red-900 uppercase">Infected (Black Pod)</span>
            </div>
          </div>
          <span class="text-2xl font-black text-red-700">{{ data.diseased ?? 0 }}</span>
        </div>

        <div class="flex items-center justify-between p-3 bg-green-50/80 rounded-lg border border-green-100 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="w-2 h-8 bg-green-500 rounded-full"></div>
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-green-600 uppercase tracking-wider mb-0.5">Detected</span>
              <span class="text-xs font-black text-green-900 uppercase">Healthy Cacao</span>
            </div>
          </div>
          <span class="text-2xl font-black text-green-700">{{ data.healthy ?? 0 }}</span>
        </div>

      </div>
    </div>
  </BaseCard>
</template>
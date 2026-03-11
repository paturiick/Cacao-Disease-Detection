<script setup>
import WarningBanner from '~/components/molecules/mission_plan_molecules/WarningBanner.vue';
import MissionControlCard from './MissionControlCard.vue';

const props = defineProps({
  hasMission: Boolean,
  isRunning: Boolean,
  isLanding: { 
    type: Boolean, 
    default: false 
  }
});

defineEmits(['run', 'force-land']);
</script>

<template>
  <div class="flex flex-col gap-5">
    
    <WarningBanner :hasMission="hasMission" />
    
    <div class="mt-auto flex flex-col gap-5">
      
      <MissionControlCard 
        :isRunning="isRunning" 
        :isDisabled="!hasMission || isRunning"
        :isLanding="isLanding"
        @run="$emit('run')"
        @force-land="$emit('force-land')"
      />

      <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="bg-slate-50 border-b border-slate-200 px-4 py-3 flex items-center gap-2">
          <svg class="w-4 h-4 text-[#0F172A]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
          <h3 class="text-xs font-bold text-[#0F172A] uppercase tracking-widest">System</h3>
        </div>
        
        <div class="p-4 flex flex-col gap-4">
          <div class="flex justify-between items-center">
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">UAV Model</span>
              <span class="text-sm font-black text-[#0F172A]">RoboMaster TT</span>
            </div>
            <span class="text-[9px] font-black uppercase text-blue-600 bg-blue-50 px-2 py-1 rounded-md border border-blue-200">DJI</span>
          </div>

          <div class="h-px w-full bg-slate-100"></div>

          <div class="flex justify-between items-center">
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Primary Sensor</span>
              <span class="text-sm font-black text-[#0F172A]">Optical Camera</span>
            </div>
            <span class="w-2 h-2 rounded-full bg-[#658D1B] shadow-[0_0_5px_#658D1B]"></span>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>
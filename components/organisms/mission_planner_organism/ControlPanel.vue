<script setup>
import WarningBanner from '~/components/molecules/mission_plan_molecules/WarningBanner.vue';
import TelemetryItem from '~/components/molecules/mission_plan_molecules/TelemetryItem.vue';
import MissionControlCard from './MissionControlCard.vue';

const props = defineProps({
  hasMission: Boolean,
  isRunning: Boolean,
  isLanding: { 
    type: Boolean, 
    default: false 
  },
  telemetry: {
    type: Object,
    default: () => ({
      gps: 'No Signal',
      battery: 0,
      batteryColor: 'bg-gray-200'
    })
  }
});

// Added the two new events here so they can be heard by mission-planner.vue
defineEmits(['run', 'force-land', 'stop-hover', 'emergency']);
</script>

<template>
  <div class="flex flex-col gap-6">
    <WarningBanner :hasMission="hasMission" />
    
    <MissionControlCard 
      :isRunning="isRunning" 
      :isDisabled="!hasMission || isRunning"
      :isLanding="isLanding"
      @run="$emit('run')"
      @force-land="$emit('force-land')"
    />

    <div class="grid grid-cols-2 gap-4">
      <TelemetryItem 
        label="Connection Status" 
        :value="telemetry.gps" 
        :barColor="telemetry.gps === 'Strong' || telemetry.gps === 'Streaming' ? 'bg-green-500' : 'bg-gray-300'" 
        :percent="telemetry.gps === 'Strong' || telemetry.gps === 'Streaming' ? 90 : 0"
      >
         <template #icon>
           <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
           </svg>
         </template>
      </TelemetryItem>
      
      <TelemetryItem 
        label="Battery" 
        :value="telemetry.gps === 'No Signal' ? 0 : telemetry.battery" 
        unit="%" 
        :barColor="telemetry.gps === 'No Signal' ? 'bg-gray-300' : telemetry.batteryColor" 
        :percent="telemetry.gps === 'No Signal' ? 0 : telemetry.battery"
      >
         <template #icon>
           <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
           </svg>
         </template>
      </TelemetryItem>
    </div>

    <div class="bg-white/95 backdrop-blur-sm rounded-xl shadow-sm border border-slate-200 p-4 flex flex-col gap-3">
      <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center">Live Overrides</p>
      
      <div class="grid grid-cols-2 gap-3">
        <button 
          @click="$emit('stop-hover')"
          class="bg-yellow-400 hover:bg-yellow-500 text-yellow-900 font-bold py-3 px-2 rounded-lg flex items-center justify-center gap-1 transition-colors shadow-sm text-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/></svg>
          Brake (Hover)
        </button>

        <button 
          @click="$emit('emergency')"
          class="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-2 rounded-lg flex items-center justify-center gap-1 transition-colors shadow-sm text-sm hover:animate-none"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          Emergency Stop
        </button>
      </div>
    </div>
    
  </div>
</template>
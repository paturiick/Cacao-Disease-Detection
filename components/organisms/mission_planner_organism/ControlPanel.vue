<script setup>
import WarningBanner from '~/components/molecules/mission_plan_molecules/WarningBanner.vue';
import TelemetryItem from '~/components/molecules/mission_plan_molecules/TelemetryItem.vue';
import MissionControlCard from './MissionControlCard.vue';

const props = defineProps({
  hasMission: Boolean,
  isRunning: Boolean,
  // 1. Add telemetry prop with "Disconnected" defaults
  telemetry: {
    type: Object,
    default: () => ({
      gps: 'No Signal',
      battery: 0,
      batteryColor: 'bg-gray-200'
    })
  }
});

defineEmits(['run']);
</script>

<template>
  <div class="flex flex-col gap-6">
    <WarningBanner :hasMission="hasMission" />
    
    <MissionControlCard 
      :isRunning="isRunning" 
      :isDisabled="!hasMission || isRunning" 
      @run="$emit('run')"
    />

    <div class="grid grid-cols-2 gap-4">
      <TelemetryItem 
        label="GPS Signal" 
        :value="telemetry.gps" 
        :barColor="telemetry.gps === 'Strong' ? 'bg-green-500' : 'bg-gray-300'" 
        :percent="telemetry.gps === 'Strong' ? 90 : 0"
      >
         <template #icon><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg></template>
      </TelemetryItem>
      
      <TelemetryItem 
        label="Battery" 
        :value="telemetry.battery" 
        unit="%" 
        :barColor="telemetry.batteryColor" 
        :percent="telemetry.battery"
      >
         <template #icon><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg></template>
      </TelemetryItem>
    </div>
  </div>
</template>
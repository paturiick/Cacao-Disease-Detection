<script setup>
import WarningBanner from '~/components/molecules/mission_plan_molecules/WarningBanner.vue';
import MissionControlCard from './MissionControlCard.vue';

const props = defineProps({
  hasMission: { type: Boolean, default: false },
  isRunning: { type: Boolean, default: false },
  telemetry: { type: Object, default: () => ({}) }
});

const emit = defineEmits(['run', 'force-land']);
</script>

<template>
  <div class="flex flex-col gap-5">
    <WarningBanner :hasMission="hasMission" />
    
    <MissionControlCard 
      :hasMission="hasMission"
      :isMissionRunning="isRunning"
      :isFlying="telemetry.gps === 'Online' && telemetry.alt > 0"
      @run-mission="$emit('run')"
      @emergency-land="$emit('force-land')"
    />
  </div>
</template>
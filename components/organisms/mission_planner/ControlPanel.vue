<script setup>
import WarningBanner from '~/components/molecules/WarningBanner.vue';
import MissionControlCard from '~/components/organisms/mission_planner/MissionControlCard.vue';
import TelemetryGrid from '~/components/organisms/mission_planner/TelemetryGrid.vue';
</script>

<template>
  <div class="h-full flex flex-col gap-4">
     
     <WarningBanner 
        title="No mission plan loaded" 
        message="Please create a mission in Mission Planner before starting." 
     />

     <MissionControlCard class="flex-1" />

     <TelemetryGrid />

  </div>
</template>
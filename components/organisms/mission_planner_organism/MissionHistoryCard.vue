<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import Button from '~/components/atoms/Button.vue';
import IconHistory from '~/components/atoms/IconHistory.vue';
import MissionStatusBadge from '~/components/molecules/mission_plan_molecules/MissionStatusBadge.vue';
import MissionListItem from '~/components/molecules/mission_plan_molecules/MissionListItem.vue';
import MissionListEmpty from '~/components/molecules/mission_plan_molecules/MissionListEmpty.vue';

const missions = ref([]); 

const isMissionActive = ref(false); 
</script>

<template>
  <BaseCard class="h-full flex flex-col">
    
    <div class="flex items-center justify-between mb-2 border-b border-gray-100 pb-1">
      <div class="text-sm font-bold text-gray-800 flex items-center gap-1">
        <IconHistory />
        Mission History
      </div>
      <MissionStatusBadge :isActive="isMissionActive" />
    </div>

    <div class="flex-1 overflow-y-auto mb-2 min-h-0 pr-1 custom-scrollbar">
      
      <MissionListEmpty v-if="missions.length === 0" />

      <div v-else class="space-y-2">
         <MissionListItem 
           v-for="(mission, index) in missions" 
           :key="index"
           :id="mission.id"
           :date="mission.date"
         />
      </div>

    </div>

    <div class="mt-auto">
      <Button class="hover:scale-105 hover:bg-[#557516] w-full text-white py-3 rounded font-bold shadow flex items-center justify-center gap-2 text-sm font-poppins transition">
        Load Mission Plan
      </Button>
    </div>

  </BaseCard>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e0e0e0;
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #bdbdbd;
}
</style>
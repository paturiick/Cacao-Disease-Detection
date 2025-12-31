<script setup>
import { reactive } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import LabeledInput from '~/components/molecules/LabeledInput.vue';

// Reactive state ensures inputs are functional but start empty
const params = reactive({
  altitude: '',
  speed: '',
  waypoints: '',
  mode: ''
});
</script>

<template>
  <BaseCard>
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
        </svg>
      </template>
      Flight Parameters
    </SectionHeader>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
       
       <LabeledInput 
         label="Altitude (m)" 
         type="number" 
         placeholder="e.g. 100" 
         v-model="params.altitude" 
       />
       
       <LabeledInput 
         label="Speed (m/s)" 
         type="number" 
         placeholder="e.g. 15" 
         v-model="params.speed" 
       />
       
       <LabeledInput 
         label="Number of Waypoints" 
         type="number" 
         placeholder="e.g. 5" 
         v-model="params.waypoints" 
       />
       
       <LabeledInput 
         label="Flight Mode" 
         type="text"
         placeholder="e.g. Stabilize" 
         v-model="params.mode" 
       />

    </div>
  </BaseCard>
</template>
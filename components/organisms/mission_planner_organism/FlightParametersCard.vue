<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import LabeledInput from '~/components/molecules/LabeledInput.vue';

defineProps(['modelValue']);
defineEmits(['update:modelValue']);
</script>

<template>
  <BaseCard class="bg-white/95 backdrop-blur-sm">
    <SectionHeader>
        <template #icon><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg></template>
        Flight Parameters
    </SectionHeader>
    
    <div class="grid grid-cols-2 gap-4 mt-4">
      <LabeledInput v-model="modelValue.altitude" label="Altitude (m)" type="number" />
      <LabeledInput v-model="modelValue.speed" label="Speed (cm/s)" type="number" />
      <LabeledInput v-model="modelValue.mode" label="Flight Mode" class="col-span-2" />
      
      <div class="col-span-2 flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg mt-2">
        <div class="flex flex-col">
          <span class="text-sm font-bold text-slate-700">Downward Camera</span>
          <span class="text-[10px] text-slate-500 font-medium">Enable Mission Pad detection</span>
        </div>
        
        <label class="relative inline-flex items-center cursor-pointer">
          <input type="checkbox" v-model="modelValue.missionPad" class="sr-only peer">
          <div class="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#658D1B]"></div>
        </label>
      </div>
      
    </div>
  </BaseCard>
</template>
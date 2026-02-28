<script setup>
import { reactive, computed, ref, watch } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import Button from '~/components/atoms/Button.vue';

const props = defineProps(['commandOptions']);
const emit = defineEmits(['add']);

const newCommand = reactive({ type: '', val: '' });

// 1. Removed speed from the initial parameters
const goParams = reactive({ x: 0, y: 0, z: 0 });

const errorMessage = ref(''); 

const currentCmdDetails = computed(() => {
  return props.commandOptions.find(c => c.value === newCommand.type) || { unit: '' };
});

watch(() => newCommand.type, () => {
  errorMessage.value = '';
});

const handleAdd = () => {
  errorMessage.value = ''; 

  if (!newCommand.type) {
    errorMessage.value = "Please select a command type.";
    return;
  }

  if (newCommand.type === 'go') {
    // 2. Only extracting x, y, z
    const { x, y, z } = goParams;

    if (x < -500 || x > 500 || y < -500 || y > 500 || z < -500 || z > 500) {
      errorMessage.value = "Safety Error: Coordinates must be between -500 and 500.";
      return;
    }

    if (x > -20 && x < 20 && y > -20 && y < 20 && z > -20 && z < 20) {
      errorMessage.value = "Safety Error: X, Y, and Z cannot all be between -20 and 20 at the same time.";
      return;
    }

    // 3. Removed speed validation and updated the emitted string
    emit('add', { type: 'go', val: `${x} ${y} ${z}` });
    
    // 4. Reset only x, y, z
    goParams.x = 0; goParams.y = 0; goParams.z = 0; 
  } 
  else {
    if (!newCommand.val) {
      errorMessage.value = "Please enter a valid duration or value.";
      return;
    }
    emit('add', { ...newCommand }); 
    newCommand.val = ''; 
  }
};
</script>

<template>
  <BaseCard class="bg-white/95 backdrop-blur-sm">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      </template>
      Add Command
    </SectionHeader>

    <div class="mt-4 space-y-4">
      
      <div class="flex flex-col group">
        <label class="text-gray-600 text-sm font-medium mb-1.5">Command Type</label>
        <select v-model="newCommand.type" class="w-full border border-gray-300 rounded-md px-4 py-2.5 text-sm bg-white focus:border-[#658D1B] focus:ring-1 outline-none">
          <option value="" disabled>Select Command</option>
          <option v-for="opt in commandOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <div v-if="newCommand.type === 'go'" class="grid grid-cols-2 gap-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
        <div class="col-span-2 text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">Target Coordinates</div>
        
        <div class="flex flex-col"><label class="text-xs text-gray-600 mb-1">X (-500 to 500)</label><input type="number" v-model="goParams.x" class="border border-gray-300 rounded px-3 py-2 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
        <div class="flex flex-col"><label class="text-xs text-gray-600 mb-1">Y (-500 to 500)</label><input type="number" v-model="goParams.y" class="border border-gray-300 rounded px-3 py-2 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
        
        <div class="flex flex-col col-span-2"><label class="text-xs text-gray-600 mb-1">Z (-500 to 500)</label><input type="number" v-model="goParams.z" class="border border-gray-300 rounded px-3 py-2 text-sm outline-none focus:border-[#658D1B] focus:ring-1" /></div>
      </div>

      <div v-else class="flex flex-col group">
        <label class="text-gray-600 text-sm font-medium mb-1.5">Duration/Distance ({{ currentCmdDetails.unit }})</label>
        <div class="flex relative">
          <input type="number" v-model="newCommand.val" min="1" class="w-full border border-gray-300 rounded-md px-4 py-2.5 pr-12 text-sm outline-none focus:border-[#658D1B] focus:ring-1" />
          <div class="absolute right-0 top-0 bottom-0 px-3 flex items-center bg-gray-50 border-l border-gray-300 rounded-r-md text-gray-500 text-xs font-bold">{{ currentCmdDetails.unit }}</div>
        </div>
      </div>

      <div v-if="errorMessage" class="bg-red-50 text-red-600 border border-red-200 p-3 rounded-md text-xs font-medium flex items-center gap-2 shadow-sm animate-pulse hover:animate-none transition-all">
        <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <span>{{ errorMessage }}</span>
      </div>

      <div class="pt-2">
        <Button @click="handleAdd" class="w-full bg-[#658D1B] hover:bg-[#557516] text-white font-bold py-3 rounded shadow-sm text-xs uppercase tracking-wide">+ Add Step</Button>
      </div>
      
    </div>
  </BaseCard>
</template>
<script setup>
import { reactive, computed } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import Button from '~/components/atoms/Button.vue';

const props = defineProps(['commandOptions']);
const emit = defineEmits(['add']);

const newCommand = reactive({ type: '', val: '' });

const currentCmdDetails = computed(() => {
  return props.commandOptions.find(c => c.value === newCommand.type) || { unit: '' };
});

const handleAdd = () => {
  if(newCommand.type && newCommand.val) {
    emit('add', { ...newCommand }); // Pass copy
    newCommand.val = ''; // Reset val only
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

      <div class="flex flex-col group">
        <label class="text-gray-600 text-sm font-medium mb-1.5">Duration ({{ currentCmdDetails.unit }})</label>
        <div class="flex relative">
          <input type="number" v-model="newCommand.val" min="1" class="w-full border border-gray-300 rounded-md px-4 py-2.5 pr-12 text-sm outline-none focus:border-[#658D1B] focus:ring-1" />
          <div class="absolute right-0 top-0 bottom-0 px-3 flex items-center bg-gray-50 border-l border-gray-300 rounded-r-md text-gray-500 text-xs font-bold">{{ currentCmdDetails.unit }}</div>
        </div>
      </div>

      <div class="pt-2">
        <Button @click="handleAdd" class="w-full bg-[#658D1B] hover:bg-[#557516] text-white font-bold py-3 rounded shadow-sm text-xs uppercase tracking-wide">+ Add Step</Button>
      </div>
    </div>
  </BaseCard>
</template>
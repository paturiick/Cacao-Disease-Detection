<script setup>
import { ref } from 'vue';
import BaseCard from '~/components/atoms/BaseCard.vue';
import Button from '~/components/atoms/Button.vue';

// State for Tabs
const activeTab = ref('history'); // 'history' or 'inactive'

// Mock Data (Empty initially as requested)
// To see data, populate this array: [{ id: 'MSN-2025-010', date: '2025-12-27 10:30:00' }, ...]
const missions = ref([]); 

// Helper to switch tabs
const setTab = (tab) => {
  activeTab.value = tab;
};
</script>

<template>
  <BaseCard class="h-full flex flex-col">
    
    <div class="flex items-center space-x-4 mb-4 border-b border-gray-100">
      <button 
        @click="setTab('history')"
        class="text-sm font-bold pb-2 flex items-center gap-1 transition-colors relative"
        :class="activeTab === 'history' ? 'text-gray-800' : 'text-gray-400 hover:text-gray-600'"
      >
        <svg v-if="activeTab === 'history'" class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
        Mission History
        <div v-if="activeTab === 'history'" class="absolute bottom-0 left-0 w-full h-[2px] bg-gray-800"></div>
      </button>

      <button 
        @click="setTab('inactive')"
        class="text-sm font-bold pb-2 px-1 transition-colors relative"
        :class="activeTab === 'inactive' ? 'text-gray-800' : 'text-gray-400 hover:text-gray-600'"
      >
        Mission Inactive
        <div v-if="activeTab === 'inactive'" class="absolute bottom-0 left-0 w-full h-[2px] bg-gray-800"></div>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto mb-4 min-h-0 pr-1 custom-scrollbar">
      
      <div v-if="missions.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400 space-y-2 opacity-60">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        <span class="text-sm font-medium">No missions recorded</span>
      </div>

      <div v-else class="space-y-3">
         <div v-for="(mission, index) in missions" :key="index" class="bg-[#F1F8E9] p-3 rounded border border-gray-100 hover:border-[#AED581] transition cursor-pointer">
           <div class="text-xs text-gray-500 font-bold">{{ mission.id }}</div>
           <div class="text-sm font-medium text-gray-800">{{ mission.date }}</div>
         </div>
      </div>

    </div>

    <div class="mt-auto">
      <Button class="w-full bg-[#AED581] hover:bg-[#9CCC65] text-white py-3 rounded font-bold shadow-sm transition font-poppins">
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
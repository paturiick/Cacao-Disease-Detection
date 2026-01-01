<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import MissionHistoryItem from '~/components/atoms/report/MissionHistoryItem.vue';

// Accepts an array of history objects as placeholder data
defineProps({
  historyList: {
    type: Array,
    required: true,
    // Example shape: { id: 'MSN-123', date: '...', selected: false }
  }
});
</script>

<template>
  <BaseCard class="h-full flex flex-col overflow-hidden">
    <div class="mb-4 border-b border-gray-100 pb-3 shrink-0">
      <h3 class="font-bold text-gray-700 font-poppins text-lg">Mission History</h3>
    </div>
    
    <div class="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin">
      <MissionHistoryItem 
        v-for="(item, index) in historyList" 
        :key:="index"
        :id="item.id"
        :date="item.date"
        :is-selected="item.selected"
      />
    </div>
  </BaseCard>
</template>
<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import MissionHistoryItem from '~/components/atoms/report/MissionHistoryItem.vue';

defineProps({
  historyList: {
    type: Array,
    required: true
  }
});
</script>

<template>
  <BaseCard class="h-full flex flex-col overflow-hidden">
    <div class="mb-4 border-b border-gray-100 pb-3 shrink-0">
      <SectionHeader class="!mb-0">
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </template>
        Mission History
      </SectionHeader>
    </div>

    <div v-if="historyList.length > 0" class="flex-1 overflow-y-auto space-y-3 pr-1 scrollbar-thin">
      <MissionHistoryItem
        v-for="(item, index) in historyList"
        :key="index"
        :id="item.id"
        :date="item.date"
        :is-selected="item.selected"
      />
    </div>

    <div v-else class="flex-1 flex flex-col items-center justify-center text-gray-400 py-8">
      <svg class="w-10 h-10 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
      <p class="text-xs font-medium text-center uppercase tracking-widest text-gray-400">No missions recorded</p>
    </div>
  </BaseCard>
</template>
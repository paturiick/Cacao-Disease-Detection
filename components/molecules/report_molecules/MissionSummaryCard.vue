<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import DataLabelValue from '~/components/atoms/report/DataLabelValue.vue';
import StatusBadge from '~/components/atoms/report/StatusBadge.vue';
import ExportButton from '~/components/atoms/report/ExportButton.vue';

defineProps({
  data: { type: Object, required: true }
});
</script>

<template>
  <BaseCard>
    <div class="flex flex-wrap items-center justify-between gap-4 mb-5 border-b border-gray-100 pb-4">
      <SectionHeader class="!mb-0">
        <template #icon>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </template>
        Mission Summary
      </SectionHeader>
      <div class="flex items-center gap-3">
        <StatusBadge />
        <ExportButton />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-5">
      <DataLabelValue label="Mission ID" :value="data.id" />
      <DataLabelValue label="Duration" :value="data.duration">
        <template #icon>
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </template>
      </DataLabelValue>
      <DataLabelValue label="Start Time" :value="data.startTime" />
      <DataLabelValue label="End Time" :value="data.endTime" />
    </div>
  </BaseCard>
</template>
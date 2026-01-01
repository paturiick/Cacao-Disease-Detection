<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import DataLabelValue from '~/components/atoms/report/DataLabelValue.vue';
import StatusBadge from '~/components/atoms/report/StatusBadge.vue';
import ExportButton from '~/components/atoms/report/ExportButton.vue';
import IconReport from '~/components/atoms/IconReport.vue';

// Accepts placeholder object for summary data
defineProps({
  data: { type: Object, required: true }
});
</script>

<template>
  <BaseCard>
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6 border-b border-gray-100 pb-4">
      <div class="flex items-center gap-2">
        <div class="w-5 h-5 text-gray-600">
           <IconReport />
        </div>
        <h3 class="font-bold text-gray-700 font-poppins text-sm">Mission Summary</h3>
      </div>
      <div class="flex items-center gap-3">
        <StatusBadge />
        <ExportButton />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-6">
      <DataLabelValue label="Mission ID" :value="data.id" />
      <DataLabelValue label="Duration" :value="data.duration">
        <template #icon>
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </template>
      </DataLabelValue>
      <DataLabelValue label="Start Time" :value="data.startTime" />
      <DataLabelValue label="End Time" :value="data.endTime" />
    </div>
  </BaseCard>
</template>
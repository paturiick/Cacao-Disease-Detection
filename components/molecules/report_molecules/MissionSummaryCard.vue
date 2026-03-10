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
      </DataLabelValue>
      <DataLabelValue label="Start Time" :value="data.startTime" />
      <DataLabelValue label="End Time" :value="data.endTime" />
    </div>
  </BaseCard>
</template>
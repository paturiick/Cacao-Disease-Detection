<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import DataField from '~/components/atoms/DataField.vue';
import IconGPS from '~/components/atoms/IconGPS.vue';

defineProps({
  data: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <BaseCard class="h-full">
    <div class="flex items-center gap-2 mb-4 border-b border-gray-100 pb-2">
      <div class="w-5 h-5 text-gray-600">
         <IconGPS />
      </div>
      <h3 class="font-bold text-gray-700 font-poppins text-sm">GPS Data</h3>
    </div>

    <div class="space-y-3">
      <DataField label="Latitude" :value="data.lat.toFixed(6) + '°'" />
      <DataField label="Longitude" :value="data.lng.toFixed(6) + '°'" />
      <DataField label="Altitude" :value="data.alt.toFixed(1) + ' m'" />
      <DataField label="Accuracy" :value="data.accuracy + ' m'" />
      <DataField label="Speed" :value="data.speed.toFixed(1) + ' m/s'" />
      <DataField label="Heading" :value="data.heading.toFixed(0) + '°'" />
    </div>
  </BaseCard>
</template>
<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import DataField from '~/components/atoms/DataField.vue';
import IconGPS from '~/components/atoms/IconGPS.vue';
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
      <DataField label="Latitude" value="37.774900°" />
      <DataField label="Longitude" value="-122.419400°" />
      <DataField label="Altitude" value="125.4 m" />
      <DataField label="Accuracy" value="2.1 m" />
      <DataField label="Speed" value="14.8 m/s" />
      <DataField label="Heading" value="245°" />
    </div>
  </BaseCard>
</template>
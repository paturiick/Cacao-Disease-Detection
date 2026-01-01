<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import IconMap from '~/components/atoms/IconMap.vue';
import MapCanvas from '~/components/atoms/MapCanvas.vue'; // Using the new Atom

defineProps({
  gpsData: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <BaseCard class="h-full flex flex-col">
    <div class="flex items-center gap-2 mb-4 border-b border-gray-100 pb-2 shrink-0">
      <div class="w-5 h-5 text-gray-600">
         <IconMap />
      </div>
      <h3 class="font-bold text-gray-700 font-poppins text-sm">Live Map View</h3>
    </div>

    <div class="flex-1 min-h-[400px] relative rounded-lg overflow-hidden border border-gray-200">
      <MapCanvas 
        :heading="gpsData.heading" 
        :lat="gpsData.lat"
        :lng="gpsData.lng"
      />
    </div>
  </BaseCard>
</template>
<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import StatTile from '~/components/atoms/report/StatTile.vue';

// Accepts placeholder object for detection stats
defineProps({
  stats: { type: Object, required: true }
});
</script>

<template>
  <BaseCard>
    <div class="mb-4">
      <h3 class="font-bold text-gray-700 font-poppins text-sm">Detection Statistics</h3>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <StatTile label="Total Cacao Pods Detected" :value="stats.totalDetected" color-class="bg-[#658D1B]/10 text-[#3E2723]" />
      <StatTile label="Cacao Pods (Unhealthy)" :value="stats.unhealthy" color-class="bg-[#C60C0C]/10 text-[#C60C0C]" />
    </div>
  </BaseCard>
</template>
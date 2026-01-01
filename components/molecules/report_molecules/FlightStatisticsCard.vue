<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import StatTile from '~/components/atoms/report/StatTile.vue';

// Accepts placeholder object for flight stats
defineProps({
  stats: { type: Object, required: true }
});
</script>

<template>
  <BaseCard>
    <div class="mb-4">
      <h3 class="font-bold text-gray-700 font-poppins text-sm">Flight Statistics</h3>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <StatTile label="Total Distance" :value="stats.distance" color-class="bg-blue-50 text-blue-900">
        <template #icon><svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg></template>
      </StatTile>
      
      <StatTile label="Average Altitude" :value="stats.altitude" color-class="bg-green-50 text-green-900" />
      <StatTile label="Average Speed" :value="stats.speed" color-class="bg-purple-50 text-purple-900" />
      <StatTile label="Waypoints Completed" :value="stats.waypoints" color-class="bg-orange-50 text-orange-900" />
      <StatTile label="Photos Captured" :value="stats.photos" color-class="bg-pink-50 text-pink-900" />
      <StatTile label="Battery Used" :value="stats.battery" color-class="bg-yellow-50 text-yellow-900" />
    </div>
  </BaseCard>
</template>
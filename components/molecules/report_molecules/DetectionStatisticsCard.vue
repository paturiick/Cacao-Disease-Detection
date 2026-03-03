<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import StatTile from '~/components/atoms/report/StatTile.vue';

defineProps({
  stats: { type: Object, required: true }
});
</script>

<template>
  <BaseCard>
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
        </svg>
      </template>
      Detection Statistics
    </SectionHeader>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <StatTile label="Total Cacao Pods Detected" :value="stats.totalDetected" color-class="bg-[#658D1B]/10 text-[#3E2723]">
        <template #icon>
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/></svg>
        </template>
      </StatTile>
      <StatTile label="Cacao Pods (Unhealthy)" :value="stats.unhealthy" color-class="bg-[#C60C0C]/10 text-[#C60C0C]">
        <template #icon>
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        </template>
      </StatTile>
    </div>
  </BaseCard>
</template>
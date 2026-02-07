<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import LabeledInput from '~/components/molecules/LabeledInput.vue';

defineProps(['modelValue']); // expects flightParams object
defineEmits(['update:modelValue']);
</script>

<template>
  <BaseCard class="bg-white/95 backdrop-blur-sm">
    <SectionHeader>
        <template #icon><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg></template>
        Flight Parameters
    </SectionHeader>
    <div class="grid grid-cols-2 gap-4 mt-4">
      <LabeledInput v-model="modelValue.altitude" label="Altitude (m)" type="number" />
      <LabeledInput v-model="modelValue.speed" label="Speed (m/s)" type="number" />
      <LabeledInput v-model="modelValue.mode" label="Flight Mode" class="col-span-2" />
    </div>
  </BaseCard>
</template>
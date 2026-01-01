<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';

defineProps({
  label: String,
  value: String
});
</script>

<template>
  <BaseCard class="flex flex-col justify-center h-24">
    <span class="text-xs font-bold text-gray-500 mb-1 font-inter">{{ label }}</span>
    <span class="text-xl font-bold text-gray-800 font-poppins">{{ value }}</span>
  </BaseCard>
</template>
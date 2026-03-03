<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';

defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true }
});
</script>

<template>
  <BaseCard class="flex items-center gap-4 h-20 px-5 border-l-[3px] border-l-[#40623F] !rounded-l-none overflow-hidden !py-3">
    <div class="w-9 h-9 rounded-lg bg-[#40623F]/10 flex items-center justify-center shrink-0 text-[#40623F]">
      <slot name="icon"></slot>
    </div>
    <div class="min-w-0">
      <p class="text-[10px] font-bold text-gray-400 uppercase tracking-wider leading-none mb-1">{{ label }}</p>
      <p class="text-xl font-bold text-gray-800 font-poppins leading-none truncate">{{ value }}</p>
    </div>
  </BaseCard>
</template>
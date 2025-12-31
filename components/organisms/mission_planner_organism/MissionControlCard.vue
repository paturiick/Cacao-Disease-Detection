<script setup>
import BaseCard from '~/components/atoms/BaseCard.vue';
import SectionHeader from '~/components/atoms/SectionHeader.vue';
import Button from '~/components/atoms/Button.vue';
import RunIcon from '~/components/atoms/RunIcon.vue';
</script>

<template>
  <BaseCard class="h-full flex flex-col justify-between">
    <SectionHeader>
      <template #icon>
        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
      </template>
      Mission Control
    </SectionHeader>
    
    <div class="flex-1 flex items-center justify-center py-4">
      <Button class="w-full text-white py-4 rounded font-bold shadow flex items-center justify-center gap-2 text-sm font-poppins transition">
        <RunIcon />
        Run Mission Plan
      </Button>
    </div>
  </BaseCard>
</template>